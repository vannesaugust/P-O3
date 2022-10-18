from tkinter import *
from customtkinter import *
from PIL import ImageTk, Image
from tkinter import ttk
from time import strftime
from HomeFrame import HomeFrame
from ControlFrame import ControlFrame
from StatisticFrame import StatisticFrame
from FrameApparaten import lijst_apparaten, lijst_verbruiken, lijst_status, lijst_deadlines

set_appearance_mode("dark")
set_default_color_theme("dark-blue")

class MainApplication(CTk):
    def __init__(self):
        super().__init__()

        self.geometry('3840x2160+0+0')
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


if __name__ == "__main__":
    app = MainApplication()
    print(lijst_apparaten)
    print(lijst_verbruiken)
    print(lijst_deadlines)
    print(lijst_status)
    app.mainloop()