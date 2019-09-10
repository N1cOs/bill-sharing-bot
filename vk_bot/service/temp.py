import json
import logging
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
        raise SyntaxException(_('exception.invalid_option'))

    option = int(options[0])
    if option not in [0, 1]:
        raise SyntaxException(_('exception.invalid_option'))

    wrapper = DebtWrapper(**data, is_current=True, is_monthly=True)
    wrapper.date = datetime.strptime(wrapper.date, Config.DATETIME_FORMAT)

    month, year = wrapper.date.month + option, wrapper.date.year
    if month == 13:
        month = 1
        year += 1

    wrapper.date = datetime(day=1, month=month, year=year)
    redis.delete(repr(key))

    return cmd.register_debt(wrapper)


def temp_pay(key, data, options):
    try:
        debts = {}
        for op, amount in options.items():
            debts[data[op - 1]] = amount
    except IndexError:
        raise SyntaxException('{} is invalid option'.format(op))

    redis.delete(repr(key))
    return cmd.register_pay(key.from_id, debts)


def cancel_cmd(key):
    redis.delete(repr(key))
    return _('cmd.cancel')


HANDLERS = {State.OWE_PERIOD: temp_owe, State.PAY: temp_pay}

OPTIONS_REGEX = re.compile(r'^((\d+?(\s?[,\s]\s?))*?)(\d+)$')
PAY_REGEX = re.compile(r'^(\d+?\s?:\s?\d+?\s*?)+$')
CANCEL_SYMBOL = '-1'


def handle(key, temp, text):
    try:
        if text == CANCEL_SYMBOL:
            return cancel_cmd(key)
        handler = HANDLERS.get(State(temp.state))

        match = OPTIONS_REGEX.match(text)
        if match:
            return handler(key, temp.data, Util.parse_options(text))

        match = PAY_REGEX.match(text)
        if match:
            return handler(key, temp.data, Util.parse_pay_options(text))
    except Exception as e:
        logging.error(e, exc_info=True)
        raise SyntaxException(_('exception.unknown'))
    else:
        raise SyntaxException(_('exception.invalid_format'))
