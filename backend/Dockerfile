FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend backend
COPY ml ml
COPY edge edge
COPY scripts scripts
COPY simulator simulator
ENV PYTHONPATH=/app
