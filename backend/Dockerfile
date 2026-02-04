# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# Final stage
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for Playwright and Xvfb
RUN apt-get update && apt-get install -y \
    curl \
    xvfb \
    libxi6 \
    && pip install --no-cache-dir playwright \
    && playwright install-deps chromium \
    && playwright install chromium \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . .
RUN chmod +x entrypoint.sh

# Ensure data directory exists for SQLite
RUN mkdir -p data

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV HEADLESS=false
ENV API_HOST=0.0.0.0
ENV API_PORT=8000
ENV DISPLAY=:99

EXPOSE 8000

CMD ["./entrypoint.sh"]
