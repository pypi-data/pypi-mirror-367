from dataclasses import dataclass
from logging import log
from .utils import lazy_load_config_file

@dataclass
class Parameters:
    try:
        python_data = lazy_load_config_file()
        if python_data:
            COM_port = python_data["COM_port"]
            steps_per_mm_h = python_data["steps_per_mm_h"]
            max_steps_h = python_data["max_steps_h"]
            steps_per_mm_x = python_data["steps_per_mm_x"]
            max_steps_x = python_data["max_steps_x"]
            steps_per_mm_shovel = python_data["steps_per_mm_shovel"]
            max_steps_shovel = python_data["max_steps_shovel"]
            steps_per_deg_turn = python_data["steps_per_deg_turn"]
            max_deg_turn = python_data["max_deg_turn"]
            lid_holder_slot = python_data["lid_holder_slot"]
            pipet_station_slot = python_data["pipet_station_slot"]
            measurement_slot = python_data["measurement_slot"]

    except Exception:
        log(msg = "json file could not be read")
