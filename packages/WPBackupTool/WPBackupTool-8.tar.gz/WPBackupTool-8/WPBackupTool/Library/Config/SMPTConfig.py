class SMPTConfig:
    def __init__(self, server, port, username, password):
        self.server = server
        self.port = port
        self.username = username
        self.password = password

    @staticmethod
    def from_config(config):
        server = config["server"]
        port = config["port"]
        username = config["username"]
        password = config["password"]

        if server is None or port is None or username is None or password is None:
            raise AttributeError()

        return SMPTConfig(server, port, username, password)