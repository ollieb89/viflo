# Minimal App Template

> Simplest possible full-stack app with Next.js + FastAPI + PostgreSQL

## Quick Start

```bash
# Start all services
docker-compose up

# Access the app
open http://localhost:3000

# API docs
open http://localhost:8000/docs
```

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Frontend   │────▶│   Backend   │────▶│  PostgreSQL │
│  Next.js    │     │   FastAPI   │     │             │
│  :3000      │     │   :8000     │     │   :5432     │
└─────────────┘     └─────────────┘     └─────────────┘
```

## What's Included

### Backend (`backend/`)

- Single `Item` model (id, name, description, completed)
- Full CRUD API at `/items`
- Auto-created database tables
- CORS enabled for frontend

### Frontend (`frontend/`)

- Single page app
- List items with checkbox for completion
- Form to create new items
- Delete button for each item
- No styling framework (plain CSS)

### E2E Tests (`e2e/`)

- 4 test cases covering CRUD operations
- Playwright configuration

## API Endpoints

| Method | Endpoint      | Description     |
| ------ | ------------- | --------------- |
| GET    | `/`           | Health check    |
| GET    | `/items`      | List all items  |
| POST   | `/items`      | Create item     |
| GET    | `/items/{id}` | Get single item |
| PATCH  | `/items/{id}` | Update item     |
| DELETE | `/items/{id}` | Delete item     |

## Development

### Backend Only

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Only

```bash
cd frontend
npm install
npm run dev
```

### Run E2E Tests

```bash
cd e2e
npm install
npx playwright install
npx playwright test
```

## Customization

1. **Add more fields**: Edit `backend/main.py` Item model
2. **Add authentication**: See backend-dev-guidelines skill
3. **Add styling**: Install Tailwind or MUI in frontend
4. **Add pagination**: Extend list endpoint with skip/limit

## Tech Stack

- **Frontend**: Next.js 14, React 18, TypeScript
- **Backend**: FastAPI, SQLAlchemy, Pydantic
- **Database**: PostgreSQL 16
- **E2E**: Playwright

## Production Notes

Before production:

- Use proper environment variables (not hardcoded)
- Add authentication
- Use migrations (Alembic) instead of `create_all`
- Add proper error handling
- Configure logging
- Use HTTPS
