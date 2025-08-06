from WPBackupTool.Library.Config.SMPTConfig import SMPTConfig


class MailConfig:
    def __init__(self, only_report_error, smpt_config, sender_name, sender_mail, receiver_name, receiver_mail):
        self.only_report_error = only_report_error
        self.smpt_config = smpt_config
        self.sender_name = sender_name
        self.sender_mail = sender_mail
        self.receiver_name = receiver_name
        self.receiver_mail = receiver_mail

    @staticmethod
    def from_config(config):
        only_report_error = False
        if 'only_report_error' in config:
            only_report_error = config['only_report_error']

        smpt_config = SMPTConfig.from_config(config["smpt"])

        sender_name = config["sender"]["name"]
        sender_mail = config["sender"]["mail"]
        receiver_name = config["receiver"]["name"]
        receiver_mail = config["receiver"]["mail"]

        if sender_name is None or sender_mail is None or receiver_name is None or receiver_mail is None:
            return None

        return MailConfig(only_report_error, smpt_config, sender_name, sender_mail, receiver_name, receiver_mail)