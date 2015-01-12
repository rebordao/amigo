#!/usr/bin/env python
'''
This script sends a survey to all the lists' members.
'''

import os
import yaml
import time
import datetime
import smtplib
import email

from email.mime.text import MIMEText

def open_smtp_conn(email_cfg, verbose = True):
    '''
    Opens SMTP connection.
    '''

    # Creates SMTP connection
    if verbose: print "Connecting to SMTP server"
    conn = smtplib.SMTP(email_cfg['smtp_server'])
    conn.starttls()

    # Log in
    if verbose: print "Logging in as '{:s}'".format(email_cfg['username'])
    conn.login(email_cfg['username'], email_cfg['password'])

    return(conn)

def ask_survey(verbose = True, *args):
    '''
    Sends survey to all team members.
    '''

    # Loads template
    today = datetime.datetime.today().strftime('%d-%m-%Y')
    body = open('templates/dev_team.txt', 'rb').read()
    subject = "Today's Survey | {:s} | {:s}".format(today, team['team_name'])

    if verbose: print "Sending survey to team '{:s}'".format(team['team_name'])
    for member in team['members']:

        # Creates survey's email
        email_body = body.format(member['name'], today, cfg['digest_time'])
        survey = MIMEText(email_body, 'plain', 'utf-8')
        survey['Subject'] = subject
        survey['From'] = "'{:s}' <{:s}>".format(
            cfg['email_cfg']['sender_name'], cfg['email_cfg']['sender_email'])
        survey['To'] = "'{:s}' <{:s}>".format(member['name'], member['email'])

        # Sends email according to the member's availability
        if datetime.datetime.today().strftime("%A") in member['availability']:
            smtp_conn.sendmail(from_addr = survey['From'],
                    to_addrs = member['email'], msg = survey.as_string())
            time.sleep(3)

if __name__ == '__main__':

    # Sets working directory
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    # Reads settings
    cfg = yaml.load(open('config.yml', 'rb'))

    # Opens connection to smtp server
    smtp_conn = open_smtp_conn(cfg['email_cfg'])

    # Sends survey to all teams
    for file_name in os.listdir(os.path.join(os.getcwd(), 'lists')):

        # Ignores the team's template (dev_team.yml.EXAMPLE)
        if "EXAMPLE" in file_name:
            continue

        # Reads team's metadata
        team_file = os.path.join(os.getcwd(), 'lists', file_name)
        team = yaml.load(open(team_file, 'rb'))

        # Sends survey to all members of the team
        ask_survey(cfg, smtp_conn, team)

    smtp_conn.quit()
