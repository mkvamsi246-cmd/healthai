# ==========================================
# HealthInsight AI - Production Dockerfile
# ==========================================

FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Set working directory
WORKDIR /app

# Install system dependencies needed for OpenCV, EasyOCR, and building wheels with retries for network resilience
RUN apt-get clean && apt-get update -o Acquire::Retries=3 && apt-get install -y -o Acquire::Retries=3 --no-install-recommends \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files
COPY requirements.txt /app/

# Install python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend files (app, ml, alembic, config files)
COPY app/ /app/app/
COPY ml/ /app/ml/
COPY alembic/ /app/alembic/
COPY alembic.ini /app/
COPY .env.example /app/.env

# Create directories for uploads and reports
RUN mkdir -p /app/uploads /app/generated_reports

# Expose port
EXPOSE 8000

# Command to run database migrations and start Gunicorn with Uvicorn workers
CMD ["sh", "-c", "python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"]
