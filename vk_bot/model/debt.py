from datetime import datetime

from sqlalchemy import (Column, String, Integer, DateTime,
                        Float, CheckConstraint, ForeignKey, Boolean)
from sqlalchemy.orm import relationship

from vk_bot.app import Base
from .user import User


class Debt(Base):
    __tablename__ = 'debt'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    date = Column(DateTime, nullable=False, default=datetime.now())
    amount = Column(Float(24), CheckConstraint('amount >= 1'))
    id_lender = Column(Integer, ForeignKey('app_user.id'))
    id_conversation = Column(Integer)

    is_current = Column(Boolean)
    period = Column(Integer)

    lender = relationship('User')

    def __init__(self, name: str, amount: float, id_conversation: int, lender: User,
                 date: DateTime = None, is_current: bool = False, period: int = 0):
        self.name = name
        self.amount = amount
        self.id_conversation = id_conversation
        self.lender = lender

        self.date = date
        self.is_current = is_current
        self.period = period

    def __repr__(self):
        return 'Debt("{}", {}, {}, {}, {})'.format(self.name, self.date, self.amount,
                                                   self.id_lender, self.id_conversation)
