# Trade Copilot

Trade intelligence platform with a FastAPI backend and a Next.js frontend.

## Requirements

- Python 3.13
- Node.js and npm
- PostgreSQL

## Configure the backend

Create `backend\.env` and set your local database credentials:

```env
DATABASE_URL=postgresql+psycopg2://<user>:<password>@localhost:5432/tradecopilot
JWT_SECRET=<a-long-random-secret>
```

Use the PostgreSQL username, password, and database configured on your machine.
Do not commit `.env` files or real credentials.

In PowerShell, install and run the backend:

```powershell
cd backend
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

The API documentation is available at `http://127.0.0.1:8000/docs`.

## Run the frontend

In a second PowerShell window:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`. The frontend's local API URL is configured in
`frontend\.env.local`. Create that file with:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```