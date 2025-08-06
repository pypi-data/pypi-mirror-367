from WPBackupTool.Utils import Helper


class FTPConfig:
    def __init__(self, host, username, password, use_sftp, server_dir, ignore_dirs):
        self.host = host
        self.username = username
        self.password = password
        self.use_sftp = use_sftp
        self.server_dir = server_dir
        self.ignore_dirs = ignore_dirs

    @staticmethod
    def from_config(config):
        try:
            if 'ftp_data' not in config:
                return None

            host = config['ftp_data']['host']
            username = config['ftp_data']['user']
            password = config['ftp_data']['password']

            use_sftp = False
            if 'use_sftp' in config['ftp_data']:
                use_sftp = config['ftp_data']['use_sftp']

            server_dir = config['ftp_data']['server_dir']
            ignore_dirs = Helper.get_value_from_dict_path(config, ['ftp_data', 'ignore_dirs'], [])

            if host is None or username is None or password is None or server_dir is None:
                raise AttributeError()

            return FTPConfig(host, username, password, use_sftp, server_dir, ignore_dirs)
        except:
            raise AttributeError("No FTP credentials in config file")