#!/usr/bin/python
# -*- coding: utf-8 -*-

import ftplib
import os
import sys
import time
import traceback
from stat import S_ISDIR

import paramiko

from WPBackupTool import FTPBackup
from WPBackupTool.Utils import Helper
from WPBackupTool.Utils.Logger import Logger

TRANSMISSION_RETRIES = 10

class SFTPBackup(FTPBackup):

    def __init__(self, backup_name):
        super().__init__(backup_name)

    def uploadFTPFilesSFTP(self, sftp, path, destination, root_path, ignore_dirs=None, interval=0.05):
        successful_transmissions = 0
        error_transmissions = 0
        error_filenames = []

        try:
            try:
                sftp.mkdir(destination)
                Logger.log("Created: " + destination, "FTP_BACKUP_"+self.backup_name)
            except:
                Logger.log("file "+destination+" existing", "FTP_BACKUP_"+self.backup_name)
            #os.chdir(destination)
        except OSError:
            pass
        except ftplib.error_perm:
            traceback.print_exc()
            Logger.log("Error: could not change to " + destination, "FTP_BACKUP_"+self.backup_name)
            sys.exit("Ending Application")

        for file in os.listdir(path):
            ignore_files = [".", ".."]

            if(file in ignore_files):
                continue

            time.sleep(interval)
            if(os.path.isdir(os.path.join(path, file))):
                dirPath = path + "/" + file


                if(ignore_dirs is not None and dirPath in ignore_dirs):
                    continue

                successful, errors, error_names = self.uploadFTPFilesSFTP(sftp, dirPath, destination+"/"+file, root_path, ignore_dirs=ignore_dirs, interval=interval)

                successful_transmissions += successful
                error_transmissions += errors
                error_filenames.extend(error_names)
            else:
                Logger.log("Uploading: "+file, "FTP_BACKUP_"+self.backup_name)
                #traceback.print_exc()

                #os.chdir(destination)

                transmission_success = False
                for i in range(1, TRANSMISSION_RETRIES):
                    try:
                        sftp.put(os.path.join(path, file), destination+"/"+file)
                        Logger.log("Uploaded: " + file, "FTP_BACKUP_"+self.backup_name)
                        transmission_success = True
                        break
                    except:
                        traceback.print_exc()
                        Logger.log("Error: File could not be uploaded " + file, "FTP_BACKUP_"+self.backup_name)
                        Logger.log("from " + path, "FTP_BACKUP_"+self.backup_name)
                        Logger.log("to " + destination+"/"+file, "FTP_BACKUP_"+self.backup_name)
                        Logger.log("retrying... ("+str(TRANSMISSION_RETRIES)+")", "FTP_BACKUP_"+self.backup_name)

                if(transmission_success):
                    successful_transmissions += 1
                else:
                    error_transmissions += 1
                    error_filenames.append(dirPath)

        return successful_transmissions, error_transmissions, error_filenames

    def downloadFTPFilesSFTP(self, sftp, path, destination, root_path, ignore_dirs=None, interval=0.05):
        successful_transmissions = 0
        error_transmissions = 0

        error_filenames = []

        if(ignore_dirs is not None and path in ignore_dirs):
            print("Ignoring path: "+str(path))
            return successful_transmissions, error_transmissions, error_filenames

        try:
            Helper.mkdir_p(destination)
            # os.chdir(destination)
            Logger.log("Created: " + destination, "FTP_BACKUP_"+self.backup_name)
        except OSError:
            pass
        except ftplib.error_perm:
            traceback.print_exc()
            Logger.log("Error: could not change to " + destination, "FTP_BACKUP_"+self.backup_name)
            sys.exit("Ending Application")

        Logger.log("current path: "+path, "FTP_BACKUP_"+self.backup_name)
        item_list = sftp.listdir(path)
        destination = str(destination)

        if not os.path.isdir(destination):
            Helper.mkdir_p(destination)

        for item in item_list:
            if self.is_directory(path + "/" + item, sftp):
                successful, errors, error_names = self.downloadFTPFilesSFTP(sftp, path + "/" + item, os.path.join(destination, item), root_path, ignore_dirs, interval)
                successful_transmissions += successful
                error_transmissions += errors
                error_filenames.extend(error_names)
            else:
                transmission_success = False
                for i in range(1, TRANSMISSION_RETRIES):
                    try:
                        sftp.get(path + "/" + item, os.path.join(destination, item))
                        Logger.log("Downloaded: " + path+"/"+item, "FTP_BACKUP_"+self.backup_name)
                        transmission_success = True
                        break
                    except:
                        traceback.print_exc()
                        Logger.log("Error: File could not be downloaded " + item, "FTP_BACKUP_"+self.backup_name)
                        Logger.log("to " + destination, "FTP_BACKUP_"+self.backup_name)
                        Logger.log("retrying... (" + str(TRANSMISSION_RETRIES) + ")", "FTP_BACKUP_"+self.backup_name)

                if (transmission_success):
                    successful_transmissions += 1
                else:
                    error_transmissions += 1
                    error_filenames.append(path + "/" + item)

        return successful_transmissions, error_transmissions, error_filenames

    def is_directory(self, path, sftp):
      try:
        return S_ISDIR(sftp.stat(path).st_mode)
      except IOError:
        #Path does not exist, so by definition not a directory
        return False

    def startBackup(self, host, user, password, serverDir, localDir, ignore_dirs=None, interval=0.05):
        port = 22

        transport = paramiko.Transport(host)
        transport.connect(username = user, password = password)
        sftp = paramiko.SFTPClient.from_transport(transport)

        return self.downloadFTPFilesSFTP(sftp, serverDir, localDir, serverDir, ignore_dirs=ignore_dirs, interval=interval)

    def startUpload(self, host, user, password, serverDir, localDir, ignore_dirs=None, interval=0.05):
        port = 22

        transport = paramiko.Transport(host)
        transport.connect(username=user, password=password)
        sftp = paramiko.SFTPClient.from_transport(transport)

        return self.uploadFTPFilesSFTP(sftp, serverDir, localDir, serverDir, ignore_dirs=ignore_dirs, interval=interval)