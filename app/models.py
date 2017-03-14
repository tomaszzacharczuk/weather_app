from datetime import datetime
from flask import current_app, request
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import login_manager, db
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import hashlib


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    users = db.relationship('User', backref='role')


user_locations = db.Table('user_locations',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('location_id', db.Integer, db.ForeignKey('locations.id'))
)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True, nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    confirmed = db.Column(db.Boolean, default=False)
    avatar_hash = db.Column(db.String(32), nullable=True)
    locations = db.relationship('Location',
                                secondary=user_locations,
                                backref=db.backref('users', lazy='dynamic'),
                                lazy='dynamic'
    )

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    @property
    def username(self):
        return self.email.split("@")[0]

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.confirm != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.avatar_hash = hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        return True


@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(int(user_id))


class Location(db.Model):
    __tablename__ = 'locations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    weather = db.relationship('Weather', backref="location")


class Weather(db.Model):
    __tablename__ = 'weathers'
    id = db.Column(db.Integer, primary_key=True)
    temperature = db.Column(db.Float, nullable=False)
    temperature_min = db.Column(db.Float, nullable=False)
    temperature_max = db.Column(db.Float, nullable=False)
    wind = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime(), default=datetime.utcnow)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'))

    @property
    def serialize_temperature(self):
        """Return object data in serializable format"""
        return {
            'temperature_min': self.temperature_min,
            'temperature': self.temperature,
            'temperature_max': self.temperature_max,
            'date': "{:%Y-%m-%d %H:%M}".format(self.date)
        }

    @property
    def serialize_wind(self):
        """Return object data in serializable format"""
        return {
            'wind': self.wind,
            'date': "{:%Y-%m-%d %H:%M}".format(self.date)
        }
