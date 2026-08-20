import pytest
import sys
sys.path.insert(0,'.')
from src.app import app

@pytest.fixture
def client():
    """Flask test client"""
    app.config['TESTING']=True
    with app.test_client() as client:
        yield client
        
def test_health(client):
    """Test Health check End Point"""
    response=client.get('/health')
    assert response.status_code==200
    assert response.json['status']=='healthy'
    
def test_create_account(client):
    """Test Account creation"""
    response=client.post('/api/accounts',json={
        "account_type": "checking",
        "balance": 1000,
        "owner_name": "Alice"
    })
    assert response.status_code== 201
    assert response.json['status'] == 'created'
    assert response.json['balance'] == 1000.0

def test_deposit(client):
    """Test deposit operation and transaction creation"""
    create_resp= client.post('/api/accounts',json={
        "account_type": "savings",
        "balance":500.0,
        "owner_name":"Bob"
    })
    account_id=create_resp.json['account_id']
    response=client.post(f'/api/accounts/{account_id}/deposit',json={"amount":250})
    print(response.json)
    assert response.status_code==200
    assert response.json['balance']==750.0
    assert 'transaction_id' in response.json
    assert 'duration_ms' in response.json
    assert response.json['duration_ms'] > 0
    
def test_withdraw_insufficient_funds(client):
    """Test withdrawal with insufficient funds"""
    create_resp=client.post('/api/accounts',json={
        "account_type":"checking",
        "balance": 100.0,
        "owner_name": "Carol"
    })
    account_id=create_resp.json['account_id']
    response= client.post(f'/api/accounts/{account_id}/withdraw',json={'amount': 200.0})
    assert response.status_code == 400
    assert 'Insufficient funds' in response.json['error']
    
def test_get_account(client):
    """Test retrieving account details"""
    create_resp = client.post('/api/accounts', json={
        'account_type': 'checking',
        'balance': 1500.0,
        'owner_name': 'David'
    })
    account_id = create_resp.json['account_id']
    
    response = client.get(f'/api/accounts/{account_id}')
    assert response.status_code == 200
    assert response.json['owner_name'] == 'David'
    assert response.json['balance'] == 1500.0
    
def test_get_transactions(client):
    create_resp= client.post('/api/accounts', json={
        "account_type": 'checking',
        "balance": 1000.0,
        "owner_name": 'Eve'
    })
    account_id=create_resp.json['account_id']
    
    # Make two deposits
    client.post(f'/api/accounts/{account_id}/deposit', json={'amount':100.0})
    client.post(f'/api/accounts/{account_id}/deposit', json={'amount':200.0})
    
    response = client.get(f'/api/accounts/{account_id}/transactions')
    assert response.status_code==200
    assert len(response.json) == 2
    assert response.json[0]['type'] == 'deposit'
    assert response.json[0]['amount'] == 100.0
    assert response.json[1]['amount'] == 200.0
    
def test_get_all_accounts(client):
    """Test retrieving all accounts"""
    client.post('/api/accounts', json={
        "account_type":'checking',
        "owner_name": 'Alice',
        "balance": 1000.0
    })
    client.post('/api/accounts', json={
        "account_type": 'savings',
        "owner_name": 'Bob',
        "balance": 2000.0
    })
    response = client.get('/api/accounts')
    assert response.status_code == 200
    assert len(response.json) >= 2
    
def test_get_accounts_by_owner(client):
    """Test filtering accounts by owner"""
    create_resp= client.post('/api/accounts', json=({
        'owner_name': 'Charlie',
        'account_type': 'checking',
        'balance': 1500.0
    }))
    account_id = create_resp.json['account_id']
    response = client.get('/api/accounts?owner=Charlie')
    assert response.status_code == 200
    assert any(acc['account_id']==account_id for acc in response.json)
    
def test_account_summary(client):
    """Test transaction summary endpoint"""
    create_resp = client.post('/api/accounts', json={
        'owner_name': 'Diana',
        'account_type': 'checking',
        'balance': 1000.0
    })
    
    account_id = create_resp.json['account_id']
    
    # Make deposits and withdrawals
    client.post(f'/api/accounts/{account_id}/deposit', json={'amount':500.0})
    client.post(f'/api/accounts/{account_id}/withdraw', json={'amount':200.0})
    
    response = client.get(f'/api/accounts/{account_id}/summary')
    print(response.json)
    assert response.status_code ==200
    assert response.json['total_deposits'] == 500.0
    assert response.json['total_withdrawals'] == 200.0
    assert response.json['transaction_count'] == 2
    assert response.json['avg_duration_ms'] > 0
    
    