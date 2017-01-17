from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import datetime

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'SyncMRLGoogleCal'


def get_credentials():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def getSevenDayInterval():
	min_date = datetime.date.today()
	min_time = datetime.time.min

	max_date = datetime.date.today() + datetime.timedelta(days=6)
	max_time = datetime.time.max

	min_datetime = datetime.datetime.combine(min_date, min_time)
	max_datetime = datetime.datetime.combine(max_date, max_time)
	
	return (min_datetime, max_datetime)

def retrieveCalendarIds():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    page_token = None
    while True:
        calendarIds = service.calendarList().list(pageToken=page_token).execute()
        for id in calendarIds['items']:
            print('%s: %s is %s' % (id['summary'], id['id'], id['accessRole']))

        page_token = calendarIds.get('nextPageToken')
	if not page_token:
	    break
    return None

def retrieveEventIds():
	credentials = get_credentials()
	http = credentials.authorize(httplib2.Http())
	service = discovery.build('calendar','v3',http=http)

	calendarId = 'l56c950i3e1mh73ebab9ovqark@group.calendar.google.com'	
	sevenDayInterval = getSevenDayInterval()

	page_token = None
	while True:
		eventIds = service.events().list(calendarId=calendarId,pageToken=page_token).execute()
		for id in eventIds['items']:
			print('%s' % id['id'])
		page_token = eventIds.get('nextPageToken')
		if not page_token:
			break
	return None


def insertEvent():
	credentials = get_credentials()
	http = credentials.authorize(httplib2.Http())
	service = discovery.build('calendar','v3',http=http)

	
	calendarId = 'l56c950i3e1mh73ebab9ovqark@group.calendar.google.com'
	eventBody = {
		'summary': 'New Thing',
		'start': {
			'dateTime': '2017-01-16T12:00:00-07:00',
			'timeZone': 'America/Los_Angeles',
		},
		'end': {
			'dateTime': '2017-01-16T14:00:00-07:00',
			'timeZone': 'America/Los_Angeles',
		},
	}
	event = service.events().insert(calendarId=calendarId,body=eventBody).execute()
	return None


def eraseWeek():
	return None

def updateSchedule(schedule):
	calendarId = 's3tsbjjflit084riito75lkvc@group.calendar.google.com'

	eraseWeek()
	for schedule_entry in schedule:
		# insertSchedule(schedule_entry)
		break
	return None

if __name__ == '__main__':
    retrieveCalendarIds()
