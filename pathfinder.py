import requests
from bs4 import BeautifulSoup
import json
import asyncio
import telegram
from dotenv import load_dotenv
from dataclasses import dataclass, asdict
import os

load_dotenv()

@dataclass
class Wohnung:
    Adresse: str = "Error: Value not found."
    Zimmer: str = "Error: Value not found."
    Wohnfläche: str = "Error: Value not found."
    Kaltmiete: str = "Error: Value not found."
    Link: str = "Error: Value not found."

#Run Counter
COUNTER_PATH = "counter.json"
MAX_RUNS_PER_DAY = 26

def read_counter():
    if not os.path.exists(COUNTER_PATH):
        return 0
    with open(COUNTER_PATH, "r") as file:
        return int(file.read())

def update_counter(counter):
    with open(COUNTER_PATH, "w") as file:
        file.write(str(counter))

def reset_counter():
    update_counter(0)
#Run counter end

def extract_info(div_item):
    # Erstellen einer Instanz der Wohnung-Datenklasse
    result = Wohnung()

    # Adresse extrahieren
    adresse_tag = div_item.find('h2')
    if adresse_tag and adresse_tag.a:
        result.Adresse = adresse_tag.get_text(strip=True)

    # Zimmer, Wohnfläche und Kaltmiete extrahieren
    for text in div_item.stripped_strings:
        if "Zimmer:" in text:
            result.Zimmer = text.split(":")[1].strip()
        elif "Wohnfläche:" in text:
            result.Wohnfläche = text.split(":")[1].strip()
        elif "Kaltmiete:" in text:
            result.Kaltmiete = text.split(":")[1].strip()

    # Link extrahieren
    link_tag = div_item.find('a', class_='mehrinfo')
    if link_tag and 'href' in link_tag.attrs:
        result.Link = "https://www.familienheim-freiburg.de" + link_tag['href']

    return result

def get_saved_results(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_results(file_path, results):
    with open(file_path, 'w') as file:
        json.dump(results, file)

def compare_results(new_results, old_results):
    new_set = {tuple(item.items()) for item in new_results}
    old_set = {tuple(item.items()) for item in old_results}
    return [dict(t) for t in new_set.difference(old_set)]

# Telegram-Benachrichtigungsfunktion
async def send_telegram_message(bot_token, chat_id, message):
    bot = telegram.Bot(bot_token)
    async with bot:
        await bot.send_message(text=message, chat_id=chat_id)

def format_ergebnis_message(ergebnis):
    message = (
        f"Neuer Fund:\n"
        f"Adresse: {ergebnis['Adresse']}\n"
        f"Zimmer: {ergebnis['Zimmer']}\n"
        f"Wohnfläche: {ergebnis['Wohnfläche']}\n"
        f"Kaltmiete: {ergebnis['Kaltmiete']}\n"
        f"Link: {ergebnis['Link']}"
    )
    return message

# Hauptfunktion, die den Bot ausführt
async def run_bot():
    # URL der Webseite und Pfad zur Speicherdatei
    #url = "https://www.familienheim-freiburg.de/wohnungen/vermietung/umland.php"
    url = "https://www.familienheim-freiburg.de/wohnungen/vermietung/freiburg.php#"
    check_url = "https://www.familienheim-freiburg.de/wohnungen/vermietung/freiburg.php#"
    save_file_path = "last_results.json"

    # Telegram Bot Token und Chat ID
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    # Letzte Ergebnisse laden
    old_results = get_saved_results(save_file_path)

    # Webseite abrufen
    response = requests.get(url)

    # Prüfen, ob die Anfrage erfolgreich war
    if response.status_code == 200:
        # HTML-Inhalt der Webseite
        html_content = response.text

        # HTML mit BeautifulSoup parsen
        soup = BeautifulSoup(html_content, 'html.parser')

        # Div-Element mit der ID 'vermietung_uebersicht' finden
        div_content = soup.find('div', id='vermietung_uebersicht')

        # Alle 'div' mit der Klasse 'item' innerhalb von 'vermietung_uebersicht' finden
        items = div_content.find_all('div', class_='item') if div_content else []

        # Ergebnisliste initialisieren
        ergebnisse = []

        # Durchlaufe alle 'div' Elemente der Klasse 'item'
        ergebnisse = [extract_info(item) for item in items]
        ergebnisse_dicts = [asdict(ergebnis) for ergebnis in ergebnisse]

        # Ergebnisse speichern
        save_results(save_file_path, ergebnisse_dicts)

        # Neue Funde prüfen und Benachrichtigungen senden
        new_finds = compare_results(ergebnisse_dicts, old_results)
        if new_finds:
            for find in new_finds:
                formatted_message = format_ergebnis_message(find)
                await send_telegram_message(bot_token, chat_id, formatted_message)
        if not items and counter >= MAX_RUNS_PER_DAY - 1:
            await send_telegram_message(bot_token, chat_id, "Keine Funde auf der Webseite. Check Yourself:\n" + check_url)

        elif items and counter >= MAX_RUNS_PER_DAY - 1:
            await send_telegram_message(bot_token, chat_id, "Heute keine neuen Funde! Check Yourself:\n" + check_url)
    else:
        await send_telegram_message(bot_token, chat_id, "Fehler beim Abrufen der Webseite: Statuscode", response.status_code)

if __name__ == '__main__':
    #Counter einlesen
    counter = read_counter()
    if counter < MAX_RUNS_PER_DAY - 1:
        asyncio.run(run_bot())
        update_counter(counter + 1)
    else:
        asyncio.run(run_bot())
        reset_counter()