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
        return register_debt(wrapper)


def register_debt(wrapper):
    user_ids = wrapper.debtors[:]
    user_ids.append(wrapper.id_lender)
    _check_users(user_ids)

    uuid = Util.get_uuid()
    wrapper.amount = float(round(wrapper.amount / len(wrapper.debtors), 2))
    wrapper.date = str(wrapper.date)

    temp = Temp(State.DEBT_ACCEPT.value, vars(wrapper))
    redis.set('{}:data'.format(uuid), json.dumps(vars(temp)), ex=timedelta(days=1))

    hl = '{}'.format(50 * '-')
    text = _('owe.debt.confirm').format(uuid, wrapper.name, wrapper.id_lender, wrapper.id_lender, hl)
    _send_confirmations(uuid, text, wrapper.debtors)

    return _('owe.debt.register')


def _check_users(user_ids):
    users = md.User.query.filter(md.User.id.in_(user_ids)).all()

    new_user_ids = [id for id in user_ids if id not in (u.id for u in users)]
    new_users = []

    for new_user in Util.get_users_info(new_user_ids):
        user = md.User(id=new_user['id'], first_name=new_user['first_name'], second_name=new_user['last_name'])
        user.gender = 'M' if new_user['sex'] == 2 else 'F'

        city = new_user.get('city')
        if city:
            user.city = md.City(id=city['id'], name=city['title'])
        new_users.append(user)

    if len(new_users) > 0:
        db.session.add_all(new_users)
        db.session.commit()


def _send_confirmations(key, text, users):
    redis.set(key, json.dumps(users), ex=timedelta(days=1))
    for id_user in users:
        Util.send_message(id_user, text)


def confirm(uuids, id_user):
    users_list = redis.mget(*uuids)
    for users in users_list:
        if users is None:
            raise SyntaxException(_('exception.confirm.outdated'))

    users_list = [json.loads(users) for users in users_list]
    for users in users_list:
        if id_user not in users:
            raise SyntaxException(_('exception.confirm.user_not_found'))

    del_keys, set_users = [], {}
    for i in range(len(users_list)):
        users, uuid = users_list[i], uuids[i]
        if len(users) == 1:
            key = '{}:{}'.format(uuid, 'data')
            temp = Temp(**json.loads(redis.get(key)))
            temp.state = State(temp.state)

            if temp.state == State.DEBT_ACCEPT:
                _confirm_debt(temp.data)
            elif temp.state == State.PAY_ACCEPT:
                _confirm_pay(temp.data['id_debt'], temp.data['id_payer'])

            del_keys.extend([key, uuid])
        else:
            users.remove(id_user)
            set_users[uuid] = json.dumps(users)

    if len(del_keys) > 0:
        redis.delete(*del_keys)
    if len(set_users) > 0:
        redis.mset(set_users)

    return _('confirm.confirmed')


def _confirm_debt(wrapper):
    if wrapper is None:
        raise SyntaxException(_('exception.confirm.outdated'))

    wrapper = md.DebtWrapper(**wrapper)
    message = save_debt(wrapper)

    Util.send_message(wrapper.id_conversation, message)


def _confirm_pay(id_debt, id_payer):
    debt = md.Debt.query.options(joinedload(md.Debt.debtors)) \
        .filter(md.Debt.id == id_debt).one()
    user = md.User.query.filter(md.User.id == id_payer).one()

    payment = md.Payment(id_debt=id_debt, amount=debt.amount, id_user=id_payer,
                         user=user, debt=debt)
    debt.debtors.remove(user)

    db.session.add(payment)
    db.session.commit()


def save_debt(wrapper):
    lender, debtors = get_users(wrapper.id_lender, wrapper.debtors)
    debt = md.Debt(name=wrapper.name, date=wrapper.date, amount=wrapper.amount,
                   id_conversation=wrapper.id_conversation, is_current=wrapper.is_current,
                   is_monthly=wrapper.is_monthly)

    debt.lender = lender
    debt.debtors = debtors

    db.session.add(debt)
    db.session.commit()
    return _('owe.debt.saved')


def get_users(id_lender, id_debtors):
    ids = id_debtors[:]
    ids.append(id_lender)
    users = md.User.query.filter(md.User.id.in_(ids)).all()

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

        hl = '\n{}\n'.format(50 * '-')
        text = hl.join(lines)
        return _('debts.info').format(hl, text)


def register_pay(id_user, id_debts):
    debts = md.Debt.query.filter(md.Debt.id.in_(id_debts)).all()
    user = md.User.query.filter(md.User.id == id_user).one()
    hl = '{}'.format(50 * '-')

    total_sum = 0
    for debt in debts:
        uuid = Util.get_uuid()
        total_sum += debt.amount

        id_lender = debt.id_lender
        text = _('cmd.pay_accept').format(uuid, debt.name, debt.amount, hl,
                                          user.id, user.first_name)
        key = '{}:data'.format(uuid)
        data = {'id_debt': debt.id, 'id_payer': id_user}
        temp = Temp(State.PAY_ACCEPT.value, data)

        redis.set(key, json.dumps(vars(temp)), ex=timedelta(days=1))
        _send_confirmations(uuid, text, [id_lender])

    return _('cmd.pay_register').format(total_sum)
