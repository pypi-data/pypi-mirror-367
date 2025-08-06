import logging
import os
from pyHarm import __version__
import platform


FORMATER_CONSOLE = logging.Formatter(
        "[ {levelname:^9}] -- {asctime} -- {message}",
        style="{",
        datefmt="%H:%M:%S",
    )

FORMATER_BANNER = logging.Formatter(
    "{message}",
    style="{",
)

LOGGER_CONFIG = dict(
    basic = dict(
        level=[logging.INFO,logging.INFO],
        formater=[FORMATER_CONSOLE]
    ),
    debug = dict(
        level=[logging.DEBUG,logging.DEBUG],
        formater=[FORMATER_CONSOLE]
    ),
    export=dict(
        level=[logging.INFO, logging.ERROR, logging.INFO],
        formater=[FORMATER_CONSOLE]*2
    )
)

def _log_banner(logger:logging.Logger, banner_formater:logging.Formatter, loaded_extensions:list[str]) :
    banner = _create_pyHarm_banner(version=__version__, licence="Apache 2.0 - open-source", loaded_extensions=loaded_extensions)
    or_handler_format = []
    for handler in logger.handlers : 
        or_handler_format.append(handler.formatter)
        handler.setFormatter(FORMATER_BANNER)
    logger.info(banner)
    for handler, formater in zip(logger.handlers,or_handler_format) : 
        handler.setFormatter(formater)
    pass

def log_the_banner(logger:logging.Logger, loaded_extensions:list[str], banner_formater:logging.Formatter=FORMATER_BANNER) : 
    _log_banner(logger=logger, banner_formater=banner_formater, loaded_extensions=loaded_extensions)
    pass

def basic_logger(name:str, debug:bool=False, *args):

    _type_logger = 'basic'
    if debug :  _type_logger = 'debug'
    _logger_congif = LOGGER_CONFIG[_type_logger]
    formater = _logger_congif['formater']

    logger = logging.getLogger(name)
    logger.setLevel(_logger_congif['level'][0])

    console_handler = logging.StreamHandler()

    console_handler.setFormatter(formater[0])
    console_handler.setLevel(_logger_congif['level'][1])

    logger.addHandler(console_handler)
    return logger

def export_logger(name:str, path:str='.', *args):

    _type_logger = 'export'
    _logger_congif = LOGGER_CONFIG[_type_logger]
    formater = _logger_congif['formater']

    logfile = os.path.join(path, 'pyharm.log')
    logger = logging.getLogger(name)
    logger.setLevel(_logger_congif['level'][0])

    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler(logfile, mode="w", encoding="utf-8")

    console_handler.setFormatter(formater[0])
    console_handler.setLevel(_logger_congif['level'][1])

    file_handler.setLevel(_logger_congif['level'][2])
    file_handler.setFormatter(formater[1])

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger


def _create_pyHarm_banner(version:str, licence:str, loaded_extensions:list[str]):
    _space = " "
    _loaded_ext_string = f"\n{_space:20}".join([f"- {e}" for e in loaded_extensions])
    banner = f"""
######################################################
##                                                  ##
##                                                  ##
##                  _   _                           ##
##      _ __  _   _| | | | __ _ _ __ _ __ ___       ##
##     | '_ \| | | | |_| |/ _` | '__| '_ ` _ \      ##
##     | |_) | |_| |  _  | (_| | |  | | | | | |     ##
##     | .__/ \__, |_| |_|\__,_|_|  |_| |_| |_|     ##
##     |_|    |___/                      v-{version:9}##
##                                                  ##
##                                                  ##
######################################################
    python      :   {platform.python_version():20}
    licence     :   {licence}
    extensions  :   {_loaded_ext_string}

"""
    return banner