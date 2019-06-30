from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship

from vk_bot.app import Base
from .city import City

user_debt = Table('user_debt', Base.metadata,
                  Column('user_id', Integer, ForeignKey('app_user.id')),
                  Column('debt_id', Integer, ForeignKey('debt.id')))


class User(Base):
    __tablename__ = 'app_user'

    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    second_name = Column(String(60), nullable=False)
    gender = Column(String(1), nullable=False)
    id_city = Column(Integer, ForeignKey('city.id'))

    city = relationship('City', back_populates='users', lazy='raise')
    debts = relationship('Debt', secondary=user_debt, lazy='raise')

    def __init__(self, first_name: str, second_name: str, gender: str,
                 id: int = None, city: City = None):
        self.id = id
        self.first_name = first_name
        self.second_name = second_name
        self.gender = gender
        self.city = city

    def __repr__(self):
        return 'User("{}", "{}", "{}", {}, {})'.\
            format(self.first_name, self.second_name, self.gender, self.id, self.id_city)
