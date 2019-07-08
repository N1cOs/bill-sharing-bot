import re

from flask import request, json

import vk_bot.service.handlers as hd
import vk_bot.service.temp as t
from vk_bot.exceptions import SyntaxException
from vk_bot.service.util import Key
from .app import app

HANDLERS = [hd.OweHandler]


@app.route('/', methods=['POST'])
def handle():
    data = json.loads(request.data)['object']
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
