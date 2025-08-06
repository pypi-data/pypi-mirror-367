import os
import pipes
import time

from WPBackupTool.Utils.Logger import Logger


class DBBackup():
    def __init__(self, db_host, db_user, db_name, db_password, path, backup_name):
        self.db_host = db_host
        self.db_user = db_user
        self.db_name = db_name
        self.db_password = db_password
        self.path = path
        self.backup_name = backup_name

    def databaseBackup(self):
        today_backup_path = os.path.join(self.path, self.db_name+"-"+time.strftime('%Y-%m-%d'))+".sql"

        try:
            os.stat(self.path)
        except:
            os.makedirs(self.path)

        Logger.log("Starting backup of database " + self.db_name, "DB_BACKUP_" + self.db_name)

        mysql_auth = "-h " + self.db_host + " -u " + self.db_user + " -p" + self.db_password + " " + self.db_name

        dumpcmd = "sudo mysqldump "+mysql_auth+" > " + pipes.quote(today_backup_path)
        Logger.log(dumpcmd, "DB_BACKUP_" + self.db_name)
        os.system(dumpcmd)

        success = False
        #Erfolg des Backups prüfen: datei existiert & dateigröße > 0
        if(os.path.isfile(today_backup_path)):
            if(os.path.getsize(today_backup_path) > 0):
                success = True

        return success