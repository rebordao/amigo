#!/usr/bin/env python
'''
This script sends a survey to all the lists' members.
'''

import os
import csv
import yaml
import time
import smtplib

from email.mime.text import MIMEText
from email.header import Header

def get_smtp_conn(email_cfg):
    '''
    Opens SMTP connection.
    '''

    # Creates SMTP connection
    server = smtplib.SMTP(email_cfg['smtp_server'])
    server.starttls()

    # Log in
    server.login(email_cfg['username'], email_cfg['password'])

    return server

def ask_survey(cfg, smtp_conn, members, list_name):
    '''
    Sends survey to all members.
    '''

    # Loads template
    date = time.strftime('%d/%m/%Y')
    body = open('templates/dev_team.txt', 'rb').read()
    subject = "Today's Survey | {:s} | {:s}".format(date, list_name[:-4])

    for member in members:

        # Creates survey's email
        body = body.format(member[0], date, cfg['digest_time'])
        email = MIMEText(body, 'plain', 'utf-8')
        email['Subject'] = Header(subject, 'utf-8')
        email['From'] = Header(cfg['email_cfg']['sender_name'], 'utf-8')
        email['To'] = Header(member[1], 'utf-8')

        # Sends email
        smtp_conn.sendmail(from_addr = email['From'], 
                to_addrs = member[1], msg = email.as_string())
        time.sleep(3)

if __name__ == '__main__':

    # Reads settings
    cfg = yaml.load(open('config.yml', 'r'))

    # Opens connection to smtp server
    smtp_conn = get_smtp_conn(cfg['email_cfg'])

    # Sends survey to all lists
    for list_name in os.listdir(os.path.join(os.getcwd(), 'lists')):

        # Loads mlist's members, skips the header
        list_file = os.path.join(os.getcwd(), 'lists', list_name)
        members = [mb for mb in csv.reader(open(list_file, 'rb'))][1:]

        # Sends survey to all members of mlist
        ask_survey(cfg, smtp_conn, members, list_name)

    smtp_conn.quit()
