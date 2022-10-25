from tkinter import *
from customtkinter import *
from PIL import ImageTk, Image
from tkinter import ttk
from time import strftime
from tkcalendar import Calendar

class HomeFrame(CTkFrame):
    def __init__(self, parent):
        CTkFrame.__init__(self,parent, width=3840, height=2160)

        background = ImageTk.PhotoImage(Image.open("solar-panel.png").resize((3840, 2160), Image.ANTIALIAS))

        my_canvas = Canvas(self, width=3840, height=2160, bg=('gray16'))
        my_canvas.pack(fill="both", expand=True)
        my_canvas.create_image((0,0), image=background)

        frame1 = CTkFrame(self, padx=10, pady=10, width=1000, height=200)
        frame1.pack_propagate('false')
        my_canvas.create_window((350,50), window=frame1, anchor="nw")
        frame2 = CTkFrame(self, padx=10, pady=10, width=1000, height=450)
        frame2.grid_propagate('false')
        my_canvas.create_window((350, 350), window=frame2, anchor="nw")

        home_title = CTkLabel(frame1, text='SMART SOLAR HOUSE', text_font=('Biome',60, 'bold'))
        home_subtitle = CTkLabel(frame1, text='Made by August Vannes, Jonas Thewis, Lander Verhoeven, Ruben Vanherpe,',text_font=('Biome', 15))
        home_subtitle2 = CTkLabel(frame1, text= 'Tibo Mattheus and Tijs Motmans', text_font=('Biome', 15))

        home_title.pack()
        home_subtitle.pack()
        home_subtitle2.pack()

        frame2.rowconfigure((0,3), uniform= 'uniform', weight=2)
        frame2.rowconfigure(1, uniform='uniform', weight=12)
        frame2.rowconfigure(2, uniform='uniform', weight=2)
        frame2.columnconfigure(0, uniform= 'uniform', weight=1)

        selected_date = CTkLabel(frame2, text='Here you can change the current date:')
        selected_date.grid(column=0, row=0, sticky='nsew', padx=5, pady=2)
        cal = Calendar(frame2, selectmode='day', date_pattern='dd-mm-y')
        cal.grid(column=0, row=1, sticky='nsew', padx=50, pady=5)

        def grad_date():
            date.config(text="The current date is: " + cal.get_date())

        btn = CTkButton(frame2, text="Confirm the chosen date",command=grad_date)
        btn.grid(column=0, row=2, sticky='nsew', padx=40, pady=2)

        date = CTkLabel(frame2, text="")
        date.grid(column=0, row=3, sticky='nsew', padx=5, pady=2)


