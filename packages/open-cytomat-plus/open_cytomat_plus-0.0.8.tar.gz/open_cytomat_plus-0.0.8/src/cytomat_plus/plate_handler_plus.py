import subprocess
import time
from typing import  Callable
from cytomat.plate_handler import PlateHandler
from cytomat.status import OverviewStatus, PlateShuttleSystemStatus
from cytomat.serial_port import SerialPort
from .parameters import Parameters
from .convert_steps import ConvertSteps as convert_steps

class PlateHandlerPlus(PlateHandler):

    def __init__(self, serial_port: SerialPort) -> None:
        self.parameters = Parameters()
        self.parameters.load()
        super().__init__(serial_port)
        self.lid_holder_slot     = self.parameters.lid_holder_slot
        self.pipet_station_slot  = self.parameters.pipet_station_slot
        self.max_steps_shovel    = self.parameters.max_steps_shovel
        self.measurement_slot    = self.parameters.measurement_slot

    
    def leave_lid_at_holder(self) -> list[Callable[[], PlateShuttleSystemStatus]]| None:
        """

        Returns
        -------
        command_list: list of Callable[[], PlateShuttleSystemStatus]
            a list of frozen commands which execute an action on the cytomat plate handler and
            return a status data object

        """
        if self.parameters.lid_holder_slot is None:
            print("Lid holder not initialized, missing arg type int at the initialisation of Object type CytomatPlus")
            return None

        command_list = [
            lambda: self.rotate_handler_to_slot(self.lid_holder_slot),
            lambda: self.move_x_to_slot(self.lid_holder_slot),
            lambda: self.run_height_in_absolute_mm(26),
            lambda: time.sleep(0.2),
            lambda: self.extend_shovel(),
            lambda: self.run_height_in_absolute_mm(14),
            lambda: time.sleep(0.2),
            lambda: self.retract_shovel(),
            lambda: self.reset_handler_position()]
        return command_list

    def get_lid_from_holder(self)-> list[Callable[[], PlateShuttleSystemStatus]] | None:
        if self.parameters.lid_holder_slot is not None:
            command_list = [
                lambda: self.rotate_handler_to_slot(self.lid_holder_slot),
                lambda: self.move_x_to_slot(self.lid_holder_slot),
                lambda: self.run_height_in_absolute_mm(16),
                lambda: self.run_x_axis_in_relative_mm(-2),
                lambda: self.extend_shovel(),
                lambda: self.run_height_in_absolute_mm(22),
                lambda: self.run_x_axis_in_relative_mm(-1),
                lambda: self.run_x_axis_in_relative_mm(1),
                lambda: self.run_shovel_in_relative_mm(-1),
                lambda: self.run_shovel_in_relative_mm(1),
                lambda: self.run_height_in_absolute_mm(23),
                lambda: self.run_x_axis_in_relative_mm(-1),
                lambda: self.run_x_axis_in_relative_mm(1),
                lambda: self.run_shovel_in_relative_mm(-1),
                lambda: self.run_shovel_in_relative_mm(1),
                lambda: self.run_height_in_absolute_mm(24),
                lambda: self.run_x_axis_in_relative_mm(-1),
                lambda: self.run_x_axis_in_relative_mm(1),
                lambda: self.run_shovel_in_relative_mm(-1),
                lambda: self.run_shovel_in_relative_mm(1),
                lambda: self.run_height_in_absolute_mm(24),
                lambda: self.retract_shovel(),
                lambda: self.reset_handler_position()]
            return command_list

    def move_below_slot(self, slot: int)->list[Callable[[], PlateShuttleSystemStatus]]:
        command_list = [
            lambda: self.rotate_handler_to_slot(slot),
            lambda: self.move_x_to_slot(slot),
            lambda: self.move_handler_below_slot_height(slot)]
        return command_list

    def pipet_station(self, rows: int, distance_mm: float, start_mm: float) -> list[Callable[[], PlateShuttleSystemStatus]]:
        if (rows * distance_mm) + start_mm > CS.steps_to_mm_shovel(self.max_steps_shovel):
            raise ValueError("The parameters are ot compatible with the Plate handler")

        command_list = [
            lambda: self.move_handler_below_slot_height(self.pipet_station_slot),
            lambda: self.run_shovel_in_relative_mm(start_mm)        
        ]
        for i in range(rows):
            command_list.append(lambda: time.sleep(0.5))
            command_list.append(lambda: self.run_shovel_in_relative_mm(distance_mm))
            command_list.append(lambda: time.sleep(0.5))
            command_list.append(lambda: self.run_height_in_relative_mm(15))
            command_list.append(lambda: time.sleep(0.5))
            command_list.append(lambda: self.run_height_in_relative_mm(-15))
            command_list.append(lambda: time.sleep(0.5))
            
        command_list.append(lambda: self.retract_shovel())
        return command_list

    def do_media_change_from_slot(self, slot: int)->list[Callable[[], PlateShuttleSystemStatus]]:
        command_list: list[OverviewStatus]
        first_part = [  lambda: self.move_plate_from_slot_to_handler(slot),
                        lambda: self.leave_lid_at_holder()]

        second_part = self.move_below_slot(slot)

        third_part = self.pipet_station()

        fourth_part = [ lambda: self.get_lid_from_holder(),
                        lambda: self.move_plate_from_handler_to_slot(slot)]

        command_list = first_part + second_part + third_part + fourth_part
        return command_list


    #TODO finisch this func
    def inverted_do_mediachange_from_slot(self, slot: int)->list[Callable[[], PlateShuttleSystemStatus]]:
        command_list = [
            lambda: self.move_plate_from_handler_to_slot(slot)]
        return command_list

    def get_plate_do_measurement_bring_back_plate(self, plate: str, slot_a: int) -> list[Callable[[], PlateShuttleSystemStatus]]:
        command_list = [
            lambda: self.move_plate_from_slot_to_handler(slot_a),
            lambda: self.move_plate_from_handler_to_slot(self.measurement_slot),
            lambda: self.run_foc(plate),
            lambda: self.move_plate_from_slot_to_handler(self.measurement_slot),
            lambda: self.move_plate_from_handler_to_slot(slot_a)]

        return command_list

    def inverted_get_plate_do_measurement_bring_back_plate(self, slot_a: int)->list[Callable[[], PlateShuttleSystemStatus]]:
        command_list = [
            lambda: self.move_plate_from_slot_to_handler(slot_a),
            lambda: self.move_plate_from_handler_to_slot(self.measurement_slot),
            lambda: time.sleep(0.1),
            lambda: self.move_plate_from_slot_to_handler(self.measurement_slot),
            lambda: self.move_plate_from_handler_to_slot(slot_a)]
        return command_list

    def move_plate_from_transfer_station_to_slot_v2(self):
        pass

    def inverted_move_plate_from_transfer_station_to_slot_v2(self, slot):
        pass

    def move_plate_from_slot_a_to_slot_b(self, slot_a: int, slot_b:int)->list[Callable[[], PlateShuttleSystemStatus]]:
        command_list = [
            lambda: self.move_plate_from_slot_to_handler(slot_a),
            lambda: self.move_plate_from_handler_to_slot(slot_b)]

        return command_list

    def run_foc(self, plate, _timeout: int =180):
        cmd_l = f'C:\\labhub\\Import\\FOC48.bat {plate}'
        
        try:
            process = subprocess.run(cmd_l, timeout=_timeout, shell = True)
            print("done")

        except subprocess.TimeoutExpired:
            print(" timeout expired")


    def inverted_move_plate_from_slot_to_transfer_station_v2(self, slot):
        pass

    def do_one_uml(self)->list[Callable[[], PlateShuttleSystemStatus]]:
        command_list = [
        lambda: self.run_shovel_in_relative_mm(-18),
        lambda: self.run_height_in_relative_mm(8),
        lambda: time.sleep(0.2),
        lambda: self.run_height_in_absolute_mm(0),
        lambda: time.sleep(0.2)]

        return command_list

    #start position is at the bottom right corner(door view)
    def get_in_mediachange_position(self)->list[Callable[[], PlateShuttleSystemStatus]]:
        command_list = [
            lambda: self.run_height_in_absolute_mm(0),
            lambda: time.sleep(0.5),
            lambda: self.rotate_handler_to_slot(self.pipet_station_slot),
            lambda: self.run_x_axis_in_absolute_mm(95.5),
            lambda: time.sleep(5),
            lambda: self.extend_shovel(),
            lambda: self.run_shovel_in_relative_mm(-1),
            lambda: time.sleep(0.2)]

        return command_list

    def switch_uml_row(self)->list[Callable[[], PlateShuttleSystemStatus]]:
        command_list = [
            lambda: self.run_x_axis_in_relative_mm(-9),
            lambda: time.sleep(0.2),
            lambda: self.extend_shovel(),
            lambda: self.run_shovel_in_relative_mm(-1)]

        return command_list

    def mediachange_test(self)->list[Callable[[], PlateShuttleSystemStatus]]:
        #possition plate below pipet station, first row, leftest uml direktly under needle
        get_in_start_position = [
            lambda: self.run_height_in_absolute_mm(0),
            lambda: time.sleep(0.5),
            lambda: self.rotate_handler_to_slot(self.pipet_station_slot),
            lambda: self.run_x_axis_in_absolute_mm(95.5),
            lambda: time.sleep(5),
            lambda: self.extend_shovel(),
            lambda: self.run_shovel_in_relative_mm(-1),
            lambda: time.sleep(0.2)
        ]

        do_one_uml = [
            lambda: self.run_shovel_in_relative_mm(-18),
            lambda: self.run_height_in_relative_mm(8),
            lambda: time.sleep(0.2),
            lambda: self.run_height_in_absolute_mm(0),
            lambda: time.sleep(0.2)
        ]

        do_one_row = []
        for i in range(6):
            do_one_row = do_one_row + do_one_uml

        switch_row = [
            lambda: self.run_x_axis_in_relative_mm(-9),
            lambda: time.sleep(0.2),
            lambda: self.extend_shovel(),
            lambda: self.run_shovel_in_relative_mm(-2)

        ]
        homing = [lambda: self.retract_shovel()]
        do_all_uml = []
        for i in range(7):
            do_all_uml += do_one_row + switch_row
        do_all_uml += do_one_row

        command_list = get_in_start_position + do_all_uml + homing + self.get_lid_from_holder()
        return command_list