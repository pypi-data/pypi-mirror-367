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

"""This modules handles the basic kernel state file in order to track which extension has been activated already """

from pathlib import Path
import json
# from pyHarm import __pyHarm_kernel_PID__, __pyHarm_kernel_UUID__, __pyHarm_kernel_DATETIME__
import psutil
import datetime
KERNEL_STATE_FILE = Path.home() / ".pyHarm" / "context.json"
BASIC_STATE = dict(
    kernels = dict(),
    cli = dict()
)


def save_kernel_state(state: dict):
    KERNEL_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    KERNEL_STATE_FILE.write_text(json.dumps(state, indent=4))

def load_kernel_state() -> dict:
    if not KERNEL_STATE_FILE.exists():
        return {}
    return json.loads(KERNEL_STATE_FILE.read_text())

def clean_kernel_state() : 
    context = load_kernel_state()
    _ks = context['kernels']
    _pid_to_clean = []
    for pid in _ks.keys() : 
        _pid = int(pid)
        if not psutil.pid_exists(_pid) : 
            _pid_to_clean.append(pid)
    for pid in _pid_to_clean : _ = _ks.pop(pid)
    save_kernel_state(context)

def init_kernel_state(pid, uuid:str, datetime:datetime.datetime):
    if not KERNEL_STATE_FILE.exists(): 
        reset_kernel_state()
    clean_kernel_state()
    context = load_kernel_state()
    _ks = context['kernels']
    _ks[pid] = dict(
        pid = pid,
        uuid = uuid,
        datetime = datetime,
        extensions = []
    )
    save_kernel_state(context)

def add_extension_to_kernel_state(pid, loaded_ext):
    _pid = str(pid)
    context = load_kernel_state()
    _ks = context['kernels']
    for ext in loaded_ext :
        _ks[_pid]['extensions'].append(ext)
    _ks[_pid]['extensions'] = list(set(_ks[_pid]['extensions']))
    save_kernel_state(context)

def read_extension_from_kernel_state(pid):
    _pid = str(pid)
    context = load_kernel_state()
    _ks = context['kernels']
    return _ks[_pid]['extensions']


def reset_kernel_state():
    if KERNEL_STATE_FILE.exists():
        KERNEL_STATE_FILE.unlink()
    KERNEL_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    KERNEL_STATE_FILE.write_text(json.dumps(BASIC_STATE, indent=4))
