import os
import yaml

def get_config():
    if not os.path.isfile("config.yaml"):
        # sys.exit("'config.yaml' not found! Please add it and try again.")
        with open("../config.yaml") as file:
            return yaml.load(file, Loader=yaml.FullLoader)
    else:
        with open("config.yaml") as file:
            return yaml.load(file, Loader=yaml.FullLoader)