import json
from datetime import datetime, timedelta

import vk_bot.model as md
from vk_bot.app import redis, db
from vk_bot.config import Config
from vk_bot.exceptions import SyntaxException
from .util import State


def handle_owe(key, id_lender, debtors, amount, is_monthly, name):
    if amount < 1:
        raise SyntaxException('Amount must be greater than or equal to 1')

    if id_lender in debtors:
        raise SyntaxException('User can\'t be owe to himself')

    if is_monthly:
        data = {'state': State.OWE_PERIOD.value, 'data': {
            'id_lender': id_lender, 'debtors': debtors, 'amount': amount, 'name': name,
            'date': datetime.now().strftime(Config.DATETIME_FORMAT), 'id_conversation': key.peer_id
        }}

        redis.set(repr(key), json.dumps(data), ex=timedelta(days=1))
        return 'current or next month?'
    else:
        wrapper = md.DebtWrapper(id_lender, name, debtors, amount,
                                 datetime.now().replace(microsecond=0), key.peer_id)
        save_debt(wrapper)
        return 'debt was saved'


def save_debt(wrapper):
    lender, debtors = get_users(wrapper.id_lender, wrapper.debtors)
    amount = float(round(wrapper.amount / len(wrapper.debtors), 2))
    debt = md.Debt(name=wrapper.name, date=wrapper.date, amount=amount, id_conversation=wrapper.id_conversation,
                   is_current=wrapper.is_current, is_monthly=wrapper.is_monthly)

    debt.lender = lender
    debt.debtors = debtors

    db.session.add(debt)
    db.session.commit()
    return 'debt was saved'


def get_users(id_lender, id_debtors):
    ids = id_debtors[:]
    ids.append(id_lender)
    users = md.User.query.filter(md.User.id.in_(ids)).all()

    for id in ids:
        if not any(id == u.id for u in users):
            # ToDo: calling vk api
            print('call vk api')
            user = md.User(id=id, first_name='user', second_name='user', gender='M')
            users.append(user)

    lender_index = 0
    for i in range(len(users)):
        if users[i].id == id_lender:
            lender_index = i
            break
    lender = users.pop(lender_index)

    return lender, users
