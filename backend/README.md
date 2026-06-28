# HealthInsight AI - Backend API

Production-ready backend for the **HealthInsight AI** platform. Built using Python, FastAPI, MySQL, SQLAlchemy ORM, EasyOCR, pdfplumber, and ReportLab.

---

## Technical Stack
- **Framework**: FastAPI (Asynchronous endpoint routing)
- **Database**: MySQL (PyMySQL driver)
- **ORM & Migrations**: SQLAlchemy & Alembic
- **Document & Text Parsing**: EasyOCR (Scanned Images/PDFs) & pdfplumber (Digital text-based PDFs)
- **Report Generation**: ReportLab (Generates custom patient PDF summaries)
- **ML Integration**: Imports and consumes `predict_health_risk()` from the `ml` package.

---

## Setup Instructions

### 1. Prerequisites
- Python 3.12+
- MySQL Server (Ensure database `healthinsight_ai` exists)

### 2. Installation
Navigate to the `backend/` directory:
```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Variables Configuration
Copy `.env.example` to `.env` and fill in your database credentials:
```bash
copy .env.example .env
```
Ensure `DATABASE_URL` is set correct for your MySQL instance, e.g.:
`mysql+pymysql://<user>:<password>@<host>:<port>/healthinsight_ai`

### 4. Running Database Migrations
Run migrations using Alembic to initialize table structures:
```bash
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```
*(Note: As a fallback, `app/main.py` automatically initializes tables on startup if Alembic migrations are bypassed).*

### 5. Running the Application
Start the Uvicorn server:
```bash
uvicorn app.main:app --reload
```
The server will start on `http://127.0.0.1:8000`.

---

## API Documentation
- **Interactive Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc Alternate Docs**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## Key Endpoint Overview
1. **Authentication (`/api/v1/auth/`)**:
   - `POST /register`: Patient profile registration
   - `POST /login`: Receives JWT Access/Refresh tokens
   - `GET /profile`: Profile lookup
   - `POST /forgot-password`: Simulates recovery
2. **Report Analysis (`/api/v1/reports/`)**:
   - `POST /analyze`: Upload report image/PDF, run OCR, extract values, score risks, save parameters.
   - `POST /compare`: Compare newer report vs. baseline report, calculating deltas and progress summaries.
   - `GET /{id}`: Details lookups.
   - `GET /{id}/download`: Streams formatted clinical PDF report.
3. **Dashboard (`/api/v1/dashboard`)**:
   - `GET`: Pulls latest health scores, current risks list, history, and timeline trend data.
