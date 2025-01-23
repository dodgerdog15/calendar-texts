import pyicloud
from pyicloud import PyiCloudService
import os
from dotenv import load_dotenv
import sys
from datetime import datetime, timedelta
import smtplib
from caldav import DAVClient
from icalendar import Calendar
 
# get .env file values
load_dotenv()
APPLE_ID = os.getenv("APPLE_ID")
APPLE_SPECIFIC_PASSWORD = os.getenv("APPLE_APP_PW")
NAME = os.getenv("NAME")
CARRIER = os.getenv("CARRIER")
PHONE_NUMBER = os.getenv("NUMBER")
FAKE_EMAIL = os.getenv("FAKE_EMAIL")
FAKE_PASSWORD = os.getenv("FAKE_PW")
APP_PASSWORD = os.getenv("APP_PW")

# convert time to 12 hour format
def convertTime(time):
    return time.strftime("%I:%M %p").lstrip("0")

# get the daily events from the apple calendars
def getDayEvents(calendars):
    today_start = datetime.combine(datetime.today(), datetime.min.time())  # Midnight
    today_end = today_start + timedelta(days=1) - timedelta(seconds=1)    # 11:59 PM
    daily_events = []
    for calendar in calendars:
        events = calendar.date_search(today_start, today_end)
        for event in events:
            cal = Calendar.from_ical(event.data)
            for component in cal.walk('vevent'):
                daily_events.append({
                    'summary': component.get('summary'),
                    'start_time': component.get('dtstart').dt,
                    'end_time': component.get('dtend').dt,
                    'location': component.get('location', 'No location')
                })
    return daily_events

# create a message from the daily events
def getMessage(daily_events):
    message = ""
    if daily_events:
        message = "Today's Events:"
        print("Today's Events:")
        for event in daily_events:
            start = convertTime(event['start_time'])
            end = convertTime(event['end_time'])
            message += f"- {event['summary']} from {start} to {end} (Location: {event['location']})"
            print(f"- {event['summary']} from {start} to {end} (Location: {event['location']})")
    else:
        message = "No events today."
        print("No events today.")
    return message

# get the events from the calendar
def getCalendarEvents():
    client = DAVClient("https://caldav.icloud.com/", username=APPLE_ID, password=APPLE_SPECIFIC_PASSWORD)
    principal = client.principal()
    calendars = principal.calendars()
    daily_events = getDayEvents(calendars)
    message = getMessage(daily_events)
    return message

# send the message using smtplib
def sendMessage(message):
    receiver = PHONE_NUMBER + CARRIER
    auth = (FAKE_EMAIL, APP_PASSWORD)
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(auth[0], auth[1])
    print("Sending message" + message)
    print(auth[0])
    print(receiver)
    try:
        server.sendmail(auth[0], receiver, message)
    except Exception as e:
        print("Error sending message")
        print(e)

# main function
def main():
    message = getCalendarEvents()
    sendMessage(message)
if __name__ == "__main__":
    main()
