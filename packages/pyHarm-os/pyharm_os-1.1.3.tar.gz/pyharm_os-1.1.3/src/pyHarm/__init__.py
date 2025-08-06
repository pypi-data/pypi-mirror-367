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

## This is the init file of pyHarm Package
"""
The pyHarm package is the core of pyHarm. It contains every modules and subpackages for pyHarm to be runnning an analysis. 
"""
from ._version import __version__, __package_name__
import uuid
import os
import datetime
from ._kernel_state import init_kernel_state, add_extension_to_kernel_state, read_extension_from_kernel_state
from pyHarm._config import load_config
import importlib.metadata

# def _load_extensions(extension_config:dict[str,list[str]], verbose: bool = True) -> tuple[dict[str,list[_plugable_types]],list[str]]:
def _load_extensions(extension_config:dict[str,list[str]], verbose: bool = True) :
    group = "pyharm.extensions"
    _status = extension_config['status']
    _loaded_extensions = dict()
    _failed_extensions = []
    if not _status : return _loaded_extensions,_failed_extensions # load nothing if extension loading is not active
    _ext_to_include:dict[str,bool] = {ext:False for ext in extension_config['include']}
    _ext_to_exclude = extension_config['exclude']

    _load_everything = "ALL" in _ext_to_include

    _extension_from_group = importlib.metadata.entry_points().select(group=group)
    for entry_point in _extension_from_group:
        if (((entry_point.name in _ext_to_include.keys()) and (entry_point.name not in _ext_to_exclude)) or (_load_everything)) : 
            try:
                _register_func = entry_point.load()
                _classes_to_plug = _register_func()
                _loaded_extensions[entry_point.name] = [False,_classes_to_plug]
                _ext_to_include[entry_point.name] = True
                # print(f"[pyHarm] Loading extension: {entry_point.name} -> {entry_point.value}")
            except Exception as e:
                _failed_extensions.append(entry_point.name)
                # print(f"[pyHarm] Failed to load extension '{entry_point.name}': {e}")
    _failed_extensions = _failed_extensions + [ext_name for ext_name,ext_loaded in _ext_to_include.items() if not ext_loaded]
    return _loaded_extensions,_failed_extensions

__pyHarm_kernel_PID__ = os.getpid()
__pyHarm_kernel_UUID__ = str(uuid.uuid4())
__pyHarm_kernel_DATETIME__ = datetime.datetime.now(datetime.timezone.utc).isoformat()

init_kernel_state(pid=__pyHarm_kernel_PID__, uuid=__pyHarm_kernel_UUID__, datetime=__pyHarm_kernel_DATETIME__)
__pyHarm_kernel_config__ = load_config()
__pyHarm_kernel_loaded_extensions__,__pyHarm_kernel_failed_extensions__ = _load_extensions(extension_config=__pyHarm_kernel_config__['extensions'])
add_extension_to_kernel_state(pid=__pyHarm_kernel_PID__, loaded_ext=__pyHarm_kernel_loaded_extensions__)

# plugin the extensions into the instance of pyHarm
from .BaseUtilFuncs import pyHarm_plugin
for ext_name,ext_char in __pyHarm_kernel_loaded_extensions__.items() : 
    loaded_satus, list_cls = ext_char
    if not loaded_satus : 
        for cls in list_cls : pyHarm_plugin(cls)
        __pyHarm_kernel_loaded_extensions__[ext_name][0] = True

from .Maestro import Maestro