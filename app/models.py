from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from . import db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))

    phone_number = db.Column(db.String(64), unique=True, index=True, nullable=False)

    city = db.Column(db.String(64))
    registration_date = db.Column(db.DateTime(), default=datetime.utcnow)
    password_hash = db.Column(db.String(128))
    account = db.Column(db.Integer, default=10)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return "User {}".format(self.name)

    def deposit(self, amount):
        self.account += amount

    def withdraw(self, amount):
        self.account -= amount


class SessionLevel(db.Model):
    __tablename__ = 'session_levels'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Text(128), unique=True)
    phone_number = db.Column(db.String(25))
    level = db.Column(db.Integer, default=0)

    def promote_level(self, level=1):
        self.level = level

    def demote_level(self):
        self.level = 0


