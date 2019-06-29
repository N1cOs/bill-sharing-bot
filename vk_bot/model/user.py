from vk_bot.app import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .city import City


class User(Base):
    __tablename__ = 'app_user'

    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    second_name = Column(String(60), nullable=False)
    gender = Column(String(1), nullable=False)
    city_id = Column(Integer, ForeignKey('city.id'))

    city = relationship('City', back_populates='users')

    def __init__(self, first_name: str, second_name: str, gender: str,
                 id: int = None, city: City = None):
        self.id = id
        self.first_name = first_name
        self.second_name = second_name
        self.gender = gender
        self.city = city

    def __repr__(self):
        return 'User("{}", "{}", "{}", {}, {})'.\
            format(self.first_name, self.second_name, self.gender, self.id, self.city_id)
