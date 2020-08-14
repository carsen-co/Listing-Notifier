
import os
import json
import random
import threading as th

from tkinter import *
import tkinter.ttk as ttk
import tkinter.font as tkfont

from utils import *

MAINDIR = os.getcwd()
_DBJSON = './resources/db.json'
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
        self.iconbitmap('./resources/icons/logo.ico')

        settings = load_settings()
        self.geometry(settings["window_geometry"])
        win_res = settings["window_resizeability"].split(',')
        self.resizable(win_res[0], win_res[1])
        
        self._frame = None
        self.switch_frame(Main)
        
        # style map treeview fix
        def fixed_map(option):
            return [elm for elm in style.map("Treeview", query_opt=option)
                    if elm[:2] != ("!disabled", "!selected")]

        style = ttk.Style()
        style.map('Treeview', foreground=fixed_map('foreground'), background=fixed_map('background'))

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

        makes_dict = load_makes()

        for make in makes_dict:
            if make['n'] == selected_make.lower():
                models = [md['m'].upper() for md in make['models']]
                models.insert(0, 'ANY')

        # adding combobox drop down list
        model_field['values'] = tuple(models)
        model_field.current(0)

    def __init__(self, master):

        Frame.__init__(self, master)

        # retrieve inserted inputs
        def retrieve_inputs():

            try:
                fields_input = load_database()
            except FileNotFoundError:
                fields_input = {}
                fields_input['searches'] = []
                fields_input['ignored'] = []

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

        makes_dict = load_makes()

        makes = [mk['n'].upper() for mk in makes_dict]
        makes.insert(0, 'ANY')

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
        price_txt = ttk.Label(mainc, text="Price range (CHF):")
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

        # search button
        search_button = Button(mainc, text="Index!",bg='#5e5e5e', fg='#eae8e8', command=retrieve_inputs)
        search_button.grid(row=80,column=10,columnspan=40,padx=(10, 10),pady=(10, 10))
        search_button['font'] = title_font


        # ========== TREE CONTENT
        global searches_tree
        # generate treeview
        searches_tree = ttk.Treeview(mainc, height=15)
        searches_tree["columns"]=("Price","Registration")
        searches_tree.column("#0", width=190, minwidth=50,anchor=CENTER)
        searches_tree.column("#1", width=140, minwidth=80,anchor=CENTER)
        searches_tree.column("#2", width=140, minwidth=60,anchor=CENTER)

        searches_tree.heading("#0", text="Vehicle", anchor=CENTER)
        searches_tree.heading("#1", text="Price", anchor=CENTER)
        searches_tree.heading("#2",text="Registration", anchor=CENTER)

        searches_tree.grid(row=90,column=10,columnspan=40,rowspan=60,padx=5)

        try:
            fields_input = load_database()
            for item in fields_input['searches']:
                if item['status']:
                    searches_tree.tag_configure('gcolor', background='#caffbf')
                    searches_tree.insert('', 'end', item['id'], text=item['manufacturer'] + ' ' + item['model'] + ' ' + item['version'], tag='gcolor', values=(item['price'], item['registration'], item['mileage']))
                else:
                    searches_tree.tag_configure('rcolor', background='#ffadad')
                    searches_tree.insert('', 'end', item['id'], text=item['manufacturer'] + ' ' + item['model'] + ' ' + item['version'], tag='rcolor', values=(item['price'], item['registration'], item['mileage']))
        except FileNotFoundError:
            pass
        except json.decoder.JSONDecodeError:
            os.remove(_DBJSON)
            with open(_DBJSON, 'w') as dbjson:
                fields_input = {}
                fields_input['searches'] = []
                fields_input['ignored'] = []
                json.dump(fields_input, dbjson)
                dbjson.close()

        # buttons
        # run button toggle
        def run():
            run_threader()
            time.sleep(1)
            thread = th.Thread(target=bar)
            thread.start()

        run_toggle_icon = PhotoImage(file="./resources/icons/run_toggle.png").subsample(4,4)
        run_toggle_button = Button(mainc, image = run_toggle_icon,compound = LEFT, bg='#fff', command=run)
        run_toggle_button.image = run_toggle_icon
        run_toggle_button.grid(row=90, column=50)
        run_toggle_button.config(width=50, height=50)

        # activator button
        def activator():
            selected_items = list(searches_tree.selection())
            if selected_items:
                for item in selected_items:
                    fields_input = load_database()
                    for i, listing in enumerate(fields_input['searches']):
                        if int(item) == int(listing['id']):
                            if listing['status']:
                                listing['status'] = False
                            else:
                                listing['status'] = True

                with open(_DBJSON, 'w') as dbjson:
                    json.dump(fields_input, dbjson)
                    dbjson.close()
                master.switch_frame(Main)

        activator_toggle_icon = PhotoImage(file="./resources/icons/activator.png").subsample(4,4)
        activator_toggle_button = Button(mainc, image = activator_toggle_icon,compound = LEFT, bg='#fff', command=activator)
        activator_toggle_button.image = activator_toggle_icon
        activator_toggle_button.grid(row=100, column=50)
        activator_toggle_button.config(width=50, height=50)

        # remove button
        def remove():
            selected_items = list(searches_tree.selection())
            if selected_items:
                for item in selected_items:
                    fields_input = load_database()
                    for listing in fields_input['searches']:
                        if int(item) == int(listing['id']):
                            fields_input['searches'].remove(listing)

                with open(_DBJSON, 'w') as dbjson:
                    json.dump(fields_input, dbjson)
                    dbjson.close()
                master.switch_frame(Main)

        remove_icon = PhotoImage(file="./resources/icons/trash.png").subsample(11,11)
        remove_button = Button(mainc, image = remove_icon,compound = LEFT, bg='#fff', command=remove)
        remove_button.image = remove_icon
        remove_button.grid(row=140, column=50)
        remove_button.config(width=50, height=50)

        # timer
        timer_txt = ttk.Label(mainc, text="Timer (seconds):")
        timer_txt['font'] = labelf
        timer_txt.grid(row=160,column=10,padx=(10,10), pady=(5,5), sticky = 'w')

        settings = load_settings()
        timer_field = ttk.Entry(mainc)
        timer_field.grid(row=160,column=20)
        timer_field.insert(0, settings['timer'])

        # confirm settings button
        def confirm_settings():
            settings = load_settings()
            with open(_SETTINGSJSON, 'w') as setjson:
                settings['timer'] = timer_field.get()
                settings['receiver'] = receiver_field.get()
                json.dump(settings, setjson)
                setjson.close()

        set_timer_icon = PhotoImage(file="./resources/icons/set.png").subsample(25,25)
        set_timer_button = Button(mainc, image = set_timer_icon,compound = LEFT, bg='#fff', command=confirm_settings)
        set_timer_button.image = set_timer_icon
        set_timer_button.grid(row=160, column=30, rowspan=20, padx=(15,1))
        set_timer_button.config(width=40, height=40)


        # receiver
        receiver_txt = ttk.Label(mainc, text="Receiver (email):")
        receiver_txt['font'] = labelf
        receiver_txt.grid(row=170,column=10,padx=(10,10), pady=(5,5), sticky = 'w')

        settings = load_settings()
        receiver_field = ttk.Entry(mainc)
        receiver_field.grid(row=170,column=20)
        receiver_field.insert(0, settings['receiver'])

        # progressbar
        def bar():
            settings = load_settings()
            bar_status = settings['running']

            while bar_status:
                settings = load_settings()
                bar_status = settings['running']

                for i in range(11):
                    progressbar['value'] = i * 10
                    self.update_idletasks()
                    time.sleep(0.4)

            progressbar['value'] = 0
            self.update_idletasks()
            time.sleep(0.4)

        progressbar = ttk.Progressbar(mainc, orient=HORIZONTAL, length=100, mode='indeterminate')
        progressbar.grid(row=160, column=40, rowspan=20)
