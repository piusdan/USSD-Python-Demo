from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import AnonymousUserMixin, UserMixin
from flask import current_app
from app.database import db, CRUDMixin
from app.login_manager import login_manager
from sqlalchemy import ForeignKey


class Permission:
    READ = 0x02
    WRITE = 0x04
    UPDATE = 0x08
    ADMINISTER = 0x80


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.READ |
                     Permission.WRITE, True),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


class User(CRUDMixin, UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64))
    phone_number = db.Column(db.String(64), unique=True, index=True, nullable=False)
    registration_date = db.Column(db.DateTime(), default=datetime.utcnow)
    password_hash = db.Column(db.String(128))
    account = db.Column(db.Float, default=10.00)
    role_id = db.Column(db.Integer,ForeignKey('roles.id'))

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.phone_number == current_app.config['ADMIN_PHONENUMBER']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    @staticmethod
    def insert_user_roles():
        users = User.query.all()
        for user in users:
            if user.phone_number == current_app.config['ADMIN_PHONENUMBER']:
                user.role = Role.query.filter_by(permissions=0xff).first()
        db.session.commit()

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
        self.account -= amount
        self.save()


class SessionLevel(CRUDMixin, db.Model):
    __tablename__ = 'session_levels'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(128), unique=True)
    phone_number = db.Column(db.String(25))
    response = db.Column(db.String(3))
    level = db.Column(db.Integer, default=0)

    def promote(self, level=1):
        self.level = level
        self.save()

    def demote(self, level=0):
        self.level = level
        self.save()

    @staticmethod
    def by_sessionId(sessionId):
        return SessionLevel.query.filter_by(session_id=sessionId).first()

    @staticmethod
    def by_phoneNumber(phone_number):
        return SessionLevel.query.filter_by(phone_number=phone_number).first()

class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
