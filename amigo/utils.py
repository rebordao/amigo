import logging
from typing import Dict
import os
import smtplib

class Utils:

    @staticmethod
    def get_cfg() -> Dict:
        """
        Returns a configuration object needed to access the email server.
        """
        return {
        'email_server': os.getenv('AMIGO_EMAIL_SERVER'),
        'username': os.getenv('AMIGO_USERNAME'),
        'password': os.getenv('AMIGO_PASSWORD')
        }

    @staticmethod
    def init_smtp_conn(cfg: Dict):
        """
        Returns a SMTP connection.
        """
        logging.info("Connecting to SMTP server as {}".format(cfg['username']))
        conn = smtplib.SMTP_SSL(cfg['email_server'], 465) # 465 is smtp port
        conn.login(cfg['username'], cfg['password'])

        return conn