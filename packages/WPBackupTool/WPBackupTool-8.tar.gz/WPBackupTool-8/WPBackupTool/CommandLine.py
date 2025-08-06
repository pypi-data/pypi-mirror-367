#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse

from WPBackupTool import WPBackupTool
from WPBackupTool.Library.Config import Config
from WPBackupTool.Utils import Logger


def main():
    # parse args
    parser = argparse.ArgumentParser(description='Create a backup of your wordpress site!')
    parser.add_argument('--config', required=True, type=str, help='Path to the json-config-file')
    parser.add_argument('--skip_db', action='store_true', help='Skip db-backup?')
    parser.add_argument('--skip_ftp', action='store_true', help='Skip ftp-backup?')
    parser.add_argument('--multithreading', action='store_true', help='Do all Backups in parrallel?')
    parser.add_argument('--logging', action='store_true', help='Write logs?')

    args = parser.parse_args()

    config_file = args.config

    config = Config.from_config_file(config_file)

    Logger.LOGGING = args.logging

    wordpressBackup = WPBackupTool(config, args.skip_db, args.skip_ftp, args.multithreading)

    wordpressBackup.start_job()


if __name__ == "__main__":
    main()
