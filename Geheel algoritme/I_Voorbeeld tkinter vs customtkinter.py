from customtkinter import *
from tkinter import *

#SIMPELE APP IN CUSTOMTKINTER:

class App1(CTk):
    def __init__(self):
        super().__init__(fg_color='black')

        set_appearance_mode('dark')
        set_default_color_theme('dark-blue')

        self.geometry("200x200")
        self.title("Small app in Customtkinter")


        frame = CTkFrame(self, corner_radius=10)
        frame.pack(fill='both', expand=1, padx=10, pady=10)

        label = CTkLabel(frame, text= 'Dit is een label', bg_color='gray20', corner_radius=10)
        label.pack(fill='both', expand=1, padx=10, pady=10)
        entry = CTkEntry(frame, text='Dit is een entry field', justify='center')
        entry.insert(0,'Dit is een entry field')
        entry.pack(fill='both', expand=1, padx=10, pady=10)
        button = CTkButton(frame, text='Dit is een button')
        button.pack(fill='both', expand=1, padx=10, pady=10)

#DEZELFDE SIMPELE APP IN TKINTER

class App2(Tk):
    def __init__(self):
        super().__init__()

        self.geometry("200x200")
        self.title("Small app in Tkinter")

        frame = Frame(self)
        frame.pack(fill='both', expand=1, padx=10, pady=10)

        label = Label(frame, text='Dit is een label')
        label.pack(fill='both', expand=1, padx=10, pady=10)
        entry = Entry(frame, text='Dit is een entry field', justify='center')
        entry.insert(0, 'Dit is een entry field')
        entry.pack(fill='both', expand=1, padx=10, pady=10)
        button = Button(frame, text='Dit is een button')
        button.pack(fill='both', expand=1, padx=10, pady=10)

if __name__ == "__main__":
    app = App1()
    app.mainloop()