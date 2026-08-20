from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

class Account(db.Model):
    __tablename__ = 'accounts'
    
    account_id = db.Column(db.String(36), primary_key=True)
    account_type = db.Column(db.String(50), nullable=False)
    balance = db.Column(db.Float, nullable=False)
    owner_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False,  default=datetime.utcnow)
    
    def deposit(self, amount: float) -> float:
        if amount <=0:
            raise ValueError("Deposite amount must be positive")
        self.balance += amount
        return self.balance
    
    def withdraw(self, amount: float) -> float:
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        self.balance -= amount
        return self.balance
    
class Transaction(db.Model):
    __tablename__ = 'transactions'
    transaction_id = db.Column(db.String(36), primary_key=True)
    account_id = db.Column(db.String(36), db.ForeignKey('accounts.account_id'), nullable=False)
    transaction_type = db.Column(db.String(50), nullable=False) # "deposit" or "withdrawal"
    amount = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False,  default=datetime.utcnow)
    status = db.Column(db.String(50), nullable=False)  # "completed", "pending", "failed"
    duration_ms = db.Column(db.Float, nullable=False)  # milliseconds taken
