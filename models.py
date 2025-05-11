from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import date

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'  # Explicit table name for clarity

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    budget_limit = db.Column(db.Float, default=0.0)

    transactions = db.relationship('Transaction', backref='user', lazy=True, cascade='all, delete-orphan')


class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(10), nullable=False)  # 'Income' or 'Expense'
    date = db.Column(db.Date, nullable=False, default=date.today)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
