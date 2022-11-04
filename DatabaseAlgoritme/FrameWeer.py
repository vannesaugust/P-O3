from tkinter import *
from customtkinter import *
from PIL import ImageTk, Image
from tkinter import ttk
from time import strftime

class FrameWeer(CTkFrame):
    def __init__(self, parent):
        CTkFrame.__init__(self,parent, bd=5, corner_radius=10)
        self.pack_propagate('false')

        title = CTkLabel(self, text='Weather', text_font=('Microsoft Himalaya', 30, 'bold'))
        title.grid(row=0, column=0, sticky='nsew')