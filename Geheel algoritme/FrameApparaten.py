from tkinter import *
from tkinter import messagebox
from customtkinter import *
from PIL import ImageTk, Image
from tkinter import ttk
from time import strftime
from Spinbox import Spinbox1, Spinbox2


global lijst_apparaten
global lijst_verbruiken
global lijst_deadlines
global lijst_status
lijst_apparaten = ['Fridge', 'Elektric Bike', 'Elektric Car', 'Dishwasher', 'Washing Manchine', 'Freezer']
lijst_soort_apparaat = ['Always on', 'Device with battery', 'Device with battery', 'Consumer', 'Consumer', 'Always on']
lijst_capaciteit = ['/', 1500, 2000, '/', '/', '/']
lijst_aantal_uren = [24, '/', '/', 2, 3, 24]
lijst_uren_na_elkaar = [24, '/', '/', 2, 3, 24]
lijst_verbruiken = [40,12,100,52,85,13,71]
lijst_deadlines = [15,17,14,'/',23,14,9]
lijst_beginuur = ['/', '/', '/', 12, 18, '/']
lijst_status = [0,1,0,0,1,1,0]

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
            status = lijst_status[nummer]
            APPARAAT(frame2, naam, soort, uren, uren_na_elkaar, capaciteit, verbruik, deadline, beginuur, status)


    def new_device(self, frame2):
        new_window = CTkToplevel(self)
        new_window.iconbitmap('solarhouseicon.ico')
        new_window.title('Add a new device')
        new_window.geometry('300x500')
        new_window.grab_set()

        new_window.rowconfigure((0,1,2,3,4,5,6,7,8,9), uniform='uniform', weight=2)
        new_window.rowconfigure(10, uniform='uniform', weight=3)
        new_window.columnconfigure('all', uniform='uniform', weight=1)

        def show_rest(event):

            """
            def show_start_time():
                if checkbox_achter_elkaar.get() == 1:
                    text_start_time = CTkLabel(new_window, text='Set a start time for the device:')
                    spinbox_start_time = Spinbox1(new_window, step_size=1)
                    checkbox_start_time = CTkCheckBox(new_window, text='No Start Time', command=checkbox_deadline_command)

                    text_start_time.grid(row=8, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
                    spinbox_start_time.grid(row=9, column=0, padx=17, pady=5, sticky='nsew')
                    checkbox_start_time.grid(row=9, column=1, padx=17, pady=5, sticky='nsew')
                else:
                    white_line_1 = CTkLabel(new_window, text='     ')
                    white_line_2 = CTkLabel(new_window, text='     ')
                    white_line_1.grid(row=8, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
                    white_line_2.grid(row=9, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
            """

            global text_verbruik, entry_verbruik, text_deadline, spinbox_deadline, checkbox_deadline, \
                spinbox_hours, checkbox_achter_elkaar, entry_capacity
            text_verbruik = CTkLabel(new_window, text='Fill in the energy usage of the device:')
            entry_verbruik = CTkEntry(new_window)
            text_verbruik.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
            entry_verbruik.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')

            if entry_soort.get() == 'Device with battery':
                text_capacity = CTkLabel(new_window, text='Fill in the battery capacity:')
                entry_capacity = CTkEntry(new_window)
                text_deadline = CTkLabel(new_window, text='Set a deadline for the device:')
                spinbox_deadline = Spinbox1(new_window, step_size=1)
                checkbox_deadline = CTkCheckBox(new_window, text='No Deadline', command=checkbox_deadline_command)

                text_capacity.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
                entry_capacity.grid(row=7, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
                text_deadline.grid(row=8, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
                spinbox_deadline.grid(row=9, column=0, padx=17, pady=5, sticky='nsew')
                checkbox_deadline.grid(row=9, column=1, padx=17, pady=5, sticky='nsew')

            if entry_soort.get() == 'Consumer':
                text_hours = CTkLabel(new_window, text='Fill in the runtime of the device:')
                spinbox_hours = Spinbox2(new_window, step_size=1)
                checkbox_achter_elkaar = CTkCheckBox(new_window, text= 'Consecutive hours')
                text_deadline = CTkLabel(new_window, text='Set a deadline for the device:')
                spinbox_deadline = Spinbox1(new_window, step_size=1)
                checkbox_deadline = CTkCheckBox(new_window, text='No Deadline', command=checkbox_deadline_command)

                text_hours.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
                spinbox_hours.grid(row=7, column=0, pady=5, sticky='nsew')
                checkbox_achter_elkaar.grid(row=7, column=1, pady=5, sticky='nsew')
                text_deadline.grid(row=8, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
                spinbox_deadline.grid(row=9, column=0, padx=17, pady=5, sticky='nsew')
                checkbox_deadline.grid(row=9, column=1, padx=17, pady=5, sticky='nsew')

                btn_bevestigen.configure(state=NORMAL)

        def apparaat_toevoegen():
            naam= entry_naam.get()
            soort = entry_soort.get()

            if soort == 'Always on':
                uren = 24
                uren_na_elkaar = 24
                capaciteit = '/'
                verbruik = entry_verbruik.get()
                deadline = '/'
                status = 'aan'

            if soort == 'Device with battery':
                uren = '/'
                uren_na_elkaar = '/'
                capaciteit = entry_capacity.get()
                verbruik = entry_verbruik.get()
                if checkbox_deadline.get() == 1:
                    deadline_apparaat = None
                else:
                    deadline_apparaat = spinbox_deadline.get()
                status = 'uit'

            if soort == 'Consumer':
                uren = spinbox_hours.get()
                if checkbox_achter_elkaar.get() == 1:
                    uren_na_elkaar == uren
                else:
                    uren_na_elkaar = '/'
                capaciteit = '/'
                verbruik = entry_verbruik.get()
                if checkbox_deadline.get() == 1:
                    deadline_apparaat = None
                else:
                    deadline_apparaat = spinbox_deadline.get()
                status = 'uit'

            APPARAAT(frame2, naam, soort, uren, uren_na_elkaar, capaciteit, verbruik, deadline, status)
            new_window.destroy()

        def checkbox_deadline_command():
            if checkbox_deadline.get() == 1:
                spinbox_deadline.inactiveer()
            else:
                spinbox_deadline.activeer()

        text_naam = CTkLabel(new_window, text='Fill in the name of the device:')
        entry_naam = CTkEntry(new_window)
        text_soort = CTkLabel(new_window, text='Select the kind of the device:')
        lijst_soorten = ['Always on', 'Device with battery', 'Consumer']
        entry_soort = CTkComboBox(new_window, values=lijst_soorten, command=show_rest)
        entry_soort.set('')
        white_space_1 = CTkLabel(new_window, text='      ')
        white_space_2 = CTkLabel(new_window, text='      ')
        white_space_3 = CTkLabel(new_window, text='      ')
        white_space_4 = CTkLabel(new_window, text='      ')
        white_space_5 = CTkLabel(new_window, text='      ')
        white_space_6 = CTkLabel(new_window, text='      ')

        text_naam.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
        entry_naam.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
        text_soort.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
        entry_soort.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
        white_space_1.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
        white_space_2.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
        white_space_3.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
        white_space_4.grid(row=7, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
        white_space_5.grid(row=8, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
        white_space_6.grid(row=9, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')

        btn_bevestigen = CTkButton(new_window, text='confirm', command=apparaat_toevoegen, state=DISABLED)
        btn_bevestigen.grid(row=10, column=1, padx=5, pady=5, sticky='nsew')
        btn_cancel = CTkButton(new_window, text='cancel', command=new_window.destroy)
        btn_cancel.grid(row=10, column=0, padx=5, pady=5, sticky='nsew')

    def edit_device(self, frame2):
        edit_window = CTkToplevel(self)
        edit_window.iconbitmap('solarhouseicon.ico')
        edit_window.title('Edit device')
        edit_window.geometry('300x400')
        edit_window.grab_set()

        edit_window.rowconfigure((0, 1, 2, 3, 4, 5,6,7), uniform='uniform', weight=2)
        edit_window.rowconfigure((8,9), uniform='uniform', weight=3)
        edit_window.columnconfigure('all', uniform='uniform', weight=1)

        def apparaat_wijzigen():
            naam_apparaat = entry_naam.get()
            verbruik_apparaat = entry_verbruik.get()
            if checkbox_deadline.get() == 1:
                deadline_apparaat = None
            else:
                deadline_apparaat = spinbox_deadline.get()
            lijst_apparaten[apparaat_nummer] = naam_apparaat
            lijst_verbruiken[apparaat_nummer] = verbruik_apparaat
            lijst_deadlines[apparaat_nummer] = deadline_apparaat
            kolom = apparaat_nummer % 3
            rij = apparaat_nummer // 3
            if naam_apparaat == '' or verbruik_apparaat == '' or deadline_apparaat == '':
                messagebox.showwarning('Warning','Please make sure to fill in all the boxes')
            else:
                APPARAAT(frame2, naam_apparaat,verbruik_apparaat,deadline_apparaat, 'uit', column=kolom, row=rij)
                edit_window.destroy()

        def set_entry(event):
            global apparaat_nummer
            apparaat_nummer = lijst_apparaten.index(choose_device.get())
            entry_naam.delete(0, 'end')
            entry_verbruik.delete(0,'end')
            entry_naam.insert(0, str(lijst_apparaten[apparaat_nummer]))
            entry_verbruik.insert(0, str(lijst_verbruiken[apparaat_nummer]))
            if lijst_deadlines[apparaat_nummer] == None:
                checkbox_deadline.select()
                spinbox_deadline.inactiveer()
            else:
                spinbox_deadline.set(lijst_deadlines[apparaat_nummer])
            btn_apparaat_verwijderen.configure(state=NORMAL)
            btn_bevestigen.configure(state=NORMAL)

        def apparaat_verwijderen():
            response = messagebox.askokcancel('Delete Device', 'Are you sure you want to delete this device?')
            if response == True:
                index = lijst_apparaten.index(choose_device.get())
                print(index)
                lijst_apparaten.pop(index)
                lijst_verbruiken.pop(index)
                lijst_deadlines.pop(index)
                lijst_status.pop(index)
                self.apparaten_in_frame(frame2)
                edit_window.destroy()

        def checkbox_command():
            if checkbox_deadline.get() == 1:
                spinbox_deadline.inactiveer()
            else:
                spinbox_deadline.activeer()

        text_choose = CTkLabel(edit_window,text='Choose the device you want to edit:')
        choose_device = CTkComboBox(edit_window, values=lijst_apparaten, command= set_entry)
        choose_device.set('')
        text_naam = CTkLabel(edit_window, text='Edit the name of the device:')
        entry_naam = CTkEntry(edit_window)
        text_verbruik = CTkLabel(edit_window, text='Edit the energy usage (in kWh):')
        entry_verbruik = CTkEntry(edit_window)
        text_deadline = CTkLabel(edit_window, text='Change the deadline for the device:')
        spinbox_deadline = Spinbox1(edit_window, step_size=1)
        checkbox_deadline = CTkCheckBox(edit_window, text ='No Deadline', command = checkbox_command)

        text_choose.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
        choose_device.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
        text_naam.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
        entry_naam.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
        text_verbruik.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
        entry_verbruik.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
        text_deadline.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
        spinbox_deadline.grid(row=7, column=0, padx=17, sticky='nsew')
        checkbox_deadline.grid(row=7, column=1, padx=17, sticky='nsew')

        btn_bevestigen = CTkButton(edit_window, text='confirm', command = apparaat_wijzigen, state=DISABLED)
        btn_bevestigen.grid(row=9, column=1, padx=5, pady=5, sticky='nsew')
        btn_cancel = CTkButton(edit_window, text='cancel', command = edit_window.destroy)
        btn_cancel.grid(row=9, column=0, padx=5, pady=5, sticky='nsew')
        btn_apparaat_verwijderen = CTkButton(edit_window, text='Delete Device', command=apparaat_verwijderen, fg_color='red', state=DISABLED)
        btn_apparaat_verwijderen.grid(row=8, column=0, columnspan=2, padx=5, pady=10, sticky='nsew')

class APPARAAT(CTkFrame):
    def __init__(self, parent, naam, soort, uren, uren_na_elkaar, capaciteit,verbruik,deadline, beginuur, status, column=None, row=None):
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
            lijst_status.append(status)

        nummer_apparaat = lijst_apparaten.index(naam)
        if column == None and row == None:
            rij = nummer_apparaat // 3
            kolom = nummer_apparaat % 3
        else:
            rij = row
            kolom = column
        self.grid(row=rij,column=kolom, sticky='nsew')

        naam_apparaat = CTkLabel(self, text=naam, text_font=('Biome', 12, 'bold'))
        naam_apparaat.grid(row=0, column=0, sticky='nsew')
        soort_apparaat = CTkLabel(self, text= soort, text_font=('Biome',10))
        soort_apparaat.grid(row=1, column=0, sticky='nsew')
        verbruik = CTkLabel(self, text='Energy Usage: ' + str(verbruik) + ' kWh', text_font=('Biome', 10))
        verbruik.grid(row=2, column=0, sticky='nsew')
        if soort == 'Consumer':
            if uren == uren_na_elkaar:
                na_elkaar = 'succesively'
            else:
                na_elkaar = 'random'
            aantal_uren = CTkLabel(self, text= 'Daily use: ' + str(uren) + ' hours (' + na_elkaar + ')', text_font=('Biome', 10))
            aantal_uren.grid(row=3, column=0, sticky='nsew')
            if beginuur == '/':
                beginuur = CTkLabel(self, text='No start time', text_font=('Biome', 10))
            else:
                beginuur = CTkLabel(self, text= 'Current start time: ' + str(beginuur) + 'u', text_font = ('Biome', 10))
            beginuur.grid(row=4, column=0, sticky='nsew')
        if soort == 'Device with battery':
            capaciteit = CTkLabel(self, text= 'Battery Capacity: ' + str(capaciteit) + ' kWh', text_font=('Biome', 10))
            capaciteit.grid(row=3, column=0, sticky='nsew')
            if deadline == '/':
                deadline = CTkLabel(self, text='No Deadline', text_font=('Biome', 10))
            else:
                deadline = CTkLabel(self, text='Current Deadline:  ' + str(deadline) + 'u', text_font=('Biome', 10))
            deadline.grid(row=4, column=0, sticky='nsew')
        if soort == 'Always on':
            white_space_1 = CTkLabel(self, text='     ', text_font=('Biome', 10))
            white_space_1.grid(row=3, column=0, sticky='nsew')
            white_space_2 = CTkLabel(self, text='     ', text_font=('Biome', 10))
            white_space_2.grid(row=4, column=0, sticky='nsew')
        if status == 1:
            bg_color = "#74d747"
            status_text = 'ON'
        else:
            bg_color = "#f83636"
            status_text = 'OFF'
        status = CTkLabel(self, text=status_text, bg_color=bg_color, width=0.1185*frame_width, height= 0.025*frame_height)
        status.grid(row=5, column=0, padx=5, pady=5)