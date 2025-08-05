from tkinter import *
from .utils import lazy_load_config_file
from .scripts.setup_cytomat_plus import get_config_dir
from .manage_settings.manager_slots import ManagerSlots
from .manage_settings.manager_config_file import ManagerConfigFile
from sqlite3 import IntegrityError
from typing import  Optional
import tkinter.font

class ManagerSettings:
    __root: Toplevel
    def __init__(self, db, root, gui):
        self.__root = Toplevel(root)
        self.__root.title('Setting Manager')
        self.__root.geometry('1280x720')
        self.__root.withdraw()
        self.__db = db
        self.__gui: GUI = gui # type: ignore

        #from utils file
        self.__config_data_json: dict = lazy_load_config_file()
        #from setup_cytomat file
        self.__config_path = get_config_dir()

        self.sync_db_with_config_file()
        self.__root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.check_box_var_foc = BooleanVar()
        self.__theme_pack: Optional[dict] = None
        self.__theme_pack_set_dark, self.__theme_pack_set_bright =  self.init_theme_pack()
        self.set_theme_pack('bright')

        self.__enter_label_settings:Optional[Label] = None
        self.__enter_label_gui: Optional[Label] = None
        self.__button_settings: Optional[Button] = None
        self.__button_gui: Optional[Button] = None
        self.__check_box_run_foc:Optional[Checkbutton] = None

        self.__default_hour_value: int = 3
        self.__hour_var = StringVar(value=str(self.__default_hour_value))
        self.__default_min_value = 0
        self.__minute_var = StringVar(value = str(self.__default_min_value))

        self.__label_foc_hour: Optional[Label] = None
        self.__entry_foc_hour: Optional[Entry] = None
        self.__entry_foc_minute: Optional[Entry] = None
        self.__label_foc_minute: Optional[Label] = None
        self.__label_middle: Optional[Label] = None
        self.__button_enter_foc: Optional[Button] = None

        self.check_box_var = BooleanVar()
        self.__check_box_theme: Optional[Checkbutton] = None

        self.top_level: Optional[ManagerSettingsTop] = None

    def get_root(self):
        return self.__root

    def display_window(self):
        self.__root.deiconify()

    def on_close(self):
        #self.no_button_callback()
        self.__root.withdraw()

    def create_overview(self):
        self.set_grid_settings()
        self.create_color_label()
        self.create_enter_label()
        self.create_button_gui()
        self.create_button_settings()
        self.create_theme_check_box()
        self.create_all_foc_check_box()
        self.create_entry_box_foc()
        self.create_enter_foc()

        #Ttheme pack is initialized in constructor
        self.aplay_theme_settings(self.__theme_pack)

    def set_grid_settings(self):
        self.__root.rowconfigure(0, weight = 1)
        self.__root.rowconfigure(1, weight = 1)
        self.__root.rowconfigure(2, weight = 1)
        self.__root.rowconfigure(3, weight = 1)
        self.__root.columnconfigure(0, weight = 4)
        self.__root.columnconfigure(1, weight = 1)
        self.__root.columnconfigure(2, weight = 1)
        self.__root.columnconfigure(3, weight = 1)
        self.__root.columnconfigure(4, weight = 1)

    def create_enter_label(self):
        font = tkinter.font.Font(family = 'Times New Roman', size = 14)

        self.__enter_label_settings = Label(self.__root, text = 'Enter Settings', font=font)
        self.__enter_label_settings.grid(row=0, column=0)

        self.__enter_label_gui = Label(self.__root, text = 'Enter Cytomat GUI', font = font)
        self.__enter_label_gui.grid(row = 2, column=0)

    def create_button_settings(self):
        self.__button_settings = Button(self.__root, text = 'Enter', command = self.settings_button_callback)
        self.__button_settings.grid(row = 1, column=0, ipadx = 40, ipady = 10, sticky='n')

    def create_button_gui(self):
        self.__button_gui = Button(self.__root, text = 'Enter', command = self.gui_button_callback)
        self.__button_gui.grid(row = 3, column=0, ipadx = 40, ipady = 10, sticky='n')

    def settings_button_callback(self):
        self.create_top_level_window()

    def gui_button_callback(self):
        self.__root.withdraw()

    def create_all_foc_check_box(self):
        self.check_box_var_foc = BooleanVar()
        self.__check_box_run_foc = Checkbutton(self.__root, text = 'Run all foc at time', variable= self.check_box_var_foc, command = self.all_foc_check_box_callback)
        self.__check_box_run_foc.grid(row = 1, column=1, sticky='w')

    def all_foc_check_box_callback(self):
        if self.check_box_var_foc.get():
            self.__entry_foc_hour.config(state='normal', textvariable=self.__hour_var)
            self.__entry_foc_minute.config(state='normal', textvariable = self.__minute_var)
            self.__button_enter_foc.config(state='normal')
        else:
            text_var_dis = StringVar(value='')
            self.__entry_foc_hour.config(textvariable=text_var_dis, state='disabled')
            self.__entry_foc_minute.config(textvariable=text_var_dis, state='disabled')
            self.__button_enter_foc.config(state='disabled')
            self.__gui.set_run_all_foc_at_time(False)

    def create_entry_box_foc(self):
        self.__label_foc_hour = Label(self.__root,  text='hour')
        self.__label_foc_hour.grid(row=1, column=1, sticky='sw')

        self.__entry_foc_hour = Entry(self.__root, state='disabled')
        self.__entry_foc_hour.grid(row = 2, column = 1, sticky='nwe')

        self.__label_foc_minute = Label(self.__root, text='minute')
        self.__label_foc_minute.grid(row=1, column=3, sticky='sw')

        self.__entry_foc_minute = Entry(self.__root, state='disabled')
        self.__entry_foc_minute.grid(row = 2, column = 3, sticky='nwe')

        self.__label_middle = Label(self.__root, text = ':')
        self.__label_middle.grid(row = 2, column = 2, sticky='new', ipadx=10)

    def create_color_label(self):
        self.__color_label = Label(self.__root, bg = 'red')
        #TODO place label

    def create_enter_foc(self):
        self.__button_enter_foc = Button(self.__root, text = 'Enter ', command = self.enter_foc_button_callback, state='disabled')
        self.__button_enter_foc.grid(row = 1, column=3, rowspan=3, sticky = 'e')

    def enter_foc_button_callback(self):
        if not self.check_box_var_foc.get():
            return

        entry_min = self.__entry_foc_minute.get()
        entry_hour = self.__entry_foc_hour.get()

        if not self.is_entries_valid(entry_min=entry_min, entry_h=entry_hour):
            self.__entry_foc_hour.delete(0, END)
            self.__entry_foc_minute.delete(0, END)

            self.__hour_var.set(str(self.__default_hour_value))
            self.__minute_var.set(str(self.__default_min_value))
            return


        self.__hour_var.set(entry_hour)
        self.__minute_var.set(entry_min)
        entry_min = int(entry_min)
        entry_hour = int(entry_hour)
        self.__gui.set_run_all_foc_at_time(bool_run=True, timer_hour=entry_hour, timer_minute=entry_min)
        print(entry_hour, entry_min)

    def is_entries_valid(self, entry_min: str, entry_h: str):
        if not entry_min.isdigit() or not entry_h.isdigit():
            return

        entry_min = int(entry_min)
        entry_h = int(entry_h)

        if entry_h > 23 or entry_min>59:
            return

        return True

    def create_theme_check_box(self):
        self.check_box_var = BooleanVar()
        self.__check_box_theme = Checkbutton(self.__root, text = 'Dark Mode', variable= self.check_box_var, command = self.theme_check_box_callback)
        self.__check_box_theme.grid(row = 0, column=1, sticky='sw')

    def theme_check_box_callback(self):
        if self.check_box_var.get():
            self.set_theme_pack('dark')
        else:
            self.set_theme_pack('bright')

        self.aplay_theme_settings(self.__theme_pack)

    def set_theme_pack(self, theme):
        if theme == 'dark':
            self.__theme_pack = self.__theme_pack_set_dark

        if theme == 'bright':
            self.__theme_pack =  self.__theme_pack_set_bright


    def get_theme_pack(self) -> dict:
        return self.__theme_pack

    def init_theme_pack(self)->tuple[dict, dict]:
        theme_pack_dark: dict = {'family': 'dark', 'entry': '#616161', 'button': '#424242', 'fg': 'white',
                                 'bg': '#454545', 'header': '#707070', 'check_box': '#626969', 'label': '#a2a6a4','fg_check_box': 'grey'}

        theme_pack_bright: dict = {'family': 'bright', 'entry': 'lightgrey', 'button': 'white', 'fg': 'black',
                                   'bg': '#E5E5E5', 'header': '#BDBDBD', 'check_box': '#E5E5E5', 'label': '#dad6cb', 'fg_check_box': 'white'}

        return theme_pack_dark, theme_pack_bright


    def aplay_theme_settings(self, theme_pack: dict):
        """
        configures the colors of the widgets according to the theme pack dictionary

        """
        bg = theme_pack['bg']
        fg = theme_pack['fg']
        entry = theme_pack['entry']
        button = theme_pack['button']
        check_box = theme_pack['check_box']
        fg_check_box = theme_pack['fg_check_box']
        label = theme_pack['label']

        self.__root.config(bg=bg)
        self.__button_settings.config(bg = button, fg = fg)
        self.__button_gui.config(bg = button, fg = fg)
        self.__enter_label_settings.config(fg = fg, bg = bg)
        self.__enter_label_gui.config(bg = bg, fg = fg)
        self.__check_box_theme.config(bg = check_box, fg = fg, selectcolor = fg_check_box)
        self.__check_box_run_foc.config(bg = check_box, fg =  fg, selectcolor=fg_check_box)
        self.__label_foc_hour.config(bg = bg, fg = fg)
        self.__label_foc_minute.config(bg = bg, fg = fg)
        self.__button_enter_foc.config(bg = button, fg  = fg)
        self.__label_middle.config(bg = bg, fg = fg)


        try:
            self.top_level.applay_theme_pack(theme_pack=self.__theme_pack)
        except Exception:
            pass

    def create_top_level_window(self):
        self.top_level = ManagerSettingsTop(root = self.__root, config_data=self.__config_data_json, config_path=self.__config_path, db = self.__db)
        self.top_level.create_overview()
        self.top_level.applay_theme_pack(theme_pack=self.__theme_pack)

    def sync_db_with_config_file(self)->None:
        """
        updates the Database after the json file has been changed
        """
        for key, value in self.__config_data_json.items():
            if not 'slot' in key:
                continue

            if not value:
                continue

            try:
                self.__db.insert_new_row(slot = value, role = 1)

            except IntegrityError:
                continue
        #Create Rows to Setup Slots
    def submit_callback(self):
        pass

class ManagerSettingsTop:
    __root: Toplevel
    def __init__(self, root, db, config_path, config_data):
        self.__root = Toplevel(root)
        self.__root.title('Settings')
        self.__root.geometry('1920x1080')
        
        self.__db = db
        self.__config_data_json = config_data
        self.__config_path = config_path

        self.__right_frame: Optional[Frame] = None
        self.__left_frame: Optional[Frame] = None

        self.__manager_config: Optional[ManagerConfigFile] = None
        self.__manager_slots: Optional[ManagerSlots] = None

        self.__theme_pack: Optional[dict] = None
        self.setup_frames()

    def get_root(self):
        return self.__root
        
    def create_overview(self):
        self.__manager_config = ManagerConfigFile(root = self.__left_frame, data = self.__config_data_json, config_directory_path = self.__config_path, db=self.__db)
        self.__manager_slots = ManagerSlots(root = self.__right_frame, db = self.__db)
        
        self.__manager_config.create_overview()
        self.__manager_slots.create_overview()

    def setup_frames(self):
        self.__left_frame = Frame(self.__root)
        self.__left_frame.grid(row = 0, column = 0, sticky = 'nsew')
                
        self.__right_frame = Frame(self.__root, bg = 'lightblue')
        self.__right_frame.grid(row = 0, column = 1, sticky = 'nsew')
        
        self.__root.columnconfigure(0, weight=1)
        self.__root.columnconfigure(1, weight = 1)
        self.__root.rowconfigure(0, weight = 1)
    
    def applay_theme_pack(self, theme_pack):
        self.__theme_pack = theme_pack
        self.__manager_config.aplay_theme_pack(theme_pack = self.__theme_pack)
        self.__manager_slots.apply_theme_pack(theme_pack = self.__theme_pack)

class ThemePack:
    def __init__(self, root):
        self.__root = root