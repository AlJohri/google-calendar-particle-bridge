from __future__ import division

import os, requests, datetime, time, dateutil.parser
from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()

access_token = None
expires_in = None
calendar_list = None

@sched.scheduled_job('interval', hours=1)
def refresh_access_token():
    global access_token, expires_in

    credentials_payload = {
    	"refresh_token": os.getenv('GOOGLE_REFRESH_TOKEN'),
    	"client_id": os.getenv('GOOGLE_CLIENT_ID'),
    	"client_secret": os.getenv('GOOGLE_CLIENT_SECRET'),
    	"grant_type": "refresh_token"
    }

    credentials_response = requests.post("https://www.googleapis.com/oauth2/v3/token", data=credentials_payload).json()
    access_token = credentials_response['access_token']
    expires_in = credentials_response['expires_in']

@sched.scheduled_job('interval', hours=1)
def refresh_calendar_list():
    global calendar_list
    calendar_list = requests.get("https://www.googleapis.com/calendar/v3/users/me/calendarList?access_token=%s" % access_token).json()['items']

est = dateutil.tz.gettz('America/New York')

def process_calendar(calendar):
    print(calendar['id'])

    calendar_payload = {
        "calendarId": calendar['id'],
        "timeMin": datetime.datetime.utcnow().isoformat() + "Z",
        "orderBy": 'startTime',
        "sortOrder": 'ascending',
        "singleEvents": 'true',
        "futureEvents": 'false',
    }

    calendar_response = requests.get("https://www.googleapis.com/calendar/v3/calendars/primary/events?access_token=%s" % access_token, params=calendar_payload).json()['items']

    # skip if no event
    if len(calendar_response) == 0: return None

    current_event = calendar_response[0]

    # skip all day events
    if current_event['start'].get('dateTime') == None: return None

    start_time = dateutil.parser.parse(current_event['start']['dateTime'], ignoretz=True).replace(tzinfo=est)

    if start_time > datetime.datetime.now().replace(tzinfo=est):
        return None
    else:
        end_time = dateutil.parser.parse(current_event['end']['dateTime'], ignoretz=True).replace(tzinfo=est)
        delta = end_time - datetime.datetime.now().replace(tzinfo=est)
        text2send = current_event['summary'] + '|-|-|' + "%f minutes" % (delta.seconds / 60)

    return text2send

def post_to_sparkcore(text2send):
    sparkcore_payload = {
        "access_token": os.getenv('SPARKCORE_ACCESS_TOKEN'),
        "name": "calevents",
        "data": text2send,
        "private": "false",
        "ttl": 0
    }

    resp = requests.post("https://api.particle.io/v1/devices/events", data=sparkcore_payload)

@sched.scheduled_job('interval', minutes=1)
def process_all_calendars():

    texts = []

    for calendar in calendar_list:
        if calendar['accessRole'] != "owner": continue
        text = process_calendar(calendar)
        if text == None:
            print "skipping calendar due to either no event or all day event"
            continue
        texts.append(process_calendar(calendar))

    for text in texts:
        print "--------------------"
        print(text)
        post_to_sparkcore(text)

if __name__ == '__main__':

    refresh_access_token()
    refresh_calendar_list()
    process_all_calendars()

    sched.start()
