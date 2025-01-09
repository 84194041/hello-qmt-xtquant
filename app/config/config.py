import os
import socket
import tomli
import shutil
from loguru import logger

root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
config_file = f"{root_dir}/config.toml"

def load_config():
    # fix: IsADirectoryError: [Errno 21] Is a directory: '/MoneyPrinterTurbo/config.toml'
    if os.path.isdir(config_file):
        shutil.rmtree(config_file)

    if not os.path.isfile(config_file):
        example_file = f"{root_dir}/config.example.toml"
        if os.path.isfile(example_file):
            shutil.copyfile(example_file, config_file)
            logger.info(f"copy config.example.toml to config.toml")

    logger.info(f"load config from file: {config_file}")

    try:
        _config_ = tomli.load(config_file)
    except Exception as e:
        logger.warning(f"load config failed: {str(e)}, try to load as utf-8-sig")
        with open(config_file, mode="r", encoding='utf-8-sig') as fp:
            _cfg_content = fp.read()
            _config_ = tomli.loads(_cfg_content)
    return _config_

_cfg = load_config()
app = _cfg.get("app", {})

log_level = app.get("log_level", "DEBUG")
listen_host = app.get("listen_host", "")
listen_port = app.get("listen_port", 1000)
project_name = app.get("project_name", "")
project_version = app.get("project_version", "")
project_description = app.get("project_description", "")
reload_debug = False
api_address = app.get("api_address", "")
service_name = app.get("service_name", "")
investment_targets = app.get("investment_targets", "")

logger.info(f"{project_name} v{project_version}")
