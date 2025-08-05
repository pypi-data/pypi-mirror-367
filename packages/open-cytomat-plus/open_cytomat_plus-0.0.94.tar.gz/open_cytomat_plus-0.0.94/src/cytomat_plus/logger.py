import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("cytomat.log"),
        logging.StreamHandler()
    ]
)

log = logging.getLogger("cytomat")