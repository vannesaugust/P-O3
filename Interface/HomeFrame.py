from tkinter import *
from customtkinter import *
from PIL import ImageTk, Image
from tkinter import ttk
from time import strftime
from tkcalendar import DateEntry, Calendar

class HomeFrame(CTkFrame):
    def __init__(self, parent):
        CTkFrame.__init__(self,parent, width=3840, height=2160)
        self.pack_propagate('false')

        home_title = CTkLabel(self, text='SMART SOLAR HOUSE')
        home_subtitle = CTkLabel(self, text='Door August Vannes, Jonas Thewis, Lander Verhoeven, Ruben Vanherpe,'
                                                  'Tibo Mattheus en Tijs Motmans')

        home_title.pack()
        home_subtitle.pack()

        global date
        date = self.get_date()

    def get_date(self):
        cal = Calendar(self,font="Arial 14", selectmode='day')
        cal.pack()
        ttk.Button(self, text="ok").pack()
        return cal.selection_get()


