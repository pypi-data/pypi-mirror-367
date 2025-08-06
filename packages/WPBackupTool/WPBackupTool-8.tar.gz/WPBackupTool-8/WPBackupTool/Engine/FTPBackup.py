#!/usr/bin/python
# -*- coding: utf-8 -*-

import ftplib
import os
import sys
import time
import traceback

from WPBackupTool.Utils import Helper
from WPBackupTool.Utils.Logger import Logger

TRANSMISSION_RETRIES = 10

class FTPBackup:

    def __init__(self, backup_name):
        self.backup_name = backup_name

    def downloadFTPFiles(self, ftp, path, destination, root_path, ignore_dirs=None, interval=0.05):
        successful_transmissions = 0
        error_transmissions = 0
        error_filenames = []

        if (ignore_dirs is not None and path in ignore_dirs):
            print("Ignoring path: " + str(path))
            return successful_transmissions, error_transmissions, error_filenames

        try:
            Helper.mkdir_p(destination)
            ftp.cwd(path)
            Logger.log("Created: " + destination, "FTP_BACKUP_"+self.backup_name)
        except OSError:
            pass
        except ftplib.error_perm:
            traceback.print_exc()
            Logger.log("Error: could not change to " + destination, "FTP_BACKUP_"+self.backup_name)
            sys.exit("Ending Application")

        filelist = ftp.nlst()

        for file in filelist:
            ignore_files = [".", ".."]

            if(file in ignore_files):
                continue

            time.sleep(interval)
            try:
                dirPath = path + "/" + file

                if(ignore_dirs is not None and dirPath in ignore_dirs):
                    continue

                ftp.cwd(dirPath)

                successful, errors, error_names = self.downloadFTPFiles(ftp, dirPath + "/", os.path.join(destination, file), root_path, ignore_dirs=ignore_dirs, interval=interval)

                successful_transmissions += successful
                error_transmissions += errors
                error_filenames.extend(error_names)

                ftp.cwd(path)
            except ftplib.error_perm:
                transmission_success = False
                for i in range(1, TRANSMISSION_RETRIES):
                    try:
                        ftp.retrbinary("RETR " + file, open(os.path.join(destination, file), "wb").write)
                        Logger.log("Downloaded: " + file, "FTP_BACKUP_"+self.backup_name)
                        transmission_success = True
                        break
                    except:
                        traceback.print_exc()
                        Logger.log("Error: File could not be downloaded " + file, "FTP_BACKUP_"+self.backup_name)
                        Logger.log("from " + ftp.pwd(), "FTP_BACKUP_"+self.backup_name)
                        Logger.log("to " + destination, "FTP_BACKUP_"+self.backup_name)
                        Logger.log("retrying... ("+str(TRANSMISSION_RETRIES)+")", "FTP_BACKUP_"+self.backup_name)

                if(transmission_success):
                    successful_transmissions += 1
                else:
                    error_transmissions += 1
                    error_filenames.append(dirPath)

        return successful_transmissions, error_transmissions, error_filenames

    def startBackup(self, host, user, password, serverDir, localDir, ignore_dirs=None, interval=0.05):
        try:
            ftp = ftplib.FTP_TLS(host)
            ftp.login(user, password)
            Logger.log("Using FTP over TLS...", "FTPBackup")
        except:
            ftp = ftplib.FTP(host)
            ftp.login(user, password)
            Logger.log("Using FTP...", "FTPBackup")

        return self.downloadFTPFiles(ftp, serverDir, localDir, serverDir, ignore_dirs=ignore_dirs, interval=interval)
