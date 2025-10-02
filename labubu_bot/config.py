import yaml
from dotenv import load_dotenv
import os

def load_config(config_path='config.yaml'):
    with open(config_path, 'r') as f:
        cfg = yaml.safe_load(f)
    load_dotenv()
    proxy = os.getenv('HTTP_PROXY')
    cfg['proxy'] = proxy
    return cfg
