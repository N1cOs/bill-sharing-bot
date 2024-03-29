import re
import uuid
from enum import Enum, auto

from vk_api.utils import get_random_id

from vk_bot.app import vk
from vk_bot.exceptions import SyntaxException


class Util:
    @staticmethod
    def parse_user_id(text):
        try:
            pipe_index = text.index('|')
            return int(text[3:pipe_index])
        except ValueError:
            raise SyntaxException(_('exception.invalid_user'))

    @staticmethod
    def parse_options(text):
        return re.split(r'\s?[\s,]\s?', text.strip())

    @staticmethod
    def send_message(peer_id, text):
        random_id = get_random_id()
        vk.method('messages.send', {'peer_id': peer_id, 'random_id': random_id, 'message': text})

    @staticmethod
    def get_users_info(user_ids):
        if len(user_ids) > 0:
            ids = ','.join(list(map(str, user_ids)))
            return vk.method('users.get', {'user_ids': ids, 'fields': 'sex, city'})
        return []

    @staticmethod
    def get_uuid():
        return uuid.uuid1().hex

    @staticmethod
    def parse_pay_options(text):
        values = re.split(r'(?<=\d)\s+(?=\d)', text)
        result = {}
        for val in values:
            temp = re.split(r'\s*:\s*', val)
            result[int(temp[0])] = float(temp[1])
        return result


class Key:
    def __init__(self, peer_id, from_id):
        self.peer_id = peer_id
        self.from_id = from_id

    def __repr__(self):
        return '{}:{}'.format(self.peer_id, self.from_id)


class State(Enum):
    OWE_PERIOD = auto()

    PAY = auto()
    SETTLE = auto()
    DELETE = auto()
    UPDATE = auto()

    DEBT_ACCEPT = auto()
    PAY_ACCEPT = auto()


class Temp:
    def __init__(self, state, data):
        self.state = state
        self.data = data
