from tkinter import *
from tkinter import messagebox
from customtkinter import *
from PIL import ImageTk, Image
from tkinter import ttk
from time import strftime
from tkcalendar import Calendar
from Spinbox import Spinbox1, Spinbox2
import sqlite3


########### Dark/Light mode en color theme instellen
set_appearance_mode("dark")
set_default_color_theme("dark-blue")

############variabelen/lijsten aanmaken
current_date = '01-01-2016'

lijst_apparaten = ['Fridge', 'Elektric Bike', 'Elektric Car', 'Dishwasher', 'Washing Manchine', 'Freezer']
lijst_soort_apparaat = ['Always on', 'Device with battery', 'Device with battery', 'Consumer', 'Consumer', 'Always on']
lijst_capaciteit = ['/', 1500, 2000, '/', '/', '/']
lijst_aantal_uren = [2, 2, 2, 2, 3, 2]
lijst_uren_na_elkaar = [2, '/', '/', 2, 3, 2]
lijst_verbruiken = [40,12,100,52,85,13]
lijst_deadlines = [15,17,14,'/',23,14]
lijst_beginuur = ['/', '/', '/', '/', 18, '/']
lijst_remember_settings = [1,0,0,1,0,1]
lijst_status = [0,1,0,0,1,1]

oppervlakte_zonnepanelen = 0

def gegevens_opvragen(current_date):
    uur = "0"
    dag = str(int(current_date[0:2]))
    maand = current_date[3:5]

    # Gegevens Belpex opvragen
    if int(maand) >= 9:
        tupleBelpex = (dag + "/" + maand + "/" + "2021 " + uur + ":00:00",)
    else:
        tupleBelpex = (dag + "/" + maand + "/" + "2022 " + uur + ":00:00",)
    print(tupleBelpex)
    con = sqlite3.connect("VolledigeDatabase.db")
    cur = con.cursor()

    res = cur.execute("SELECT DatumBelpex FROM Stroomprijzen")
    Dates = res.fetchall()

    index = [tup for tup in Dates].index(tupleBelpex)

    res = cur.execute("SELECT Prijs FROM Stroomprijzen")
    Prijzen = res.fetchall()

    Prijzen24uur = []
    for i in range(0, 24):
        prijs = Prijzen[index - i]
        prijsString = str(prijs)
        prijsCijfers = prijsString[6:-3]
        prijsCijfersPunt = prijsCijfers.replace(",", ".")
        prijsFloat = float(prijsCijfersPunt)
        Prijzen24uur.append(prijsFloat)
    # Print lijst met de prijzen van de komende 24 uur
    print(Prijzen24uur)

    # Gegevens Weer opvragen
    uur = "00"
    dag = current_date[0:2]
    maand = current_date[3:5]

    tupleWeer = ("2016" + "-" + maand + "-" + dag + "T" + uur + ":00:00Z",)

    con = sqlite3.connect("VolledigeDatabase.db")
    cur = con.cursor()

    res = cur.execute("SELECT DatumWeer FROM Weer")
    Dates = res.fetchall()

    index = [tup for tup in Dates].index(tupleWeer)

    res = cur.execute("SELECT Windsnelheid, Temperatuur, RadiatieDirect, RadiatieDiffuse FROM Weer")
    alleGegevens = res.fetchall()

    TemperatuurList = []
    RadiatieList = []
    for i in range(0, 24):
        dagGegevens = alleGegevens[index + i]
        TemperatuurList.append(float(dagGegevens[1]))
        RadiatieList.append(float(dagGegevens[2]) + float(dagGegevens[3]))
    Gegevens24uur = [TemperatuurList, RadiatieList]
    # Print lijst onderverdeeld in een lijst met de temperaturen van de komende 24 uur
    #                              en een lijst voor de radiatie van de komende 24 uur
    print(Gegevens24uur)
    return Prijzen24uur, Gegevens24uur


#MainApplication: main window instellen + de drie tabs aanmaken met verwijzigen naar HomeFrame, ControlFrame en StatisticFrame
class MainApplication(CTk):
    def __init__(self):
        super().__init__()

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        screen_resolution = str(screen_width) + 'x' + str(screen_height) + '0' + '0'

        self.geometry(screen_resolution)
        self.title("SMART SOLAR HOUSE")
        self.iconbitmap('solarhouseicon.ico')

        my_notebook = ttk.Notebook(self)
        my_notebook.pack()

        frame_home = HomeFrame(my_notebook)
        frame_controls = ControlFrame(my_notebook)
        frame_statistics = StatisticFrame(my_notebook)

        frame_home.pack(fill='both', expand=1)
        frame_controls.pack(fill='both', expand=1)
        frame_statistics.pack(fill='both', expand=1)

        my_notebook.add(frame_home, text='HOME')
        my_notebook.add(frame_controls, text='CONTROLS')
        my_notebook.add(frame_statistics, text='STATISTICS')

#Home Frame aanmaken met titel, namen projectdeelnemers en kalender om datum te kiezen

class HomeFrame(CTkFrame):
    def __init__(self, parent):
        CTkFrame.__init__(self,parent)

        frame_width = self.winfo_screenwidth()
        frame_height = self.winfo_screenheight()

        my_canvas = Canvas(self, width=frame_width, height=frame_height, bg=('gray16'))
        my_canvas.pack(fill="both", expand=True)

        frame1 = CTkFrame(self, padx=10, pady=10, width=0.5*frame_width, height=0.16*frame_height)
        frame1.pack_propagate('false')
        my_canvas.create_window((350,50), window=frame1, anchor="nw")
        frame2 = CTkFrame(self, padx=10, pady=10, width=0.5*frame_width, height=0.35*frame_height)
        frame2.grid_propagate('false')
        my_canvas.create_window((350, 300), window=frame2, anchor="nw")
        frame3 = CTkFrame(self, padx=10, pady=10, width=0.5*frame_width, height=0.1*frame_height)
        frame3.grid_propagate('false')
        my_canvas.create_window((350, 800), window=frame3, anchor="nw")

        home_title = CTkLabel(frame1, text='SMART SOLAR HOUSE', text_font=('Biome',60, 'bold'))
        home_subtitle = CTkLabel(frame1, text='Made by August Vannes, Jonas Thewis, Lander Verhoeven, Ruben Vanherpe,',text_font=('Biome', 15))
        home_subtitle2 = CTkLabel(frame1, text= 'Tibo Mattheus and Tijs Motmans', text_font=('Biome', 15))

        home_title.pack()
        home_subtitle.pack()
        home_subtitle2.pack()

        frame2.rowconfigure(0, uniform= 'uniform', weight=2)
        frame2.rowconfigure(1, uniform='uniform', weight=12)
        frame2.rowconfigure(2, uniform='uniform', weight=2)
        frame2.columnconfigure(0, uniform='uniform', weight=1)

        selected_date = CTkLabel(frame2, text='Here you can change the current date:', text_font=('Biome',15))
        selected_date.grid(column=0, row=0, sticky='nsew', padx=5, pady=2)
        cal = Calendar(frame2, selectmode='day', date_pattern='dd-mm-y')
        cal.grid(column=0, row=1, sticky='nsew', padx=50, pady=5)

        def grad_date():
            global current_date,Prijzen24uur, Gegevens24uur
            current_date = cal.get_date()
            label_day.configure(text=str(current_date[0:2]))
            label_month.configure(text=str(current_date[3:5]))
            label_year.configure(text=str(current_date[6:10]))
            Prijzen24uur, Gegevens24uur = gegevens_opvragen(current_date)

        btn = CTkButton(frame2, text="Confirm the chosen date",command=grad_date)
        btn.grid(column=0, row=2, sticky='nsew', padx=40, pady=5)

        frame3.grid_rowconfigure(0, uniform='uniform', weight=1)
        frame3.grid_columnconfigure((0, 2, 6, 8), uniform='uniform', weight=5)
        frame3.grid_columnconfigure(4, uniform='uniform', weight=8)
        frame3.grid_columnconfigure((1, 3, 5, 7), uniform='uniform', weight=1)

        day = CTkFrame(frame3, bd=5, corner_radius=10)
        day.grid(row=3, column=0, padx=5, sticky='nsew')
        streep1 = CTkLabel(frame3, text='-', text_font=('Biome', 50, 'bold'))
        streep1.grid(row=3, column=1, sticky='nsew')
        month = CTkFrame(frame3, bd=5, corner_radius=10)
        month.grid(row=3, column=2, padx=5, sticky='nsew')
        streep2 = CTkLabel(frame3, text='-', text_font=('Biome', 50, 'bold'))
        streep2.grid(row=3, column=3, sticky='nsew')
        year = CTkFrame(frame3, bd=5, corner_radius=10)
        year.grid(row=3, column=4, padx=5, sticky='nsew')
        separator = ttk.Separator(frame3, orient='vertical')
        separator.grid(row=3, column=5, sticky='ns', pady=20)
        hours= CTkFrame(frame3, bd=5, corner_radius=10)
        hours.grid(row=3, column=6, padx=5, sticky='nsew')
        dubbel_punt = CTkLabel(frame3, text=':', text_font=('Biome', 50, 'bold'))
        dubbel_punt.grid(row=3, column=7, sticky='nsew')
        minutes = CTkFrame(frame3, bd=5, corner_radius=10)
        minutes.grid(row=3, column=8, padx=5, sticky='nsew')

        label_day = CTkLabel(day, text=str(current_date[0:2]), text_font=('Biome', 50))
        label_day.pack(fill='both', expand=1)
        label_month = CTkLabel(month, text=str(current_date[3:5]), text_font=('Biome', 50))
        label_month.pack(fill='both', expand=1)
        label_year = CTkLabel(year, text=str(current_date[6:10]), text_font=('Biome', 50))
        label_year.pack(fill='both', expand=1)
        label_hours = CTkLabel(hours, text='00', text_font=('Biome', 50))
        label_hours.pack(fill='both', expand=1)
        label_minutes = CTkLabel(minutes, text='00', text_font=('Biome', 50))
        label_minutes.pack(fill='both', expand=1)

#ControlFrame aanmaken met verwijzingen naar FrameTemperatuur, FrameBatterijen en FrameApparaten

class ControlFrame(CTkFrame):
    def __init__(self, parent):
        CTkFrame.__init__(self,parent)
        self.pack_propagate('false')

        self.grid_columnconfigure((0, 1), uniform="uniform", weight=1)
        self.grid_rowconfigure((0,1,2), uniform="uniform", weight=1)

        frame_temperatuur = FrameTemperatuur(self)
        frame_batterijen = FrameBatterijen(self)
        frame_apparaten = FrameApparaten(self)
        frame_zonnepanelen = FrameZonnepanelen(self)

        frame_temperatuur.grid(row=0, column=0, padx=5, sticky='nsew')
        frame_batterijen.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')
        frame_apparaten.grid(row=0, column=1, rowspan=3, padx=5, pady=5, sticky='nsew')
        frame_zonnepanelen.grid(row=2, column=0,padx=5, pady=5, sticky='nsew')

#Frame om de temperatuur van het huis (warmtepomp) te regelen

class FrameTemperatuur(CTkFrame):
    def __init__(self, parent):
        CTkFrame.__init__(self,parent, bd=5, corner_radius=10)
        self.pack_propagate('false')

        title = CTkLabel(self, text='Temperature', text_font=('Microsoft Himalaya', 30, 'bold'))
        title.grid(row=0, column=0, sticky='nsew')

#Frame om de status van de batterijen te controleren

class FrameBatterijen(CTkFrame):
    def __init__(self, parent):
        CTkFrame.__init__(self,parent, bd=5, corner_radius=10)
        self.pack_propagate('false')

        title = CTkLabel(self, text='Battery', text_font=('Microsoft Himalaya', 30, 'bold'))
        title.grid(row=0, column=0, sticky='nsew')

#Frame om de zonnepanelen te controleren

class FrameZonnepanelen(CTkFrame):
    def __init__(self, parent):
        CTkFrame.__init__(self,parent, bd=5, corner_radius=10)
        self.pack_propagate('false')

        self.grid_rowconfigure((0),'uniform')
        title = CTkLabel(self, text='Solar Panels', text_font=('Microsoft Himalaya', 30, 'bold'))
        title.grid(row=0, column=0, sticky='nsew')

        frame1 = CTkFrame(self)



#Frame om de apparaten in het huishouden te controleren
class FrameApparaten(CTkFrame):
    def __init__(self, parent):
        CTkFrame.__init__(self,parent, bd=5, corner_radius=10)
        self.pack_propagate('false')

        self.grid_rowconfigure((0,2), uniform="uniform", weight=1)
        self.grid_rowconfigure(1, uniform="uniform", weight=16)
        self.grid_columnconfigure((0,1), uniform="uniform", weight=1)
        global frame_height
        global frame_width
        frame_height = self.winfo_screenheight()
        frame_width = self.winfo_screenwidth()

        btn_newdevice = CTkButton(self, text='Add new device', command=lambda: self.new_device(frame2))
        btn_newdevice.grid(row=2,column=1, padx=5, sticky='nsew')
        btn_editdevice = CTkButton(self, text='Edit existing device', command=lambda: self.edit_device(frame2))
        btn_editdevice.grid(row=2, column=0, padx=5, sticky='nsew')
        title = CTkLabel(self, text="Current Devices", text_font=('Microsoft Himalaya', 30, 'bold'), pady=0)
        title.grid(row=0,column=0,columnspan=2,sticky = 'nsew')
        frame1 = CTkFrame(self, fg_color='gray', pady=0)
        frame1.grid(row=1,column=0, columnspan=2, sticky='nsew')

        my_canvas = Canvas(frame1)
        my_canvas.pack(side='left',fill='both', expand=1, pady=0)

        my_scrollbar = CTkScrollbar(frame1,orientation='vertical', command=my_canvas.yview)
        my_scrollbar.pack(side=RIGHT,fill='y')

        frame2 = CTkFrame(my_canvas, corner_radius=0)
        my_canvas.create_window((0, 0), window=frame2, anchor='nw', height=2000)

        my_canvas.configure(yscrollcommand=my_scrollbar.set)
        my_canvas.bind('<Configure>', lambda e: my_canvas.configure(scrollregion=my_canvas.bbox("all")))

        self.apparaten_in_frame(frame2)

    def apparaten_in_frame(self,frame2):
        for widget in frame2.winfo_children():
            widget.destroy()
        for nummer in range(len(lijst_apparaten)):
            naam = lijst_apparaten[nummer]
            soort = lijst_soort_apparaat[nummer]
            uren = lijst_aantal_uren[nummer]
            uren_na_elkaar = lijst_uren_na_elkaar[nummer]
            capaciteit = lijst_capaciteit[nummer]
            verbruik = lijst_verbruiken[nummer]
            deadline = lijst_deadlines[nummer]
            beginuur = lijst_beginuur[nummer]
            remember = lijst_remember_settings[nummer]
            status = lijst_status[nummer]
            APPARAAT(frame2, naam, soort, uren, uren_na_elkaar, capaciteit, verbruik, deadline, beginuur, remember,status)


    def new_device(self, frame2):
        new_window = CTkToplevel(self)
        new_window.iconbitmap('solarhouseicon.ico')
        new_window.title('Add a new device')
        new_window.geometry('300x610')
        new_window.grab_set()

        new_window.rowconfigure((0,1,2,3,4,5,6,7,8,9,10,11,12), uniform='uniform', weight=2)
        new_window.rowconfigure(13, uniform='uniform', weight=3)
        new_window.columnconfigure('all', uniform='uniform', weight=1)

        def show_rest(event):
            global entry_verbruik, spinbox_deadline, checkbox_deadline, spinbox_hours, checkbox_consecutive, \
                entry_capacity, checkbox_beginuur, spinbox_beginuur, checkbox_remember

            for widget in new_window.winfo_children()[4:]:
                widget.destroy()

            label_verbruik = CTkLabel(new_window, text='Fill in the energy usage of the device:')
            entry_verbruik = CTkEntry(new_window)
            label_verbruik.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
            entry_verbruik.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')

            if entry_soort.get() == 'Device with battery':
                label_capacity = CTkLabel(new_window, text='Fill in the battery capacity:')
                entry_capacity = CTkEntry(new_window)
                label_beginuur = CTkLabel(new_window, text='Set a start time for the device:')
                spinbox_beginuur = Spinbox1(new_window, step_size=1)
                checkbox_beginuur = CTkCheckBox(new_window, text ='No Starttime', command=checkbox_command)
                label_deadline = CTkLabel(new_window, text='Set a deadline for the device:')
                spinbox_deadline = Spinbox1(new_window, step_size=1)
                checkbox_deadline = CTkCheckBox(new_window, text='No Deadline', command=checkbox_command)
                checkbox_remember = CTkCheckBox(new_window, text='Remember start time and deadline')

                label_capacity.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
                entry_capacity.grid(row=7, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
                label_beginuur.grid(row=8, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
                spinbox_beginuur.grid(row=9, column=0, padx=17, pady=5, sticky='nsew')
                checkbox_beginuur.grid(row=9, column=1, padx=17, pady=5, sticky='nsew')
                label_deadline.grid(row=10, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
                spinbox_deadline.grid(row=11, column=0, padx=17, pady=5, sticky='nsew')
                checkbox_deadline.grid(row=11, column=1, padx=17, pady=5, sticky='nsew')
                checkbox_remember.grid(row=12, column=0, columnspan=2, padx=35, pady=5, sticky='nsew')

            if entry_soort.get() == 'Consumer':
                label_hours = CTkLabel(new_window, text='Fill in the runtime of the device:')
                spinbox_hours = Spinbox2(new_window, step_size=1)
                checkbox_consecutive = CTkCheckBox(new_window, text= 'Consecutive hours')
                label_beginuur = CTkLabel(new_window, text='Set a start time for the device: ')
                spinbox_beginuur = Spinbox1(new_window, step_size=1)
                checkbox_beginuur = CTkCheckBox(new_window, text= 'No Starttime', command=checkbox_command)
                label_deadline = CTkLabel(new_window, text='Set a deadline for the device:')
                spinbox_deadline = Spinbox1(new_window, step_size=1)
                checkbox_deadline = CTkCheckBox(new_window, text='No Deadline', command=checkbox_command)
                checkbox_remember = CTkCheckBox(new_window, text='Remember start time and deadline')

                label_hours.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
                spinbox_hours.grid(row=7, column=0, padx=8, pady=5, sticky='nsew')
                checkbox_consecutive.grid(row=7, column=1, padx=8, pady=5, sticky='nsew')
                label_beginuur.grid(row=8, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
                spinbox_beginuur.grid(row=9, column=0, padx=17, pady=5, sticky='nsew')
                checkbox_beginuur.grid(row=9, column=1, padx=17, pady=5, sticky='nsew')
                label_deadline.grid(row=10, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
                spinbox_deadline.grid(row=11, column=0, padx=17, pady=5, sticky='nsew')
                checkbox_deadline.grid(row=11, column=1, padx=17, pady=5, sticky='nsew')
                checkbox_remember.grid(row=12, column=0, columnspan=2, padx=35, pady=5, sticky='nsew')

            btn_confirm = CTkButton(new_window, text='confirm', command=apparaat_toevoegen)
            btn_confirm.grid(row=13, column=1, padx=5, pady=5, sticky='nsew')
            btn_cancel = CTkButton(new_window, text='cancel', command=new_window.destroy)
            btn_cancel.grid(row=13, column=0, padx=5, pady=5, sticky='nsew')

        def apparaat_toevoegen():
            naam= entry_naam.get()
            soort = entry_soort.get()

            if soort == 'Always on':
                uren = 24
                uren_na_elkaar = 24
                capaciteit = '/'
                verbruik = entry_verbruik.get()
                deadline = '/'
                beginuur = '/'
                remember = 1
                status = 1

            if soort == 'Device with battery':
                uren = '/'
                uren_na_elkaar = '/'
                capaciteit = entry_capacity.get()
                verbruik = entry_verbruik.get()
                if checkbox_beginuur.get() == 1:
                    beginuur = '/'
                else:
                    beginuur = spinbox_beginuur.get()
                if checkbox_deadline.get() == 1:
                    deadline = '/'
                else:
                    deadline = spinbox_deadline.get()
                remember = checkbox_remember.get()
                status = 0

            if soort == 'Consumer':
                uren = spinbox_hours.get()
                if checkbox_consecutive.get() == 1:
                    uren_na_elkaar = uren
                else:
                    uren_na_elkaar = '/'
                capaciteit = '/'
                verbruik = entry_verbruik.get()
                if checkbox_beginuur.get() == 1:
                    beginuur = '/'
                else:
                    beginuur = spinbox_beginuur.get()
                if checkbox_deadline.get() == 1:
                    deadline = '/'
                else:
                    deadline = spinbox_deadline.get()
                remember = checkbox_remember.get()
                status = 0

            if naam=='' or soort=='' or uren=='' or uren_na_elkaar=='' or capaciteit=='' or deadline=='':
                messagebox.showwarning('Warning','Please make sure to fill in all the boxes')
            else:
                APPARAAT(frame2, naam, soort, uren, uren_na_elkaar, capaciteit, verbruik, deadline, beginuur, remember, status)
                new_window.destroy()

        def checkbox_command():
            if checkbox_deadline.get() == 1:
                spinbox_deadline.inactiveer()
            else:
                spinbox_deadline.activeer()
            if checkbox_beginuur.get() == 1:
                spinbox_beginuur.inactiveer()
            else:
                spinbox_beginuur.activeer()

        label_naam = CTkLabel(new_window, text='Fill in the name of the device:')
        entry_naam = CTkEntry(new_window)
        label_soort = CTkLabel(new_window, text='Select the kind of the device:')
        lijst_soorten = ['Always on', 'Device with battery', 'Consumer']
        entry_soort = CTkComboBox(new_window, values=lijst_soorten, command=show_rest)
        entry_soort.set('')

        label_naam.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
        entry_naam.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
        label_soort.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
        entry_soort.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')

        btn_confirm = CTkButton(new_window, text='confirm', command=apparaat_toevoegen)
        btn_confirm.grid(row=13, column=1, padx=5, pady=5, sticky='nsew')
        btn_cancel = CTkButton(new_window, text='cancel', command=new_window.destroy)
        btn_cancel.grid(row=13, column=0, padx=5, pady=5, sticky='nsew')

    def edit_device(self, frame2):
        edit_window = CTkToplevel(self)
        edit_window.iconbitmap('solarhouseicon.ico')
        edit_window.title('Edit device')
        edit_window.geometry('300x650')
        edit_window.grab_set()

        edit_window.rowconfigure((0, 1, 2, 3, 4, 5,6,7,8,9,10,11,12), uniform='uniform', weight=2)
        edit_window.rowconfigure((13,14), uniform='uniform', weight=3)
        edit_window.columnconfigure('all', uniform='uniform', weight=1)

        def apparaat_wijzigen():
            soort = lijst_soort_apparaat[apparaat_nummer]

            if soort == 'Always on':
                naam = entry_naam_2.get()
                uren = 24
                uren_na_elkaar = 24
                capaciteit = '/'
                verbruik = entry_verbruik_2.get()
                deadline = '/'
                beginuur = '/'
                remember = 0
                status = 1

            if soort == 'Device with battery':
                naam = entry_naam_2.get()
                uren = '/'
                uren_na_elkaar = '/'
                capaciteit = entry_capacity_2.get()
                verbruik = entry_verbruik_2.get()
                if checkbox_beginuur_2.get() == 1:
                    beginuur = '/'
                else:
                    beginuur = spinbox_beginuur_2.get()
                if checkbox_deadline_2.get() == 1:
                    deadline = '/'
                else:
                    deadline = spinbox_deadline_2.get()
                remember = checkbox_remember_2.get()
                status = 0

            if soort == 'Consumer':
                uren = spinbox_hours_2.get()
                if checkbox_consecutive_2.get() == 1:
                    uren_na_elkaar = uren
                else:
                    uren_na_elkaar = '/'
                capaciteit = '/'
                verbruik = entry_verbruik_2.get()
                if checkbox_beginuur_2.get() == 1:
                    beginuur = '/'
                else:
                    beginuur = spinbox_beginuur_2.get()
                if checkbox_deadline_2.get() == 1:
                    deadline = '/'
                else:
                    deadline = spinbox_deadline_2.get()
                checkbox_remember_2.get()
                status = 0

            kolom = apparaat_nummer % 3
            rij = apparaat_nummer // 3

            if naam == '' or capaciteit == '' or uren == '' or uren_na_elkaar == '' or verbruik == '' or deadline == '' or beginuur == '':
                messagebox.showwarning('Warning','Please make sure to fill in all the boxes')
            else:
                lijst_apparaten[apparaat_nummer] = naam
                lijst_soort_apparaat[apparaat_nummer] = soort
                lijst_capaciteit[apparaat_nummer] = capaciteit
                lijst_aantal_uren[apparaat_nummer] = uren
                lijst_aantal_uren[apparaat_nummer] = uren_na_elkaar
                lijst_verbruiken[apparaat_nummer] = verbruik
                lijst_deadlines[apparaat_nummer] = deadline
                lijst_beginuur[apparaat_nummer] = beginuur
                lijst_remember_settings[apparaat_nummer] = remember
                lijst_status[apparaat_nummer] = status
                APPARAAT(frame2,naam, soort, uren, uren_na_elkaar, capaciteit, verbruik, deadline, beginuur,remember,status, column=kolom, row=rij)
                edit_window.destroy()

        def show_options(event):
            global entry_naam_2, entry_verbruik_2, spinbox_deadline_2, checkbox_deadline_2, spinbox_hours_2, checkbox_consecutive_2, \
                entry_capacity_2, checkbox_beginuur_2, spinbox_beginuur_2, checkbox_remember_2
            global apparaat_nummer

            for widget in edit_window.winfo_children()[2:]:
                widget.destroy()

            apparaat_nummer = lijst_apparaten.index(choose_device.get())
            label_naam_2 = CTkLabel(edit_window, text='Edit the name of the device:')
            entry_naam_2 = CTkEntry(edit_window)
            entry_naam_2.delete(0,'end')
            entry_naam_2.insert(0,lijst_apparaten[apparaat_nummer])
            label_verbruik_2 = CTkLabel(edit_window, text='Edit the energy usage (in kWh):')
            entry_verbruik_2 = CTkEntry(edit_window)
            entry_verbruik_2.delete(0,'end')
            entry_verbruik_2.insert(0,lijst_verbruiken[apparaat_nummer])

            label_naam_2.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
            entry_naam_2.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
            label_verbruik_2.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
            entry_verbruik_2.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')

            if lijst_soort_apparaat[apparaat_nummer] == 'Always on':
                pass

            else:
                if lijst_soort_apparaat[apparaat_nummer] == 'Device with battery':
                    label_capacity_2 = CTkLabel(edit_window, text='Change the battery capacity from the device:')
                    entry_capacity_2 = CTkEntry(edit_window)
                    entry_capacity_2.delete(0,'end')
                    entry_capacity_2.insert(0, lijst_capaciteit[apparaat_nummer])
                    label_capacity_2.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
                    entry_capacity_2.grid(row=7, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')

                if lijst_soort_apparaat[apparaat_nummer] == 'Consumer':
                    label_hours_2 = CTkLabel(edit_window, text='Edit the runtime of the device:')
                    spinbox_hours_2 = Spinbox2(edit_window, step_size=1)
                    checkbox_consecutive_2 = CTkCheckBox(edit_window, text='Consecutive hours')
                    spinbox_hours_2.set(lijst_aantal_uren[apparaat_nummer])
                    if lijst_aantal_uren[apparaat_nummer] == lijst_uren_na_elkaar[apparaat_nummer]:
                        checkbox_consecutive_2.select()

                    label_hours_2.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
                    spinbox_hours_2.grid(row=7, column=0, padx=5, pady=5, sticky='nsew')
                    checkbox_consecutive_2.grid(row=7, column=1, padx=5, pady=5, sticky='nsew')

                label_beginuur_2 = CTkLabel(edit_window, text='Change the start time for the device:')
                spinbox_beginuur_2 = Spinbox1(edit_window, step_size=1)
                checkbox_beginuur_2 = CTkCheckBox(edit_window, text='No Start Time', command=checkbox_command2)
                if lijst_beginuur[apparaat_nummer] == '/':
                    checkbox_beginuur_2.select()
                    spinbox_beginuur_2.inactiveer()
                else:
                    spinbox_beginuur_2.set(lijst_beginuur[apparaat_nummer])

                label_deadline_2 = CTkLabel(edit_window, text='Change the deadline for the device:')
                spinbox_deadline_2 = Spinbox1(edit_window, step_size=1)
                checkbox_deadline_2 = CTkCheckBox(edit_window, text='No Deadline', command=checkbox_command1)
                if lijst_deadlines[apparaat_nummer] == '/':
                    checkbox_deadline_2.select()
                    spinbox_deadline_2.inactiveer()
                else:
                    spinbox_deadline_2.set(lijst_deadlines[apparaat_nummer])

                checkbox_remember_2 = CTkCheckBox(edit_window, text='Remember start time and deadline')
                if lijst_remember_settings[apparaat_nummer] == 1:
                    checkbox_remember_2.select()


                label_beginuur_2.grid(row=8, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
                spinbox_beginuur_2.grid(row=9, column=0, padx=17, pady=5, sticky='nsew')
                checkbox_beginuur_2.grid(row=9, column=1, padx=17, pady=5, sticky='nsew')
                label_deadline_2.grid(row=10, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
                spinbox_deadline_2.grid(row=11, column=0, padx=17, pady=5, sticky='nsew')
                checkbox_deadline_2.grid(row=11, column=1, padx=17, pady=5, sticky='nsew')
                checkbox_remember_2.grid(row=12, column=0,columnspan=2, padx=35, pady=5, sticky='nsew')

            btn_confirm_2 = CTkButton(edit_window, text='confirm', command=apparaat_wijzigen, state=NORMAL)
            btn_confirm_2.grid(row=14, column=1, padx=5, pady=5, sticky='nsew')
            btn_cancel_2 = CTkButton(edit_window, text='cancel', command=edit_window.destroy)
            btn_cancel_2.grid(row=14, column=0, padx=5, pady=5, sticky='nsew')
            btn_delete_device = CTkButton(edit_window, text='Delete Device', command=apparaat_verwijderen,
                                                 fg_color='red', state=NORMAL)
            btn_delete_device.grid(row=13, column=0, columnspan=2, padx=5, pady=10, sticky='nsew')

        def apparaat_verwijderen():
            response = messagebox.askokcancel('Delete Device', 'Are you sure you want to delete this device?')
            if response == True:
                lijst_apparaten.pop(apparaat_nummer)
                lijst_soort_apparaat.pop(apparaat_nummer)
                lijst_capaciteit.pop(apparaat_nummer)
                lijst_aantal_uren.pop(apparaat_nummer)
                lijst_uren_na_elkaar.pop(apparaat_nummer)
                lijst_verbruiken.pop(apparaat_nummer)
                lijst_deadlines.pop(apparaat_nummer)
                lijst_beginuur.pop(apparaat_nummer)
                lijst_remember_settings.pop(apparaat_nummer)
                lijst_status.pop(apparaat_nummer)
                self.apparaten_in_frame(frame2)
                edit_window.destroy()

        def checkbox_command1():
            if checkbox_deadline_2.get() == 1:
                spinbox_deadline_2.inactiveer()
            else:
                spinbox_deadline_2.activeer()

        def checkbox_command2():
            if checkbox_beginuur_2.get() == 1:
                spinbox_beginuur_2.inactiveer()
            else:
                spinbox_beginuur_2.activeer()

        text_choose = CTkLabel(edit_window,text='Choose the device you want to edit:')
        choose_device = CTkComboBox(edit_window, values=lijst_apparaten, command= show_options)
        choose_device.set('')

        text_choose.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
        choose_device.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')

        btn_confirm_2 = CTkButton(edit_window, text='confirm', command = apparaat_wijzigen, state=DISABLED)
        btn_confirm_2.grid(row=14, column=1, padx=5, pady=5, sticky='nsew')
        btn_cancel_2 = CTkButton(edit_window, text='cancel', command = edit_window.destroy)
        btn_cancel_2.grid(row=14, column=0, padx=5, pady=5, sticky='nsew')
        btn_delete_device = CTkButton(edit_window, text='Delete Device', command=apparaat_verwijderen, fg_color='red', state=DISABLED)
        btn_delete_device.grid(row=13, column=0, columnspan=2, padx=5, pady=10, sticky='nsew')

class APPARAAT(CTkFrame):
    def __init__(self, parent, naam, soort, uren, uren_na_elkaar, capaciteit,verbruik,deadline, beginuur, remember, status, column=None, row=None):
        CTkFrame.__init__(self, parent, bd=5, corner_radius=10)
        self.pack_propagate('false')

        self.rowconfigure('all',uniform="uniform", weight=1)
        self.columnconfigure('all', uniform = 'uniform', weight=1)

        if naam not in lijst_apparaten:
            lijst_apparaten.append(naam)
            lijst_soort_apparaat.append(soort)
            lijst_aantal_uren.append(uren)
            lijst_uren_na_elkaar.append(uren_na_elkaar)
            lijst_capaciteit.append(capaciteit)
            lijst_verbruiken.append(verbruik)
            lijst_deadlines.append(deadline)
            lijst_beginuur.append(beginuur)
            lijst_remember_settings.append(remember)
            lijst_status.append(status)

        nummer_apparaat = lijst_apparaten.index(naam)

        if column == None and row == None:
            rij = nummer_apparaat // 3
            kolom = nummer_apparaat % 3
        else:
            rij = row
            kolom = column
        self.grid(row=rij,column=kolom, sticky='nsew')

        label_naam = CTkLabel(self, text=naam, text_font=('Biome', 12, 'bold'))
        label_naam.grid(row=0, column=0, sticky='nsew')
        label_soort = CTkLabel(self, text= soort, text_font=('Biome',10))
        label_soort.grid(row=1, column=0, sticky='nsew')
        label_verbruik = CTkLabel(self, text='Energy Usage: ' + str(verbruik) + ' kWh', text_font=('Biome', 10))
        label_verbruik.grid(row=2, column=0, sticky='nsew')
        if soort == 'Consumer':
            if uren == uren_na_elkaar:
                na_elkaar = 'succesively'
            else:
                na_elkaar = 'random'
            label_uren = CTkLabel(self, text= 'Daily use: ' + str(uren) + ' hours (' + na_elkaar + ')', text_font=('Biome', 10))
            label_uren.grid(row=3, column=0, sticky='nsew')
            if beginuur == '/':
                label_beginuur = CTkLabel(self, text='No start time', text_font=('Biome', 10))
            else:
                label_beginuur = CTkLabel(self, text= 'Current start time: ' + str(beginuur) + 'u', text_font = ('Biome', 10))
            label_beginuur.grid(row=4, column=0, sticky='nsew')
            if deadline == '/':
                label_deadline = CTkLabel(self, text='No Deadline', text_font=('Biome', 10))
            else:
                label_deadline = CTkLabel(self, text= 'Current Deadline: ' + str(deadline) + 'u', text_font = ('Biome', 10))
            label_deadline.grid(row=5, column=0, sticky='nsew')

        if soort == 'Device with battery':
            label_capaciteit = CTkLabel(self, text= 'Battery Capacity: ' + str(capaciteit) + ' kWh', text_font=('Biome', 10))
            label_capaciteit.grid(row=3, column=0, sticky='nsew')
            if beginuur == '/':
                label_beginuur = CTkLabel(self, text='No start time', text_font=('Biome', 10))
            else:
                label_beginuur = CTkLabel(self, text='Current start time: ' + str(beginuur) + 'u',
                                          text_font=('Biome', 10))
            label_beginuur.grid(row=4, column=0, sticky='nsew')
            if deadline == '/':
                label_deadline = CTkLabel(self, text='No Deadline', text_font=('Biome', 10))
            else:
                label_deadline = CTkLabel(self, text='Current Deadline: ' + str(deadline) + 'u',
                                          text_font=('Biome', 10))
            label_deadline.grid(row=5, column=0, sticky='nsew')

        if soort == 'Always on':
            white_space_1 = CTkLabel(self, text='     ', text_font=('Biome', 10))
            white_space_1.grid(row=3, column=0, sticky='nsew')
            white_space_2 = CTkLabel(self, text='     ', text_font=('Biome', 10))
            white_space_2.grid(row=4, column=0, sticky='nsew')
            white_space_3 = CTkLabel(self, text='     ', text_font=('Biome', 10))
            white_space_3.grid(row=5, column=0, sticky='nsew')

        if status == 1:
            bg_color = "#74d747"
            status_text = 'ON'
        else:
            bg_color = "#f83636"
            status_text = 'OFF'
        status = CTkLabel(self, text=status_text, bg_color=bg_color, width=0.1185*frame_width, height= 0.025*frame_height)
        status.grid(row=6, column=0, padx=5, pady=5)

#StatisticFrame met verwijzingen naar ...
class StatisticFrame(CTkFrame):
    def __init__(self, parent):
        CTkFrame.__init__(self,parent, width=3840, height=2160)
        self.pack_propagate('false')

        self.grid_columnconfigure((0, 1), uniform="uniform", weight=2)
        self.grid_columnconfigure(2, uniform="uniform", weight=3)
        self.grid_rowconfigure(0, uniform="uniform", weight=2)
        self.grid_rowconfigure(1, uniform="uniform", weight=1)

        frame_PvsC = FramePvsC(self)
        frame_verbruikers = FrameVerbruikers(self)
        frame_energieprijs = FrameEnergieprijs(self)
        frame_weer = FrameWeer(self)
        frame_totalen = FrameTotalen(self)

        frame_PvsC.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
        frame_verbruikers.grid(row=0, column=2, padx=5, pady=5, sticky='nsew')
        frame_energieprijs.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')
        frame_weer.grid(row=1, column=1, padx=5, pady=5, sticky='nsew')
        frame_totalen.grid(row=1, column=2, padx=5, pady=5, sticky='nsew')

#Frame PvsC: grafiek van de productie en consumptie van energie

class FramePvsC(CTkFrame):
    def __init__(self, parent):
        CTkFrame.__init__(self,parent, bd=5, corner_radius=10)
        self.pack_propagate('false')

        title = CTkLabel(self, text='Production vs Consumption', text_font=('Microsoft Himalaya', 30, 'bold'))
        title.grid(row=0, column=0, sticky='nsew')

#FrameVerbruikers: cirkeldiagram met grootste verbruikers in het huis (eventueel)

class FrameVerbruikers(CTkFrame):
    def __init__(self, parent):
        CTkFrame.__init__(self,parent, bd=5, corner_radius=10)
        self.pack_propagate('false')

        title = CTkLabel(self, text='Consumers', text_font=('Microsoft Himalaya', 30, 'bold'))
        title.grid(row=0, column=0, sticky='nsew')

#FrameEnergieprijs: geeft huidige energieprijs weer

class FrameEnergieprijs(CTkFrame):
    def __init__(self, parent):
        CTkFrame.__init__(self,parent, bd=5, corner_radius=10)
        self.pack_propagate('false')

        title = CTkLabel(self, text='Energy Price', text_font=('Microsoft Himalaya', 30, 'bold'))
        title.grid(row=0, column=0, sticky='nsew')

#FrameWeer: geeft huidgie weerssituatie weer:

class FrameWeer(CTkFrame):
    def __init__(self, parent):
        CTkFrame.__init__(self,parent, bd=5, corner_radius=10)
        self.pack_propagate('false')

        title = CTkLabel(self, text='Weather', text_font=('Microsoft Himalaya', 30, 'bold'))
        title.grid(row=0, column=0, sticky='nsew')



#FrameTotalen: geeft nog enkele statistieken weer:

class FrameTotalen(CTkFrame):
    def __init__(self, parent):
        CTkFrame.__init__(self,parent, bd=5, corner_radius=10)
        self.pack_propagate('false')

        title = CTkLabel(self, text='Totals', text_font=('Microsoft Himalaya', 30, 'bold'))
        title.grid(row=0, column=0, sticky='nsew')


if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()
    print(lijst_apparaten)
    print(lijst_verbruiken)
    print(lijst_deadlines)
    print(lijst_status)
    print(lijst_remember_settings)
    print(current_date)
    print(Prijzen24uur)
    print(Gegevens24uur)
