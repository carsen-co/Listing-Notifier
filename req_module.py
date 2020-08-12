
import json
import requests
from bs4 import BeautifulSoup

_DBJSON = './resources/db.json'
_MAKESJSON = './resources/makes.json'

HEADERS = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebkit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'}

# main search thread
def search_thread():

    with open(_DBJSON) as dbjson:
        fields_input = json.load(dbjson)
        dbjson.close()

    for item in fields_input['searches']:
        url = generate_url(item)
        #response = fetch(url)

# generate url for parameters
def generate_url(search_item) -> str:

    # read makes file
    with open(_MAKESJSON, 'r', encoding="utf-8", newline='') as mjson:
        data = mjson.read()
        makes_dict = (json.loads(data))
        makes_dict = makes_dict['autoscout24_ch']
        mjson.close()

    url = 'https://www.autoscout24.ch/de/autos/'
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


    url_param += '&vehtyp=10'

    return url


# make call and get resulting links
#def fetch(url : str):
#
#    page = requests.get(url, headers = HEADERS)
#    soup = BeautifulSoup(page.content, 'html.parser')