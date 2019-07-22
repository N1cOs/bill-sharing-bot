import re

import vk_bot.service.commands as cmd
from vk_bot.config import Config
from vk_bot.exceptions import SyntaxException
from .util import Util


class Handler:
    def __init__(self, match, key):
        self.match = match
        self.key = key

    def handle_cmd(self, match, key):
        pass

    def handle(self):
        try:
            return self.handle_cmd(self.match, self.key)
        except SyntaxException:
            raise
        except Exception as e:
            print(e.args)
            raise SyntaxException('Error occurred while parsing. Check format')


class OweHandler(Handler):
    PATTERN = r'^(?P<debtors>(?:\[.+?\|.+?\]\s*,?\s*)+){}\s(?P<user>\[.+?\|.+?\]\s)?' \
              r'(?P<amount>\d+?[.,]?\d*?)\s(:?(?P<period>{})\s)?(?P<name>.+)$'

    @staticmethod
    def match(text):
        pattern = OweHandler.PATTERN.format(_('cmd.owe'), _('monthly'))
        return re.match(pattern, text)

    def handle_cmd(self, match, key):
        debtors = Util.parse_options(match.group('debtors'))
        debtors_id = list({Util.parse_user_id(d.strip()) for d in debtors})

        user = match.group('user')
        lender_id = Util.parse_user_id(user) if user else key.from_id

        amount_str = match.group('amount').replace(',', '.')
        amount = round(float(amount_str), 2)

        period = match.group('period')
        if period is None:
            is_monthly = False
        else:
            is_monthly = True
        name = match.group('name')

        return cmd.handle_owe(key, lender_id, debtors_id, amount, is_monthly, name)


class PayHandler(Handler):
    PATTERN = r'^(?P<user>\[.+?\|.+?\]\s)?{}$'

    @staticmethod
    def match(text):
        pattern = PayHandler.PATTERN.format(_('cmd.pay'))
        return re.match(pattern, text)

    def handle_cmd(self, match, key):
        lender = match.group('user')
        id_lender = Util.parse_user_id(lender) if lender else None

        return cmd.handle_pay(id_lender, key)


class ConfirmHandler(Handler):
    PATTERN = r'\A#(?P<uuid>[abcdef\d]+)$'

    def __init__(self, match, key, text, reply_message):
        super().__init__(match, key)

        self.text = text
        self.reply_message = reply_message

    @staticmethod
    def match(text):
        return re.match(ConfirmHandler.PATTERN, text, re.MULTILINE)

    def handle_cmd(self, match, key):
        uuid = match.group('uuid')

        if self.reply_message['from_id'] != (-Config.VK_GROUP_ID):
            raise SyntaxException(_('exception.confirm.bad_id'))

        if self.text != '1':
            raise SyntaxException(_('exception.confirm.not_confirmed'))

        return cmd.confirm(uuid, key.from_id)
