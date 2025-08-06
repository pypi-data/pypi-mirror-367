# WPBackupTool
A Wordpress Backup Tool

#Usage
WPBackupTool --config=[PATH_TO_CONFIG_JSON] [--skip_db] [--skip_ftp] [--multithreading] [--logging]

Example Config-file:
[
  {
    "use_sftp": "true",
    "ftp_data": {
      "host": "ftp.example.com",
      "user": "ftp",
      "password": "123",
      "server_dir": "PATH_TO_WEBSITE"
    },
    "db_data": [
      {"host": "sql.example.com", "user": "sql", "db_name": "database", "password": "1234"}
    ],
    "backup_name": "MyWebsite",
    "backup_path": "C:\\website_backups\\MyWebsite"
  }
]
