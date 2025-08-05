from tkinter import *
from ..db import DB
from typing import Optional, Any

class ManagerSlots():
    __root: Frame
    __db: DB
    def __init__(self, root, db):
        self.__root = root
        self.__db: DB = db
        self.__row_obj_list = []

        # dict: key: tupel(start: int, end: int), value: SlotsRow()
        self.__dict_of_rows: dict = {}
        self.__reserved_slots = self.__db.get_roled_slots()
        self.__all_slots_list: list = self.__db.get_unroled_slots()

        self.__header_slots: Optional[Label] = None
        self.__entry_bottom: Optional[Entry] = None
        self.__entry_top: Optional[Entry] = None
        self.__label_middle: Optional[Label] = None
        self.__entry_upper: Optional[Entry] = None
        self.__button_enter: Optional[Button] = None

    def create_overview(self):
        self.set_grid_settings()
        self.create_header()
        self.create_entry_area()
        self.update_display()
    
    def create_header(self):
        self.__header_slots = Label(self.__root, text = "Set the Slots wich should be used", font = ('Helvetica', 20), pady = 1, padx = 1, relief='solid')
        self.__header_slots.grid(row = 0, column=0, columnspan = 4, sticky='nsew', ipady = 30)
        
    def create_entry_area(self):
        y = 12
        entry_bottom = Variable(value='bottom')
        entry_upper = Variable(value='upper')
        
        self.__entry_bottom = Entry(self.__root, textvariable = entry_bottom, justify = 'center')
        self.__entry_bottom.grid(row = 1, column = 0, sticky = 'nsew', ipady = y)
        
        self.__label_middle = Label(self.__root, text = '-', font=('Helvetica', 14))
        self.__label_middle.grid(row= 1, column = 1, sticky = 'nsew', ipady = y)
        
        self.__entry_upper = Entry(self.__root, textvariable = entry_upper, justify = 'center')
        self.__entry_upper.grid(row = 1, column = 2, sticky = 'nsew', ipady = y)
    
        self.__button_enter = Button(self.__root, text = 'Enter', command = self.enter_button_callback)
        self.__button_enter.grid(row = 1, column = 3, sticky = 'nsew', ipady = y)
    
    def set_grid_settings(self):
        #self.__root.rowconfigure(0, weight=2)
        #self.__root.rowconfigure(1, weight=1)
        self.__root.rowconfigure(2, weight=1)
        self.__root.rowconfigure(3, weight=2)
        self.__root.rowconfigure(4, weight=2)
        self.__root.columnconfigure(0, weight = 2)
        self.__root.columnconfigure(1, weight = 1)
        self.__root.columnconfigure(2, weight = 2)
        self.__root.columnconfigure(3, weight = 1)
        
    def apply_theme_pack(self, theme_pack: dict) -> None:
        """
        applies theme pack by decoding given theme pack dictionary and configure tkinter widgets

        Parameters
        ----------
        theme_pack: dict
            dictionary with
        """
        self.__theme_pack = theme_pack
        bg = theme_pack['bg']
        fg = theme_pack['fg']
        entry = theme_pack['entry']
        button = theme_pack['button']
        header = theme_pack['header']
        
        self.__root.config(bg = bg)
        self.__header_slots.config(bg=header, fg = fg)
        self.__label_middle.config(bg = bg, fg = fg)
        self.__entry_upper.config(bg = entry, fg = fg)
        self.__entry_bottom.config(bg = entry, fg = fg)
        self.__button_enter.config(bg = button, fg = fg)
        
        if len(self.__dict_of_rows)<1:
            return
        
        for row in self.__dict_of_rows.values():
            row: SlotsRow
            row.aplay_theme_pack(theme_pack=self.__theme_pack)

        
    def enter_button_callback(self):
        entry_bottom_str = self.__entry_bottom.get()
        entry_upper_str = self.__entry_upper.get()
        self.__entry_bottom.delete(0, END)
        self.__entry_upper.delete(0, END)
        
        if not self.is_entry_valid(entry_bottom= entry_bottom_str, entry_upper = entry_upper_str):
            return
        
        entry_bottom = int(entry_bottom_str)
        entry_upper = int(entry_upper_str)

        entry_list = self.get_int_list_from_entry(entry_b = entry_bottom, entry_u = entry_upper)

        new_slots_list = self.get_excluded_list(list_a= entry_list, list_b=self.__all_slots_list)

        self.update_db(new_slots_list)

        #update variables
        self.__reserved_slots = self.__db.get_roled_slots()
        self.__all_slots_list: list = self.__db.get_unroled_slots()

        self.update_display()

    def is_entry_valid(self, entry_bottom: str, entry_upper: str):
        if not entry_bottom.isdigit() or not entry_upper.isdigit():
            return
        
        entry_bottom_int = int(entry_bottom)
        entry_upper_int = int(entry_upper)
        
        if entry_upper_int < entry_bottom_int:
            return
        
        print(entry_bottom_int)
        entry_list = self.get_int_list_from_entry(entry_b = entry_bottom_int, entry_u = entry_upper_int)
        
        #checks if the entry contains roled slots
        if list(set(entry_list) & set(self.__reserved_slots)):
            return
        
        #checks if the entry is completly cotained in allready used slots
        if not list(set(entry_list) - set(self.__all_slots_list)):
            print(list(set(entry_list) - set(self.__all_slots_list)))
            print('contained')
            return
        
        print("entry valid")
        return True

    def update_display(self):
        consecutive_slots = self.__db.get_consecutive_slots()
        if len(self.__dict_of_rows) > 0:
            for row in self.__dict_of_rows.values():
                row.delete_row()
            self.__dict_of_rows = {}
        
        for idx, key in enumerate(consecutive_slots.keys()):
            self.__dict_of_rows[key] = SlotsRow(root= self.__root, bottom = key[0], upper= key[1], row_idx=idx + 2)
            try:
                self.__dict_of_rows[key].aplay_theme_pack(self.__theme_pack)
            except AttributeError:
                pass

    def get_int_list_from_entry(self, entry_b: int, entry_u: int)->list:
        entry_list = []
        for i in range(entry_b, entry_u+1):
            entry_list.append(i)

        return entry_list

    #gets list a and list b and returns the elemnts witch a contain and b not
    def get_excluded_list(self, list_a: list, list_b: list)->list:
        return list(set(list_a) - set(list_b))

    def update_db(self, list_to_insert: list):
        for slot in list_to_insert:
            self.__db.insert_new_row(slot)


class SlotsRow:
    def __init__(self, root: Toplevel, bottom: int, upper, row_idx: int) -> None:
        self.__root = root
        self.__bottom = bottom
        self.__upper = upper
        self.__row_idx = row_idx
        self.create_row()
    
    def create_row(self):
        self.set_grid_settings()
        self.__label_slots = Label(self.__root, text = f"{self.__bottom} - {self.__upper}", relief='solid')
        self.__label_slots.grid(column=0, columnspan= 3, row=self.__row_idx, sticky='nsew')

        self.__button_delete = Button(self.__root, text= 'delete', command = self.delete_button_callback, relief='solid')
        self.__button_delete.grid(column=3, row=self.__row_idx, sticky='nsew')

    def set_grid_settings(self):
        self.__root.columnconfigure(0, weight=2)
        self.__root.columnconfigure(1, weight=1)
        self.__root.rowconfigure(self.__row_idx, weight = 1)

    def delete_button_callback(self):
        pass

    def delete_row(self):
        self.__label_slots.destroy()
        self.__button_delete.destroy()

    def aplay_theme_pack(self, theme_pack):
        bg = theme_pack['bg']
        fg = theme_pack['fg']
        entry = theme_pack['entry']
        button = theme_pack['button']
        header = theme_pack['header']

        self.__label_slots.config(bg=bg, fg=fg)
        self.__button_delete.config(bg=button, fg = fg)