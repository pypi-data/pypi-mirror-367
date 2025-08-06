class DBConfig:
    def __init__(self, host, name, user, password):
        self.host = host
        self.name = name
        self.user = user
        self.password = password

    @staticmethod
    def from_config(config):
        try:
            db_configs = []

            if 'db_data' in config:
                for config in config['db_data']:
                    host = config['host']
                    name = config['db_name']
                    user = config['user']
                    password = config['password']

                    if host is None or name is None or user is None or password is None:
                        raise AttributeError()

                    db_configs.append(DBConfig(host, name, user, password))
            return db_configs
        except:
            raise AttributeError("No DB credentials in config file")