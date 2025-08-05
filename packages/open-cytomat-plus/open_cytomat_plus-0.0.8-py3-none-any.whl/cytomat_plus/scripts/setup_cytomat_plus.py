import shutil
from pathlib import Path
from .create_db import create_db
import sys
import os

def get_config_dir():
    return Path("C:/ProgramData/Cytomat")

def get_db_path():
    return get_config_dir().joinpath('slots.db')

def get_sample_path():
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).parent.parent.parent
        base_path.joinpath("data")
        print(base_path)

    sample_config_file = base_path / "sample_config.json"
    return sample_config_file


def find_file_in_meipass(filename):
    if not getattr(sys, "frozen", False):
        raise RuntimeError(
            "The Script has to executed as .exe file (by using Pyinstaller)."
        )

    meipass_dir = sys._MEIPASS
    for root, dirs, files in os.walk(meipass_dir):
        if filename in files:
            return os.path.join(root, filename)

def find():
    filename_to_find = "sample_config.json"
    full_path = find_file_in_meipass(filename_to_find)

    if full_path:
        print(f""
            f"Die Datei '{filename_to_find}' wurde gefunden unter: {full_path}")
    else:
        print(
            f"Die Datei '{filename_to_find}' wurde im _MEIPASS Ordner nicht gefunden."
        )

def create_config_directory():
    config_dir = get_config_dir()
    try:
        if not config_dir.exists():
            os.mkdir(config_dir)
            print(f""
                  f"Created: {config_dir}")
        else:
            print(f""
                  f"already exits: {config_dir}")

    except Exception as e:
        print(f"""  
            Path directory could not be created: {e}
            -
            Please Create manualy: {config_dir}""")

def create_data_base():
    db_file = get_db_path()
    # Create DataBase and copy into recent Created config directory
    try:
        if not db_file.exists():
            create_db(db_file)
            print(f""
                  f"copied sample DataBase to: {db_file}")
        else:
            print(f""
                  f"DataBase file allready exits: {db_file}")

    except Exception as e:
        print(f""" 
                Error: {e}
                -
                Please run funktion create_db(Path) in the program cytomat/scripts/create_db.py
                -
                choose the Path: 'C:/ProgrammData/Cytomat/slots.db'""")


def create_config_file():
    config_dir = get_config_dir()
    config_file = config_dir.joinpath('config.json')
    sample_config_file = get_sample_path

    try:
        if not config_file.exists():
            shutil.copy2(sample_config_file, config_file)
            print(f""
                  f"copied sample configs to: {config_dir}")

    except Exception as e:
        print(f"""
            Error:{e}
            -
            Please copy: {sample_config_file} into: {config_dir}"""
        )

def setup_config_dir():
    create_config_directory()
    create_config_file()
    create_data_base()

def post_install():
    setup_config_dir()

if __name__ == '__main__':
    post_install()