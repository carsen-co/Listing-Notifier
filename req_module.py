
import json
import time
import pyperclip
import pyautogui
import webbrowser
from bs4 import BeautifulSoup

_DBJSON = './resources/db.json'
_MAKESJSON = './resources/makes.json'
CHROME_PATH = r'C:\Users\markh\AppData\Local\Google\Chrome\Application\chrome.exe'
BASE_URL = 'https://www.autoscout24.ch/de/autos/'

# main search thread
def search_thread():

    with open(_DBJSON) as dbjson:
        fields_input = json.load(dbjson)
        dbjson.close()

    for item in fields_input['searches']:
        url = generate_url(item)
        response = req_fetch(url)

# generate url for parameters
def generate_url(search_item) -> str:

    # read makes file
    with open(_MAKESJSON, 'r', encoding="utf-8", newline='') as mjson:
        data = mjson.read()
        makes_dict = (json.loads(data))
        makes_dict = makes_dict['autoscout24_ch']
        mjson.close()

    url_param = ''

    # get make and model id
    for make in makes_dict:
        if make['n'] == search_item['manufacturer']:
            make_id = make['i']
            url_param = make['n'] + '?make=' + make_id
            for model in make['models']:
                if model['m'] == search_item['model']:
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

    return BASE_URL + url_param

def req_fetch(url : str):

    # generate webbrowser object
    webbrowser.register('chrome', None, webbrowser.GenericBrowser(CHROME_PATH))
    webbrowser.get('chrome').open(url, new=0, autoraise=True)
    time.sleep(10)

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

    containers = soup.find_all('section')
    for listing in containers[-1].find_all('article'):
        link = listing.find('a')['href']
        print('https://www.autoscout24.ch' + link)

# running tests
if __name__ == '__main__':

    search_thread()
