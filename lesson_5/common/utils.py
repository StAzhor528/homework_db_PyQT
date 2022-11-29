"""Утилиты"""
import logging
import os
import sys
import json
import traceback
from datetime import datetime, date
from functools import wraps
from json import JSONEncoder

sys.path.append(os.path.join(os.getcwd(), '..'))
from .variables import MAX_PACKAGE_LENGTH, ENCODING
from errors import IncorrectDataRecivedError, NonDictInputError


def log(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        script_name = sys.argv[0].split('/')[-1]

        if script_name == 'client.py':
            UTILS_LOGGER = logging.getLogger('client')
        elif script_name == 'server.py':
            UTILS_LOGGER = logging.getLogger('server')
        f = func(*args, **kwargs)
        UTILS_LOGGER.info(f'Вызванна функция {func.__name__} c аргументами {args}, {kwargs}')
        UTILS_LOGGER.info(
            f'Функция {func.__name__} вызвана из функции {traceback.format_stack()[0].strip().split()[-1]}')
        return f

    return wrap


@log
def get_msg(sock):
    encoded_response = sock.recv(MAX_PACKAGE_LENGTH)
    if isinstance(encoded_response, bytes):
        json_response = encoded_response.decode(ENCODING)
        response = json.loads(json_response)
        if isinstance(response, dict):
            return response
        else:
            raise IncorrectDataRecivedError
    else:
        raise IncorrectDataRecivedError


@log
def send_msg(sock, msg):
    if not isinstance(msg, dict):
        raise NonDictInputError
    js_message = json.dumps(msg)
    encoded_message = js_message.encode(ENCODING)
    sock.send(encoded_message)
