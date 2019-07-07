import re

import vk_bot.service.commands as cmd
from vk_bot.exceptions import SyntaxException
from .util import Util


class OweHandler:
    PATTERN = r'^(?P<debtors>(?:\[.+?\|.+?\]\s*,?\s*)+){}\s(?P<user>\[.+?\|.+?\]\s)?' \
              r'(?P<amount>\d+?[.,]?\d*?)\s(:?(?P<period>\d+?)\s)?(?P<name>.+)$'

    @staticmethod
    def match(text):
        pattern = OweHandler.PATTERN.format(_('cmd.owe'))
        return re.match(pattern, text)

    @staticmethod
    def handle(match, key):
        try:
            debtors = re.split(r',|(?<=\])\s+(?=\[)', match.group('debtors'))
            debtors_id = [Util.parse_user_id(d.strip()) for d in debtors]

            user = match.group('user')
            lender_id = Util.parse_user_id(user) if user else key.from_id

            amount_str = match.group('amount').replace(',', '.')
            amount = round(float(amount_str), 2)

            period = match.group('period')
            if period is None:
                period = 0
            else:
                period = int(period)
            name = match.group('name')

            return cmd.handle_owe(key, lender_id, debtors_id, amount, period, name)
        except Exception as e:
            print(e)
            raise SyntaxException('Error occurred while parsing. Check format')
