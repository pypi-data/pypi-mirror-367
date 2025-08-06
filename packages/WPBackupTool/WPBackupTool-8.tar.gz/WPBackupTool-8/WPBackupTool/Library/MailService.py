import smtplib
import ssl
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from WPBackupTool.Library.Model.LogItem import LogItem
from WPBackupTool.Utils.Logger import Logger


class MailService:
    def __init__(self, smpt_config, sender_name, sender_mail):
        self.smpt_config = smpt_config
        self.sender_name = sender_name
        self.sender_mail = sender_mail

    def send_mail_to_user(self, user, subject, message):
        pass

    def send_mail(self, receiver_name, receiver_mail, subject, message):
        message_data = MIMEMultipart()

        # setup the parameters of the message
        message_data['From'] = self.sender_name + "<" + self.sender_mail + ">"
        message_data['To'] = receiver_name + "<" + receiver_mail + ">"
        message_data['Subject'] = subject

        # add in the message body
        message_data.attach(MIMEText(message, 'html'))

        self.send_mail_data(message_data)

    def send_mail_data(self, message):
        connection = self.setup_server_connection()
        connection.send_message(message)
        connection.quit()

    def setup_server_connection(self):
        context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        server = smtplib.SMTP(self.smpt_config.server, self.smpt_config.port)
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(self.smpt_config.username, self.smpt_config.password)
        return server

    def send_result_mail(self, receiver_name, receiver_mail, results):
        if len(results) is 0:
            Logger.log("Nothing to report", self.__class__.__name__)
            return

        today = date.today()
        subject = "Backup Report ("+str(today.strftime('%d.%m.%Y'))+")"

        message = LogItem.many_to_string(results, html=True)

        self.send_mail(receiver_name, receiver_mail, subject, message)