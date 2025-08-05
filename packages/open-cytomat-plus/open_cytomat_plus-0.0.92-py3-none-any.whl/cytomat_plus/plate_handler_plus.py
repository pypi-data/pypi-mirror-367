import subprocess
import time
from typing import  Callable
from cytomat.plate_handler import PlateHandler
from cytomat.status import OverviewStatus, PlateShuttleSystemStatus
from cytomat.serial_port import SerialPort
from .parameters import Parameters
from .convert_steps import ConvertSteps

class PlateHandlerPlus(PlateHandler):

    def __init__(self, serial_port: SerialPort) -> None:
        super().__init__(serial_port)

        try:
            self.parameters = Parameters()
            self.lid_holder_slot     = self.parameters.lid_holder_slot
            self.pipet_station_slot  = self.parameters.pipet_station_slot
            self.max_steps_shovel    = self.parameters.max_steps_shovel
            self.measurement_slot    = self.parameters.measurement_slot

            self.is_param_load = True

        except Exception:
            self.is_param_load = False

        self.convert_steps = ConvertSteps()

              
    def move_x_to_slot(self, slot: int) -> PlateShuttleSystemStatus:
        """time
        Move along to the given slot (only moves along the x axis)

        Parameters
        ----------
        slot
            The target slot
        """
        return self._PlateHandler__serial_port.issue_action_command(f"ll:xp {slot:03}")

    def warning_msg(self):
        print(
            """
    WARNING!!! This command does not check if the handler is in a safe position.
    This can cause crashes. Make sure it is safe to run."""
        )
        inp = input(
            """
            To deactivate this warning message and execute the command: press Y
            To just execute the command: press N
            To exit the script: press E"""
        )

        match inp.upper():
            case "Y":
                self.warning = False
            case "N":
                self.warning = True
            case "E":
                exit()
            case _:
                self.warning_msg()

    from typing import Callable

    def run_shovel_in_absolute_mm(self, mm: float) -> list[Callable[[], PlateShuttleSystemStatus]] | None:
        """Run the shovel to an absolute mm position."""
        if self.warning:
            self.warning_msg()
            return None
        steps = self.convert_steps.mm_to_steps_shovel(mm)
        return [lambda: self.__serial_port.issue_action_command(f"sb:sa {steps:05}")]

    def run_shovel_in_relative_mm(self, mm: float) -> list[Callable[[], PlateShuttleSystemStatus]] | None:
        """Run the shovel relatively in mm."""
        if self.warning:
            self.warning_msg()
            return None
        steps = self.convert_steps.mm_to_steps_shovel(mm)
        return [lambda: self.__serial_port.issue_action_command(f"sb:sr {steps:05}")]

    def run_turn_in_absolute_mm(self, mm: float) -> list[Callable[[], PlateShuttleSystemStatus]] | None:
        """Run turn to an absolute position in mm (interpreted as degrees)."""
        if self.warning:
            self.warning_msg()
            return None
        steps = self.convert_steps.deg_to_steps_turn(mm)
        return [lambda: self.__serial_port.issue_action_command(f"sb:da {steps:05}")]

    def run_turn_in_relative_mm(self, mm: float) -> list[Callable[[], PlateShuttleSystemStatus]] | None:
        """Run turn relatively in mm (interpreted as degrees)."""
        if self.warning:
            self.warning_msg()
            return None
        steps = self.convert_steps.deg_to_steps_turn(mm)
        return [lambda: self.__serial_port.issue_action_command(f"sb:dr {steps:05}")]

    def run_height_in_absolute_mm(self, mm: float) -> list[Callable[[], PlateShuttleSystemStatus]] | None:
        """Run height to an absolute mm position."""
        if self.warning:
            self.warning_msg()
            return None
        steps = self.convert_steps.mm_to_steps_h(mm)
        return [lambda: self.__serial_port.issue_action_command(f"sb:ha {steps:05}")]

    def run_height_in_relative_mm(self, mm: float) -> list[Callable[[], PlateShuttleSystemStatus]] | None:
        """Run height relatively in mm."""
        if self.warning:
            self.warning_msg()
            return None
        steps = self.convert_steps.mm_to_steps_h(mm)
        return [lambda: self.__serial_port.issue_action_command(f"sb:hr {steps:05}")]

    def run_turntable_in_absolute_mm(self, mm: float) -> list[Callable[[], PlateShuttleSystemStatus]] | None:
        """Run turntable to an absolute mm position (interpreted as degrees)."""
        if self.warning:
            self.warning_msg()
            return None
        steps = self.convert_steps.deg_to_steps_turn(mm)
        return [lambda: self.__serial_port.issue_action_command(f"sb:ka {steps:05}")]

    def run_turntable_in_relative_mm(self, mm: float) -> list[Callable[[], PlateShuttleSystemStatus]] | None:
        """Run turntable relatively in mm (interpreted as degrees)."""
        if self.warning:
            self.warning_msg()
            return None
        steps = self.convert_steps.deg_to_steps_turn(mm)
        return [lambda: self.__serial_port.issue_action_command(f"sb:kr {steps:05}")]

    def run_x_axis_in_absolute_mm(self, mm: float) -> list[Callable[[], PlateShuttleSystemStatus]] | None:
        """Run x-axis to an absolute mm position."""
        if self.warning:
            self.warning_msg()
            return None
        steps = self.convert_steps.mm_to_steps_x(mm)
        return [lambda: self.__serial_port.issue_action_command(f"sb:xa {steps:05}")]

    def run_x_axis_in_relative_mm(self, mm: float) -> list[Callable[[], PlateShuttleSystemStatus]] | None:
        """Run x-axis relatively in mm."""
        if self.warning:
            self.warning_msg()
            return None
        steps = self.convert_steps.mm_to_steps_x(mm)
        return [lambda: self.__serial_port.issue_action_command(f"sb:xr {steps:05}")]

    def run_transfer_station_in_absolute_mm(self, mm: float) -> list[Callable[[], PlateShuttleSystemStatus]] | None:
        """Run transfer station to an absolute mm position (interpreted as x-axis movement)."""
        if self.warning:
            self.warning_msg()
            return None
        steps = self.convert_steps.mm_to_steps_x(mm)
        return [lambda: self.__serial_port.issue_action_command(f"sb:ta {steps:05}")]
    
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


    #TODO finish this func
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