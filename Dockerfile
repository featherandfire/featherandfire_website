FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN SECRET_KEY=build-only python manage.py collectstatic --noinput

EXPOSE 8080

CMD sh -c "python manage.py migrate --noinput && python manage.py bootstrap_admin && gunicorn config.wsgi:application --bind 0.0.0.0:8080 --workers 3 --timeout 120 --access-logfile -"
