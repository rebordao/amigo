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

def connect_to_server(email_server):
    '''
    Opens connection to the email server.
    '''

    # Creates SMTP connection
    server = smtplib.SMTP(email_server['smtp_server'])
    server.starttls()

    # Log in
    server.login(email_server['username'], email_server['password'])

    return(server)

def ask_survey(cfg, server, members, mlist):
    '''
    Sends survey to all members.
    '''

    # Loads email's template
    date = time.strftime('%d/%m/%Y')
    body = open('templates/dev_team_survey.txt', 'rb').read()
    subject = "Today's Survey | {:s} | {:s}".format(date, mlist[:-4])

    for member in members:

        # Creates survey's email
        body = body.format(member[0], date, cfg['digest_time'])
        email = MIMEText(body, 'plain', 'utf-8')
        email['Subject'] = Header(subject, 'utf-8')
        email['From'] = Header(cfg['email_server']['sender_name'], 'utf-8')
        email['To'] = Header(member[1], 'utf-8')

        # Sends email
        server.sendmail(from_addr = email['From'], to_addrs = member[1],
                msg = email.as_string())
        time.sleep(3)

if __name__ == '__main__':

    # Reads settings
    cfg = yaml.load(open('config.yml', 'r'))

    # Opens connection to the email server
    server = connect_to_server(cfg['email_server'])

    # Sends the survey to all lists
    for mlist in os.listdir(os.path.join(os.getcwd(), 'lists')):

        # Loads mlist's members, skips the header
        list_file = os.path.abspath(os.path.join(os.getcwd(), 'lists', mlist))
        members = [m for m in csv.reader(open(list_file, 'rb'))][1:]

        # Sends the survey to the members
        ask_survey(cfg, server, members, mlist)

    server.quit()
