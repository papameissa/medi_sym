from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    plan = db.Column(db.String(20), default='free')  # free, premium
    monthly_uses = db.Column(db.Integer, default=0)
    last_reset_date = db.Column(db.Date, default=date.today)
    subscription_expires = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    consultations = db.relationship('Consultation', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def reset_monthly_uses_if_needed(self):
        today = date.today()
        if self.last_reset_date.month != today.month or self.last_reset_date.year != today.year:
            self.monthly_uses = 0
            self.last_reset_date = today
            db.session.commit()

    def can_consult(self):
        self.reset_monthly_uses_if_needed()
        if self.plan == 'premium':
            if self.subscription_expires and self.subscription_expires < datetime.utcnow():
                self.plan = 'free'
                db.session.commit()
                return self.monthly_uses < 10
            return True
        return self.monthly_uses < 10

    def remaining_uses(self):
        self.reset_monthly_uses_if_needed()
        if self.plan == 'premium':
            if self.subscription_expires and self.subscription_expires < datetime.utcnow():
                self.plan = 'free'
                db.session.commit()
                return max(0, 10 - self.monthly_uses)
            return '∞'
        return max(0, 10 - self.monthly_uses)

    @property
    def is_premium(self):
        if self.plan != 'premium':
            return False
        if self.subscription_expires and self.subscription_expires < datetime.utcnow():
            self.plan = 'free'
            db.session.commit()
            return False
        return True


class Consultation(db.Model):
    __tablename__ = 'consultations'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    symptoms_text = db.Column(db.Text, nullable=False)
    results = db.Column(db.Text, nullable=True)      # résumé JSON mots-clés
    ai_analysis = db.Column(db.Text, nullable=True)   # analyse complète Claude IA
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Setting(db.Model):
    __tablename__ = 'settings'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.String(500), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @staticmethod
    def get(key, default=None):
        s = Setting.query.filter_by(key=key).first()
        return s.value if s else default

    @staticmethod
    def set(key, value):
        s = Setting.query.filter_by(key=key).first()
        if s:
            s.value = str(value)
            s.updated_at = datetime.utcnow()
        else:
            s = Setting(key=key, value=str(value))
            db.session.add(s)
        db.session.commit()


class SubscriptionRequest(db.Model):
    __tablename__ = 'subscription_requests'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    payment_proof = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='subscription_requests')
