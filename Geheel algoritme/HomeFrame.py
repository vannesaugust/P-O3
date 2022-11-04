from tkinter import *
from customtkinter import *
from PIL import ImageTk, Image
from tkinter import ttk
from time import strftime
from tkcalendar import Calendar

global current_date
current_date = '01-01-2016'

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
            current_date = cal.get_date()
            label_day.configure(text=str(current_date[0:2]))
            label_month.configure(text=str(current_date[3:5]))
            label_year.configure(text=str(current_date[6:10]))

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
