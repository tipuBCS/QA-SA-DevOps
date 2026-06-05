# QA-SA-DevOps

Room Booker API — a serverless room booking system built with AWS Lambda, DynamoDB, and API Gateway.

## Getting Started

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- AWS credentials configured (`aws configure` or environment variables)

### Environment Setup

Before running the API or tests, create your `.env` file:

```bash
cd api
cp .env.example .env
```

Then edit `.env` with your values. See [`api/.env.example`](api/.env.example) for all available variables and their descriptions.

#### Required Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `API_URL` | Base URL of your deployed API (for integration tests) | — |
| `TEST_ADMIN_EMAIL` | Admin email for seeding & integration tests | — |
| `TEST_ADMIN_PASSWORD` | Admin password for seeding & integration tests | — |

#### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_TABLE_NAME` | DynamoDB table name | `room-booker` |
| `JWT_SECRET` | Secret key for signing JWT tokens | `dev-secret-change-in-production` |
| `JWT_EXPIRY_HOURS` | Token expiry duration in hours | `1` |
| `AWS_REGION` | AWS region for DynamoDB | `eu-west-2` |

> **Important:** Change `JWT_SECRET` to a strong, unique value for any non-local environment.

### Seed Admin User

After deploying the stack and setting up `.env`:

```bash
cd api
uv run python scripts/seed_admin.py
```

### Run Unit Tests

```bash
cd api
uv run pytest tests/ -v --ignore=tests/integration
```

### Run Integration Tests

Requires a deployed API and seeded admin user:

```bash
cd api
uv run pytest tests/integration/ -v
```
