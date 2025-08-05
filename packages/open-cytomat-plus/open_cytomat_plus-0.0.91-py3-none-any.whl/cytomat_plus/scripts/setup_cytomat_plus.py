import os
import sys
import shutil
from pathlib import Path
import logging
from .create_db import create_db

# 1. Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("setup.log"),  # Optional: Protokolliert in Datei
        logging.StreamHandler()            # Und auf der Konsole
    ]
)
log = logging.getLogger(__name__)

# 2. Helper functions
def get_config_dir() -> Path:
    return Path("C:/ProgramData/Cytomat")

def get_db_path() -> Path:
    return get_config_dir() / "slots.db"

def get_sample_config_path() -> Path:
    """
    The Package could be packed into an .exe therefore the file management could differ.
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).parent.parent / "data"
    return base_path / "sample_config.json"

# 3. Main setup function
def setup_config_dir() -> None:
    """
    Ensures the configuration directory, database, and config file exist.
    Creates them if missing and logs all actions.
    """
    config_dir = get_config_dir()
    db_file = get_db_path()
    config_file = config_dir / "config.json"
    sample_config_file = get_sample_config_path()

    # Step 1: Create config directory
    try:
        if not config_dir.exists():
            os.makedirs(config_dir)
            log.info(f"Created config directory: {config_dir}")
        else:
            log.info(f"Config directory already exists: {config_dir}")
    except Exception as e:
        log.error(f"Could not create config directory: {e}\nPlease create manually: {config_dir}")

    # Step 2: Create database file if not present
    try:
        if not db_file.exists():
            create_db(db_file)
            log.info(f"Created database file at: {db_file}")
        else:
            log.info(f"Database file already exists: {db_file}")
    except Exception as e:
        log.error(f"Failed to create database file: {e}\n"
                  f"Please run create_db() manually or ensure the file exists: {db_file}")

    # Step 3: Copy config file if not present
    try:
        if not config_file.exists():
            shutil.copy2(sample_config_file, config_file)
            log.info(f"Copied sample config to: {config_file}")
        else:
            log.info(f"Config file already exists: {config_file}")
    except Exception as e:
        log.error(f"Could not copy sample config: {e}\n"
                  f"Please manually copy: {sample_config_file} → {config_file}")

# 4. Optional post-install function
def post_install():
    log.info("Running post-install setup...")
    setup_config_dir()
if __name__ == '__main__':
    post_install()