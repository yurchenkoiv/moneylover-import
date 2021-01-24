import yaml


def load_csv_config(path: str) -> dict:
    try:
        with open(path) as csv_config_file:
            csv_config_dict = yaml.load(csv_config_file, Loader=yaml.FullLoader)
            return csv_config_dict
    except Exception as e:
        raise Exception(f"Can't load config from {path}")


def validate_csv_config(csv_config_dict: dict) -> None:
    mandatory: list = ['filePath', 'withHeaders', 'dateFormat', 'delimiter', 'csvHeader', 'categories']
    csv_columns: list = ['date', 'type', 'category', 'amount']
    if not all(k in csv_config_dict for k in mandatory):
        raise Exception(f"Some of the mandatory fields are missing in the csv config file. Mandatory fields: {mandatory}")
    if not all(k in csv_config_dict['csvHeader'] for k in csv_columns):
        raise Exception(f"Mapping for some mandatory columns missing. Mandatory mapping: {csv_columns}")


def validate_main_config(config: dict):
    if config.get('jwtToken') is None:
        raise Exception("Create jwtToken in main config")
    if config['jwtToken'] == '':
        raise Exception("jwtToken cant be empty")

try:
    with open('config.yaml') as f:
        config_dict: dict = yaml.load(f, Loader=yaml.FullLoader)
        validate_main_config(config_dict)
except Exception as e:
    raise Exception("Can't load config from config.yaml")




