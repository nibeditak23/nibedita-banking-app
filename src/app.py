from flask import Flask ,jsonify,request
from flask_sqlalchemy import SQLAlchemy
from src.models import Account, db
from datetime import datetime
import uuid
import os

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
    account = Account.query.filter_by(account_id=account_id).first()
    if not account:
        return jsonify({"error":"Account not found"}),404
    data=request.get_json()
    amount=float(data.get('amount',0))
    try:
        new_balance=account.deposit(amount)
        db.session.commit()
        return jsonify({
            "account_id":account_id,
            "balance":new_balance,
            "status":"deposit successful"
        }),200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error":str(e)}),400
@app.route('/api/accounts/<account_id>/withdraw',methods=['POST'])
def withdraw(account_id):
    """Withdraw funds from an account"""
    account = Account.query.filter_by(account_id=account_id).first()
    if not account:
        return jsonify({"error":"Account not found"}),404
    data=request.get_json()
    amount=float(data.get('amount',0))
    try:
        new_balance=account.withdraw(amount)
        db.session.commit()
        return jsonify({
            "account_id":account_id,
            "balance":new_balance,
            "status":"Withdrawal successful"
        }),200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error":str(e)}),400
if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=5000)
    
