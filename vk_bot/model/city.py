from vk_bot.app import Base
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship


class City(Base):
    __tablename__ = 'city'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)

    users = relationship('User', back_populates='city')

    def __init__(self, name: str, id: int = None):
        self.id = id
        self.name = name

    def __repr__(self):
        return 'City({}, "{}")'.format(self.id, self.name)
