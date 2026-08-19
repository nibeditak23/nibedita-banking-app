from dataclasses import dataclass
from datetime import datetime

@dataclass
class Account:
    account_id:str
    account_type:str
    balance:float
    owner_name:str
    created_at:datetime
    def deposit(self,amount:float) -> float:
        if amount<=0:
            raise ValueError("Deposit amount must be positive")
        self.balance += amount
        return self.balance
    def withdraw(self,amount:float)->float:
        if amount<=0:
            raise ValueError("Withdrawal amount must be positive")
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        self.balance -= amount
        return self.balance