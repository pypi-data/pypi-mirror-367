from tkinter import *
import tkinter.font
import json
from typing import Optional
from re import match
from types import NoneType
from ..db import DB
#from cytomat_plus.scripts.setup_cytomat_plus import get_config_dir

class ManagerConfigFile:
    __root: Frame
    __db: DB
    def __init__(self, root, config_directory_path, data, db: DB) -> None:
        self.__root = root
        self.__data = data
        self.__db = db
        self.__config_directory_path = config_directory_path

        self.__row_obj_list = []
        self.__header_config: Optional[Label] = None
        self.__warning_Label: Optional[Label] = None
        self.__theme_pack: Optional[dict] = None

        self.create_overview()

    def create_overview(self):
        self.set_grid_settings()
        self.create_header_config()
        self.create_warning_message()
        self.create_row_obejcts()
        
    def create_header_config(self):
        self.__header_config = Label(self.__root, text = "Set specific parameters for the Cytomat", font=('Helvetica', 20), pady = 1, padx = 1, relief='solid')
        self.__header_config.grid(row = 0, column = 0, sticky = 'nsew', columnspan = 3, ipady=30)
    
    def create_warning_message(self):
        warning_msg =  """Warning Message: blablablalblablbllbalbllball"""
        
        self.__warning_Label = Label(self.__root, text = warning_msg, font=('Helvetica', 16), pady = 1, padx = 1, bg = 'red')
        self.__warning_Label.grid(row = 1, column=0, columnspan = 3, sticky='nsew')
        
    def set_grid_settings(self):
        #self.__root.rowconfigure(0, weight=1)
        self.__root.rowconfigure(1, weight=0)
        
        self.__root.grid_columnconfigure(0, weight=2)
        self.__root.grid_columnconfigure(1, weight=2)
        self.__root.grid_columnconfigure(2, weight=1)

    def determine_use_case(self, key):
        if 'slot' in key:
            return 'slot'

        if key == 'COM_port':
            return 'COM_port'

        return 'parameter'

    def aplay_theme_pack(self, theme_pack: dict):
        self.__theme_pack = theme_pack
        bg = theme_pack['bg']
        fg = theme_pack['fg']
        entry = theme_pack['entry']
        button = theme_pack['button']
        header = theme_pack['header']
        
        self.__root.config(bg = bg)
        self.__header_config.config(bg = header, fg = fg)
        
        for row in self.__row_obj_list:
            row: ConfigFileRow
            row.aplay_theme_pack(theme_pack=self.__theme_pack)
        
    def create_row_obejcts(self):
        self.__row_obj_list = []
        for index, (key, value) in enumerate(self.__data.items()):
            use_case = self.determine_use_case(key)
            row_obj = ConfigFileRow( root = self.__root, key = key, value = value,
                                            type = type(value), row_idx = index + 2, data = self.__data, 
                                            file_path = self.__config_directory_path, use_case= use_case, db = self.__db)
            self.__row_obj_list.append(row_obj)
        
class ConfigFileRow:
    __root: Frame
    __db: DB
    def __init__(self, root: Frame, file_path, key, value, type, row_idx, data, db, use_case):
        self.__key = key
        self.__value = value
        self.__type = type
        self.__root = root
        self.__row_idx = row_idx
        self.__data = data
        self.__use_case = use_case
        self.__file_path = file_path
        self.__db = db
        self.__db.get_slots()

        self.__row_label: Optional[Label] = None
        self.__row_entry: Optional[Entry] = None
        self.__enter_button: Optional[Button] = None
        self.entry: Optional[str] = None
        self.create_row()

    def create_row(self):
        self.__root.rowconfigure(self.__row_idx, weight = 1)
        self.create_label()
        self.create_entry()
        self.create_enter_button()

    def create_label(self):
        font = tkinter.font.Font(family = 'Times New Roman', size = 14)
        self.__row_label = Label(self.__root, text = str(self.__key), font=font, relief='solid',  pady = 5, padx = 1)
        self.__row_label.grid(row=self.__row_idx, column = 0, sticky='nsew', ipadx = len(str(self.__value)))

    def create_entry(self):
        entry_text = StringVar(value = self.__value)
        self.__row_entry = Entry(self.__root, textvariable = entry_text)
        self.__row_entry.grid(row = self.__row_idx, column = 1, sticky='nsew', ipadx = len(str(self.__value)))

    def create_enter_button(self):
        self.__enter_button = Button(self.__root, text = "Enter", command = self.enter_button_callback, font=('Helvetica', 12))
        self.__enter_button.grid(row = self.__row_idx, column = 2, sticky='nsew', ipadx = len('entry'))
        
    def aplay_theme_pack(self, theme_pack: dict):
        bg = theme_pack['bg']
        fg = theme_pack['fg']
        entry = theme_pack['entry']
        button = theme_pack['button']
        
        self.__row_entry.config(bg = entry, fg = fg)
        self.__enter_button.config(bg = button, fg = fg)
        self.__row_label.config(bg = bg, fg = fg)
        
    def enter_button_callback(self):
        self.entry = self.__row_entry.get()
        print(f"entry: {self.entry}")
        print(f"value: {self.__value}")
        
        if not self.is_entry_valid(entry = self.entry):
            self.__row_entry.delete(0, END)
            if self.__value is not None:
                self.__row_entry.insert(0, self.__value)
            return
        
        if self.entry is None:
            self.__row_entry.delete(0, END)
        
        if self.__use_case == 'slot':
            self.slot_entry_changes(old_slot = self.__value, entry = self.entry)
            
        self.__value = self.entry
        self.__data[self.__key] = self.__value
        self.write_into_json_file(self.__data)
        
        print(f"""
              used_slots: {self.get_used_slots()})
              """)

    def slot_entry_changes(self, old_slot, entry):
        print("do slot changes")
        if entry is None:
            self.db_delete_slot(old_slot)
            return
        
        if old_slot is None:
            self.db_insert_new_slot(slot = entry, role=1)
            
        else:
            
            self.db_update_slot(new_slot = self.entry, old_slot= self.__value)
   
    """
    """
    def is_entry_valid(self, entry: str):
        if entry == self.__value:
            return False
        
        if self.__use_case == 'parameter':
            return self.is_entry_valid_parameter(entry)
            
        if self.__use_case == 'slot':
            return self.is_entry_valid_slot(entry)
        
        if self.__use_case == 'COM_port':
            return self.is_entry_valid_comport(entry)
        
    def is_entry_valid_parameter(self, entry: str):
        if entry.isdigit() and (not self.__type is int) and (not self.__type is NoneType):
            print("g")
            print(self.__type)
            return
        
        if not entry.isdigit() and self.__type is int:
            print("f")
            return
        
        if entry.isdigit() and self.__type is int:
            self.entry = int(entry)
            
        if entry == "":
            self.entry = 0
            
        return True
    
    def is_entry_valid_slot(self, entry):
        if entry == "":
            self.entry = None
            return True
            
        if not entry.isdigit():
            return
            
        if int(entry) < 1:
            return
        
        if int(entry) in self.get_used_slots():
            print("entry invalid")
            return

        self.entry = int(entry)
        return True
        
    def is_entry_valid_comport(self, entry: str) -> bool:
        """
        Checks if the entry for comport is valid by using s regular expression: COM'int'

        Parameters
        ----------
        entry : str
            entry out of Entry comport widget
        """
        comp = r"^COM\d+$" 
            
        if not bool(match(comp, entry)):
            print("invalid COMport")
            return False
        return True
            
    """
    """
    def write_into_json_file(self, data):
        with open(self.__file_path / 'config.json', 'w') as file:
            json.dump(data, file, indent=4)
            
    """
    database actions
    """
    def db_delete_slot(self, slot) -> None:
        self.__db.delete_row(slot = slot)
        
    def db_insert_new_slot(self, slot, role) -> None:
        self.__db.insert_new_row(slot = slot, role = role)
        
    def db_update_slot(self, new_slot, old_slot) -> None:
        self.__db.update_slot(new_slot = new_slot, old_slot=old_slot)
        
    def get_used_slots(self)->list[int]:
        return self.__db.get_slots()