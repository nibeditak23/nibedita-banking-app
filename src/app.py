from flask import Flask ,jsonify,request
from src.models import Account
from datetime import datetime
import uuid

app=Flask(__name__)
accounts = {}

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
        accounts[account_id]= account
        return jsonify({
            "account_id":account_id,
            "status":'created',
            "balance":account.balance            
        }),201
    except Exception as e:
        return jsonify({"error":str(e)}),400
        
@app.route('/api/accounts/<account_id>',methods=['GET'])
def get_account(account_id):
    if account_id not in accounts:
        return jsonify({"error":"Account not found"}),404
    acc=accounts[account_id]
    return jsonify({
        "account_id":acc.account_id,
        "account_type":acc.account_type,
        "balance":acc.balance,
        "owner_name":acc.owner_name
    }),200
    
@app.route('/api/accounts/<account_id>/deposit',methods=['POST'])
def deposit(account_id):
    if account_id not in accounts:
        return jsonify({"error":"Account not found"}),404
    data=request.get_json()
    amount=float(data.get('amount',0))
    try:
        acc=accounts.get(account_id)
        new_balance=acc.deposit(amount)
        return jsonify({
            "account_id":account_id,
            "balance":new_balance,
            "status":"deposit successful"
        }),200
    except Exception as e:
        return jsonify({"error":str(e)}),400
@app.route('/api/accounts/<account_id>/withdraw',methods=['POST'])
def withdraw(account_id):
    if account_id not in accounts:
        return jsonify({"error":"Account not found"}),404
    data=request.get_json()
    amount=float(data.get('amount',0))
    try:
        account=accounts[account_id]
        new_balance=account.withdraw(amount)
        return jsonify({
            "account_id":account_id,
            "balance":new_balance,
            "status":"Withdrawal successful"
        }),200
    except Exception as e:
        return jsonify({"error":str(e)}),400
if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=5000)
    
