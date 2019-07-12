from datetime import datetime

from vk_bot.app import db
from .user import user_debt


class Debt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.now())
    amount = db.Column(db.Float(24), db.CheckConstraint('amount >= 1'))
    id_lender = db.Column(db.Integer, db.ForeignKey('app_user.id'))
    id_conversation = db.Column(db.Integer)

    is_current = db.Column(db.Boolean, default=False)
    is_monthly = db.Column(db.Boolean, default=False)

    debtors = db.relationship('User', secondary=user_debt)
    lender = db.relationship('User')

    def __repr__(self):
        return 'Debt("{}", {}, {}, {}, {})'.format(self.name, self.date, self.amount,
                                                   self.id_lender, self.id_conversation)


class DebtWrapper:
    def __init__(self, id_lender, name, debtors, amount,
                 date, id_conversation, is_monthly=False, is_current=False):
        self.id_lender = id_lender
        self.name = name
        self.debtors = debtors
        self.amount = amount
        self.is_monthly = is_monthly
        self.date = date
        self.id_conversation = id_conversation
        self.is_current = is_current
