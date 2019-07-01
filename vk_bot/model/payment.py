from datetime import datetime

from vk_bot.app import db


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_debt = db.Column(db.Integer, db.ForeignKey('debt.id'))
    date = db.Column(db.DateTime, nullable=False, default=datetime.now())
    amount = db.Column(db.Integer, nullable=False)
    id_user = db.Column(db.Integer, db.ForeignKey('app_user.id'))

    debt = db.relationship('Debt')
    user = db.relationship('User')

    def __repr__(self):
        return 'Payment({}, {}, {}, {})'.format(self.id_debt, self.date,
                                                self.amount, self.id_user)
