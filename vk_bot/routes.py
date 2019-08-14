import re
import logging
import vk_bot.service.scheduler

from flask import request, json, abort

import vk_bot.service.handlers as hd
import vk_bot.service.temp as t
from vk_bot.exceptions import SyntaxException
from vk_bot.service.util import Key, Util
from .app import app
from .config import Config

MESSAGE_NEW, CONFIRMATION = 'message_new', 'confirmation'

HANDLERS = [hd.OweHandler, hd.PayHandler, hd.HelpHandler]


@app.route('/', methods=['POST'])
def handle():
    req = json.loads(request.data)
    event_type = req['type']
    if event_type == MESSAGE_NEW:
        in_message = req['object']
        text = in_message['text'] = re.sub(r'\s{2,}?(?=\S)', ' ', in_message['text'])

        key = Key(in_message['peer_id'], in_message['from_id'])
        temp = t.is_temp_state(key)

        reply_message = in_message.get('reply_message')
        fwd_messages = in_message.get('fwd_messages') or []
        messages = [reply_message] if reply_message else fwd_messages

        try:
            if len(messages) > 0:
                matches = []
                for msg in messages:
                    match = hd.ConfirmHandler.match(msg['text'])
                    if match:
                        matches.append(match)
                    else:
                        reply = _('exception.confirm.bad_forward')
                        break
                else:
                    handler = hd.ConfirmHandler(in_message, matches, messages)
                    reply = handler.handle()
            elif temp:
                reply = t.handle(key, temp, text)
            else:
                for Handler in HANDLERS:
                    match = Handler.match(text)
                    if match:
                        handler = Handler(in_message, match)
                        reply = handler.handle()
                        break
                else:
                    reply = _('exception.cmd.not_recognised')
        except SyntaxException as e:
            reply = e.message
        except Exception as e:
            logging.error(e, exc_info=True)
            reply = _('exception.unknown')

        Util.send_message(key.peer_id, reply)
        return 'ok'
    elif event_type == CONFIRMATION:
        return Config.VK_CONFIRMATION_STRING
    abort(400)
