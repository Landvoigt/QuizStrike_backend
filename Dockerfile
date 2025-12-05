FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    nano \
    sqlite3 \
    gettext \
    --no-install-recommends \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY entrypoint.sh /app/entrypoint.sh
RUN sed -i 's/\r$//' /app/entrypoint.sh && chmod +x /app/entrypoint.sh

COPY . .

ENV DJANGO_SETTINGS_MODULE=quizstrike.settings
ENV PYTHONUNBUFFERED=1
ENV DEBUG=False

ENTRYPOINT ["/app/entrypoint.sh"]
