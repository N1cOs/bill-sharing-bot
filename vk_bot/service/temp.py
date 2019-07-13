import json
import re
from datetime import datetime

import vk_bot.service.commands as cmd
from vk_bot.app import redis
from vk_bot.config import Config
from vk_bot.exceptions import SyntaxException
from vk_bot.model import DebtWrapper
from .util import Temp, State, Util


def is_temp_state(key):
    res = redis.get(repr(key))
    if res:
        return Temp(**json.loads(res))
    return None


def temp_owe(key, data, options):
    """0 - current period, 1 - next period"""
    if len(options) != 1:
        raise SyntaxException('Invalid option')

    option = int(options[0])
    if option not in [0, 1]:
        raise SyntaxException('Invalid option')

    wrapper = DebtWrapper(**data, is_current=True, is_monthly=True)
    wrapper.date = datetime.strptime(wrapper.date, Config.DATETIME_FORMAT)

    month, year = wrapper.date.month + option, wrapper.date.year
    if month == 13:
        month = 1
        year += 1

    wrapper.date = datetime(day=1, month=month, year=year)
    redis.delete(repr(key))

    return cmd.save_debt(wrapper)


HANDLERS = {State.OWE_PERIOD: temp_owe}

OPTIONS_REGEX = re.compile(r'^((\d+?(\s?[,\s]\s?))*?)(\d+)$')


def handle(key, temp, text):
    match = OPTIONS_REGEX.match(text)
    if match:
        options = Util.parse_options(text)
        handler = HANDLERS.get(State(temp.state))
        if handler:
            return handler(key, temp.data, options)
    raise SyntaxException('Invalid format for options')
