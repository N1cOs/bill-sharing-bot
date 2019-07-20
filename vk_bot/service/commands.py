import json
from datetime import datetime, timedelta

from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound

import vk_bot.model as md
from vk_bot.app import redis, db
from vk_bot.config import Config
from vk_bot.exceptions import SyntaxException
from .util import State, Temp, Util


def handle_owe(key, id_lender, debtors, amount, is_monthly, name):
    if amount < 1:
        raise SyntaxException(_('exception.amount'))

    if id_lender in debtors:
        raise SyntaxException(_('exception.owe_himself'))

    if is_monthly:
        data = {'state': State.OWE_PERIOD.value, 'data': {
            'id_lender': id_lender, 'debtors': debtors, 'amount': amount, 'name': name,
            'date': datetime.now().strftime(Config.DATETIME_FORMAT), 'id_conversation': key.peer_id
        }}

        redis.set(repr(key), json.dumps(data), ex=timedelta(days=1))
        return _('owe.period')
    else:
        wrapper = md.DebtWrapper(id_lender, name, debtors, amount,
                                 datetime.now().replace(microsecond=0), key.peer_id)
        save_debt(wrapper)
        return _('owe.debt.register')


def save_debt(wrapper):
    lender, debtors = get_users(wrapper.id_lender, wrapper.debtors)
    amount = float(round(wrapper.amount / len(wrapper.debtors), 2))
    debt = md.Debt(name=wrapper.name, date=wrapper.date, amount=amount, id_conversation=wrapper.id_conversation,
                   is_current=wrapper.is_current, is_monthly=wrapper.is_monthly)

    debt.lender = lender
    debt.debtors = debtors

    db.session.add(debt)
    db.session.commit()
    # ToDo: add sending messages for confirmation
    return _('owe.debt.saved')


def get_users(id_lender, id_debtors):
    ids = id_debtors[:]
    ids.append(id_lender)
    users = md.User.query.filter(md.User.id.in_(ids)).all()

    new_user_ids = [id for id in ids if id not in (u.id for u in users)]
    for new_user in Util.get_users_info(new_user_ids):
        user = md.User(id=new_user['id'], first_name=new_user['first_name'], second_name=new_user['last_name'])
        user.gender = 'M' if new_user['sex'] == 2 else 'F'

        city = new_user.get('city')
        if city:
            user.city = md.City(id=city['id'], name=city['title'])
        users.append(user)

    lender_index = 0
    for i in range(len(users)):
        if users[i].id == id_lender:
            lender_index = i
            break
    lender = users.pop(lender_index)

    return lender, users


def handle_pay(id_lender, key):
    try:
        if id_lender:
            if key.peer_id == key.from_id:
                user = md.User.query.options(joinedload(md.User.debts)) \
                    .filter(md.User.id == key.from_id) \
                    .filter(md.Debt.id_lender == id_lender) \
                    .one()
            else:
                user = md.User.query.options(joinedload(md.User.debts)) \
                    .filter(md.User.id == key.from_id) \
                    .filter(md.Debt.id_lender == id_lender) \
                    .filter(md.Debt.id_conversation == key.peer_id) \
                    .one()
        else:
            if key.peer_id == key.from_id:
                user = md.User.query.options(joinedload(md.User.debts)) \
                    .filter(md.User.id == key.from_id) \
                    .one()
            else:
                user = md.User.query.options(joinedload(md.User.debts)) \
                    .filter(md.User.id == key.from_id) \
                    .filter(md.Debt.id_conversation == key.peer_id) \
                    .one()
    except NoResultFound:
        raise SyntaxException(_('exception.no_debts'))
    else:
        users = md.User.query.filter(md.User.id.in_({d.id_lender for d in user.debts})).all()
        users = {u.id: '{} {}'.format(u.first_name, u.second_name) for u in users}

        debts, lines = [], []
        for index, debt in enumerate(user.debts, 1):
            lines.append('{}.{}'.format(index, debt.info(users[debt.id_lender])))
            debts.append(debt.id)

        temp = Temp(State.PAY.value, debts)
        redis.set(repr(key), json.dumps(vars(temp)), ex=timedelta(days=1))

        text = '\n{}\n'.format(50 * '-').join(lines)
        return _('debts.info').format(text)
