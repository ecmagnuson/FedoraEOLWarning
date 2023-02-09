import json
import re
import requests
import subprocess
from datetime import date, datetime

def fedora_version():
    #Get the current version of Fedora on machine script is ran from
    version = subprocess.getoutput('cat /etc/fedora-release')
    return re.search(r"\d+", version).group()

def EOL(fedora_versions):
    #Get the EOL for the current version of Fedora
    for version in fedora_versions:
        if version["cycle"] == fedora_version():
            EOL = version["eol"]
            eol_date = datetime.strptime(EOL, "%Y-%m-%d").date()
            return eol_date

def dates():
    r = requests.get("https://endoflife.date/api/fedora.json")
    fedora_versions = r.json()
    d = {}
    d["current_version"] = fedora_version()
    d["latest_version"] = fedora_versions[0]["cycle"]
    d["date_now"] = str(date.today())
    d["eol"] = str(EOL(fedora_versions))
    #Bad work around
    #Can't dump datetime, has to be a str
    #But to get the days_till_death need a datetime object
    now = datetime.strptime(d["date_now"], '%Y-%m-%d').date()
    eol = datetime.strptime(d["eol"], '%Y-%m-%d').date()
    d["days_till_death"] = (eol - now).days
    return d

def update_data(d):
    #update the date_now and days_till_death
    d["date_now"] = str(date.today())
    now = datetime.strptime(d["date_now"], '%Y-%m-%d').date()
    eol = datetime.strptime(d["eol"], '%Y-%m-%d').date()
    d["days_till_death"] = (eol - now).days
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=4)

def main():
    try:
        with open("data.json") as f:
            data = json.load(f)

            if data["date_now"] != str(date.today()):
                update_data(data)

        if data['days_till_death'] <= 10:
            title = f"Fedora {data['current_version']} is EOL in {data['days_till_death']} days"
            message = f"Update to {data['latest_version']} by {data['eol']}"
            subprocess.run(f"notify-send '{title}' '{message}'",shell=True)

    except FileNotFoundError:
        data = dates()
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()