#import required modules
from dotenv import load_dotenv
import os
import datetime
import requests
import subprocess

#import .env file
load_dotenv()

##############################################################################

#Date and Holiday functions
def is_weekend(date):
    return date.weekday() > 4

#Copy paste out of Calendarific Doku.
def is_holiday(date, country_code, region):
    api_url = "https://calendarific.com/api/v2/holidays"
    api_key = os.getenv("CAL_API")
    params = {
        "api_key": api_key,
        "country": country_code,
        "year": date.year,
        "location": region
    }

    response = requests.get(api_url, params) #params=
    holidays = response.json().get('response', {}).get('holidays', [])
    
    return any(hol['date']['iso'] == date.isoformat() for hol in holidays)

def get_next_workday(date):
    next_day = date + datetime.timedelta(days=1)
    while is_weekend(next_day) or is_holiday(next_day, country_code, region):
        next_day += datetime.timedelta(days=1)
    return next_day
#End of Copy and Paste

def remove_tempjobs(current_crontab):
    # Entfernt alle Cron-Einträge, die mit #tempjob markiert sind
    filtered_lines = []
    for line in current_crontab.splitlines():
        if "#tempjob" not in line:
            filtered_lines.append(line)
    return '\n'.join(filtered_lines)

def create_cron_job(date, wrapper_path):
    day = date.day
    month = date.month
    #Check if CRONJOB is correct
    new_cron_entry = f"*/30 6-17 {day} {month} * python3 {wrapper_path} #tempjob"

    # Aktuelle Crontabs auslesen
    current_crontab = subprocess.check_output("crontab -l", shell=True).decode()
    # Zählen, wie viele #tempjob Einträge vorhanden sind
    tempjob_count = current_crontab.count("#tempjob")
    # Wenn ein oder mehr #tempjob Einträge existieren, entferne sie alle
    if tempjob_count > 0:
        current_crontab = remove_tempjobs(current_crontab)
    # Hinzufügen des neuen Cronjobs
    updated_crontab = f"{current_crontab}\n{new_cron_entry}"
    subprocess.run(f'echo "{updated_crontab}" | crontab -', shell=True)

##############################################################################
    
#Hauptlogik des Skripts
today = datetime.datetime.now().date()
#Specific Date for Debugging
#!today = datetime.date(2023, 12, 15)
country_code = "DE"  # Deutschland
region = "BW"  # Baden-Württemberg
wrapper_path = os.path.expanduser("~/pathfinder/wrapper.py")            #needs to be checked 

if is_holiday(today, country_code, region) or is_weekend(today):
    next_date = get_next_workday(today)
    create_cron_job(next_date, wrapper_path)
else:
    # Pfad zur pathfinder.py im gleichen Projektordner
    pathfinder_path = os.path.expanduser("~/pathfinder/pathfinder.py")
    subprocess.run(["/usr/bin/python3", pathfinder_path])
    print("Bot Exec finished.")