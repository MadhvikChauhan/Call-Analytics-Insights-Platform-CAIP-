# 📞 Call Analytics & Insights Platform (CAIP)

**CAIP** is a production-ready **FastAPI + SQLAlchemy + Celery** backend for managing and analyzing company call records.  
It supports multi-company access control, asynchronous audio processing, and analytics insights generation.

---

## 🚀 Features

- ✅ Company-level authentication via `X-API-KEY`
- ✅ Async SQLAlchemy + PostgreSQL
- ✅ File uploads (WAV/MP3)
- ✅ Celery background tasks for transcription & NLP simulation
- ✅ Insights and aggregated analytics reports
- ✅ Logging (info, debug, warning, error, exception)
- ✅ Alembic migrations for database schema
- ✅ Docker-ready setup with Redis + Postgres

---

## ⚙️ Installation Steps (From Scratch)

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/MadhvikChauhan/Call-Analytics-Insights-Platform-CAIP-.git
cd Call-Analytics-Insights-Platform-CAIP-
```

### 2️⃣ Create and Activate Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # (Windows: venv\Scripts\activate)
```

### 3️⃣ Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4️⃣ Configure Environment Variables
```bash
cp .env.example .env
```
Example:
```
DEBUG=True
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/caip
REDIS_URL=redis://localhost:6379/0
MEDIA_ROOT=./media
MEDIA_URL=/media/
```

### 5️⃣ Initialize Database (Alembic)
```bash
alembic revision --autogenerate -m "initial migration"
alembic upgrade head
```

### 6️⃣ Start Redis + Celery
```bash
celery -A app.celery_app.celery worker --loglevel=info
```

### 7️⃣ Run FastAPI
```bash
uvicorn app.main:app --reload
```

Server: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 🧪 Test Flow

1. Create a company → get API key  
2. POST `/api/calls/` → upload call  
3. Celery processes audio  
4. GET `/api/calls/{call_id}/insight`  
5. GET `/api/reports/` → analytics  
6. POST `/api/reports/` → regenerate

---

## 🧭 Alembic Commands

```bash
alembic revision --autogenerate -m "create tables"
alembic upgrade head
alembic downgrade -1
```

---

## 🧾 Logging

- Stored at `logs/app.log`
- Levels: debug, info, warning, error, exception

---

## 🧰 Docker Setup

```bash
docker compose up --build
```

---

## ⚠️ Troubleshooting

| Issue | Fix |
|-------|-----|
| DB connection error | Ensure Postgres URL is correct |
| Redis unavailable | Start `redis-server` |
| Module not found | Run from project root |

---

## 💡 Author
Developed by Madhvik Chauhan
