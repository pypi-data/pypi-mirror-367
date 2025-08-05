from cytomat.cytomat import Cytomat
from cytomat.status import OverviewStatus, PlateShuttleSystemStatus
from .plate_handler_plus import PlateHandlerPlus
from .db import DB
from typing import Union, Callable
from pd_stepper.pd_stepper import PDStepper
#from ws_barcode_scanner import BarcodeScanner
import time


#current firmware settings: left stack 1-21, right stack 22-42
class CytomatPlus(Cytomat):
    plate_handler: PlateHandlerPlus
    
    def __init__(self, serial_port: str):
        super().__init__(serial_port)
        self.plate_handler = PlateHandlerPlus(self._Cytomat__serial_port)
        self.pd_stepper = PDStepper("COM7")#dummy
        self.pump = self.pd_stepper.controller

        self.db = DB()
        print("cytomat")
        #self.scanner = BarcodeScanner("COM3")

    def wait_until_not_busy(self, timeout: float  = 30, poll_intervall: float = 0.05):
        status = self.overview_status
        max_time = timeout
        start_time = time.time()
        while status.command_in_process:
            if (time.time()-start_time) >= max_time:
                raise TimeoutError(f"Device still busy after {max_time} seconds")
            time.sleep(poll_intervall)
            status = self.overview_status

        duration = time.time()-start_time
        print(f"was busy for {duration} seconds")

    def execute(self, command_list: list[Callable[[], PlateShuttleSystemStatus]], timeout: float = 30, poll_interval: float = 0.5) -> None :
        if not isinstance(command_list, list):
            command_list = [command_list]

        for command in command_list:
            time.sleep(0.2)
            self.wait_until_not_busy(timeout, poll_interval)
            try:
                print("start command")
                response = command()
                self.wait_until_not_busy(timeout = timeout, poll_intervall = poll_interval)
                print("end command")
            except Exception as e:
                #self.plate_handler.initialize()
                raise e

    def read_barcode(self):
        self.scanner.query_for_codes()

    def get_status(self)->OverviewStatus:
        return self.overview_status

    def mediachange_from_slot_for_row(self, slot: int, rows: list[int]):
        self.pump.set_target_position(4000)