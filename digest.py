#!/usr/bin/env python
'''
This script builds and sends the survey to all the lists' members.
'''

import os
import re
import yaml
import time
import datetime
import email
import smtplib
import imaplib

from email.mime.text import MIMEText

def open_smtp_conn(email_cfg, verbose = True):
    '''
    Opens SMTP connection.
    '''

    # Creates SMTP connection
    if verbose: print "Connecting to SMTP server..."
    conn = smtplib.SMTP(email_cfg['smtp_server'])
    conn.starttls()

    # Log in
    if verbose: print "Logging in as '{:s}'".format(email_cfg['username'])
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
    if verbose: print "Logging in as '{:s}'".format(email_cfg['username'])
    conn.login(email_cfg['username'], email_cfg['password'])
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

def get_raw_emails(verbose = True, *args):
    '''
    Reads yesterday's replyies.
    '''

    # Opens IMAP conn
    imap_conn = open_imap_conn(cfg['email_cfg'])

    # Builds subject of yesterday
    yesterday = datetime.date.today() - datetime.timedelta(days = 1)
    subject = "{:s} | {:s}".format(
            yesterday.strftime('%d-%m-%Y'), team['team_name'])

    # Gets ids of the emails with that subject
    sta, ids = imap_conn.search(None, '(HEADER Subject "{:s}")'.format(subject))

    # Gets raw emails
    if verbose: print "Reading emails"
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
    raw_emails = get_raw_emails(cfg['email_cfg'], team)

    # Aggregates them into one digest
    digest = ''
    for raw_email in raw_emails:
        digest += raw_email['From'] + '\n' + remove_empty_lines(
                parse_raw_email(raw_email)) + '\n'

    return(digest)

def clean_digest(digest, verbose = True):
    '''
    Preprocess digest.
    '''

    if verbose: print "Cleaning emails"
    clean_digest = ''
    for line in digest.splitlines():
        if (not line.startswith('>') and 
                not "Amigo <reminder@mentis-consulting.be>" in line):
            clean_digest += line + '\n'

    return(clean_digest)

def add_missing_members(team, digest):
    '''
    Adds indication of the members that didn't reply to the survey.
    '''

    print "Adding missing members"
    yesterday = datetime.datetime.today() - datetime.timedelta(days = 1)
    for member in team['members']:
        if (yesterday.strftime("%A") in member['availability'] and 
                not member['email'] in digest):
            digest += "\n{:s} <{:s}>".format(
                member['name'], member['email']) + "\nDid not reply to the survey.\n"
    return(digest)

if __name__ == '__main__':

    # Reads settings
    cfg = yaml.load(open('config.yml', 'r'))

    # Opens connection to smtp server
    smtp_conn = open_smtp_conn(cfg['email_cfg'])

    # Sends survey to all teams
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
        digest = clean_digest(digest)

        # Adding members that didn't reply
        digest = add_missing_members(team, digest)

        # Builds subject of yesterday
        yesterday = datetime.date.today() - datetime.timedelta(days = 1)
        subject = "Digest | {:s} | {:s}".format(
                yesterday.strftime('%d-%m-%Y'), team['team_name'])

        # Sends digest to team
        print "Sending digest to team '{:s}'".format(team['team_name'])
        members = [val for val in team['members']]
        members.append(team['team_leader'])
        for member in members:

            # Creates email headers
            dig_email = MIMEText(digest, 'plain', 'utf-8')
            dig_email['Subject'] = subject
            dig_email['From'] = "'{:s}' <{:s}>".format(
                cfg['email_cfg']['sender_name'], cfg[
                'email_cfg']['sender_email'])
            dig_email['To'] = "'{:s}' <{:s}>".format(
                    member['name'], member['email'])

            # Sends email
            smtp_conn.sendmail(from_addr = cfg['email_cfg']['sender_name'], 
                    to_addrs = member['email'], msg = dig_email.as_string())
            time.sleep(3)

    smtp_conn.quit()
