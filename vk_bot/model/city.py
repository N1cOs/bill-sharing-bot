from vk_bot.app import db


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    users = db.relationship('User', back_populates='city')

    def __repr__(self):
        return 'City({}, "{}")'.format(self.id, self.name)
