from .scripts.setup_cytomat_plus import get_config_dir
import jso


def lazy_load_config_file():
    try:
        config_file = get_config_dir() / "config.json"
        with open(config_file, "r") as f:
            python_data = json.load(f)
            print("Data loaded")
            return python_data
    except Exception as e:

        print(f"Data not loaded due to: {e}")
        print(f"config file: {config_file} not found")
        return None