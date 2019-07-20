import re
from enum import Enum, auto

from vk_api.utils import get_random_id

from vk_bot.app import vk


class Util:
    @staticmethod
    def parse_user_id(text):
        pipe_index = text.index('|')
        return int(text[3:pipe_index])

    @staticmethod
    def parse_options(text):
        return re.split(r'\s?[\s,]\s?', text.strip())

    @staticmethod
    def send_message(peer_id, text):
        random_id = get_random_id()
        vk.method('messages.send', {'peer_id': peer_id, 'random_id': random_id, 'message': text})


class Key:
    def __init__(self, peer_id, from_id):
        self.peer_id = peer_id
        self.from_id = from_id

    def __repr__(self):
        return '{}:{}'.format(self.peer_id, self.from_id)


class State(Enum):
    OWE_PERIOD = auto()
    DEBT_ACCEPT = auto()
    PAY_ACCEPT = auto()

    PAY = auto()
    SETTLE = auto()
    DELETE = auto()
    UPDATE = auto()


class Temp:
    def __init__(self, state, data):
        self.state = state
        self.data = data
