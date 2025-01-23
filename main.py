import pyicloud
from pyicloud import PyiCloudService
import os
from dotenv import load_dotenv
import sys
from datetime import datetime, timedelta
import smtplib

# get .env file values
load_dotenv()
appleID = os.getenv("APPLE_ID")
password = os.getenv("PASSWORD")
name = os.getenv("NAME")
carrier = os.getenv("CARRIER")
number = os.getenv("NUMBER")
fake_email = os.getenv("FAKE_EMAIL")
fake_pw = os.getenv("FAKE_PW")
app_password = os.getenv("APP_PW")

# save credentials for icloud
api = PyiCloudService(appleID, password)

# uses 2 factor authentication
if api.requires_2fa:
    print("Two-factor authentication required.")
    code = input("Enter the code you received of one of your approved devices: ")
    result = api.validate_2fa_code(code)
    print("Code validation result: %s" % result)

    if not result:
        print("Failed to verify security code")
        sys.exit(1)

    if not api.is_trusted_session:
        print("Session is not trusted. Requesting trust...")
        result = api.trust_session()
        print("Session trust result %s" % result)

        if not result:
            print("Failed to request trust. You will likely be prompted for the code again in the coming weeks")
elif api.requires_2sa:
    import click
    print("Two-step authentication required. Your trusted devices are:")

    devices = api.trusted_devices
    for i, device in enumerate(devices):
        print(
            "  %s: %s" % (i, device.get('deviceName',
            "SMS to %s" % device.get('phoneNumber')))
        )

    device = click.prompt('Which device would you like to use?', default=0)
    device = devices[device]
    if not api.send_verification_code(device):
        print("Failed to send verification code")
        sys.exit(1)

    code = click.prompt('Please enter validation code')
    if not api.validate_verification_code(device, code):
        print("Failed to verify verification code")
        sys.exit(1)

# get the calendar events
now = datetime.now()
start_of_day = datetime(now.year, now.month, now.day, 0, 0, 0)  # Today at 12:00 AM
end_of_day = start_of_day + timedelta(days=1)  # Tomorrow at 12:00 AM

api.calendar.refresh_client()
events = api.calendar.events(start_of_day, end_of_day)
print(start_of_day)
print(end_of_day)
message = ""
if not events:
    message = "No events found for today"
    print("No events found for today")
else:
    # how I actually want it formatted
    message = f"Hi {name}! Here are your events for today:"
    print(f"Hi {name}! Here are your events for today:")
    for event in events:
        # convert time to readable format
        
        event_datettime = datetime(event['startDate'][1], event['startDate'][2], event['startDate'][3], event['startDate'][4], event['startDate'][5])
        readable_time = event_datettime.strftime("%I:%M %p")
        message += f"You have {event['title']} at {readable_time}"
        print(f"You have {event['title']} at {readable_time}")

# send the text message
receiver = number + carrier
auth = (fake_email, app_password)
server = smtplib.SMTP("smtp.gmail.com", 587)
server.starttls()
server.login(auth[0], auth[1])
server.sendmail(auth[0], receiver, message)