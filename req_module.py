
import os
import json
import time
import requests
import pyperclip
import pyautogui
import webbrowser
from bs4 import BeautifulSoup

import utils

import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

_DBJSON = './resources/db.json'

HEADERS = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebkit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'}

with open('./resources/chrome_path.txt', 'r') as cp:
    CHROME_PATH = r'%s' % cp.read()

AUTOSCOUT_URL = 'https://www.autoscout24.ch/de/autos/'
ANIBIS_URL = 'https://www.anibis.ch/fr/c/automobiles-voitures-de-tourisme'

# main search thread
def search_thread():

    fields_input = utils.load_database()

    # check each item for updates and collect links
    links = []
    for item in fields_input['searches']:
        if item['status']:
            url = autoscout_generate_url(item)
            temp_urls = req_fetch(url)
            for link in temp_urls:
                links.append(link)

            url = anibis_generate_url(item)
            temp_urls = req_fetch(url)
            for link in temp_urls:
                links.append(link)

    # send notification
    if links:
        send_mail(links)

# generate autoscout url for parameters
def autoscout_generate_url(search_item) -> str:

    # read makes file
    makes_dict = utils.load_makes('autoscout24_ch')

    url_param = ''

    # get make and model id
    for make in makes_dict:
        if make['n'] == search_item['manufacturer'].lower():
            make_id = make['i']
            url_param = make['n'] + '?make=' + make_id
            for model in make['models']:
                if model['m'] == search_item['model'].lower():
                    model_id = model['v']
                    url_param = make['n'] + '--' + model['m'] + '?make=' + make_id + '&model=' + model_id

    # add model version
    if search_item['version'] != '':
        url_param += '&typename=' + search_item['version']

    # price
    price = search_item['price'].split(' - ')
    if price[0] != '':
        url_param += '&pricefrom=' + price[0]
    if price[1] != '':
        url_param += '&priceto=' + price[1]

    # registration
    reg = search_item['registration'].split(' - ')
    if reg[0] != '':
        url_param += '&yearfrom=' + reg[0]
    if reg[1] != '':
        url_param += '&yearto=' + reg[1]

    # mileage
    mileage = search_item['mileage'].split(' - ')
    if mileage[0] != '':
        url_param += '&kmfrom=' + mileage[0]
    if mileage[1] != '':
        url_param += '&kmto=' + mileage[1]

    url_param += '&vehtyp=10'

    return AUTOSCOUT_URL + url_param

# generate anibis url for parameters
def anibis_generate_url(search_item) -> str:

    # read makes file
    makes_dict = utils.load_makes('anibis_ch')

    url_param = ''

    # get make and model id
    for make in makes_dict:
        if make['n'] == search_item['manufacturer'].lower():
            make_id = make['i']
            url_param = '?aidl=' + make_id

    # price
    if search_item['price'] != ' - ':
        price = search_item['price'].split(' - ')
        if price[0] != '':
            url_param += '&aral=834_' + price[0]
        else:
            url_param += '&aral=834_0'
        if price[1] != '':
            url_param += '_' + price[1]
        else:
            url_param += '_0'

    # mileage
    if search_item['mileage'] != ' - ':
        mileage = search_item['mileage'].split(' - ')
        if mileage[0] != '':
            url_param += '%2C832_' + mileage[0]
        else:
            url_param += '%2C832_0'
        if mileage[1] != '':
            url_param += '_' + mileage[1]
        else:
            url_param += '_0'

    # registration
    if search_item['registration'] != ' - ':
        reg = search_item['registration'].split(' - ')
        if reg[0] != '':
            url_param += '%2C833_' + reg[0]
        else:
            url_param += '%2C833_0'
        if reg[1] != '':
            url_param += '_' + reg[1]
        else:
            url_param += '_'

    url_param += '&atxl=13358_'

    # model
    if search_item['model']:
        url_param += '%25' + search_item['model']

    # add model version
    if search_item['version'] != '':
        url_param += '%20' + search_item['version']
    
    url_param += '%25'

    return ANIBIS_URL + url_param

# fetch the url for the listings
def req_fetch(url : str):
    print(url)
    # load json data
    fields_input = utils.load_database()

    if 'autoscout24' in url:
        # generate webbrowser object
        webbrowser.register('chrome', None, webbrowser.GenericBrowser(CHROME_PATH))
        webbrowser.get('chrome').open(url, new=0, autoraise=True)
        time.sleep(4)

        # navigate using shortcuts and transfer clipboard markup to variable
        pyautogui.hotkey('ctrl', 'u')
        time.sleep(2)
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(2)
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(2)
        
        markup = pyperclip.paste()

        pyautogui.hotkey('ctrl', 'w')
        pyautogui.hotkey('ctrl', 'w')

        # parse local variable markup
        soup = BeautifulSoup(markup, "html.parser")

        try:
            # parse listings if any
            containers = soup.find_all('section')
            links = ['https://www.autoscout24.ch' + listing.find('a')['href'] for listing in containers[-1].find_all('article')]
            links = [link for link in links if link not in fields_input['ignored']]
        except IndexError:
            # Captcha raised
            return []

    elif 'anibis' in url:
        page = requests.get(url, headers = HEADERS)
        soup = BeautifulSoup(page.content, 'html.parser')

        links = ['https://www.anibis.ch' + article.find('a')['href'] for article in soup.find_all('article') if article.get_text() != '']
        links = [link for link in links if link not in fields_input['ignored']]

    # add to ignored
    with open(_DBJSON, 'w') as dbjson:
        for link in links:
            fields_input['ignored'].append(link)
        json.dump(fields_input, dbjson)
        dbjson.close()
    return links

# send mail to the address specified in settings
def send_mail(links):
    
    # read settings
    settings = utils.load_settings()

    receiver = settings['receiver']
    sender = settings['email']
    password = settings['password']

    # create message
    message = MIMEMultipart("alternative")
    message["Subject"] = "New listings found"
    message["From"] = "ListingNotifier"
    message["To"] = receiver
    
    message_body = "New listings have been posted up following your indexed search parameters. Here are the links: "
    for link in links:
        message_body += "\n\n%s" % link
    message.attach(MIMEText(message_body, "plain"))

    # set up server and send message
    port = 465
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(sender, password)
        server.sendmail(sender, receiver, message.as_string())
