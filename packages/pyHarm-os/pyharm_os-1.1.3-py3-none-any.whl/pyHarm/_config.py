# Copyright 2024 SAFRAN SA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This modules handles the basic functionalities to write and load the basic configuration file for pyHarm into the HOME of the user"""
from pathlib import Path
import json
from pyHarm.BaseUtilFuncs import getCustomOptionDictionary
import copy
import os
CONFIG_DIR = Path.home() / ".pyHarm"
CONFIG_FILE = CONFIG_DIR / "settings.json"

DEFAULT_CONFIG = {
    "extensions": {
        "status":True,
        "include":[],
        "exclude":[],
    },
}

def ensure_config_exists():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_FILE.exists():
        CONFIG_FILE.write_text(json.dumps(DEFAULT_CONFIG, indent=4))

def _deep_merge_dicts(base: dict, override: dict) -> dict:
    result = base.copy()
    for key, value in override.items():
        if key in result:
            if isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = _deep_merge_dicts(result[key], value)
            elif isinstance(result[key], list) and isinstance(value, list):
                # If the local list is non-empty, override it
                if value:
                    result[key] = value
                # Else keep the global one (do nothing)
            else:
                result[key] = value
        else:
            result[key] = value
    return result

def load_config(user_only:bool=False, folder_project:str=None):
    # Ensure global config exists
    ensure_config_exists()
    # Load user config
    with CONFIG_FILE.open("r") as f:
        _user_config = json.load(f)
    config = copy.copy(_user_config)
    if not user_only : 
        # Check for local config: ./.pyHarm/settings.json
        if folder_project : _basic_path = Path.cwd() / folder_project
        else :_basic_path = Path.cwd()
        local_config_file = _basic_path / ".pyHarm" / "settings.json"
        if local_config_file.exists():
            with local_config_file.open("r") as f:
                _local_config = json.load(f)
            config = _deep_merge_dicts(_user_config,_local_config)
    return config

def reset_config():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(DEFAULT_CONFIG, indent=4))
