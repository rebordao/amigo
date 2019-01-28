#!/usr/bin/env python
'''
This script sends a survey to all the lists' members.
'''
import os
import logging
from typing import Dict
import sys
import yaml
import time
from datetime import datetime
import smtplib

from amigo.utils import Utils

# from email.mime.text import MIMEText

def sends_survey(cfg: Dict, smtp_conn, team) -> None:
    """
    Sends survey to all team members.
    """

    # Load survey's template
    body = open('survey_template.txt', 'rb').read().decode('utf-8')

    # Create survey's subject
    today = datetime.today().date().strftime("%d-%m-%Y")
    subject = "Today's Survey | {} | {}".format(today, team['team_name'])

    logging.info("Sending survey to team {}".format(team['team_name']))
    for member in team['members']:

        # Create survey's email
        email_body = body.format(member['name'], today)
        # survey = MIMEText(email_body, 'plain', 'utf-8')
        # survey['Subject'] = subject
        # survey['From'] = "'{:s}' <{:s}>".format(
        #     cfg['sender_name'], cfg['sender_email'])
        # survey['To'] = "'{:s}' <{:s}>".format(member['name'], member['email'])

        # Send email according to the member's availability
        if datetime.today().strftime("%A") in member['availability']:
            pass
            # smtp_conn.sendmail(
            #     from_addr = survey['From'],
            #     to_addrs = member['email'],
            #     msg = survey.as_string())
            time.sleep(0.3)

if __name__ == '__main__':

    # Set working directory
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    # Initialise logger
    logging.basicConfig(
        stream=sys.stdout,
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%Y%m%d %H:%M:%S',
        level='INFO')

    # Read settings
    cfg = Utils.get_cfg()

    # Open connection to smtp server
    smtp_conn = Utils.init_smtp_conn(cfg)

    # Send survey to all teams
    for file_name in os.listdir(os.path.join(os.getcwd(), 'lists')):

        # Ignore the team's template file (dev_team.yml.EXAMPLE)
        if "EXAMPLE" in file_name:
            continue

        # Read team's data
        team_file = os.path.join(os.getcwd(), 'lists', file_name)
        team = yaml.load(open(team_file, 'rb'))

        # Send survey to all members in team
        sends_survey(cfg, smtp_conn, team)

    smtp_conn.quit()
