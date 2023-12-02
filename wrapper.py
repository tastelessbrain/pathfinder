from dotenv import load_dotenv
import os
import datetime
import requests
import subprocess

load_dotenv()
CAL_API = os.getenv("CAL_API")

def is_weekend(date):
    return date.weekday() > 4

def is_holiday(date, country_code, region):
    api_url = "https://calendarific.com/api/v2/holidays"
    api_key = CAL_API
    params = {
        "api_key": api_key,
        "country": country_code,
        "year": date.year,
        "location": region
    }

    response = requests.get(api_url, params=params)
    holidays = response.json().get('response', {}).get('holidays', [])
    
    return any(hol['date']['iso'] == date.isoformat() for hol in holidays)

def get_next_weekday(date):
    next_day = date + datetime.timedelta(days=1)
    while is_weekend(next_day):
        next_day += datetime.timedelta(days=1)
    return next_day

def remove_tempjobs(current_crontab):
    # Entfernt alle Cron-Einträge, die mit #tempjob markiert sind
    return '\n'.join(line for line in current_crontab.splitlines() if "#tempjob" not in line)

def create_cron_job(date, script_path):
    day = date.day
    month = date.month
    new_cron_entry = f"*/30 6-19 {day} {month} * python {script_path} #tempjob"

    current_crontab = subprocess.check_output("crontab -l", shell=True).decode()
    
    # Zählen, wie viele #tempjob Einträge vorhanden sind
    tempjob_count = current_crontab.count("#tempjob")

    # Wenn zwei oder mehr #tempjob Einträge existieren, entferne sie alle
    if tempjob_count >= 2:
        current_crontab = remove_tempjobs(current_crontab)

    # Hinzufügen des neuen Cronjobs
    updated_crontab = f"{current_crontab}\n{new_cron_entry}"
    subprocess.run(f"echo '{updated_crontab}' | crontab -", shell=True)


# Hauptlogik des Skripts
today = datetime.datetime.now().date()
#Specific Date for Debugging
specific_date = datetime.date(2023, 12, 1)
country_code = "DE"  # Deutschland
region = "BW"  # Baden-Württemberg
script_path = "/home/pi/pathfinder/wrapper.py"

if is_holiday(today, country_code, region) or is_weekend(today):
    next_day = get_next_weekday(today)
    create_cron_job(next_day, script_path)
    print(next_day, today)
else:
    # Pfad zur pathfinder.py im gleichen Projektordner
    pathfinder_path = os.path.join(os.path.dirname(script_path), "pathfinder.py")
    subprocess.run(["python", pathfinder_path])
    print("Bot Exec finished.")