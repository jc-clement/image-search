FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin/uvicorn /usr/local/bin/uvicorn
COPY src/ .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
