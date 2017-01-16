import mechanicalsoup
import GCalHelper

def loginMRL():
	user = 'user'
	pass = 'password'
	website = 'https://cmmserv.mrl.illinois.edu/schedule/login.asp'
	
	browser = mechanicalsoup.Browser()
	login_page = browser.get(website)
	login_form = login_page.soup.select('form')[0]

	login_form.select('#usrID')[0]['value'] = user
	login_form.select('#usrPswd')[0]['value'] = pass

	home_page = browser.submit(login_form, login_page.url)

	return home_page.soup

def findScheduleForWeek(homePage):
	schedule_div = homePage.find(text='Scheduled sessions in the next 7 days').parent.parent
	schedule_rows = schedule_div.find_all('tr')
	schedule = []

	for row in schedule_rows:
		columns = row.find_all('td')
		schedule_item = []
		
		for column in columns:
			schedule_item.append(column.string)

		schedule.append(schedule_item)
	
	schedule.pop(0)
	for item in schedule:
		item.pop(3)
	
	return schedule

def updateSchedule(schedule):
	GCalHelper.eraseWeek()
	GCalHelper.insertSchedule(schedule)
	return None


if __name__ == '__main__':
	homePage = loginMRL()
	schedule = findScheduleForWeek(homePage)
	updateSchedule(schedule)
	return None
