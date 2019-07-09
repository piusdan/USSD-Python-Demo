# from app.ussd.utils import kenya_time

from .database import db, AuditColumns
from .util import kenya_time


class User(AuditColumns, db.Model):
    __tablename__ = 'users'
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    username = db.Column(
        db.String(64),
        index=True
    )
    phone_number = db.Column(
        db.String(64),
        unique=True,
        index=True,
        nullable=False
    )
    account = db.Column(
        db.Float,
        default=10.00
    )
    reg_date = db.Column(
        db.DateTime,
        default=kenya_time
    )
    validation = db.Column(
        db.String,
        default=""
    )
    city = db.Column(db.String(32), default="")

    def __repr__(self):
        return "User {}".format(self.name)

    @staticmethod
    def by_phoneNumber(phone_number):
        return User.query.filter_by(phone_number=phone_number).first()

    @staticmethod
    def by_username(username):
        return User.query.filter_by(username=username).first()

    def deposit(self, amount):
        self.account += amount
        self.save()

    def withdraw(self, amount):
        if self.amount > self.account:
            raise Exception("Cannot overwithdraw")
        self.account -= amount
        self.save()


class AnonymousUser(): pass
