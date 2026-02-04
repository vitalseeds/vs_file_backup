# /// script
# requires-python = ">=3.14"
# dependencies = ["platformdirs"]
# ///

from pathlib import Path
from platformdirs import user_config_dir

APP_NAME = "vs_backup"
CONFIG_DIR = Path(user_config_dir(APP_NAME))

print(CONFIG_DIR)