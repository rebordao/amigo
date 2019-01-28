# Amigo

## Description

This tool can be used to do daily status updates by email.

It works by emailing your team at 4 PM and each member replies
describing what he/she did during the day. Those replies will
be aggregated into a digest and shared within the team next day at 9.30 AM.

## Notes

The survey’s reply:

- should be brief, preferably by items;
- should refer any success or difficulty faced during the tasks;
- ideally only takes a few seconds to read;
- if a team member sends more than one reply, only the last one is considered;
- needs to be sent from the same email address where it was received;
- empty lines and lines starting with > are ignored.
- signatures need to be removed to avoid being included in the digest.

## Setup

1. Set up your SMTP and IMAP server by filling in the file `cfg.yml.EXAMPLE`.
Then rename it as `cfg.yml`.
1. For each team create a yaml file that follows the template's structure
defined in `templates/dev_team.yml.EXAMPLE`. Instead `dev_team` use the name
of your team. In this file define each member's name, email and availability.
1. Test if the files can be executed by running them directly (`./survey.py`
and `./digest.py`). You may need to change its permissions by
  > `sudo chmod 755 survey.py digest.py`
1. Deploy the code in a serverless setup either in Google Cloud
or AWS with two cronjobs, one for the survey and another for the digest.

  > `0 16 * * 1-5 /path to survey.py`
  > `0 9 30 * 2-6 /path to digest.py`

  This sends the survey every weekday, and the digest on the days when the
  previous day was a weekday (Tuesday, Wednesday, Thursday, Friday, Saturday).

By default the team leader doesn't receive the survey, just the digest. To
overcome this use a dummy email for the team leader's email and add him/her
as a regular team member.

## Dependencies

Environmental variables:

AMIGO_EMAIL_SERVER:
AMIGO_USERNAME:
AMIGO_PASSWORD:

AMIGO_SMTP_PORT: 465
AMIGO_IMAP_PORT: 993

## License

Distributed under a MIT License. Check `LICENSE.md` for details.

## Authors

This tool was written by [Antonio Rebordao](
https://www.linkedin.com/in/rebordao).
