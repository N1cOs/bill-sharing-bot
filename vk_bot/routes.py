import re

from flask import request, json, abort

import vk_bot.service.handlers as hd
import vk_bot.service.temp as t
from vk_bot.exceptions import SyntaxException
from vk_bot.service.util import Key
from .app import app
from .config import Config

MESSAGE_NEW, CONFIRMATION = 'message_new', 'confirmation'

HANDLERS = [hd.OweHandler]


@app.route('/', methods=['POST'])
def handle():
    req = json.loads(request.data)
    event_type = req['type']
    if event_type == MESSAGE_NEW:
        data = req['object']
        text = re.sub(r'\s{2,}?(?=\S)', ' ', data['text'])

        key = Key(data['peer_id'], data['from_id'])
        temp = t.is_temp_state(key)
        try:
            if temp:
                return t.handle(key, temp, text)

            for handler in HANDLERS:
                match = handler.match(text)
                if match:
                    return handler.handle(match, key)
            return 'error'
        except SyntaxException as e:
            return e.message
    elif event_type == CONFIRMATION:
        return Config.VK_CONFIRMATION_STRING
    abort(400)
