# Amigo

## Description

This tool helps synchronizing a team, promotes transparency and communication.
It emails your team at 4 PM, each member replies describing what he/she did 
during the day, then those replies will be aggregated into a digest and 
shared within the team next day at 9 AM.

## Notes

About the survey’s reply:

- should be brief, preferably by items;
- should refer any success or difficulty faced during the tasks;
- should take less than 30 seconds to read and 10 minutes to write;
- if a team member sends more than one reply, only the last one is considered;
- empty lines and lines starting with > are ignored.

## Setup

1. Set up your SMTP and IMAP server by filling in the file `cfg.yml.EXAMPLE`. 
Then rename it as `cfg.yml`.
2. For each team create a yaml file that follows the template's structure 
defined in `templates/dev_team.yml.EXAMPLE`. Instead `dev_team` use the name
of your team. In this file define each member's name, email and availability.
3. Test if the files can be executed by running them directly (`./survey.py` 
and `./digest.py`). You may need to change its permissions by 

  > `sudo chmod 755 survey.py digest.py`

4. Now add two cronjobs, one for the survey and another for the digest.

  > crontab -e

  and add to the end of the `crontab` the following lines:

  > `0 16 * * 1-5 /path to survey.py`  
  > `0 9 * * 2-6 /path to digest.py`

  This sends the survey every weekday, and the digest on the days when the 
  previous day was a weekday (Tuesday, Wednesday, Thursday, Friday, Saturday).

The team leader by default doesn't receive the survey, just the digest. To 
overcome this use a dummy email for the team leader's email and add him/her 
as a regular team member.

## Dependencies

Our production system is a Debian Stable LTS and we had `pyaml` as a dependency.

## License

Distributed under a MIT License. Check `LICENSE.md` for details.

## Authors

This tool was written by [Antonio Rebordao](
https://www.linkedin.com/in/rebordao).
