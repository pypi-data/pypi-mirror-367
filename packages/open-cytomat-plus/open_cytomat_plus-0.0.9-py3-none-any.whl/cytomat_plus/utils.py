from .scripts.setup_cytomat_plus import get_config_dir
import json
from logging import log

def lazy_load_config_file():
    try:
        config_file = get_config_dir() / "config.json"
        with open(config_file, "r") as f:
            python_data = json.load(f)
            log.info("Config data loaded successfully.")
            return python_data
    except Exception as e:
        log.error(f"Failed to load config data: {e}")
        log.warning(f"Config file not found or unreadable: {config_file}")
        return None