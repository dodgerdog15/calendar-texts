import pyicloud
from pyicloud import PyiCloudService
import os
from dotenv import load_dotenv
import sys
from datetime import datetime, timedelta
import smtplib
from caldav import DAVClient
from icalendar import Calendar


def convertTime(time):
    return time.strftime("%I:%M %p").lstrip("0")
# get .env file values
load_dotenv()
appleID = os.getenv("APPLE_ID")
apple_specific_password = os.getenv("APPLE_APP_PW")
name = os.getenv("NAME")
carrier = os.getenv("CARRIER")
number = os.getenv("NUMBER")
fake_email = os.getenv("FAKE_EMAIL")
fake_pw = os.getenv("FAKE_PW")
app_password = os.getenv("APP_PW")

# trying caldav way
client = DAVClient("https://caldav.icloud.com/", username=appleID, password=apple_specific_password)
principal = client.principal()
calendars = principal.calendars()
for calendar in calendars:
    print(calendar.name)

# Define start and end of today
today_start = datetime.combine(datetime.today(), datetime.min.time())  # Midnight
today_end = today_start + timedelta(days=1) - timedelta(seconds=1)    # 11:59 PM

 # Collect events for the day
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

# Print events
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

# send the text message
receiver = number + carrier
auth = (fake_email, app_password)
server = smtplib.SMTP("smtp.gmail.com", 587)
server.starttls()
server.login(auth[0], auth[1])
server.sendmail(auth[0], receiver, message)