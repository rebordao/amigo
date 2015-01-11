#!/usr/bin/env python
'''
This script sends a survey to all the lists' members.
'''

import os
import yaml
import time
import smtplib
import email

from email.mime.text import MIMEText
from email.header import Header

def open_smtp_conn(email_cfg, verbose = True):
    '''
    Opens SMTP connection.
    '''

    # Creates SMTP connection
    if verbose: print "Connecting to SMTP server"
    conn = smtplib.SMTP(email_cfg['smtp_server'])
    conn.starttls()

    # Log in
    if verbose: print "Logging in as {:s}".format(email_cfg['username'])
    conn.login(email_cfg['username'], email_cfg['password'])

    return(conn)

def ask_survey(verbose = True, *args):
    '''
    Sends survey to all team members.
    '''

    # Loads template
    date = time.strftime('%d-%m-%Y')
    body = open('templates/dev_team.txt', 'rb').read()
    subject = "Today's Survey | {:s} | {:s}".format(date, team['team_name'])

    if verbose: print "Sending survey to team '{:s}'".format(team['team_name'])
    for member in team['members']:

        # Creates survey's email
        body = body.format(member['name'], date, cfg['digest_time'])
        surv_email = MIMEText(body, 'plain', 'utf-8')
        surv_email['Subject'] = Header(subject, 'utf-8')
        surv_email['From'] = Header(cfg['email_cfg']['sender_name'], 'utf-8')
        surv_email['To'] = Header(member['email'], 'utf-8')

        # Sends email
        smtp_conn.sendmail(from_addr = surv_email['From'], 
                to_addrs = member['email'], msg = surv_email.as_string())
        time.sleep(3)

if __name__ == '__main__':

    # Reads settings
    cfg = yaml.load(open('config.yml', 'r'))

    # Opens connection to smtp server
    smtp_conn = open_smtp_conn(email_cfg = cfg['email_cfg'])

    # Sends survey to all teams
    for file_name in os.listdir(os.path.join(os.getcwd(), 'lists')):

        # Reads team's metadata
        team_file = os.path.join(os.getcwd(), 'lists', file_name)
        team = yaml.load(open(team_file, 'r'))

        # Sends survey to all members of the team
        ask_survey(cfg, smtp_conn, team)

    smtp_conn.quit()
