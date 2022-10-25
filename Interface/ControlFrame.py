from tkinter import *
from customtkinter import *
from PIL import ImageTk, Image
from tkinter import ttk
from time import strftime
from FrameApparaten import FrameApparaten
from FrameBatterijen import FrameBatterijen
from FrameTemperatuur import FrameTemperatuur


class ControlFrame(CTkFrame):
    def __init__(self, parent):
        CTkFrame.__init__(self,parent)
        self.pack_propagate('false')

        self.grid_columnconfigure((0, 1), uniform="uniform", weight=1)
        self.grid_rowconfigure((0,1), uniform="uniform", weight=1)

        frame_temperatuur = FrameTemperatuur(self)
        frame_batterijen = FrameBatterijen(self)
        frame_apparaten = FrameApparaten(self)

        frame_temperatuur.grid(row=0, column=0, padx=5, sticky='nsew')
        frame_batterijen.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')
        frame_apparaten.grid(row=0, column=1, rowspan=3, padx=5, pady=5, sticky='nsew')