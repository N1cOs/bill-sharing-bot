import json
import re
from datetime import timedelta, datetime
from calendar import monthrange

import vk_bot.service.commands as cmd
from vk_bot.app import redis
from vk_bot.model import DebtWrapper
from .util import Temp, State, Util
from vk_bot.exceptions import SyntaxException
from vk_bot.config import Config


def is_temp_state(key):
    res = redis.get(repr(key))
    if res:
        return Temp(**json.loads(res))
    return None


def temp_owe(key, data, options):
    """0 - current period, 1 - next period"""
    if len(options) == 1:
        option = int(options[0])

        wrapper = DebtWrapper(**data)
        wrapper.is_current = True
        wrapper.date = datetime.strptime(wrapper.date, Config.DATETIME_FORMAT)

        if option == 1:
            if wrapper.period == 30:
                _, days = monthrange(wrapper.date.year, wrapper.date.month)
                delta = days - wrapper.date.day + 1
                wrapper.date += timedelta(days=delta)
            else:
                wrapper.date += timedelta(days=wrapper.period)
        elif option == 0:
            if wrapper.period == 30:
                delta = wrapper.date.day - 1
                wrapper.date -= timedelta(days=delta)
            else:
                wrapper.date -= timedelta(days=wrapper.period)
        else:
            raise SyntaxException('Invalid option')

        redis.delete(repr(key))
        return cmd.save_debt(wrapper)
    raise SyntaxException('Invalid option')


HANDLERS = {State.OWE_PERIOD: temp_owe}
OPTIONS_REGEX = re.compile(r'^((\d+?(\s?,\s?))*?)(\d+)$')


def handle(key, temp, text):
    match = OPTIONS_REGEX.match(text)
    if match:
        options = Util.parse_options(text)
        for state, handler in HANDLERS.items():
            if temp.state == state.value:
                return handler(key, temp.data, options)
    raise SyntaxException('Invalid format for options')
