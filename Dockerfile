FROM python:3.10
WORKDIR /app
COPY requirements-locked.txt .
RUN pip install --no-cache-dir -r requirements-locked.txt
COPY . .
COPY secure-keys/sa-key.json /app/secure-keys/sa-key.json
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/secure-keys/sa-key.json
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]