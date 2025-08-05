import time
from datetime import datetime, timedelta
from tkinter import *
from tkinter.ttk import Progressbar
from typing import  Optional
from cytomat.parameters import Parameters
from cytomat.status import OverviewStatus
from .manager_settings import ManagerSettings
from .db import DB
from .cytomat_plus import CytomatPlus

class GUI:
    __root: Tk
    __cytomat: CytomatPlus
    __DB: DB
    __manager_settings: ManagerSettings
    def __init__(self):
        self.__root = Tk()
        self.__root.title('Cytomat Gui')
        self.__root.geometry('1920x1080')

        self.__parameters = Parameters()
        self.__parameters.load()
        #self.__root.attributes('-fullscreen', True)

        self.__cytomat = CytomatPlus(self.__parameters.COM_port)
        self.__DB = DB()

        self.__manager_settings = ManagerSettings(db = self.__DB, root = self.__root, gui = self)
        self.__manager_settings.create_overview()

        self.__interrupted: bool = False
        self.checker: bool = False
        self.busy_v: bool = False
        self.__pause: bool = False
        self.__root.protocol('WM_DELETE_WINDOW', self.on_close)
        self.busy_row: Optional[int] = None
        #contains all slots where role = 0 in form of a dictionary 
        self.__db_data: list[dict] = self.__DB.get_rows_role_dict(role = 0)
        self.after_id = None
        self.after_id_2 = None
        self.check_if_transfer_occupied()

        self.__list_of_row_objects: Optional[list[GUI_row]] = None
        self.__header_1: Optional[Label] = None
        self.__header_2: Optional[Label] = None
        self.__header_3: Optional[Label] = None
        self.__header_4: Optional[Label] = None
        self.__setting_button: Optional[Button] = None

        self.__ran_all_foc: Optional[bool] = None

        self.__insert_window: Optional[Toplevel] = None
        self.year: Optional[StringVar] = None
        self.month: Optional[StringVar] = None
        self.day: Optional[StringVar] = None
        self.index_: Optional[StringVar] = None

        self.wait_for_submit: Optional[IntVar] = None
        self.submit_insert: Optional[bool] = None

        self.__progress_window: Optional[Toplevel] = None
        self.__progressbar: Optional[Progressbar] = None
        self.__status_label: Optional[Label] = None
        self.__pause_btn: Optional[Button] = None

        self.__reboot_window: Optional[Toplevel] = None
        self.__cyto_init_btn: Optional[Button] = None
        self.__continue_btn: Optional[Button] = None
        self.__get_back_btn: Optional[Button] = None

        self.__interrupt_window_submit: Optional[IntVar] = None #Type later: IntVar
        self.current_task_idx: Optional[int] = None

        self.submit_delete_wait: Optional[IntVar] = None
        self.__submit_delete_window: Optional[Toplevel] = None
        self.__submit_delete_label: Optional[Label] = None
        self.__submit_delete_btn: Optional[Button] = None
        self.__cancel_delete: [Button] = None
        self.submit_delete: Optional[bool] = None

        self.interrupt_state = None
        self.__display_interrupt_action:Optional[Toplevel] = None
        self.__display_action_label: Optional[Label] = None
        self.__header_run: Optional[Label] = None
        self.__run_all_btn: Optional[Button] = None
        self.__run_specific_btn: Optional[Button] = None
        self.__choose_specific_window: Optional[Toplevel] = None
        self.__specific_plates_dict: Optional[dict[int, GUI_row]] = {}
        self.__multiple_media_change_btn: Optional[Button] = None
        self.__multiple_eject_btn: Optional[Button] = None
        self.__multiple_measurement_btn: Optional[Button] = None

    def get_root(self):
        return self.__root

    def set_busy_state(self, busy: bool) -> None:
        """
        sets every row to given busy state

        Parameters
        ----------
        busy: bool
            represents if the GUI/Cytomat is in a busy state
        """
        for row in self.__list_of_row_objects:
            row.busy(busy)

    def get_cytomat_status(self) -> OverviewStatus:
        return self.__cytomat.get_status()

    def create_overview(self) -> None:
        """
        Creates Overview contents and sets arrangement settings
        """
        self.set_dynamic_window_settings()
        self.create_headers()
        self.create_setting_button()
        self.create_row_objects()
        self.create_row_run_all()

    #every row in th gui consists of an object of the gui_row class
    def create_row_objects(self) -> None:
        self.__list_of_row_objects = []
        """
        Creates one row of type gui_row for each row in db_data and adds row object to list
        """
        for row_idx, data_dict in enumerate(self.__db_data):
            row = GUI_row(row_idx+2, root=self.__root, gui = self, db = self.__DB, cytomat=self.__cytomat, transfer_oc=self.checker, data = data_dict)
            self.__list_of_row_objects.append(row)

    def update_overview(self) -> None:
        """
        each row ist getting flashed with updated db_data content
        """
        self.__db_data = self.__DB.get_rows_role_dict()
        self.create_row_objects()

    def set_dynamic_window_settings(self) -> None:
        """
        Overview grid is set proportional to window size
        """
        self.__root.columnconfigure(0, weight=1)
        self.__root.columnconfigure(1, weight=1)
        self.__root.columnconfigure(2, weight=1)
        self.__root.columnconfigure(3, weight=1)
        self.__root.columnconfigure(4, weight=1)
        self.__root.columnconfigure(5, weight=1)

        for i in range(1, len(self.__db_data) + 2):
            self.__root.rowconfigure(i, weight = 1)


    def create_headers(self) -> None:
        """
        Defines and places the headers
        """
        y = 30
        self.__header_1: Label = Label(self.__root, text='SlotNumer', bg= 'lightgray', relief='solid', borderwidth= 2, pady = 5, font=('Helvetica', 16) )
        self.__header_1.grid(column=0, row=0, pady = 20, sticky = 'ew', columnspan= 1, ipadx = len('SlotNumber'), ipady=y)

        self.__header_2: Label = Label(self.__root, text='Role', bg= 'lightgray', relief='solid', borderwidth= 2, pady = 5, font=('Helvetica', 16) )
        self.__header_2.grid(column=1, row=0, pady = 20, sticky = 'ew', columnspan= 1, ipadx = len('Role'), ipady=y)

        self.__header_3: Label = Label(self.__root, text='AssignedPlatePlateId', bg= 'lightgray', relief='solid', borderwidth= 2, pady = 5 , font=('Helvetica', 16))
        self.__header_3.grid(column=2, row=0, pady = 20, sticky = 'new', columnspan= 1, ipadx= len('AssignedPlatePlateId'), ipady=y)

        self.__header_4: Label = Label(self.__root, text='command', bg= 'lightgray', relief='solid', borderwidth= 2, pady = 5, font=('Helvetica', 16) )
        self.__header_4.grid(column=3, row=0, pady = 20, sticky = 'new', columnspan= 3, ipadx = len('commands'), ipady=y)

    def create_setting_button(self):
        """
        Defines and places the setting Button
        """
        self.__setting_button = Button(self.__root, text = "Settings", command = self.setting_button_callback)
        self.__setting_button.grid(row = 0, column = 5, ipadx = 15, ipady = 15, sticky='ne', pady=5)

    def setting_button_callback(self):
        self.__manager_settings.display_window()

    def create_row_run_all(self)->None:
        """
        creates a row to control commands of all plates at once

        """
        self.__row_one_frame = Frame(self.__root)
        self.__row_one_frame.grid(row = 1, column=0, columnspan=3, sticky='nsew')

        self.__row_one_frame.columnconfigure(0, weight=1)
        self.__row_one_frame.columnconfigure(1, weight=2)
        self.__row_one_frame.columnconfigure(2, weight=2)
        self.__row_one_frame.rowconfigure(0, weight=1)

        self.__header_run = Label(self.__row_one_frame, text='Run:', bg= 'lightgray', relief='solid', borderwidth= 2, pady = 5 , font=('Helvetica', 16))
        self.__header_run.grid(row = 0, column = 0, sticky = 'nsew', columnspan= 1, ipadx= len('run'))

        self.__run_all_btn = Button(self.__row_one_frame, text = 'All', command=self.run_all_btn_callback, bg= 'yellow', relief='raised', borderwidth= 2, pady = 5 , font=('Helvetica', 16))
        self.__run_all_btn.grid(row = 0, column = 1, sticky = 'nsew', columnspan= 1, ipadx= len('all'))

        self.__run_specific_btn = Button(self.__row_one_frame, text='Specific', command= self.run_specific_btn_callback,  bg = 'green',  relief='raised', borderwidth= 2, pady = 5 , font=('Helvetica', 16))
        self.__run_specific_btn.grid(row = 0, column = 2, sticky = 'nsew', columnspan= 1)

        self.__multiple_media_change_btn = Button(self.__root, text ='Media-change', command=self.multiple_media_change_callback, relief='raised', font=('Helvetica', 16))
        self.__multiple_media_change_btn.grid(row = 1, column = 3, sticky ='nsew', columnspan= 1)

        self.__multiple_eject_btn = Button(self.__root, text = 'Eject', command = self.multiple_eject_callback, relief='raised', font=('Helvetica', 16))
        self.__multiple_eject_btn.grid(row = 1, column = 4, sticky = 'nsew', columnspan= 1)

        self.__multiple_measurement_btn = Button(self.__root, text = 'Measurement', command=self.multiple_measurement_callback, relief='raised', font=('Helvetica', 16))
        self.__multiple_measurement_btn.grid(row = 1, column = 5, sticky = 'nsew', columnspan= 1)

    def run_all_btn_callback(self)->None:
        self.__run_all_btn.config(bg="green")
        self.__run_specific_btn.config(bg="yellow")

        self.__specific_plates_dict = self.get_assigned_plate_row_objects()

    def run_specific_btn_callback(self)->None:
        self.create_choose_specific_window()

        self.__run_all_btn.config(bg="yellow")
        self.__run_specific_btn.config(bg="green")

    def create_choose_specific_window(self)->None:
        """
        creates a window of 5 x n Buttons which represent all usable slots. It allows to mark all slots separately to use at once
        """
        self.__choose_specific_window = Toplevel(self.__root)
        self.__choose_specific_window.title("Choose Plates")
        self.__choose_specific_window.geometry('400x400')

        assigned_plate_row_objects_list: list[GUI_row] = self.get_assigned_plate_row_objects()

        for idx, row in enumerate(assigned_plate_row_objects_list):
            column = idx// 5
            row_idx = idx % 5
            if row.slot in self.__specific_plates_dict.keys():
                toggle_state = BooleanVar(value = True)
                bg = 'green'
            else:
                toggle_state = BooleanVar(value = False)
                bg = 'red'
            square_button = Button(self.__choose_specific_window, text= row.slot, bg = bg)
            square_button.config(command=lambda b = square_button, toggle = toggle_state, row_obj = row: self.square_button_callback(b, toggle, row_obj))

            square_button.grid(row = row_idx, column = column, sticky='nsew')
        for i in range(len(self.__list_of_row_objects)//5 +1):
            self.__choose_specific_window.columnconfigure(i, weight = 1)

        self.__choose_specific_window.rowconfigure(0, weight = 1)
        self.__choose_specific_window.rowconfigure(1, weight=1)
        self.__choose_specific_window.rowconfigure(2, weight=1)
        self.__choose_specific_window.rowconfigure(3, weight=1)
        self.__choose_specific_window.rowconfigure(4, weight=1)

    def get_assigned_plate_row_objects(self)->list:
        """
        returns a list of all row objects which have assigned plates
        """
        assigned_plate_row_objects_list = []
        for row in self.__list_of_row_objects:
            if row.plate:
                assigned_plate_row_objects_list.append(row)
        return assigned_plate_row_objects_list

    def square_button_callback(self, btn: Button, tog: BooleanVar, row_obj)->None:
        """
        updates the self.__choose_specific_window widget, and self.__specific_slots_list which is used to run multiple plate commands at 'once'
        Parameters
        ----------
        btn : Button
            object of caller Button, used to update the button color
        tog: BooleanVar
            toggle value: should the slot be used?
        row_obj: GUI_row
            row obj used to update self.__specific_slots_list
        """
        current = tog.get()
        tog.set(not current)

        if tog.get():
            btn.config(bg="green")
            self.__specific_plates_dict[row_obj.slot] = row_obj
        else:
            btn.config(bg='red')
            del self.__specific_plates_dict[row_obj.slot]

    def multiple_media_change_callback(self):
        for key_row in self.__specific_plates_dict.keys():
            self.__specific_plates_dict[key_row].callback_mediachange()

    def multiple_measurement_callback(self):
        for key_row in self.__specific_plates_dict.keys():
            self.__specific_plates_dict[key_row].callback_measurement()

    def multiple_eject_callback(self)->None:
        """
        loops through all row obj in self.__specific_plates_dict and ejects the associated plate. If the Plate has not been
        lifted from the transfer station 10 sec. after it has been ejected it gets inserted again.

        """
        for key_row in self.__specific_plates_dict.keys():

            self.__specific_plates_dict[key_row].callback_eject()
            time_start = time.time()
            max_time = 10
            bool_insert = True
            while time.time() - time_start < max_time:
                if self.get_cytomat_status().transfer_station_occupied:
                    time.sleep(0.5)
                else:
                    bool_insert = False
                    break
            if bool_insert:
                self.__specific_plates_dict[key_row].callback_insert()

    """
    """
    def set_run_all_foc_at_time(self, bool_run: bool = False, timer_hour: int = 3, timer_minute: int = 0, time_buffer: int = 5) -> None:
        """
        controls the check_time_run_all_foc to run the run_all_foc at a specific time. Gets called in ManagerSettings class

        Parameters
        ----------
        bool_run: bool
            should the run all foc run

        timer_hour: int
            at what hour should run_all_foc run

        timer_minute: int
            at what minute should run_all_foc run

        time_buffer: int
            how many minutes of buffer should run_all_foc have to run(default 5 min)
        """
        if bool_run is True:
            self.__ran_all_foc = False
            self.check_time_run_all_foc(timer_hour=timer_hour, timer_minute=timer_minute, time_buffer=time_buffer)

        elif self.after_id_2 is not None:
            self.__root.after_cancel(self.after_id_2)

    def check_time_run_all_foc(self, timer_hour, timer_minute, time_buffer: int = 5) -> None:
        """
        checks if current time is in the interval of given time plus buffer, if so run_all_foc is called else it recalls itself with a delay of 10000ms

        Parameters
        ----------
         timer_hour: int
            at what hour should run_all_foc run

        timer_minute: int
            at what minute should run_all_foc run

        time_buffer: int
            how many minutes of buffer should run_all_foc have to run(default 5 min)
        """
        if not self.__root.winfo_exists():
            return

        time_now = datetime.now()

        midnight = datetime(time_now.year, time_now.month, time_now.day)
        timer = midnight + timedelta(hours=timer_hour, minutes=timer_minute)

        time_buffer_delta = timedelta(minutes=time_buffer)

        if timer <= time_now <= timer + time_buffer_delta:
            if self.__ran_all_foc is False:
                self.run_all_foc()
                self.__ran_all_foc = True

        if time_now > timer + time_buffer_delta:
            self.__ran_all_foc = False

        self.after_id_2 = self.__root.after(10000, self.check_time_run_all_foc, timer_hour, timer_minute, time_buffer)

    def run_all_foc(self) -> None:
        """
        loops through every row in Database and lets the task_manager execute measurement. In the meantime the GUI is blocked/busy state True
        """
        self.set_busy_state(True)
        data_rows: list[dict] = self.__DB.get_rows_role_dict(role = 0)

        for data in data_rows:
            if data['plate'] is None:
                continue
            slot = data['slot']
            plate = data['plate']
            print(f"slot: {slot}, plate: {plate}")
            try:
                self.task_manager(self.__cytomat.plate_handler.get_plate_do_measurement_bring_back_plate(slot_a = slot, plate = plate))

            except Exception as e:
                print(f'execute canceled due to: {e}')

        self.set_busy_state(False)
        self.busy_v = False
        self.update_overview()

    def check_if_transfer_occupied(self) -> None:
        """
        every 100ms the function calls itself as long the main window exists(without blocking the main thread) and checks if the transfer station state has changed.
        If so the function updates the overview
        """
        if not self.__root.winfo_exists():
            return

        transfer_station_occupied = self.get_cytomat_status().transfer_station_occupied
        if self.checker != transfer_station_occupied:
            self.checker = transfer_station_occupied
            self.update_overview()

        self.after_id = self.__root.after(25, self.check_if_transfer_occupied)

    def on_close(self) -> None:
        """
        Kills all the background operations to close the main window properly without raising an error
        """
        if self.after_id is not None:
            self.__root.after_cancel(self.after_id)

        if self.after_id_2 is not None:
            self.__root.after_cancel(self.after_id_2)
        self.__root.destroy()

    def create_insert_new_plate_window(self, slot) -> None:
        """
        creates a window to insert new plates. It consists of a year, month, day and index Entry, which can be in- or decresed by a plus or minus button.

        Parameters
        ----------
        slot: int
            slot number to insert new plate
        """
        self.__insert_window = Toplevel(master=self.__root)
        self.__insert_window.title('insert window')
        self.__insert_window.geometry('1000x400+400+400')

        self.__insert_window.columnconfigure(0, weight=1)
        self.__insert_window.columnconfigure(1, weight=1)
        self.__insert_window.columnconfigure(2, weight=1)
        self.__insert_window.columnconfigure(3, weight=1)
        self.__insert_window.columnconfigure(4, weight=1)
        self.__insert_window.columnconfigure(5, weight=1)

        self.__insert_window.rowconfigure(0, weight=1)
        self.__insert_window.rowconfigure(1, weight=1)
        self.__insert_window.rowconfigure(2, weight=1)
        self.__insert_window.rowconfigure(2, weight=1)

        current_year = datetime.now().year
        current_month = datetime.now().month
        current_day = datetime.now().day

        self.year = StringVar()
        self.month = StringVar()
        self.day = StringVar()
        self.index_ = StringVar()

        self.year.set(f'{current_year:02}')
        self.month.set(f'{current_month:02}')
        self.day.set(f'{current_day:02}')
        self.index_.set('a')

        year_label = Label(master = self.__insert_window, text= 'year', font = ('Helvetica', 14), relief='solid')
        month_label = Label(master = self.__insert_window, text = 'month', font = ('Helvetica', 14),relief='solid')
        day_label = Label(master = self.__insert_window, text = 'day', font = ('Helvetica', 14), relief='solid')
        index_label = Label(master = self.__insert_window, text ='index', font = ('Helvetica', 14), relief='solid')

        year_label.grid(row = 1, column = 0, ipady = 20, sticky = 'ew')
        month_label.grid(row = 1, column = 1, ipady = 20, sticky = 'ew')
        day_label.grid(row = 1, column = 2, ipady = 20, sticky = 'ew')
        index_label.grid(row = 1, column = 3, ipady = 20, sticky = 'ew')

        entry_year = Entry(master = self.__insert_window, textvariable = self.year,  state = 'readonly', relief = 'solid', font = ('Helvetica', 14))
        entry_month = Entry(master =self.__insert_window, textvariable =self.month,  state='readonly', relief = 'solid', font = ('Helvetica', 14))
        entry_day = Entry(master =self.__insert_window, textvariable = self.day, state='readonly', relief = 'solid', font = ('Helvetica', 14))
        entry_idx = Entry(master =self.__insert_window,textvariable = self.index_, state = 'readonly',relief = 'solid', font = ('Helvetica', 14))

        entry_year.grid(row = 2, column = 0, ipady = 40, ipadx = 80)
        entry_month.grid(row = 2, column = 1,ipady = 40, ipadx = 80)
        entry_day.grid(row = 2, column = 2, ipady = 40, ipadx = 80)
        entry_idx.grid(row = 2, column = 3,ipady = 40, ipadx= 80)

        submit_btn = Button(master =self.__insert_window, text = "Submit",command = lambda: self.submit_btn_callback(slot), font = ('Helvetica', 12), relief = 'solid')
        submit_btn.grid(row=0, column=4, ipadx = 80, ipady = 40, rowspan=4, sticky='ns')

        year_btn_plus = Button(master =self.__insert_window, text = '+', command = lambda: self.year_change(0), font = ('Helvetica', 20), relief = 'solid')
        year_btn_minus = Button(master =self.__insert_window, text = '-', command = lambda: self.year_change(1), font = ('Helvetica', 20), relief = 'solid')
        year_btn_plus.grid(row = 0, column=0, sticky = 'ew', ipady = 40)
        year_btn_minus.grid(row = 3, column=0, sticky = 'ew', ipady = 40)

        month_btn_plus = Button(master =self.__insert_window, text = '+', command = lambda: self.month_change(0), font = ('Helvetica', 20), relief = 'solid')
        month_btn_minus = Button(master =self.__insert_window, text = '-', command = lambda: self.month_change(1), font = ('Helvetica', 20), relief = 'solid')
        month_btn_plus.grid(row = 0, column = 1, sticky = 'ew', ipady = 40)
        month_btn_minus.grid(row = 3, column = 1, sticky = 'ew', ipady = 40)

        day_btn_plus = Button(master =self.__insert_window, text = '+', command = lambda: self.day_change(0), font = ('Helvetica', 20), relief = 'solid')
        day_btn_minus = Button(master =self.__insert_window, text = '-', command = lambda: self.day_change(1), font = ('Helvetica', 20), relief = 'solid')
        day_btn_plus.grid(row = 0, column = 2, sticky = 'ew', ipady = 40)
        day_btn_minus.grid(row = 3, column = 2, sticky = 'ew', ipady = 40)

        idx_btn_plus = Button(master =self.__insert_window, text = '+', command = lambda: self.idx_change(0), font = ('Helvetica', 20), relief = 'solid')
        idx_btn_minus = Button(master =self.__insert_window, text = '-', command = lambda: self.idx_change(1), font = ('Helvetica', 20), relief = 'solid')
        idx_btn_plus.grid(row = 0, column = 3, sticky = 'ew', ipady = 40)
        idx_btn_minus.grid(row=3, column = 3, sticky = 'ew', ipady = 40)

        self.__insert_window.protocol('WM_DELETE_WINDOW',self.on_close_insert_window)

        self.__insert_window.update()
        self.__insert_window.update_idletasks()
        self.wait_for_submit = IntVar()

    def on_close_insert_window(self) -> None:
        """
        gets called as soon the insert window is closed and
        """
        self.submit_insert = False
        self.close_insert_window()
        #Boolean variable which is used to continue inside callback(gui_row)
        self.wait_for_submit.set(1)

    def close_insert_window(self) -> None:
        self.__insert_window.destroy()

    def submit_btn_callback(self, slot: int) -> None:
        """
        callback function to the submit button, assigns new plate to a given slot in Database and sets flags for completion
        of insert and for success of insert

        Parameters
        ----------
        slot: int
            the slot number whew the new plate should be assigned to
        """
        plate_id = self.year.get() + self.month.get() + self.day.get() + self.index_.get()

        if self.__DB.is_plate_assigned(plate_id):
            print("This Plate is already assigned to a Slot")
            return
        self.__DB.assigne_plate(plate_id=plate_id, slot = slot)
        self.close_insert_window()
        self.update_overview()
        self.submit_insert = True
        self.wait_for_submit.set(1)

    def year_change(self, p_o_m: int) -> None:
        """
        changes the current year in entry_year of the inset window by +-1

        Parameters
        ----------
        p_o_m: int
            stands for plus or minus, 0 is plus, 1 is minus
        """
        curr_year = int(self.year.get())
        if p_o_m == 0:
            new_year = curr_year + 1
        else:
            new_year = curr_year - 1

        self.year.set(f'{new_year:02}')

    def month_change(self, p_o_m: int) -> None:
        """
        changes the month year in entry_month of the inset window by +-1
        lowest is 1, highest 12

        Parameters
        ----------
        p_o_m: int
            stands for plus or minus, 0 is plus, 1 is minus
        """
        curr_month = int(self.month.get())
        if p_o_m == 0:
            new_month = curr_month +1
        else:
            new_month = curr_month -1

        if new_month > 12:
            new_month = 1

        if new_month < 1:
            new_month = 12
        self.month.set(f'{new_month:02}')

    def day_change(self, p_o_m: int) -> None:
        """
        changes the current day in entry_day of the inset window by +-1
        lowest is 1, highest 31

        Parameters
        ----------
        p_o_m: int
            stands for plus or minus, 0 is plus, 1 is minus
        """
        curr_day = int(self.day.get())
        if p_o_m == 0:
            new_day = curr_day +1
        else:
            new_day = curr_day -1

        if new_day >31:
            new_day = 1

        if new_day <1:
            new_day =31

        self.day.set(f'{new_day:02}')

    def idx_change(self, p_o_m: int) -> None:
        """
        changes the current letter in entry_idx of the inset window by +-1(alphabetic order)
        lowest is a, highest z

        Parameters
        ----------
        p_o_m: int
            stands for plus or minus, 0 is plus, 1 is minus
        """
        curr_index = self.index_.get()
        curr_ascii = ord(curr_index)
        if p_o_m == 0:
            new_ascii = curr_ascii + 1
        else:
            new_ascii = curr_ascii - 1

        if new_ascii > ord('z'):
            new_index = 'a'
        elif new_ascii < ord('a'):
            new_index = 'z'
        else:
            new_index = chr(new_ascii)

        self.index_.set(new_index)

    def create_progress_window(self) -> None:
        """
        Creates a progress window with opens when a command has been clicked. Consisting of a progress bar, status label and an interrupt button
        """
        self.__progress_window = Toplevel(master=self.__root)
        self.__progress_window.geometry('800x200+400+400')
        self.__progress_window.title('Progress window')
        #self.__progress_window.overrideredirect(True)

        self.__progressbar = Progressbar(self.__progress_window, maximum=100)
        self.__progressbar.grid(row = 0, column=0, columnspan=2, padx=5, pady = 50, sticky = 'new', ipadx = 200)

        self.__status_label = Label(self.__progress_window, text = "status")
        self.__status_label.grid(row = 0, column=1, columnspan=2, ipadx = 200, pady = 50, sticky = 'sew')

        self.__pause_btn = Button(self.__progress_window, text="Pause", bg = 'red', command = self.pause_btn_callback)
        self.__pause_btn.grid(row = 0, column = 3, ipadx = 100, ipady = 50, pady = 20, padx=5)

        self.__progress_window.update()

    def close_progress_window(self) -> None:
        self.__progress_window.destroy()

    def pause_btn_callback(self) -> None:
        self.__pause = True
        self.create_interrupt_window()
        print("set .__pause to True")

    def get_interrupted(self):
        return self.__interrupted

    def set_interrupted(self, vbool: bool) -> None:
        self.__interrupted = vbool

    def update_progressbar(self, percent: float) -> None:
        self.__progressbar['value'] = percent
        self.__root.update_idletasks()

    def update_status_label(self, text: str) -> None:
        self.__status_label.config(text = text)
        self.__root.update()

    def is_progress_window_exists(self)->bool:
        try:
            return self.__progress_window.winfo_exists()

        except Exception:
            return False

    def task_manager(self, task_list)->None:
        """
        Gets a list of commands and executes them in cytomat.execute() one by one while checking if no error or pause has occurred.
        Parameters
        ----------
        task_list : list[Callable[[], PlateShuttleSystemStatus]]
        """
        print("task manager")
        task_completed = None
        for idx, command in enumerate(task_list):
            self.current_task_idx = idx
            if self.__pause is True:
                self.__pause = False
                self.__root.wait_variable(self.__interrupt_window_submit)

                if self.interrupt_state != 'continue':
                    task_completed = False
                    print(task_completed)
                    return

            try:
                self.__cytomat.execute(command, timeout=120)

            except Exception as error:
                print(f"error: {error}")
                self.error_handler(error)
                return

            if self.is_progress_window_exists():
                self.update_progressbar(idx/len(task_list) * 100)
                self.update_status_label(command.__name__)
                self.__progress_window.update()
            time.sleep(0.5)
        print("done id: task_manager")
        task_completed = True
        print(task_completed)
        return

    def error_handler(self, error) -> None:
        print(error)
        #TODO: Error handling

    def create_interrupt_window(self) -> None:
        """
        Creates a window to Initialize the Plate handler, gets called after a command has been interrupted
        """
        self.__reboot_window = Toplevel(master=self.__root)
        self.__reboot_window.title('Interrupt window')
        self.__reboot_window.geometry('600x350+400+400')
        self.__reboot_window.overrideredirect(True)

        self.__interrupt_window_submit = IntVar()

        self.__cyto_init_btn = Button(self.__reboot_window, bg = 'red', text="Re-Init Cytomat PH", command = self.callback_cyto_init_btn, relief='solid', font=('Helvetica', 16))
        self.__cyto_init_btn.pack(expand=True, fill='both')

        self.__continue_btn = Button(self.__reboot_window, text="Continue", command = self.callback_continue_btn, font =('Helvetica', 16))
        self.__continue_btn.pack(expand=True, fill='both')

        self.__get_back_btn = Button(self.__reboot_window, text = "Undo command", command=lambda: self.callback_get_back_btn(), font =('Helvetica', 16))
        self.__get_back_btn.pack(expand = True, fill = 'both')

        self.__reboot_window.update()
        self.__reboot_window.update_idletasks()

    def callback_get_back_btn(self) -> None:
        self.interrupt_state = ['get_back', self.current_task_idx]
        self.__interrupted = True
        self.__reboot_window.destroy()
        self.__interrupt_window_submit.set(1)

    def callback_cyto_init_btn(self):
        self.interrupt_state = ['reinitialize']
        self.__interrupted = True
        self.__reboot_window.destroy()
        self.__interrupt_window_submit.set(1)

    def callback_continue_btn(self):
        self.interrupt_state = 'continue'
        self.__interrupt_window_submit.set(1)
        self.__reboot_window.destroy()
    """
    """
    def create_interrupt_actions_window(self):
        self.__display_interrupt_action = Toplevel(master =self.__root)
        self.__display_interrupt_action.geometry('600x350+400+400')
        self.__display_interrupt_action.title('Interrupt Action')

        self.__display_action_label = Label(master=self.__display_interrupt_action, text ="currently doing:")
        self.__display_action_label.pack(expand=True, fill='both')

    def modify_display_label(self, text_):
        self.__display_action_label.config(text=text_)
        self.__display_interrupt_action.update()

    def destroy_display_interrupt(self):
        self.__display_interrupt_action.destroy()

    def create_submit_delete_window(self, plate: str):
        self.submit_delete_wait = IntVar()

        self.__submit_delete_window = Toplevel(master=self.__root)
        self.__submit_delete_window.geometry('600x350+400+400')
        self.__submit_delete_window.title('Submit Delete')
        self.__submit_delete_window.overrideredirect(True)

        self.__submit_delete_window.columnconfigure(0, weight=1)
        self.__submit_delete_window.columnconfigure(1, weight=1)
        self.__submit_delete_window.columnconfigure(2, weight=1)
        self.__submit_delete_window.rowconfigure(0, weight=1)
        self.__submit_delete_window.rowconfigure(1, weight=1)
        self.__submit_delete_window.rowconfigure(2, weight=1)

        self.__submit_delete_label = Label(master= self.__submit_delete_window, relief = 'solid', text = f"To delete plate: {plate} press button", font = ('Helvetica', 14), bg = 'lightgrey')
        self.__submit_delete_label.grid(row =0, column=0, sticky='nsew', columnspan=3)

        self.__submit_delete_btn = Button(master = self.__submit_delete_window, command=self.submit_delete_callback, text ="Commit Delete", bg = 'red', font = ('Helvetica', 14))
        self.__submit_delete_btn.grid(row=1, column=1, sticky='nsew')

        self.__cancel_delete = Button(master = self.__submit_delete_window, command=self.cancel_delete, text = "Cancel", font = ('Helvetica', 14))
        self.__cancel_delete.grid(row=2, column=1, sticky='nsew')

    def submit_delete_callback(self):
        self.submit_delete = True
        self.submit_delete_wait.set(1)
        self.__submit_delete_window.destroy()

    def cancel_delete(self):
        self.submit_delete = False
        self.submit_delete_wait.set(1)
        self.__submit_delete_window.destroy()

class GUI_row:
    __label_slot    : Label
    __label_role    : Label
    __label_plate   : Label
    __btn_media     : Button
    __btn_eject     : Button
    __btn_measurement   : Button
    __DB            : DB
    cy              : CytomatPlus
    row_idx         : int
    command_map: dict
    #db_row: DB_row

    def __init__(self, row_idx, root, gui, db, cytomat, transfer_oc: bool, data: dict):
        """
        Every row of the gui consists of an object of the GUI_row class, 6 columns of which 3 are data and 3 commands
        """
        self.__root: Tk = root
        self.cy: CytomatPlus = cytomat
        self.gui: GUI = gui
        self.__DB = db

        self.row_idx = row_idx

        self.slot = data['slot']
        self.role = data['role']
        self.plate = data['plate']
        self.occupied = data['occupied']

        self.transfer_oc = transfer_oc
        self.cyto_status = self.gui.get_cytomat_status()
        self.command_map = self.command_map_()
        self.create()

    def create(self):
        if self.plate is None:
            plate_bool = False
        else: 
            plate_bool = True

        if self.occupied == 0:
            occupied_bool = False
        else:
            occupied_bool = True

        command_map = self.command_map[(self.transfer_oc, plate_bool, occupied_bool)]
        
        cmd_left =      command_map['cmd_left']
        bg_left =       command_map['color_left']
        text_left =     command_map['text_left']
        state_left =    command_map['state_left']

        cmd_middle =    command_map['cmd_middle']
        bg_middle =     command_map['color_middle']
        text_middle =   command_map['text_middle']
        state_middle =  command_map['state_middle']

        cmd_right =     command_map['cmd_right']
        bg_right =      command_map['color_right']
        text_right =    command_map['text_right']
        state_right =   command_map['state_right']
        
        self.__btn_media = Button(self.__root, text = text_left, bg = bg_left, command= cmd_left, state = state_left, font=('Helvetica', 14))
        self.__btn_eject = Button(self.__root, text = text_middle, bg = bg_middle, command = cmd_middle, state = state_middle, font=('Helvetica', 14))
        self.__btn_measurement = Button(self.__root, text = text_right, bg = bg_right, command = cmd_right, state = state_right, font=('Helvetica', 14))

        self.__label_slot =Label(self.__root, text=self.slot , relief='solid',  pady = 1, padx = 1, font=('Helvetica', 14))
        self.__label_role =Label(self.__root, text=self.role , relief='solid',  pady = 1, padx = 1, font=('Helvetica', 14))
        self.__label_plate=Label(self.__root, text=self.plate, relief='solid', pady = 1, padx = 1, font=('Helvetica', 14))

        if self.gui.busy_v is True:
            self.busy(True)
            
        if self.gui.busy_row == self.row_idx:
            self.busy_row(True)

        if self.role == 1:
            self.busy(True)

        self.__label_slot.grid(  column = 0, row = self.row_idx, sticky='nsew', pady = 1)
        self.__label_role.grid(  column = 1, row = self.row_idx, sticky='nsew', pady = 1)
        self.__label_plate.grid( column = 2, row = self.row_idx, sticky='nsew', pady = 1)
        self.__btn_media.grid(   column=  3, row = self.row_idx, sticky = 'nsew', ipadx = len('mediachange'))
        self.__btn_eject.grid(   column=  4, row = self.row_idx, sticky = 'nsew', ipadx = len('Insert'))
        self.__btn_measurement.grid(column=  5, row = self.row_idx, sticky ='nsew', ipadx = len('Test'))

    def command_map_(self)->dict:
        """
        Maps all possible Button-states according to three bools: 1. transfer_station_occupied? 2. plate_is_assigned? 3. is_slot_occupied?

        """
        cmd_map = {
            (False, False, False): {'cmd_left': None, 'state_left': 'disabled', 'color_left': 'white', 'text_left' :'mediachange',
                                    'cmd_middle': lambda: self.callback_register(), 'state_middle': 'normal', 'color_middle': 'green', 'text_middle':'Register',
                                    'cmd_right': None, 'state_right': 'disabled', 'color_right': 'white', 'text_right': 'FOC48'},

            (False, False, True): {'cmd_left': None, 'state_left': 'disabled', 'color_left': 'grey', 'text_left' :'None',
                                    'cmd_middle': None, 'state_middle': 'disabled', 'color_middle': 'grey', 'text_middle':'None',
                                    'cmd_right': None, 'state_right': 'disabled', 'color_right': 'grey', 'text_right': 'None'},

            (False, True, False): {'cmd_left': None, 'state_left': 'disabled', 'color_left': 'white', 'text_left' :'mediachange',
                                    'cmd_middle': lambda: self.callback_delete(), 'state_middle': 'normal', 'color_middle': 'yellow', 'text_middle':'Delete',
                                    'cmd_right': None, 'state_right': 'disabled', 'color_right': 'white', 'text_right': 'FOC48'},

            (False, True, True): {'cmd_left': lambda: self.callback_mediachange(), 'state_left': 'normal', 'color_left': 'green', 'text_left' :'mediachange',
                                    'cmd_middle': lambda: self.callback_eject(), 'state_middle': 'normal', 'color_middle': 'green', 'text_middle':'Eject',
                                    'cmd_right': lambda: self.callback_measurement(), 'state_right': 'normal', 'color_right': 'green', 'text_right': 'FOC48'},

            (True, False, False): {'cmd_left': None, 'state_left': 'disabled', 'color_left': 'white', 'text_left' :'mediachange',
                                    'cmd_middle': lambda: self.callback_register(), 'state_middle': 'normal', 'color_middle': 'green', 'text_middle':'Register',
                                    'cmd_right': None, 'state_right': 'disabled', 'color_right': 'white', 'text_right': 'FOC48'},

            (True, False, True): {'cmd_left': None, 'state_left': 'disabled', 'color_left': 'grey', 'text_left' :'None',
                                    'cmd_middle': None, 'state_middle': 'disabled', 'color_middle': 'grey', 'text_middle':'None',
                                    'cmd_right': None, 'state_right': 'disabled', 'color_right': 'grey', 'text_right': 'None'},

            (True, True, False): {'cmd_left': None, 'state_left': 'disabled', 'color_left': 'white', 'text_left' :'mediachange',
                                    'cmd_middle': lambda: self.callback_insert(), 'state_middle': 'normal', 'color_middle': 'green', 'text_middle':'Insert',
                                    'cmd_right': None, 'state_right': 'disabled', 'color_right': 'white', 'text_right': 'FOC48'},

            (True, True, True): {'cmd_left': lambda: self.callback_mediachange(), 'state_left': 'normal', 'color_left': 'green', 'text_left' :'mediachange',
                                    'cmd_middle': None, 'state_middle': 'disabled', 'color_middle': 'grey', 'text_middle':'Insert',
                                    'cmd_right': lambda: self.callback_measurement(), 'state_right': 'normal', 'color_right': 'green', 'text_right': 'FOC48'},
            }
        return cmd_map
    
    def busy(self, lock: bool) -> None:
        """
        Sets the row to busy state

        Parameters
        ----------

        lock: bool
            parameter for busy state
        """
        if lock is True:
            self.__label_slot.config( bg = 'grey')        
            self.__label_role.config( bg = 'grey')        
            self.__label_plate.config(bg = 'grey')        
            self.__btn_media.config(state = DISABLED, bg = 'grey')
            self.__btn_eject.config(state = DISABLED, bg = 'grey')
            self.__btn_measurement.config(state = DISABLED, bg ='grey')
        else:
            self.__label_slot.config(bg = 'white')      
            self.__label_role.config(bg = 'white')        
            self.__label_plate.config(bg = 'white')        
            self.__btn_media.config(state = NORMAL)
            self.__btn_eject.config(state = NORMAL)
            self.__btn_measurement.config(state = NORMAL)
        self.__root.update()

    def busy_row(self, lock: bool) -> None:
        """
        is a command executed the row is set to busy state/specific color to determine which row is getting executed.
        """
        if lock is True:
            self.__label_slot.config(bg= 'green')
            self.__label_role.config(bg= 'green')
            self.__label_plate.config(bg= 'green') 
        else:
            self.__label_slot.config(bg= 'white')
            self.__label_role.config(bg= 'white')
            self.__label_plate.config(bg= 'white')
        self.__root.update()

    """
    Callback functions of the Buttons
    """
    def callback_register(self) -> None:
        """
        checks if the busy bool is not busy, the assigned role is the right one and if the plate is not assigned already.
        Then sets the Gui to busy and then calls create_insert_new_plate window out of gui
        """
        if self.gui.busy_v is True:
            return

        if self.role != 0:
            print("This Plate is not for storage")
            return

        if self.plate is not None:
            print("The Slot is already assigned to a Plate")
            return

        self.gui.busy_v = True
        self.gui.busy_row = int(self.row_idx)
        self.gui.set_busy_state(True)
        self.busy_row(True)

        self.gui.create_insert_new_plate_window(self.slot)
        self.__root.wait_variable(self.gui.wait_for_submit)
        
        self.gui.busy_v = False
        self.gui.busy_row = None
        self.gui.update_overview()

    def callback_delete(self) -> None:
        """
        Delete logics, sets gui to busy, opens delete window, deletes if submit_delete out of gui is True, then updates overview
        """
        self.gui.busy_v = True
        self.gui.busy_row = int(self.row_idx)

        self.gui.set_busy_state(True)
        self.busy_row(True)

        self.gui.create_submit_delete_window(plate = self.plate)
        self.__root.wait_variable(self.gui.submit_delete_wait)

        if self.gui.submit_delete is True:
            self.delete_plate()

        self.gui.busy_v = False
        self.gui.busy_row = None
        self.gui.update_overview()


    def delete_plate(self):
        self.__DB.delete_plate(self.slot)
        print('deleted')

    """
    insert logics
    """
    def callback_insert(self):
        status = self.gui.get_cytomat_status()

        #Basic checks, looking if the Plate is in the right state:
        if status.transfer_station_occupied is False:
            print("There is no plate on the transfer station")
            return

        if self.gui.busy_v is True:
            return

        if self.role != 0:
            print("This Plate is not for storage")
            return

        #Blocking all the other buttons, Gui is busy now
        self.gui.busy_v = True
        self.gui.busy_row = int(self.row_idx)

        self.gui.set_busy_state(True)
        self.busy_row(True)

        self.gui.create_progress_window()

        self.gui.task_manager([lambda: self.cy.plate_handler.move_plate_from_transfer_station_to_slot(self.slot)])

        self.gui.close_progress_window()

        if self.gui.get_interrupted() is True:
            self.gui.set_interrupted(False)
            self.gui.create_interrupt_actions_window()

            self.choose_interrupt_action(key = 'insert')
        else:
            self.__DB.update_occupied(self.slot, 1)

        self.__root.update()
        self.gui.busy_v = False
        self.gui.busy_row = None
        self.gui.update_overview()

    def insert(self):
        self.cy.execute([lambda: self.cy.plate_handler.move_plate_from_transfer_station_to_slot(self.slot)], timeout = 20)
 
    def invert_insert_list(self, current_idx: int)->list:
        inverted_list = self.cy.plate_handler.inverted_move_plate_from_transfer_station_to_slot_v2(self.slot)
        modified_invert_list = []
        for i in range(current_idx):
            modified_invert_list.append(inverted_list[i])

        return modified_invert_list
    """
    eject logics
    """
    def callback_eject(self):
        status = self.gui.get_cytomat_status()

        if status.transfer_station_occupied is True:
            print("The transfer station is occupied")
            return

        if self.gui.busy_v is True:
            return

        if self.role != 0:
            print("This Plate is not for storage")
            return

        if self.plate is None:
            print("This slot is not assigned to a plate")
            return

        self.gui.busy_v = True
        self.gui.busy_row = int(self.row_idx)
        self.gui.set_busy_state(True)
        self.busy_row(True)

        self.gui.create_progress_window()

        self.gui.task_manager(task_list = [lambda: self.cy.plate_handler.move_plate_from_slot_to_transfer_station(self.slot)])

        self.gui.close_progress_window()

        if self.gui.get_interrupted() is True:
            self.gui.create_interrupt_actions_window()

            self.gui.set_interrupted(False)

            self.choose_interrupt_action(key = 'eject')
            self.gui.destroy_display_interrupt()

        else:
            self.__DB.update_occupied(self.slot, 0)    #TODO update in re_init_window 

        self.__root.update()
        self.gui.busy_v = False
        self.gui.busy_row = None
        self.gui.update_overview()

    def eject(self):
        print("running eject")
        self.cy.execute([lambda: self.cy.plate_handler.move_plate_from_slot_to_transfer_station(self.slot)], timeout = 20)
        print("eject Done")

    def invert_eject_list(self, current_idx: int)->list:
        inverted_list = self.cy.plate_handler.inverted_move_plate_from_slot_to_transfer_station_v2(self.slot)
        modified_invert_list = []
        for i in range(current_idx+1):
            modified_invert_list.append(inverted_list[i])

        return modified_invert_list

    """
    mediachange logics
    """
    def callback_mediachange(self):
        if self.gui.busy_v is True:
            return

        if self.role != 0:
            print("his Plate is not for mediachange")
            return

        if self.plate is None:
            print("This slot is not assigned to a plate")
            return

        self.gui.busy_v = True
        self.gui.busy_row = int(self.row_idx)
        self.gui.set_busy_state(True)
        self.busy_row(True)

        self.gui.create_progress_window()

        self.gui.task_manager(task_list = self.cy.plate_handler.test3())
        self.gui.close_progress_window()

        if self.gui.get_interrupted() is True:
            """if self.gui.error_raised:
                print("Error raised")"""

            self.gui.set_interrupted(False)
            self.gui.create_interrupt_actions_window()

            self.choose_interrupt_action(key='mediachange')
            self.gui.destroy_display_interrupt()

        self.gui.busy_v = False
        self.gui.busy_row = None
        self.gui.update_overview()

    def invert_mediachange_list(self, current_idx):
        inverted_list = self.cy.plate_handler.inverted_test3()
        modified_invert_list = []
        for i in range(current_idx):
            modified_invert_list.append(inverted_list[i])

        return modified_invert_list

    """
    measurement logics
    """
    def callback_measurement(self):
        #self.__DB.delete_plate(row_idx=self.row_idx-1)
        if self.gui.busy_v is True:
            print("Cyto is busy")
            return

        if self.role != 0:
            print("This Plate is not for mediachange")
            return

        if self.plate is None:
            print("This slot is not assigned to a plate")
            return

        if self.cyto_status.shovel_occupied is True:
            print("shovel occupied")
            return
        
        self.gui.busy_v = True
        self.gui.busy_row = int(self.row_idx)
        self.gui.set_busy_state(True)
        self.busy_row(True)

        self.gui.create_progress_window()
        self.gui.task_manager(self.measurement())

        self.gui.close_progress_window()

        if self.gui.get_interrupted() is True:
            
            self.gui.set_interrupted(False)

            self.gui.create_interrupt_actions_window()
            self.choose_interrupt_action(key='measurement')
            self.gui.destroy_display_interrupt()
                
            """self.__DB.write_log(time_stamp = datetime.now(), action= '', plate_id=self.plate)"""
  
        self.gui.busy_v = False
        self.gui.busy_row = None
        self.gui.update_overview()

    def measurement(self):
        return self.cy.plate_handler.get_plate_do_measurement_bring_back_plate(plate = self.plate, slot_a = self.slot)

    def invert_measurement_list(self, current_idx):
        inverted_list = self.cy.plate_handler.inverted_get_plate_do_measurement_bring_back_plate(slot_a = self.slot)
        modified_invert_list = []
        for i in range(current_idx):
            modified_invert_list.append(inverted_list[i])

        return modified_invert_list

    def init_plate_handler(self):
        self.cy.execute([self.cy.plate_handler.initialize])

    def choose_interrupt_action(self, key):
        command_mapping = {'mediachange': self.invert_mediachange_list,
                           'eject': self.invert_eject_list,
                           'insert': self.invert_insert_list,
                           'measurement': self.invert_measurement_list}

        match self.gui.interrupt_state[0]:
                case 'initialize':
                    self.gui.modify_display_label(text_ ="Currently doing: Initializing plate handler")
                    self.gui.task_manager([self.init_plate_handler])
                case 'get_back':
                    self.gui.modify_display_label(text_ ="Currently doing: Reversing the action")
                    modified_invert_list = command_mapping[key](self.gui.interrupt_state[1])
                    self.gui.task_manager(task_list=modified_invert_list)
                case _: 
                    pass