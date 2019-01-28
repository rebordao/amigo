#!/usr/bin/env python3
'''
This script builds and sends the survey to all the lists' members.
'''
import os
import logging
from typing import Dict
# import re
# import yaml
# import time
# import datetime
# import email
import smtplib
# import imaplib

# from email.mime.text import MIMEText


def cfg() -> Dict:
    """
    Returns a configuration object needed to access the email server.
    """
    return {
       'email_server': os.getenv('AMIGO_EMAIL_SERVER'),
       'smtp_port': str(os.getenv('AMIGO_SMTP_PORT')),
       'imap_port': str(463),
       'username': os.getenv('AMIGO_USERNAME'),
       'password': os.getenv('AMIGO_PASSWORD')
    }

def open_email_conn(cfg: Dict):
    """
    Returns a SMTP connection.
    """
    logging.info("Connecting to SMTP server")
    smtp_url = cfg['email_server'] + ':' + cfg['smtp_port']
    conn = smtplib.SMTP(smtp_url)
    conn.starttls()

    logging.info("Logging in as '{:s}'".format(cfg['username']))
    conn.login(cfg['username'], cfg['password'])

    return conn

def open_imap_conn(cfg):
    '''
    Opens IMAP connection.
    '''
    # Creates IMAP connection
    logging.info("Connecting to IMAP server")
    conn = imaplib.IMAP4_SSL(cfg['imap_server'])

    # Log in
    logging.info("Logging in as '{:s}'".format(cfg['username']))
    conn.login(cfg['username'], cfg['password'])
    conn.list()

    # Connects to Inbox
    conn.select("inbox")

    return(conn)

def remove_empty_lines(txt):
    '''
    Removes empty lines from a text.
    '''
    return re.sub("\n\s*\n*", "\n", txt)

def parse_raw_email(raw_email):
    '''
    Parses a raw message instance.
    '''
    maintype = raw_email.get_content_maintype()

    if maintype == 'multipart':
        for part in raw_email.get_payload():
            if part.get_content_maintype() == 'text':
                return part.get_payload()
    elif maintype == 'text':
        return(raw_email.get_payload())

def get_raw_emails(*args):
    '''
    Reads yesterday's replies.
    '''
    # Opens IMAP conn
    imap_conn = open_imap_conn(cfg)

    # Creates subject of yesterday
    yesterday = datetime.date.today() - datetime.timedelta(days = 1)
    subject = "{:s} | {:s}".format(
            yesterday.strftime('%d-%m-%Y'), team['team_name'])

    # Gets ids of the emails with that subject
    sta, ids = imap_conn.search(None, '(HEADER Subject "{:s}")'.format(subject))

    # Gets raw emails
    logging.info("Reading emails")
    raw_emails = []
    for eid in ids[0].split():
        status, msg_data = imap_conn.fetch(eid, '(RFC822)')
        for part in msg_data:
            if isinstance(part, tuple):
                raw_emails.append(email.message_from_string(part[1]))

    return(raw_emails)

def build_digest(*args):
    '''
    Builds digest.
    '''
    # Gets raw emails
    raw_emails = get_raw_emails(cfg, team)

    # Aggregates them into one digest
    digest = ''
    emails = []
    for raw_email in reversed(raw_emails):
        if raw_email['From'] in emails:
            continue
        digest += raw_email['From'] + '\n' + remove_empty_lines(
            parse_raw_email(raw_email)) + '\n'
        emails.append(raw_email['From'])

    return(digest)

def clean_digest(*args):
    '''
    Cleans digest.
    '''
    logging.info("Cleaning emails")

    # Cleans the digest by removing quoted lines, etc
    # !!! You may need to edit this method to adapt it to your needs !!!
    clean_digest = ''
    sender = '{:s} <{:s}>'.format(cfg['sender_name'], cfg['sender_email'])
    for line in digest.splitlines():
        if (not line.startswith('>') and not sender in line and
            not "wrote:" in line):
            clean_digest += '\n' + line

    return(clean_digest)

def add_missing_members(team, digest):
    '''
    Adds indication of the members that didn't reply to the survey.
    '''
    logging.info("Adding missing members")
    yesterday = datetime.datetime.today() - datetime.timedelta(days = 1)
    for member in team['members']:
        if (yesterday.strftime("%A") in member['availability'] and
                not member['email'] in digest):
            recipient = "\n{:s} <{:s}>".format(member['name'], member['email'])
            digest +=  recipient + "\nDid not reply to the survey.\n"
    return(digest)

if __name__ == '__main__':

    # Sets working directory
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    # Reads settings
    cfg = yaml.load(open('config.yml', 'r'))

    # Opens connection to smtp server
    smtp_conn = open_smtp_conn(cfg)

    # Sends digest to all teams
    for file_name in os.listdir(os.path.join(os.getcwd(), 'lists')):

        # Ignores the team's template (dev_team.yml.EXAMPLE)
        if "EXAMPLE" in file_name:
            continue

        # Reads team's metadata
        team_file = os.path.join(os.getcwd(), 'lists', file_name)
        team = yaml.load(open(team_file, 'r'))

        # Builds digest
        digest = build_digest(cfg, team)

        # Cleans digest
        digest = clean_digest(cfg, digest)

        # Adds members that didn't reply
        digest = add_missing_members(team, digest)

        # Builds subject
        yesterday = datetime.date.today() - datetime.timedelta(days = 1)
        subject = "Digest | {:s} | {:s}".format(
                yesterday.strftime('%d-%m-%Y'), team['team_name'])

        # Sends digest to team
        logging.info("Sending digest to team '{:s}'".format(team['team_name']))
        members = [val for val in team['members']]
        members.append(team['team_leader'])
        for member in members:

            # Creates email headers
            edigest = MIMEText(digest, 'plain', 'utf-8')
            edigest['Subject'] = subject
            edigest['From'] = "'{:s}' <{:s}>".format(
                cfg['sender_name'], cfg['sender_email'])
            edigest['To'] = "'{:s}' <{:s}>".format(member['name'], member['email'])

            # Sends email
            #smtp_conn.sendmail(
                # from_addr = cfg['sender_name'],
                # to_addrs = member['email'],
                # msg = edigest.as_string())
            time.sleep(3)

    smtp_conn.quit()
