import re

from flask import request, json, abort

import vk_bot.service.handlers as hd
import vk_bot.service.temp as t
from vk_bot.exceptions import SyntaxException
from vk_bot.service.util import Key, Util
from .app import app
from .config import Config

MESSAGE_NEW, CONFIRMATION = 'message_new', 'confirmation'

HANDLERS = [hd.OweHandler, hd.PayHandler]


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
                message = t.handle(key, temp, text)
            else:
                for Handler in HANDLERS:
                    match = Handler.match(text)
                    if match:
                        handler = Handler(match, key)
                        message = handler.handle()
                        break
                else:
                    message = _('exception.cmd.not_recognised')
        except SyntaxException as e:
            message = e.message

        Util.send_message(key.peer_id, message)
        return 'ok'
    elif event_type == CONFIRMATION:
        return Config.VK_CONFIRMATION_STRING
    abort(400)
