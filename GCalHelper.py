from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import datetime
import dateutil.tz
import rfc3339

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


def getService():
	credentials = get_credentials()
	http = credentials.authorize(httplib2.Http())
	service = discovery.build('calendar', 'v3', http=http)
	
	return service


def getSevenDayInterval():
	min_date = datetime.date.today() + datetime.timedelta(days=1)
	min_time = datetime.time.min

	max_date = datetime.date.today() + datetime.timedelta(days=7)
	max_time = datetime.time.max

	min_datetime = datetime.datetime.combine(min_date, min_time)
	max_datetime = datetime.datetime.combine(max_date, max_time)

	min_datetime = rfc3339.rfc3339(min_datetime,utc=True)
	max_datetime = rfc3339.rfc3339(max_datetime,utc=True)

	return (min_datetime, max_datetime)


def retrieveCalendarIds():
	service = getService()
	
	page_token = None
	while True:
		calendarIds = service.calendarList().list(pageToken=page_token).execute()
		for id in calendarIds['items']:
			print('%s: %s is %s' % (id['summary'], id['id'], id['accessRole']))

		page_token = calendarIds.get('nextPageToken')
		if not page_token:
			break
	return None


def retrieveEventIds(calendarId):
	service = getService()

	sevenDayInterval = getSevenDayInterval()

	event_entries = []

	page_token = None
	while True:
		eventIds = service.events().list(calendarId=calendarId,
					pageToken=page_token,
					timeMin=sevenDayInterval[0],
					timeMax=sevenDayInterval[1]).execute()
		for id in eventIds['items']:
			event_entries.append(id['id'])
		page_token = eventIds.get('nextPageToken')
		if not page_token:
			break
	
	return event_entries


def eraseWeekEvents(calendarId):
	service = getService()
	
	eventIds = retrieveEventIds(calendarId)
	for id in eventIds:
		service.events().delete(calendarId=calendarId, eventId=id).execute()
	return None


def extractDatetime(datetime_string):
	datetime_output = datetime.datetime.strptime(datetime_string, '%m/%d/%Y %H:%M:%S %p')
	datetime_output = datetime_output + datetime.timedelta(days=1)

	return rfc3339.rfc3339(datetime_output,utc=True)


def convertToEvent(schedule_entry):
	eventBody = {}
	eventBody['summary'] = schedule_entry[0]
	eventBody['start'] = {}
	eventBody['end'] = {}
	eventBody['start']['dateTime'] = extractDatetime(schedule_entry[1])
	eventBody['end']['dateTime'] = extractDatetime(schedule_entry[2])
	
	return eventBody


def updateSchedule(schedule):
	service = getService()
	
	calendarId = schedule.pop(0)

	eraseWeekEvents(calendarId)
	
	for schedule_entry in schedule:
		eventBody = convertToEvent(schedule_entry)
		service.events().insert(calendarId=calendarId,
					body=eventBody).execute()

	return None

if __name__ == '__main__':
	calendarId = 'l56c950i3e1mh73ebab9ovqark@group.calendar.google.com'
	eraseWeekEvents(calendarId)
