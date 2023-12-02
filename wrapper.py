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

def create_cron_job(date, script_path):
    # Befehl zum Erstellen eines einmaligen Cronjobs für den spezifischen Tag
    day = date.day
    month = date.month
    command = f"(crontab -l ; echo '*/30 6-19 {day} {month} * python {script_path}') | crontab -"
    subprocess.run(command, shell=True)

# Hauptlogik des Skripts
today = datetime.datetime.now().date()
specific_date = datetime.date(2024, 1, 1)
country_code = "DE"  # Deutschland
region = "BW"  # Baden-Württemberg
script_path = "/home/pi/pathfinder/wrapper.py"

if is_holiday(today, country_code, region) or is_weekend(today):
    next_day = get_next_weekday(today)
    create_cron_job(next_day, script_path)
    print(next_day, today)
