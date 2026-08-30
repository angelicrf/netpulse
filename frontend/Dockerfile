FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY frontend /app/frontend
COPY backend /app/backend
COPY .env /app/.env

ENV PYTHONPATH=/app

EXPOSE 8501

CMD ["python", "-m", "streamlit", "run", "frontend/streamlit_app.py", "--server.headless=true", "--server.address=0.0.0.0", "--server.port=8501"]
