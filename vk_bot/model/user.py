from vk_bot.app import db

user_debt = db.Table('user_debt',
                     db.Column('user_id', db.Integer, db.ForeignKey('app_user.id')),
                     db.Column('debt_id', db.Integer, db.ForeignKey('debt.id')))


class User(db.Model):
    __tablename__ = 'app_user'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    second_name = db.Column(db.String(60), nullable=False)
    gender = db.Column(db.String(1), nullable=False)
    id_city = db.Column(db.Integer, db.ForeignKey('city.id'))

    city = db.relationship('City', back_populates='users', lazy='raise')
    debts = db.relationship('Debt', secondary=user_debt, lazy='raise')

    def __repr__(self):
        return 'User("{}", "{}", "{}", {}, {})'.\
            format(self.first_name, self.second_name, self.gender, self.id, self.id_city)
