import re
import vk_bot.service.commands as cmd
from vk_bot.exceptions import SyntaxException


class Parser:
    OWES_PATTERN = r'^(?P<debtors>(?:\[.+?\|.+?\]\s*,?\s*)+)owes\s(?P<user>\[.+?\|.+?\]\s)?' \
              r'(?P<amount>\d+?[.,]?\d*?)\s(?P<param>monthly|weekly\s)?(?P<name>.+)$'

    def parse_owe(self, match):
        try:
            debtors = re.split(r',|(?<=\])\s+(?=\[)', match.group('debtors'))
            debtors_id = [Util.parse_user_id(d.strip()) for d in debtors]

            user = match.group('user')
            lender_id = Util.parse_user_id(user) if user else self.data['from_id']

            amount = float(match.group('amount'))
            regularity = match.group('param')
            name = match.group('name')

            print(lender_id, debtors_id, amount, regularity, name)
            return cmd.handle_owe(lender_id, debtors_id, amount, regularity, name)
        except Exception:
            raise SyntaxException('Error occurred while parsing. Check format')

    HANDLERS = {OWES_PATTERN: parse_owe}

    def __init__(self, data):
        self.data = data

    def handle(self):
        text = re.sub(r'\s{2,}?(?=\S)', ' ', self.data['text'])
        for pattern, handler in self.HANDLERS.items():
            match = re.match(pattern, text)
            if match:
                return handler(self, match)
        raise SyntaxException('Error! Command was not recognised')


class Util:
    @staticmethod
    def parse_user_id(text):
        pipe_index = text.index('|')
        return int(text[3:pipe_index])
