from datetime import datetime

from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from vk_bot.app import Base
from .debt import Debt
from .user import User


class Payment(Base):
    __tablename__ = 'payment'

    id = Column(Integer, primary_key=True)
    id_debt = Column(Integer, ForeignKey('debt.id'))
    date = Column(DateTime, nullable=False, default=datetime.now())
    amount = Column(Integer, nullable=False)
    id_user = Column(Integer, ForeignKey('app_user.id'))

    debt = relationship('Debt')
    user = relationship('User')

    def __init__(self, amount: int, debt: Debt, user: User):
        self.amount = amount
        self.debt = debt
        self.user = user

    def __repr__(self):
        return 'Payment({}, {}, {}, {})'.format(self.id_debt, self.date,
                                                self.amount, self.id_user)
