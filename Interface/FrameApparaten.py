from tkinter import *
from customtkinter import *
from PIL import ImageTk, Image
from tkinter import ttk
from time import strftime


global lijst_apparaten
global lijst_verbruiken
global lijst_deadlines
global lijst_status
lijst_apparaten = []
lijst_verbruiken = []
lijst_deadlines = []
lijst_status = []

class FrameApparaten(CTkFrame):
    def __init__(self, parent):
        CTkFrame.__init__(self,parent, bd=5, corner_radius=10)
        self.pack_propagate('false')

        self.grid_rowconfigure((0,2), uniform="uniform", weight=1)
        self.grid_rowconfigure(1, uniform="uniform", weight=16)
        self.grid_columnconfigure((0,1), uniform="uniform", weight=1)

        btn_newdevice = CTkButton(self, text='Add new device', command=lambda: self.new_device(frame2))
        btn_newdevice.grid(row=2,column=1, padx=5, sticky='nsew')
        btn_editdevice = CTkButton(self, text='Edit existing device', command=self.edit_device)
        btn_editdevice.grid(row=2, column=0, padx=5, sticky='nsew')
        title = CTkLabel(self, text="CURRENT DEVICES")
        title.grid(row=0, sticky = 'nsew')
        frame1 = CTkFrame(self)
        frame1.grid(row=1,column=0, columnspan=2, sticky='nsew')

        my_canvas = CTkCanvas(frame1)
        my_canvas.pack(side='left',fill='both', expand=1)

        my_scrollbar = CTkScrollbar(frame1,orientation='vertical', command=my_canvas.yview)
        my_scrollbar.pack(side=RIGHT,fill='y')

        frame2 = CTkFrame(my_canvas)
        my_canvas.create_window((0, 0), window=frame2, anchor='nw')

        my_canvas.configure(yscrollcommand=my_scrollbar.set)
        my_canvas.bind('<Configure>', lambda e: my_canvas.configure(scrollregion=my_canvas.bbox("all")))


        APPARAAT(frame2, 'frigo', 40, 10.00,'aan')
        APPARAAT(frame2, 'wasmachine1',80, 15.00, 'uit')
        APPARAAT(frame2, 'wasmachine2', 80, 15.00, 'uit')
        APPARAAT(frame2, 'wasmachine3', 80, 15.00, 'uit')
        APPARAAT(frame2, 'wasmachine4', 80, 15.00, 'uit')
        APPARAAT(frame2, 'wasmachine5', 80, 15.00, 'uit')
        APPARAAT(frame2, 'wasmachine6', 80, 15.00, 'uit')
        APPARAAT(frame2, 'wasmachine7', 80, 15.00, 'uit')
        APPARAAT(frame2, 'wasmachine8', 80, 15.00, 'uit')
        APPARAAT(frame2, 'wasmachine9', 80, 15.00, 'uit')
        APPARAAT(frame2, 'wasmachine10', 80, 15.00, 'uit')
        APPARAAT(frame2, 'wasmachine11', 80, 15.00, 'aan')
        APPARAAT(frame2, 'wasmachine12', 80, 15.00, 'uit')
        APPARAAT(frame2, 'wasmachine13', 80, 15.00, 'uit')
        APPARAAT(frame2, 'wasmachine14', 80, 15.00, 'uit')
        APPARAAT(frame2, 'wasmachine15', 80, 15.00, 'uit')
        APPARAAT(frame2, 'wasmachine16', 80, 15.00, 'aan')
        APPARAAT(frame2, 'wasmachine17', 80, 15.00, 'uit')
        APPARAAT(frame2, 'wasmachine18', 80, 15.00, 'uit')

    def new_device(self, frame2):
        new_window = CTkToplevel(self)
        new_window.iconbitmap('solarhouseicon.ico')
        new_window.title('Add a new device')
        new_window.geometry('700x700')

        text_naam = CTkLabel(new_window, text='Vul de naam van het apparaat in:')
        entry_naam = CTkEntry(new_window)
        text_verbruik = CTkLabel(new_window, text='Geef het verbruik van het apparaat:')
        entry_verbruik = CTkEntry(new_window)
        text_deadline = CTkLabel(new_window, text='Voeg eventueel een deadline toe:')
        entry_deadline = CTkEntry(new_window)

        text_naam.grid(row=0, column=0, columnspan=2)
        entry_naam.grid(row=1, column=0, columnspan=2)
        text_verbruik.grid(row=2, column=0, columnspan=2)
        entry_verbruik.grid(row=3, column=0, columnspan=2)
        text_deadline.grid(row=4, column=0, columnspan=2)
        entry_deadline.grid(row=5, column=0, columnspan=2)

        def apparaat_toevoegen():
            naam_apparaat = entry_naam.get()
            verbruik_apparaat = entry_verbruik.get()
            deadline_apparaat = entry_deadline.get()
            APPARAAT(frame2, str(naam_apparaat), str(verbruik_apparaat), str(deadline_apparaat), 'uit')
            new_window.destroy()

        btn_bevestigen = CTkButton(new_window, text='confirm', command = apparaat_toevoegen)
        btn_bevestigen.grid(row=6, column=0)

        btn_cancel = CTkButton(new_window, text='cancel', command = new_window.destroy)
        btn_cancel.grid(row=6, column=1)

    def edit_device(self):
        edit_window = CTkToplevel(self)
        edit_window.iconbitmap('solarhouseicon.ico')
        edit_window.title('Edit device')
        edit_window.geometry('700x700')

        text_naam = CTkLabel(edit_window,text='Choose the device you want to edit:')


class APPARAAT(CTkFrame):
    def __init__(self, parent, naam_apparaat, verbruik,deadline,status):
        CTkFrame.__init__(self, parent,bd=5, corner_radius=5)

        self.rowconfigure('all',uniform="uniform", weight=1)
        self.columnconfigure('all', uniform = 'uniform', weight=1)

        lijst_apparaten.append(naam_apparaat)
        lijst_verbruiken.append(verbruik)
        lijst_deadlines.append(deadline)
        lijst_status.append(status)
        aantal_apparaten = len(lijst_apparaten)
        if aantal_apparaten % 3 == 0:
            rij = (aantal_apparaten // 3) - 1
        else:
            rij = aantal_apparaten // 3
        if aantal_apparaten % 3 == 0:
            kolom = 2
        else:
            kolom = (aantal_apparaten % 3) - 1
        self.grid(row=rij,column=kolom, sticky='nsew')

        naam_apparaat = CTkLabel(self, text=naam_apparaat)
        naam_apparaat.grid(row=0, column=0)
        verbruik = CTkLabel(self, text='Verbruik ='+str(verbruik))
        verbruik.grid(row=1, column=0)
        deadline = CTkLabel(self, text='Huidige deadline ='+str(deadline)+'u')
        deadline.grid(row=2, column=0)
        if status == "aan":
            bg_color = "green"
        else:
            bg_color = "red"
        status = CTkLabel(self, text=str(status), height=25, width=240, bg_color=bg_color, corner_radius=10)
        status.grid(row=6, column=0)

