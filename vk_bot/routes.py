import re

from flask import request, json

import vk_bot.service.handlers as hd
from vk_bot.exceptions import SyntaxException
from .app import app

HANDLERS = [hd.OweHandler]


@app.route('/', methods=['POST'])
def handle():
    data = json.loads(request.data)['object']
    text = re.sub(r'\s{2,}?(?=\S)', ' ', data['text'])
    try:
        for handler in HANDLERS:
            match = handler.match(text)
            if match:
                handler.handle(match, data)
                return 'ok'
        return 'error'
    except SyntaxException as e:
        return e.message
