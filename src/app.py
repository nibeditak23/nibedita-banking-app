from flask import Flask ,jsonify,request
from flask_sqlalchemy import SQLAlchemy
from src.models import Account, db, Transaction
from datetime import datetime
import uuid
import os
import time

app=Flask(__name__)
#accounts = {}
# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg://bankuser:bankpass123@localhost:5432/banking_app'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Create tables when app starts
with app.app_context():
    db.create_all()

@app.route('/health',methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status":"healthy"}),200

@app.route('/api/accounts',methods=['POST'])
def create_account():
    """Create a New Account"""
    data=request.get_json()
    account_id=str(uuid.uuid4())
    try:
        account=Account(
            account_id=account_id,
            account_type=data.get('account_type','checking'),
            balance=float(data.get('balance',0)),
            owner_name=data.get('owner_name'),
            created_at=datetime.now()
        )
        db.session.add(account)
        db.session.commit()
        
        return jsonify({
            "account_id":account_id,
            "status":'created',
            "balance":account.balance            
        }),201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error":str(e)}),400
        
@app.route('/api/accounts/<account_id>',methods=['GET'])
def get_account(account_id):
    """Retrive account details"""
    account = Account.query.filter_by(account_id=account_id).first()
    
    if not account:
        return jsonify({"error":"Account not found"}),404
    
    return jsonify({
        "account_id":account.account_id,
        "account_type":account.account_type,
        "balance":account.balance,
        "owner_name":account.owner_name
    }),200
    
@app.route('/api/accounts/<account_id>/deposit',methods=['POST'])
def deposit(account_id):
    """Deposit funds into an account"""
    
    # Note: duration_ms measures app logic only (excludes DB commit time)
    start_time = time.time() * 1000 # Convert to milliseconds
    account = Account.query.filter_by(account_id=account_id).first()
    if not account:
        return jsonify({"error":"Account not found"}),404
    data=request.get_json()
    amount=float(data.get('amount',0))
    try:
        new_balance=account.deposit(amount)
        #Calculate duration
        end_time = time.time() * 1000
        duration_ms = end_time - start_time
        
        #Create Transaction record
        transaction = Transaction(
            transaction_id = str(uuid.uuid4()),
            account_id=account_id,
            transaction_type = 'deposit',
            amount= amount,
            timestamp=datetime.now(),
            status='completed',
            duration_ms=duration_ms
        )
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({
            "account_id":account_id,
            "balance":new_balance,
            "status":"deposit successful",
            "transaction_id":transaction.transaction_id,
            "duration_ms":transaction.duration_ms
        }),200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error":str(e)}),400
@app.route('/api/accounts/<account_id>/withdraw',methods=['POST'])
def withdraw(account_id):
    """Withdraw funds from an account"""
    
    # Note: duration_ms measures app logic only (excludes DB commit time)
    start_time = time.time() * 1000
    
    account = Account.query.filter_by(account_id=account_id).first()
    
    if not account:
        return jsonify({"error":"Account not found"}),404
    
    data=request.get_json()
    amount=float(data.get('amount',0))
    
    try:
        new_balance=account.withdraw(amount)
        end_time = time.time() * 1000
        duration_ms = end_time - start_time
        
        transaction = Transaction(
            transaction_id=str(uuid.uuid4()),
            account_id=account_id,
            transaction_type='withdrawal',
            amount=amount,
            timestamp=datetime.now(),
            status = 'completed',
            duration_ms=duration_ms
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({
            "account_id":account_id,
            "balance":new_balance,
            "status":"Withdrawal successful",
            "transaction_id":transaction.transaction_id,
            "duration_ms":transaction.duration_ms
        }),200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error":str(e)}),400
    
@app.route('/api/accounts/<account_id>/transactions', methods=['GET'])
def get_transactions(account_id):
    """Retrieve transaction history for an account"""
    account = Account.query.filter_by(account_id=account_id).all()
    if not account:
        return jsonify({'error':'Account not found'}), 404
    
    transactions = Transaction.query.filter_by(account_id=account_id).all()
    
    return jsonify([{
        "transaction_id":t.transaction_id,
        "account_id":t.account_id,
        "type":t.transaction_type,
        "amount":t.amount,
        "timestamp":t.timestamp.isoformat(),
        "status":t.status,
        "duration_ms":t.duration_ms
    } for t in transactions]), 200
    
@app.route('/api/accounts', methods=['GET'])
def get_accounts():
    """Retrive all accounts optionally by Owner"""
    owner = request.args.get('owner')
    
    if owner:
        accounts=Account.query.filter_by(owner_name = owner).all()
    else:
        accounts=Account.query.all()
        
    return jsonify([{
        "account_id": acc.account_id,
        "owner_name": acc.owner_name,
        "account_type": acc.account_type,
        "balance": acc.balance,
        "created_at": acc.created_at.isoformat()
    } for acc in accounts]), 200
    
@app.route('/api/accounts/<account_id>/summary', methods=['GET'])
def account_summary(account_id):
    """Get transaction summary for an account"""
    account = Account.query.filter_by(account_id=account_id).first()
    if not account:
        return jsonify({"error":"Account not Found"}), 404
    
    transactions = Transaction.query.filter_by(account_id=account_id).all()
    
    if not transactions:
        return jsonify({
            "account_id":account_id,
            "owner_name":account.owner_name,
            "current_balance":account.balance,
            "total_deposits": 0,
            "total_withdrawals": 0,
            "transaction_count": 0,
            "avg_duration_ms": 0
        }),200
        
    deposits = [t.amount for t in transactions if t.transaction_type == 'deposit']
    withdrawals = [t.amount for t in transactions if t.transaction_type == 'withdrawal']
    duration = [t.duration_ms for t in transactions]
    
    return jsonify ({
        "account_id": account_id,
        "owner_name": account.owner_name,
        "current_balance": account.balance,
        "total_deposits": sum(deposits),
        "total_withdrawals": sum(withdrawals),
        "transaction_count": len(duration),
        "avg_duration_ms": sum(duration)/len(duration) if duration else 0
    }), 200
    
    
if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=5000)
    
