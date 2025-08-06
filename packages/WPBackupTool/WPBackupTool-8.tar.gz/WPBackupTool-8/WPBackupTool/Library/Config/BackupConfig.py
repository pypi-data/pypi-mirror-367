from WPBackupTool.Library.Config.DBConfig import DBConfig
from WPBackupTool.Library.Config.FTPConfig import FTPConfig


class BackupConfig:
    def __init__(self, backup_name, backup_path, db_configs, ftp_config):
        self.backup_name = backup_name
        self.backup_path = backup_path
        self.db_configs = db_configs
        self.ftp_config = ftp_config

    @staticmethod
    def from_config(config):
        configs = []
        try:
            for config_item in config:
                backup_name = config_item['backup_name']
                if backup_name is None:
                    raise AttributeError()

                backup_path = config_item['backup_path']
                if backup_path is None:
                    raise AttributeError()

                db_configs = DBConfig.from_config(config_item)
                ftp_config = FTPConfig.from_config(config_item)

                configs.append(BackupConfig(backup_name, backup_path, db_configs, ftp_config))
        except:
            raise AttributeError("Incorrect formatted config-file")

        return configs