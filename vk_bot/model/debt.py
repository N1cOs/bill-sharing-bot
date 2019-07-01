from datetime import datetime

from vk_bot.app import db


class Debt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.now())
    amount = db.Column(db.Float(24), db.CheckConstraint('amount >= 1'))
    id_lender = db.Column(db.Integer, db.ForeignKey('app_user.id'))
    id_conversation = db.Column(db.Integer)

    is_current = db.Column(db.Boolean)
    period = db.Column(db.Integer)

    lender = db.relationship('User')

    def __repr__(self):
        return 'Debt("{}", {}, {}, {}, {})'.format(self.name, self.date, self.amount,
                                                   self.id_lender, self.id_conversation)
