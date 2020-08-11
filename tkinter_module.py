
import os
import json
import threading as th

from tkinter import *
import tkinter.ttk as ttk
import tkinter.font as tkfont

global maindir
maindir = os.getcwd()


class Interface(Tk):
    
    def refresh(self):
        self.destroy()
        self.__init__()
    
    def __init__(self):
        super().__init__()
        self.title("Listing Notifier")
        #self.iconbitmap('./path')

        # read and apply settings
        with open('./resources/settings.json', mode='r') as st:
            settings = st.read()
            settings = (json.loads(settings))
            settings = settings['settings'][0]
            st.close()

        self.geometry(settings["window_geometry"])
        win_res = settings["window_resizeability"].split(',')
        self.resizable(win_res[0], win_res[1])
        
        # dynamically change models based on the manufacturer selected
        def change_models(model_field, selected_make):
            model_field.destroy()

            model_field = ttk.Combobox(mainc, width = 17) 
            model_field.grid(row=30,column=20)

            with open("./resources/makes.json", 'r', encoding="utf-8", newline='') as mjson:
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

        # retrieve inserted inputs
        def retrieve_inputs():
            
            search_input = []
            search_input.append(make_field.get())
            search_input.append(model_field.get())
            search_input.append(price_field_from.get())
            search_input.append(price_field_to.get())
            search_input.append(reg_field_from.get())
            search_input.append(reg_field_to.get())
            search_input.append(mileage_field_from.get())
            search_input.append(mileage_field_to.get())

            threads = []
            search_thread = th.Thread(target=search, args = (maindir, search_input))
            search_thread.start()
            threads = []
            threads.append(search_thread)
            threads_thread = th.Thread(target=search_thread, args = (threads[0],))
            threads_thread.start()


        # ========== MAIN CONTENT
        title_font = tkfont.Font(family='Montserrat' ,size=16, weight='bold')
        labelf = tkfont.Font(family='Montserrat' ,size=12)
        
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

        with open("./resources/makes.json", 'r', encoding="utf-8", newline='') as mjson:
            data = mjson.read()
            makes_dict = (json.loads(data))
            makes_dict = makes_dict['autoscout24_ch']
            mjson.close()

        makes = [mk['n'] for mk in makes_dict]
        makes.insert(0, 'Any')

        # combobox drop down list 
        make_field['values'] = tuple(makes)
        make_field.current(0)
        make_field.bind("<<ComboboxSelected>>", lambda _ : change_models(model_field, make_field.get()))


        # model
        model_version_txt = ttk.Label(mainc, text="Car model:")
        model_version_txt['font'] = labelf
        model_version_txt.grid(row=20,column=20,padx=(10,10), pady=(5,5), sticky = 'w')
        
        model_field = ttk.Entry(mainc)
        model_field.grid(row=30,column=20)


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


        # search button
        search_button = Button(mainc, text="Index!",bg='#5e5e5e', fg='#eae8e8', command=retrieve_inputs)
        search_button.grid(row=80,column=10,columnspan=40,padx=(10, 10),pady=(10, 10))
        search_button['font'] = title_font
