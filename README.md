# Banking Application - AI Performance Testing Portfolio Project

## Overview

A performance-testable banking application built with Flask, PostgreSQL, and SQLAlchemy.

**Goal:** Demonstrate performance engineering capabilities through transaction tracking, metrics collection, and load testing.

---

## Architecture

- **Framework:** Flask (Python)
- **Database:** PostgreSQL (Docker)
- **ORM:** SQLAlchemy
- **Testing:** Pytest
- **Performance Metrics:** Transaction duration tracking (ms)

---

## Features (Weeks 1-4)

### Accounts
- Create account
- Retrieve account details
- List all accounts
- Filter accounts by owner
- Account summary with analytics

### Transactions
- Deposit to account
- Withdraw from account
- Transaction history retrieval
- Performance metrics per transaction

### Analytics
- Total deposits per account
- Total withdrawals per account
- Transaction count
- Average operation duration (ms)

---

## API Endpoints

### Health Check
- `GET /health` — Health check

### Accounts
- `POST /api/accounts` — Create account
- `GET /api/accounts/<account_id>` — Get account details
- `GET /api/accounts` — List all accounts
- `GET /api/accounts?owner=name` — Filter by owner

### Transactions
- `POST /api/accounts/<account_id>/deposit` — Deposit money
- `POST /api/accounts/<account_id>/withdraw` — Withdraw money
- `GET /api/accounts/<account_id>/transactions` — Transaction history

### Analytics
- `GET /api/accounts/<account_id>/summary` — Account summary (deposits, withdrawals, avg duration)

---

## Running Locally

### Prerequisites
- Python 3.13+
- Docker & Docker Compose
- Git

### Setup

1. Clone repository
```bash
git clone https://github.com/nibeditak23/nibedita-banking-app.git
cd nibedita-banking-app
```

2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate  # Windows
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Start PostgreSQL
```bash
docker-compose up -d
```

5. Run Flask app
```bash
python -m src.app
```

App runs on `http://localhost:5000`

---

## Database Access

### Connect to PostgreSQL directly
```bash
docker exec -it banking_db psql -U bankuser -d banking_app
```

### Useful queries
```sql
-- View all accounts
SELECT account_id, owner_name, balance FROM accounts;

-- View all transactions
SELECT * FROM transactions ORDER BY timestamp DESC;

-- Account with most transactions
SELECT account_id, COUNT(*) as txn_count FROM transactions GROUP BY account_id;

-- Average transaction duration by type
SELECT transaction_type, AVG(duration_ms) as avg_duration FROM transactions GROUP BY transaction_type;
```

---

## Testing

### Run all tests
```bash
pytest tests/test_app.py -v
```

### Test coverage
- 9 tests passing
- Health check, account operations, transactions, analytics

---

## Testing Endpoints

### Using curl (terminal)
```bash
# Health check
curl http://localhost:5000/health

# Create account
curl -X POST http://localhost:5000/api/accounts \
  -H "Content-Type: application/json" \
  -d '{"owner_name": "Alice", "account_type": "checking", "balance": 1000}'

# Deposit
curl -X POST http://localhost:5000/api/accounts/YOUR_ACCOUNT_ID/deposit \
  -H "Content-Type: application/json" \
  -d '{"amount": 250}'

# Get all accounts
curl http://localhost:5000/api/accounts

# Account summary
curl http://localhost:5000/api/accounts/YOUR_ACCOUNT_ID/summary
```

### Using Postman
1. Open [Postman](https://www.postman.com)
2. Create new requests for each endpoint above
3. Set method (GET/POST), URL, and JSON body
4. View responses with transaction_id and duration_ms

---

## Performance Metrics

Each transaction records:
- `transaction_id` — Unique identifier
- `duration_ms` — Operation time (excludes DB commit)
- `timestamp` — When operation occurred
- `status` — "completed", "pending", "failed"

**Note:** `duration_ms` measures app logic only (excludes network latency and DB commit time).

---

## Progress

**Window 2 (Weeks 1-4): Python + Docker**

| Phase | Status | Details |
|-------|--------|---------|
| Day 1 | ✓ Complete | Flask setup, basic endpoints, pytest |
| Day 2 | ✓ Complete | PostgreSQL integration, SQLAlchemy ORM |
| Day 3 | ✓ Complete | Transaction tracking, performance metrics |
| Day 4 | ✓ Complete | Query endpoints, analytics |
| Days 5-8 | → Next | JMeter load testing |
| Days 9-12 | → Next | AI integration |

---

## Next Steps

- Week 2: JMeter load testing (baseline performance)
- Week 3: Containerize with Docker multi-service
- Weeks 4-12: AI test generation, performance evaluation

---

## Author

Nibedita — Performance Engineering & AI Testing