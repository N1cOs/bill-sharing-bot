import re
import logging

import vk_bot.service.commands as cmd
from vk_bot.config import Config
from vk_bot.exceptions import SyntaxException
from .util import Util, Key


class Handler:
    def __init__(self, message, match):
        self.message = message
        self.match = match

        self.key = Key(message['peer_id'], message['from_id'])

    def handle_cmd(self, match, key):
        pass

    def handle(self):
        try:
            return self.handle_cmd(self.match, self.key)
        except SyntaxException:
            raise
        except Exception as e:
            logging.error(e, exc_info=True)
            raise SyntaxException(_('exception.unknown'))


class OweHandler(Handler):
    PATTERN = r'^(?P<debtors>(?:\[.+?\|.+?\]\s*,?\s*)+){}\s(?P<user>\[.+?\|.+?\]\s)?' \
              r'(?P<amount>\d+?[.,]?\d*?)\s(:?(?P<period>{})\s)?(?P<name>.+)$'

    @staticmethod
    def match(text):
        pattern = OweHandler.PATTERN.format(_('cmd.owe'), _('monthly'))
        return re.match(pattern, text, re.IGNORECASE)

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
        return re.match(pattern, text, re.IGNORECASE)

    def handle_cmd(self, match, key):
        lender = match.group('user')
        id_lender = Util.parse_user_id(lender) if lender else None

        return cmd.handle_pay(id_lender, key)


class ConfirmHandler(Handler):
    PATTERN = r'\A#(?P<uuid>[abcdef\d]+)$'

    def __init__(self, message, matches, messages):
        super().__init__(message, None)

        self.matches = matches
        self.messages = messages

    @staticmethod
    def match(text):
        return re.match(ConfirmHandler.PATTERN, text, re.MULTILINE)

    def handle_cmd(self, match, key):
        for msg in self.messages:
            if msg['from_id'] != (-Config.VK_GROUP_ID):
                raise SyntaxException(_('exception.confirm.bad_id'))

        if self.message['text'] != '1':
            raise SyntaxException(_('exception.confirm.not_confirmed'))

        uuids = list({m.group('uuid') for m in self.matches})

        return cmd.confirm(uuids, key.from_id)


class HelpHandler(Handler):
    PATTERN = r'^{}$'

    @staticmethod
    def match(text):
        pattern = HelpHandler.PATTERN.format(_('cmd.help'))
        return re.match(pattern, text, re.IGNORECASE)

    def handle_cmd(self, match, key):
        return _('cmd.help_message')
