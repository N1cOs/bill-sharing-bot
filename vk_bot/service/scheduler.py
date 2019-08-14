import threading
import time
from datetime import datetime

import schedule
from sqlalchemy.orm import joinedload

import vk_bot.model as md
from vk_bot.app import db


def update_debts():
    debts = md.Debt.query.options(joinedload(md.Debt.debtors)) \
        .filter(md.Debt.is_current) \
        .all()

    month = datetime.now().month
    for debt in debts:
        if month > debt.date.month:
            if debt.date.month != 12:
                new_date = debt.date.replace(month=debt.date.month + 1)
            else:
                new_date = debt.date.replace(year=debt.date.year + 1, month=1)

            new_debt = md.Debt(name=debt.name, date=new_date, amount=debt.amount, is_current=True,
                               is_monthly=True, id_lender=debt.id_lender, id_conversation=debt.id_conversation,
                               left_amount=debt.amount, debtors=debt.debtors, lender=debt.lender)
            debt.is_current = False

            db.session.add(new_debt)
    db.session.commit()


def run():
    schedule.every().day.at("00:00").do(update_debts)

    while True:
        schedule.run_pending()
        time.sleep(60)


threading.Thread(target=run, daemon=True).start()
