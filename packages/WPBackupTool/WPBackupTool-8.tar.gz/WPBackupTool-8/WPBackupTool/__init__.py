import os
import shutil
import time
import traceback
from threading import Thread

from WPBackupTool.Library.MailService import MailService
from WPBackupTool.Library.Model.DBLog import DBLog
from WPBackupTool.Library.Model.FTPLog import FTPLog
from WPBackupTool.Library.Model.LogItem import LogItem
from WPBackupTool.Library.ThreadWithReturnValue import ThreadWithReturnValue
from WPBackupTool.Utils import Helper
from WPBackupTool.Engine.DBBackup import DBBackup
from WPBackupTool.Engine.FTPBackup import FTPBackup
from WPBackupTool.Utils.Logger import Logger
from WPBackupTool.Engine.SFTPBackup import SFTPBackup
from WPBackupTool.Utils.ZipCompression import ZipCompression


class WPBackupTool():
    def __init__(self, config, skip_db=False, skip_ftp=False, multithreading=False):
        self.config = config
        self.multithreading = multithreading
        self.skip_db = skip_db
        self.skip_ftp = skip_ftp

        Logger.log("Skipping db backup: "+str(self.skip_db))
        Logger.log("Skipping ftp backup: "+str(self.skip_ftp))

    def start_job(self):
        results = self.do_website_backups()

        self.send_backup_result_mail(results)

    def send_backup_result_mail(self, results):
        mail_config = self.config.mail_config

        if mail_config is None:
            return

        mail_service = MailService(mail_config.smpt_config,
                                   mail_config.sender_name,
                                   mail_config.sender_mail)

        results_to_report = []
        for result in results:
            if mail_config.only_report_error and result.was_success():
                continue
            results_to_report.append(result)

        mail_service.send_result_mail(mail_config.receiver_name, mail_config.receiver_mail, results_to_report)

    def do_website_backups(self):
        backup_results = []

        if self.multithreading:
            threads = []

            for website_config in self.config.backup_configs:
                thread = ThreadWithReturnValue(target=self.do_website_backup, args=(website_config,))
                threads.append(thread)

            for thread in threads:
                thread.start()

            for thread in threads:
                backup_results.append(thread.join())
        else:
            for website_config in self.config.backup_configs:
                backup_results.append(self.do_website_backup(website_config))

        return backup_results


    def do_website_backup(self, website_config):
        backup_path = website_config.backup_path
        backup_name = website_config.backup_name

        ftp_config = None
        if website_config.ftp_config is not None:
            ftp_config = website_config.ftp_config

        db_configs = None
        if website_config.db_configs is not None:
            db_configs = website_config.db_configs

        if not os.path.isdir(backup_path):
            Helper.mkdir_p(backup_path)

        if not os.path.isdir(os.path.join(backup_path, backup_name)):
            Helper.mkdir_p(os.path.join(backup_path, backup_name))

        backup_child_dir = backup_name + "_" + time.strftime('%Y-%m-%d')
        total_backup_path = os.path.join(backup_path, backup_name, backup_child_dir)

        ftp_backup_path = os.path.join(total_backup_path, backup_name)
        db_backup_path = os.path.join(total_backup_path, "db")

        db_log = None
        ftp_log = None

        try:
            #Create backup directories
            Helper.mkdir_p(ftp_backup_path)
            Helper.mkdir_p(db_backup_path)

            Logger.log("saving sql-files to " + db_backup_path)

            db_log = self.do_db_backups(db_configs, db_backup_path, backup_name)

            ftp_log = self.do_ftp_backup(ftp_config, backup_name, ftp_backup_path)

            backup_path_done = os.path.join(backup_path, backup_name, backup_child_dir + "_done")

            Logger.log(total_backup_path+" ==> "+backup_path_done)

            shutil.move(total_backup_path, backup_path_done)
        except Exception as e:
            traceback.print_exc()
            backup_path_done = None

        log_item = LogItem(backup_name, db_log, ftp_log)

        log_path = self.create_log_file(backup_path, backup_name, log_item)

        Logger.log(log_item.to_string(), self.__class__.__name__)

        if backup_path_done is not None:
            Logger.log("backup path done: " + backup_path_done)
            shutil.move(log_path, backup_path_done)
            if log_item.was_success():
                ZipCompression(backup_path_done).compress(delete_source=True)
            else:
                backup_path_error = os.path.join(backup_path, backup_name, backup_child_dir + "_error")
                shutil.move(backup_path_done, backup_path_error)
        return log_item

    def create_log_file(self, backup_path, backup_name, log_item):
        # log_datei erstellen
        log_path = os.path.join(backup_path, backup_name, backup_name + "_log_" + time.strftime('%Y-%m-%d') + ".txt")
        open(log_path, 'a').close()
        log_file = open(log_path, "w")
        log_file.write(log_item.to_string())
        log_file.close()
        return log_path

    def do_db_backups(self, db_configs, backup_path, backup_name):
        db_log = DBLog()

        if not self.skip_db and db_configs is not None:
            for db in db_configs:
                db_backup = DBBackup(db.host, db.user, db.name, db.password, backup_path, backup_name)
                db_backup_success = db_backup.databaseBackup()

                if (db_backup_success is False):
                    db_log.error(backup_name)
                else:
                    db_log.success(backup_name)

        return db_log

    def do_ftp_backup(self, ftp_config, backup_name, backup_path):
        ftp_log = FTPLog()

        if not self.skip_ftp and ftp_config is not None:
            ignore_dirs = None
            if ftp_config.ignore_dirs is not None:
                ignore_dirs = ftp_config.ignore_dirs

            Logger.log("saving ftp-files to " + backup_path)

            if ftp_config.use_sftp:
                print("Using SFTP...")
                ftp_backup = SFTPBackup(backup_name)
            else:
                print("Using FTP...")
                ftp_backup = FTPBackup(backup_name)

            successful, errors, error_filenames = ftp_backup.startBackup(ftp_config.host, ftp_config.username,
                                                                        ftp_config.password, ftp_config.server_dir,
                                                                        backup_path, ignore_dirs, interval=0.01)
            ftp_log.success(successful)
            ftp_log.error(errors)
            ftp_log.error_files(error_filenames)

            Logger.log("ftp-backup for " + backup_name + " complete. " + str(successful) + \
                  " successful transmissions, " + str(errors) + " errors")

        return ftp_log
