from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os import getenv
from smtplib import SMTP_SSL

from dotenv import load_dotenv


def send_email(to: str, subject: str, text: str) -> bool:
    """
    Sends an email using smtp_ssl
    :param to: target e-mail address
    :param subject: subject of an email
    :param text: text of an email
    :return: is sending successful
    """
    load_dotenv()  # load environment
    addr_from = getenv('FROM')
    password = getenv('PASSWORD')
    msg = MIMEMultipart()

    msg['From'] = addr_from
    msg['To'] = to
    msg['Subject'] = subject
    msg['Content-Type'] = 'text/plai'
    msg['MIME-Version'] = '1.0'
    msg['charset'] = 'utf-8'
    # set params to the message
    try:
        msg.attach(MIMEText(text, 'plain'))  # add text
        with SMTP_SSL(getenv('SMTP_HOST'), port=int(getenv("SMTP_PORT"))) as server:  # creating a sender
            server.login(addr_from, password)  # login
            server.send_message(msg)
    except Exception as e:
        if e:
            pass
        return False
    return True
