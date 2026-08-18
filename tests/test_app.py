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
    """Test Deposit operation"""
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