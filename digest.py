#!/usr/bin/env python
'''
This script builds and sends the survey to all the lists' members.
'''

import os
import csv
import yaml
import datetime
import time
import email
import re
import smtplib
import imaplib

from email.mime.text import MIMEText
from email.header import Header

def open_smtp_conn(email_cfg, verbose = True):
    '''
    Opens SMTP connection.
    '''

    # Creates SMTP connection
    if verbose: print "Connecting to SMTP server..."
    conn = smtplib.SMTP(email_cfg['smtp_server'])
    conn.starttls()

    # Log in
    if verbose: print "Logging in as {:s}".format(email_cfg['username'])
    conn.login(email_cfg['username'], email_cfg['password'])

    return(conn)

def open_imap_conn(email_cfg, verbose = True):
    '''
    Opens IMAP connection.
    '''

    # Creates IMAP connection
    if verbose: print "Connecting to IMAP server..."
    conn = imaplib.IMAP4_SSL('imap.gmail.com')

    # Log in
    if verbose: print "Logging in as {:s}".format(email_cfg['username'])
    conn.login(email_cfg['username'], email_cfg['password'])
    conn.list()

    # Connects to Inbox
    conn.select("inbox")

    return(conn)

def parse_raw_email(email_instance):
    '''
    Parses a raw message instance..
    '''

    maintype = email_instance.get_content_maintype()

    if maintype == 'multipart':
        for part in email_instance.get_payload():
            if part.get_content_maintype() == 'text':
                return part.get_payload()
    elif maintype == 'text':
        return(email_instance.get_payload())

def get_raw_emails(email_cfg, list_name):
    '''
    Reads yesterday's replyies.
    '''

    # Opens IMAP conn
    imap_conn = open_imap_conn(email_cfg)

    # Builds subject of yesterday
    yesterday = datetime.date.today() - datetime.timedelta(days = 1)
    subject = "{:s} | {:s}".format(yesterday.strftime('%d-%m-%Y'), list_name[:-4])

    # Gets ids of the emails with that subject
    fl, ids = imap_conn.search(None, '(HEADER Subject "{:s}")'.format(subject))

    # Gets raw emails
    raw_emails = []
    for eid in ids[0].split():
        status, msg_data = imap_conn.fetch(eid, '(RFC822)')
        for part in msg_data:
            if isinstance(part, tuple):
                raw_emails.append(email.message_from_string(part[1]))

    return(raw_emails)

def build_digest(cfg, members, list_name):
    '''
    Builds digest.
    '''

    # Gets raw emails
    raw_emails = get_raw_emails(cfg['email_cfg'], list_name)

    # Aggregates them into one digest
    digest = ''
    for raw_email in raw_emails:
        digest = digest + raw_email['From'] + '\n' + remove_empty_lines(
                parse_raw_email(raw_email)) + '\n'

    return(digest)

def remove_empty_lines(txt):
    return re.sub("\n\s*\n*", "\n", txt)

def clean_digest(digest):
    '''
    Cleans digest.
    '''

    clean_digest = ''
    for line in digest.splitlines():
        if not line.startswith('>') and not "Amigo <reminder@mentis-consulting.be>" in line:
            clean_digest = clean_digest + line + '\n'

    return(clean_digest)

if __name__ == '__main__':

    # Reads settings
    cfg = yaml.load(open('config.yml', 'r'))

    # Opens connection to smtp server
    smtp_conn = open_smtp_conn(email_cfg = cfg['email_cfg'])

    for list_name in os.listdir(os.path.join(os.getcwd(), 'lists')):

        # Loads list_name's members, skips header
        list_file = os.path.join(os.getcwd(), 'lists', list_name)
        members = [member for member in csv.reader(open(list_file, 'rb'))][1:]

        # Builds digest
        digest = build_digest(cfg, members, list_name)

        # Cleans digest
        digest = clean_digest(digest)

        # Builds subject of yesterday
        yesterday = datetime.date.today() - datetime.timedelta(days = 1)
        subject = "Digest {:s} | {:s}".format(
                yesterday.strftime('%d-%m-%Y'), list_name[:-4])

        # Sends digest
        for member in members:

            # Creates digest's email
            email = MIMEText(digest, 'plain', 'utf-8')
            email['Subject'] = Header(subject, 'utf-8')
            email['From'] = Header(cfg['email_cfg']['sender_name'], 'utf-8')
            email['To'] = Header(member[1], 'utf-8')

            # Sends email
            smtp_conn.sendmail(from_addr = cfg['email_cfg']['sender_name'],
                    to_addrs = member[1], msg = email.as_string())
            time.sleep(3)

        smtp_conn.quit()
