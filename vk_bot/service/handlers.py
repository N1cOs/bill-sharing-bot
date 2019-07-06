import re

import vk_bot.service.commands as cmd
from vk_bot.exceptions import SyntaxException


class OweHandler:
    PATTERN = r'^(?P<debtors>(?:\[.+?\|.+?\]\s*,?\s*)+){}\s(?P<user>\[.+?\|.+?\]\s)?' \
              r'(?P<amount>\d+?[.,]?\d*?)\s(:?(?P<param>{}|{}|{})\s)?(?P<name>.+)$'

    @staticmethod
    def match(text):
        pattern = OweHandler.PATTERN.format(*(_('pattern.owe').split()))
        return re.match(pattern, text)

    @staticmethod
    def handle(match, data):
        try:
            debtors = re.split(r',|(?<=\])\s+(?=\[)', match.group('debtors'))
            debtors_id = [Util.parse_user_id(d.strip()) for d in debtors]

            user = match.group('user')
            lender_id = Util.parse_user_id(user) if user else data['from_id']

            amount_str = match.group('amount').replace(',', '.')
            amount = round(float(amount_str), 2)
            regularity = match.group('param')

            name = match.group('name')
            if regularity is None:
                name = name.split(' ', 1)[1]

            return cmd.handle_owe(lender_id, debtors_id, amount, regularity, name)
        except Exception:
            raise SyntaxException('Error occurred while parsing. Check format')


class Util:
    @staticmethod
    def parse_user_id(text):
        pipe_index = text.index('|')
        return int(text[3:pipe_index])
