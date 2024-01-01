import os #import os for .env and paths
from dotenv import load_dotenv #import .env file loader
import datetime #import datetime for timehandling
import requests #import requests for html handling
from bs4 import BeautifulSoup #import bs4 for html, xml and json handling
import json #import jsaon for bs4 to be able to handle json
from dataclasses import dataclass, asdict #import dataclasses for flat object and dictionary for json conversion
from urllib.parse import urljoin #import urljoin for correct "/" handling in urls
#import dataclasses #no idea why this is needed but it is for the uuid4 to work
#import uuid #import uuid for flat object id generation | not really necessary at this scale also i can use other fields for unique identification for example the string of the linkin the link is unique
import telegram #import telegram bot library for telegram message handling
import asyncio #on my scale not really necessary but needed for telegram message handling to work

load_dotenv() #load .env file

############################################
@dataclass
class Wohnung:
    Adresse: str = "Error: Value not found."
    Zimmer: str = "Error: Value not found."
    Wohnfläche: str = "Error: Value not found."
    Kaltmiete: str = "Error: Value not found."
    Kontakt: str = "Error: Value not found."
    Mail: str = "Error: Value not found."
    Telefon: str = "Error: Value not found."
    Link: str = "Error: Value not found."
    #id: str = "Error: Value not found."    #not really necessary at this scale also i can use other fields for unique identification for example the string of the linkin the link is unique
    found: str = "Error: Value not found."  #not yet needed either but could be used for more detailed messages | also prevents a flat from getting ignored if it os online again after some time
############################################

############################################
#run counter for end of day message && result counter
run_counter_path = os.path.expanduser("~/pathfinder/run_counter.json") #path to run counter
max_runs_per_day = 24 #!Configurable max runs per day | needs to be adjusted if cronjob is changed
result_counter_path = os.path.expanduser("~/pathfinder/result_counter.json") #path to result counter

#read the counter
def read_counter(counter_path):
    if not os.path.exists(counter_path): #if run counter file does not exist return 0
        return 0
    with open(counter_path, "r") as file: #in every other case return the value of the run counter file as integer
        return int(file.read())
    
#update the counter
def update_counter(new_counter_value, counter_path):
    with open(counter_path, "w") as file: #write the value of the run counter to the run counter file
        file.write(str(new_counter_value))
############################################
        
############################################
##############Result handdling##############

#dayly result counter for end of day message

#could be replaced by a more general counter function
#got replaced by a more general counter function | look in the section above

#Read and save search results
def read_saved_search_results():
    try:
        with open(os.path.expanduser("~/pathfinder/saved_search_results.json"), "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        return []
    
#read_saved_search_results = read_saved_search_results() #read the saved search results
    
#function to check if a flat is already in the saved search results
#def in_search_results(flat):
#    for saved_flat in read_saved_search_results(): #for every flat in the saved search results | this logic could lead to performance issues on larger scales
#        if flat == saved_flat: #if the flat is already in the saved search results return true
#            return True
#    return False #if the flat is not in the saved search results return false

def in_search_results(flat):
    for saved_flat in read_saved_search_results():
        # Compare only the specified fields
        if (flat['Adresse'] == saved_flat['Adresse'] and
            flat['Zimmer'] == saved_flat['Zimmer'] and
            flat['Wohnfläche'] == saved_flat['Wohnfläche'] and
            flat['Kaltmiete'] == saved_flat['Kaltmiete'] and
            flat['Link'] == saved_flat['Link'] and
            flat['found'] == saved_flat['found']):
            return True
    return False

#add new search result to saved search results | check for performance issues
def add_new_search_result(flat):
    saved_search_results = read_saved_search_results() #read the saved search results
    saved_search_results.append(flat) #add the new search result to the saved search results
    with open(os.path.expanduser("~/pathfinder/saved_search_results.json"), "w") as file: #write the new search results to the search results file
        json.dump(saved_search_results, file)
############################################

############################################
########html, xlml, and json handling#######

#request url
def visit_url(url):
    return requests.get(url)

#get html of response, beautify and make it readable with bs4 (get rid of whitespaces and stuff)
def get_html(recived_request):
    recived_request.text
    beautified_html = BeautifulSoup(recived_request.text, 'html.parser')
    return beautified_html

#function to take xlml and a searchterm to extract and return its value
def extract_value_from_xlml(xlml, searchterm):
    for text in xlml.stripped_strings:
        if searchterm in text:
            return text.split(":")[1].strip()
    return "Error: Value not found."

#construct a flat object from a div item
def construct_flat_from_div_item(div_item):
    # Erstellen einer Instanz der Wohnung-Datenklasse
    result = Wohnung()

    # Adresse extrahieren
    adresse_tag = div_item.find('h2')                                   #look into unicode handling because of ß
    if adresse_tag and adresse_tag.a:
        result.Adresse = adresse_tag.get_text(strip=True)

    # Zimmer, Wohnfläche und Kaltmiete extrahieren
    result.Zimmer = extract_value_from_xlml(div_item, "Zimmer:")
    result.Wohnfläche = extract_value_from_xlml(div_item, "Wohnfläche:") #look into unicode handling because of \u00b2 is becoming \u00c2\u00b2
    result.Kaltmiete = extract_value_from_xlml(div_item, "Kaltmiete:")
    result.found = str(datetime.datetime.now().date())

    # Link extrahieren
    link_tag = div_item.find('a', class_='mehrinfo')
    if link_tag and 'href' in link_tag.attrs:
        #TODO: check / handling in urljoin and strucutre of link_tag in live environment
        base_url = "https://www.familienheim-freiburg.de/wohnungen/vermietung/" #base url for live environment
        #!base_url = "http://localhost/wohnungen/vermietung/" #base url for local testing
        result.Link = urljoin(base_url, link_tag['href'])
    
    #id generieren
    #result.id = str(uuid.uuid4())

    return result

#extract the phone number from the asp div/detail page
def extract_phone_number(asp_div):
    # Get all the text nodes in the asp_div div
    text_nodes = asp_div.find_all(string=True)
    # Filter out empty strings and strip whitespace
    text_nodes = [text.strip() for text in text_nodes if text.strip()]
    # The phone number is likely to be the text node that contains a '/'
    phone_number = next((text for text in text_nodes if '/' in text and '-' in text), None)
    if phone_number:
        # If a phone number is found, remove all whitespaces, "/" and "-"
        phone_number = phone_number.replace(' ', '').replace('/', '').replace('-', '')
        return phone_number
    # If no phone number is found, return None
    return None

############################################

############################################
##########telegram message handling#########

#construct a flat result message from a flat object
def construct_flat_result_message(flat):
    message = (
        f"Neue Wohnung gefunden!\n"
        f"Adresse: {flat['Adresse']}\n"
        f"Wohnfläche: {flat['Wohnfläche']}\n"
        f"Zimmer: {flat['Zimmer']}\n"
        f"Kaltmiete: {flat['Kaltmiete']}\n"
        f"Kontakt: {flat['Kontakt']}\n"
        f"Mail: {flat['Mail']}\n"
        f"Telefon: {flat['Telefon']}\n"
        f"Link: {flat['Link']}\n"
    )
    return message

def construct_end_of_day_message():
    no_new_flats_message = (
        f"End of day message:\n"
        f"Es wurden leider keine neuen Wohnungen gefunden.\n"
        f"Check yourself: https://www.familienheim-freiburg.de/wohnungen/vermietung/freiburg.html\n"
        f"Good night!"
    )
    new_flats_message = (
        f"End of day message:\n"
        f"Es wurden {read_counter(result_counter_path)} neue Wohnungen gefunden.\n"
        f"See in the Messages above for more information.\n"
        f"Good night!"
    )
    if read_counter(result_counter_path) > 0:
        update_counter(0, result_counter_path) #reset the result counter
        return new_flats_message
    elif read_counter(result_counter_path) == 0:
        return no_new_flats_message

#send a telegram message through the bot | api token and chat id are stored in .env file
async def send_telegram_message(message):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    bot = telegram.Bot(bot_token)
    reply_markup = telegram.InlineKeyboardMarkup([[telegram.InlineKeyboardButton("Reply", callback_data="reply")]])
    async with bot:
        await bot.send_message(text=message, chat_id=chat_id, reply_markup=reply_markup)
############################################

############################################
###############Main_Script##################

#if config file does not exist create it
if not os.path.exists(os.path.expanduser("~/pathfinder/config.json")):
    #ask for config values #!API Token and Chat ID are setup in .env file
    config = {}
    config['Nachname'] = input("Nachname: ")
    config['Vorname'] = input("Vorname: ")
    config['Mail'] = input("Mail: ")
    config['Telefon'] = int(input("Telefon: 0-9 ohne +49 "))
    config['Maximale Kaltmiete'] = int(input("Maximale Kaltmiete: In Euro ohne € Zeichen "))
    config['Minimale Wohnfläche'] = int(input("Minimale Wohnfläche: In Quadratmeter ohne m² Zeichen "))
    config['Minimum Zimmer'] = int(input("Minimum Zimmer: (ganze Zahlen) "))

    #write config to config file
    with open(os.path.expanduser("~/pathfinder/config.json"), "w") as file:
        json.dump(config, file)
    
    print("...Config file created.\nSetup completed. Please restart the script.")
    exit
else:
    #read config file
    with open(os.path.expanduser("~/pathfinder/config.json"), "r") as file:
        config = json.load(file)

    ############################################

    #increase the run counter by 1
    update_counter(read_counter(run_counter_path) + 1, run_counter_path)

    #Array of current new search results
    new_results = []

    #get the html of freiburg overview page
    #live url
    freiburg_req = visit_url("https://www.familienheim-freiburg.de/wohnungen/vermietung/freiburg.html")
    #local url for testing
    #!freiburg_req = visit_url("http://localhost/wohnungen/vermietung/freiburg2.html")

    #check if request was successful
    if freiburg_req.status_code == 200:
        #get the whole div with id vermietung_uebersicht | every flat is in there with class=item
        vermietung_uebersicht = get_html(freiburg_req).find('div', id='vermietung_uebersicht')

        #get flats as array  still as xml | if no flat rerurn empty array
        found_flats_xml = vermietung_uebersicht.find_all('div', class_='item') if vermietung_uebersicht else []

        #convert flats to class
        found_flats_classes = [construct_flat_from_div_item(flat) for flat in found_flats_xml]
        found_flats_json = [asdict(flat) for flat in found_flats_classes]

        #TODO: print(found_flats_classes)   #find better way of debugging
        #TODO: print(found_flats_json)      #find better way of debugging

        #check for every flat if it is in the already known search results
        for flat in found_flats_json:
            if in_search_results(flat):
                #if the flat is already known i ignore it and print a message for debugging
                print("Flat already in search results. Ignoring it.")

            else:
                #add the flat to the new results array && increase the result counter by 1
                update_counter(read_counter(result_counter_path) + 1, result_counter_path)
                new_results.append(flat)

        #now get the missing information from the detail page
        for result in new_results:
            #get the html of the detail page
            detail_req = visit_url(result['Link'])

            #check if request was successful
            if detail_req.status_code == 200:
                asp_div = get_html(detail_req).find('div', class_='asp')

                #get and add the name, mail and phone number from the asp div
                asp_name = asp_div.find('strong').get_text(strip=True)
                result['Kontakt'] = asp_name
                asp_mail = asp_div.find('a').get('href').strip('mailto:') #strip mailto: from the mail as it is not needed
                result['Mail'] = asp_mail
                asp_phone = extract_phone_number(asp_div)
                result['Telefon'] = asp_phone

            else:                
                #send telegram message | not yet implemented
                asyncio.run(send_telegram_message(f"An Error occured while trying to get the detail page of a flat. Statuscode: {detail_req.status_code} {result['Link']}"))

            #save the new search results to saved_search_results.json
            add_new_search_result(result)

            #send telegram message with flat information.
            asyncio.run(send_telegram_message(construct_flat_result_message(result)))

        #end of day message handling && reset run counter
        if read_counter(run_counter_path) == max_runs_per_day:
            #send telegram message with end of day message
            asyncio.run(send_telegram_message(construct_end_of_day_message()))
            #reset the run counter
            update_counter(0, run_counter_path)
    else:
        #telegram Nachricht senden
        asyncio.run(send_telegram_message(f"An Error occured while trying to get the overview page of the flats. Statuscode: {freiburg_req.status_code} \n {freiburg_req.url}"))
        exit
