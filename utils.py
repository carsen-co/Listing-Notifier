
import json
import time
import threading as th

from req_module import search_thread

_DBJSON = './resources/db.json'
_MAKESJSON = './resources/makes.json'
_SETTINGSJSON = './resources/settings.json'

def load_settings():
    with open(_SETTINGSJSON, mode='r') as st:
        settings = st.read()
        settings = (json.loads(settings))
        st.close()
    return settings
    
def load_makes():
    with open(_MAKESJSON, 'r', encoding="utf-8", newline='') as mjson:
        data = mjson.read()
        makes_dict = (json.loads(data))
        makes_dict = makes_dict['autoscout24_ch']
        mjson.close()
    return makes_dict

def load_database():
    with open(_DBJSON) as dbjson:
        fields_input = json.load(dbjson)
        dbjson.close()
    return fields_input

# run toggle functions
def run_threader():
    settings = load_settings()

    running = settings['running']
    if running:
        running = False
        with open(_SETTINGSJSON, 'w') as setjson:
            settings['running'] = False
            json.dump(settings, setjson)
            setjson.close()
    else:
        running = True
        with open(_SETTINGSJSON, 'w') as setjson:
            settings['running'] = True
            json.dump(settings, setjson)
            setjson.close()
        thread = th.Thread(target=run_thread)
        thread.start()

def run_thread():
    settings = load_settings()
    running = settings['running']

    while running:
        time.sleep(int(settings['timer']) / 2)
        search_thread()
        time.sleep(int(settings['timer']) / 2)
        settings = load_settings()
        running = settings['running']
