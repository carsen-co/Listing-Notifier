
import os
import json
import random
import threading as th

from tkinter import *
import tkinter.ttk as ttk
import tkinter.font as tkfont

from req_module import search_thread

MAINDIR = os.getcwd()
_DBJSON = './resources/db.json'
_MAKESJSON = './resources/makes.json'
_SETTINGSJSON = './resources/settings.json'

class Interface(Tk):
    
    # refresh interface
    def refresh(self):
        self.destroy()
        self.__init__()

    def __init__(self):

        # __init__ begin
        super().__init__()
        self.title("Listing Notifier")
        #self.iconbitmap('./path')

        # read and apply settings
        with open(_SETTINGSJSON, mode='r') as st:
            settings = st.read()
            settings = (json.loads(settings))
            settings = settings['settings']
            st.close()

        self.geometry(settings["window_geometry"])
        win_res = settings["window_resizeability"].split(',')
        self.resizable(win_res[0], win_res[1])
        
        self._frame = None
        self.switch_frame(Main)
            
    def switch_frame(self, frame_class):
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.grid()


class Main(Frame):

    # dynamically change models based on the manufacturer selected
    def change_models(self, mainc, selected_make):
        
        global model_field
        model_field = ttk.Combobox(mainc, width = 17) 
        model_field.grid(row=30,column=20)

        with open(_MAKESJSON, 'r', encoding="utf-8", newline='') as mjson:
            data = mjson.read()
            makes_dict = (json.loads(data))
            makes_dict = makes_dict['autoscout24_ch']
            mjson.close()

        for make in makes_dict:
            if make['n'] == selected_make:
                models = [md['m'] for md in make['models']]
                models.insert(0, 'Any')

        # adding combobox drop down list 
        model_field['values'] = tuple(models)
        model_field.current(0)

    def __init__(self, master):

        Frame.__init__(self, master)

        # retrieve inserted inputs
        def retrieve_inputs():

            try:
                with open(_DBJSON) as dbjson:
                    fields_input = json.load(dbjson)
                    dbjson.close()
            except FileNotFoundError:
                fields_input = {}
                fields_input['searches'] = []

            search = {}
            existing_ids = [item['id'] for item in fields_input['searches']]
            search['id'] = random.randint(1111,9999)
            while search['id'] in existing_ids:
                search['id'] = random.randint(1111,9999)
            search['status'] = True
            search['manufacturer'] = make_field.get()
            try:
                search['model'] = model_field.get()
            except NameError:
                search['model'] = ''
            search['version'] = model_version_field.get()
            search['price'] = str(price_field_from.get()) + " - " + str(price_field_to.get())
            search['registration'] = str(reg_field_from.get()) + " - " + str(reg_field_to.get())
            search['mileage'] = str(mileage_field_from.get()) + " - " + str(mileage_field_to.get())
            fields_input['searches'].append(search)

            with open(_DBJSON, 'w') as dbjson:
                json.dump(fields_input, dbjson)

            master.switch_frame(Main)


        # ========== SEARCH CONTENT
        title_font = tkfont.Font(family='Montserrat' ,size=16, weight='bold')
        labelf = tkfont.Font(family='Montserrat' ,size=12)
        cbbox = tkfont.Font(family='Montserrat' ,size=9)
        self.option_add("*TCombobox*Listbox*Font", cbbox)
        
        mainc = ttk.Frame(self)
        mainc.config(width = 600, height = 700)
        mainc.grid(row = 20, column = 0,sticky="new")


        # title
        title = ttk.Label(mainc, text = "Index a new search")
        title.grid(row = 10, column = 10, columnspan = 40,padx=(10,10), pady=(5,5))
        title['font'] = title_font


        # manufacturer
        make_txt = ttk.Label(mainc, text="Car manufacturer:")
        make_txt['font'] = labelf
        make_txt.grid(row=20,column=10,padx=(10,10), pady=(5,5), sticky = 'w')

        make_field = ttk.Combobox(mainc, width = 17) 
        make_field.grid(row=30,column=10)

        with open(_MAKESJSON, 'r', encoding="utf-8", newline='') as mjson:
            data = mjson.read()
            makes_dict = (json.loads(data))
            makes_dict = makes_dict['autoscout24_ch']
            mjson.close()

        makes = [mk['n'] for mk in makes_dict]
        makes.insert(0, 'Any')

        # combobox drop down list 
        make_field['values'] = tuple(makes)
        make_field.current(0)
        make_field.bind("<<ComboboxSelected>>", lambda _ : self.change_models(mainc, make_field.get()))


        # model
        model_version_txt = ttk.Label(mainc, text="Car model:")
        model_version_txt['font'] = labelf
        model_version_txt.grid(row=20,column=20,padx=(10,10), pady=(5,5), sticky = 'w')


        # model version
        model_version_txt = ttk.Label(mainc, text="Model version:")
        model_version_txt['font'] = labelf
        model_version_txt.grid(row=20,column=40,padx=(10,10), pady=(5,5), sticky = 'w')
        
        model_version_field = ttk.Entry(mainc)
        model_version_field.grid(row=30,column=40, pady=(5,10))


        # price
        price_txt = ttk.Label(mainc, text="Price range (EURO):")
        price_txt['font'] = labelf
        price_txt.grid(row=40,column=10,padx=(10,10), pady=(5,5), sticky = 'w')
        # from
        price_field_from = ttk.Entry(mainc)
        price_field_from.grid(row=40,column=20)
        #to
        price_txt_to = ttk.Label(mainc, text="to")
        price_txt_to['font'] = labelf
        price_txt_to.grid(row=40,column=30,padx=(10,10), pady=(5,5))
        price_field_to = ttk.Entry(mainc)
        price_field_to.grid(row=40,column=40)


        # mileage
        mileage_txt = ttk.Label(mainc, text="Mileage range (KM):")
        mileage_txt['font'] = labelf
        mileage_txt.grid(row=50,column=10,padx=(10,10), pady=(5,5), sticky = 'w')
        # from
        mileage_field_from = ttk.Entry(mainc)
        mileage_field_from.grid(row=50,column=20)
        #to
        mileage_txt_to = ttk.Label(mainc, text="to")
        mileage_txt_to['font'] = labelf
        mileage_txt_to.grid(row=50,column=30,padx=(10,10), pady=(5,5))
        mileage_field_to = ttk.Entry(mainc)
        mileage_field_to.grid(row=50,column=40)


        # registration
        reg_txt = ttk.Label(mainc, text="Registration years:")
        reg_txt['font'] = labelf
        reg_txt.grid(row=60,column=10,padx=(10,10), pady=(5,5), sticky = 'w')
        # from
        reg_field_from = ttk.Entry(mainc)
        reg_field_from.grid(row=60,column=20)
        #to
        reg_txt_to = ttk.Label(mainc, text="to")
        reg_txt_to['font'] = labelf
        reg_txt_to.grid(row=60,column=30,padx=(10,10), pady=(5,5))
        reg_field_to = ttk.Entry(mainc)
        reg_field_to.grid(row=60,column=40)


        # timer
        timer_txt = ttk.Label(mainc, text="Timer\n(seconds):")
        timer_txt['font'] = labelf
        timer_txt.grid(row=20,column=50,padx=(10,10), pady=(5,5), sticky = 'w')

        with open(_SETTINGSJSON, mode='r') as st:
            settings = st.read()
            settings = (json.loads(settings))
            timer = StringVar(mainc, value=settings['settings']['timer'])
            timer = StringVar()
            timer.set(settings['settings']['timer'])
            st.close()
        timer_field = ttk.Entry(mainc, textvariable=timer)
        timer_field.grid(row=30,column=50)


        # search button
        search_button = Button(mainc, text="Index!",bg='#5e5e5e', fg='#eae8e8', command=retrieve_inputs)
        search_button.grid(row=80,column=10,columnspan=40,padx=(10, 10),pady=(10, 10))
        search_button['font'] = title_font


        # ========== TREE CONTENT
        global searches_tree
        # generate treeview
        searches_tree = ttk.Treeview(mainc, height=15)
        searches_tree["columns"]=("Vehicle","Price","Registration","Mileage")
        searches_tree.column("#0", width=60, minwidth=50,anchor=CENTER)
        searches_tree.column("#1", width=150, minwidth=80,anchor=CENTER)
        searches_tree.column("#2", width=120, minwidth=60,anchor=CENTER)
        searches_tree.column("#3", width=100, minwidth=40,anchor=CENTER)
        searches_tree.column("#4", width=100, minwidth=70,anchor=CENTER)

        searches_tree.heading("#0", text="Status", anchor=CENTER)
        searches_tree.heading("#1", text="Vehicle", anchor=CENTER)
        searches_tree.heading("#2",text="Price", anchor=CENTER)
        searches_tree.heading("#3", text="Registration", anchor=CENTER)
        searches_tree.heading("#4", text="Mileage", anchor=CENTER)

        searches_tree.grid(row=90,column=10,columnspan=40,padx=5)

        try:
            with open(_DBJSON) as dbjson:
                fields_input = json.load(dbjson)
                dbjson.close()
                for item in fields_input['searches']:
                    if item['status']:
                        status = "Active"
                    else:
                        status = "Inactive"
                    searches_tree.insert('', 'end', text=status, values=(item['manufacturer'] + ' ' + item['model'] + ' ' + item['version'], item['price'], item['registration'], item['mileage'], item['id']))
        except FileNotFoundError:
            pass
