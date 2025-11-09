FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir fastapi uvicorn google-generativeai anthropic openai kubernetes

EXPOSE 8000

CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]
