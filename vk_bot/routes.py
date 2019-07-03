from .app import app
from flask import request, json
from vk_bot.service.parser import Parser
from vk_bot.exceptions import SyntaxException


@app.route('/', methods=['POST'])
def handle():
    data = json.loads(request.data)['object']
    parser = Parser(data)
    try:
        parser.handle()
        return 'ok'
    except SyntaxException as e:
        return e.message
