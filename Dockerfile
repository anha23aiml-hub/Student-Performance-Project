
FROM python:3.11-slim

WORKDIR /app

COPY requirements-api.txt .
RUN python -m pip install --upgrade pip && python -m pip install --no-cache-dir --index-url https://pypi.org/simple --retries 10 --timeout 180 -r requirements-api.txt

COPY api/ ./api/
COPY model_export/ ./model_export/

EXPOSE 8000

CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]
