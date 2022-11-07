from customtkinter import *
from typing import Union, Callable

class Spinbox1(CTkFrame):
    def __init__(self, *args,
                 width: int = 100,
                 height: int = 32,
                 step_size: Union[int, float] = 1,
                 command: Callable = None,
                 **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)

        self.step_size = step_size
        self.command = command

        self.grid_columnconfigure((0, 2), weight=0)  # buttons don't expand
        self.grid_columnconfigure(1, weight=1)  # entry expands

        self.subtract_button = CTkButton(self, text="-", width=height-6, height=height-6,
                                                       command=self.subtract_button_callback)
        self.subtract_button.grid(row=0, column=0, padx=(3, 0), pady=3)

        self.entry = CTkEntry(self, width=width-(2*height), height=height-6, justify="right")
        self.entry.grid(row=0, column=1, columnspan=1, padx=3, pady=3, sticky="ew")

        self.add_button = CTkButton(self, text="+", width=height-6, height=height-6,
                                                  command=self.add_button_callback)
        self.add_button.grid(row=0, column=2, padx=(0, 3), pady=3)

        # default value
        self.entry.insert(0, "01:00")
        self.subtract_button.configure(state='DISABLED')

    def add_button_callback(self):
        if self.command is not None:
            self.command()
        try:
            inhoud = self.entry.get()
            if inhoud[0] == 0:
                nummer = inhoud[1]
            else:
                nummer = inhoud[0:2]
            value = int(nummer) + self.step_size
            self.entry.delete(0, "end")
            if value < 10:
                self.entry.insert(0, '0'+str(value)+':00')
            else:
                self.entry.insert(0, str(value)+ ':00')
            if value == 24:
                self.add_button.configure(state=DISABLED)
            else:
                self.subtract_button.configure(state=NORMAL)
        except ValueError:
            return

    def subtract_button_callback(self):
        if self.command is not None:
            self.command()
        try:
            inhoud = self.entry.get()
            if inhoud[0] == 0:
                nummer = inhoud[1]
            else:
                nummer = inhoud[0:2]
            value = int(nummer) - self.step_size
            self.entry.delete(0, "end")
            if value < 10:
                self.entry.insert(0, '0' + str(value) + ':00')
            else:
                self.entry.insert(0, str(value) + ':00')
            if value == 1:
                self.subtract_button.configure(state=DISABLED)
            else:
                self.add_button.configure(state=NORMAL)
        except ValueError:
            return

    def get(self) -> Union[int, None]:
        try:
            inhoud = self.entry.get()
            if inhoud[0] == 0:
                nummer = inhoud[1]
            else:
                nummer = inhoud[0:2]
            return int(nummer)
        except ValueError:
            return None

    def set(self, value: int):
        self.entry.delete(0, "end")
        if value < 10:
            self.entry.insert(0, '0' + str(value) + ':00')
        else:
            self.entry.insert(0, str(value) + ':00')

    def inactiveer(self):
        self.subtract_button.configure(state=DISABLED, fg_color='gray')
        self.add_button.configure(state=DISABLED, fg_color='gray')
        self.entry.delete(0,"end")

    def activeer(self):
        self.subtract_button.configure(state=NORMAL, fg_color='#395E9C')
        self.add_button.configure(state=NORMAL, fg_color='#395E9C')
        self.entry.insert(0, "01:00")


class Spinbox2(CTkFrame):
    def __init__(self, *args,
                 width: int = 100,
                 height: int = 32,
                 step_size: Union[int, float] = 1,
                 command: Callable = None,
                 **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)

        self.step_size = step_size
        self.command = command

        self.grid_columnconfigure((0, 2), weight=0)  # buttons don't expand
        self.grid_columnconfigure(1, weight=1)  # entry expands

        self.subtract_button = CTkButton(self, text="-", width=height-6, height=height-6,
                                                       command=self.subtract_button_callback)
        self.subtract_button.grid(row=0, column=0, padx=(3, 0), pady=3)

        self.entry = CTkEntry(self, width=width-(2*height), height=height-6, justify="right")
        self.entry.grid(row=0, column=1, columnspan=1, padx=3, pady=3, sticky="ew")

        self.add_button = CTkButton(self, text="+", width=height-6, height=height-6,
                                                  command=self.add_button_callback)
        self.add_button.grid(row=0, column=2, padx=(0, 3), pady=3)

        # default value
        self.entry.insert(0, "1 hour")
        self.subtract_button.configure(state='DISABLED')

    def add_button_callback(self):
        if self.command is not None:
            self.command()
        try:
            inhoud = self.entry.get()
            nummer = inhoud[:2]
            value = int(nummer) + self.step_size
            self.entry.delete(0, "end")
            if value == 1:
                self.entry.insert(0, str(value) + ' hour')
            else:
                self.entry.insert(0, str(value) + ' hours')
            if value == 24:
                self.add_button.configure(state=DISABLED)
            else:
                self.subtract_button.configure(state=NORMAL)
        except ValueError:
            return

    def subtract_button_callback(self):
        if self.command is not None:
            self.command()
        try:
            inhoud = self.entry.get()
            nummer = inhoud[:2]
            value = int(nummer) - self.step_size
            self.entry.delete(0, "end")
            if value == 1:
                self.entry.insert(0, str(value) + ' hour')
            else:
                self.entry.insert(0, str(value) + ' hours')
            if value == 1:
                self.subtract_button.configure(state=DISABLED)
            else:
                self.add_button.configure(state=NORMAL)
        except ValueError:
            return

    def get(self) -> Union[int, None]:
        try:
            inhoud = self.entry.get()
            nummer = inhoud[:2]
            return int(nummer)
        except ValueError:
            return None

    def set(self, value: int):
        self.entry.delete(0, "end")
        if value == 1:
            self.entry.insert(0, str(value) + ' hour')
        else:
            self.entry.insert(0, str(value) + ' hours')

    def inactiveer(self):
        self.subtract_button.configure(state=DISABLED, fg_color='gray')
        self.add_button.configure(state=DISABLED, fg_color='gray')
        self.entry.delete(0,"end")

    def activeer(self):
        self.subtract_button.configure(state=NORMAL, fg_color='#395E9C')
        self.add_button.configure(state=NORMAL, fg_color='#395E9C')
        self.entry.insert(0, 0)