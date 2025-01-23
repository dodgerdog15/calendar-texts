import schedule
import time
import subprocess
import sys
import os

def run_daily_calendar_script():
    # Use the current script's directory to construct the full path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(current_dir, "main.py")
    
    # Run the script using the default Python interpreter
    subprocess.run(["python3", script_path])


# Schedule the script to run at 9:00 AM daily
schedule.every().day.at("09:00").do(run_daily_calendar_script)

# Keep the script running
while True:
    schedule.run_pending()
    time.sleep(1)