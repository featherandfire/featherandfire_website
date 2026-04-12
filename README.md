| Layer | Technology |
|---|---|
| Framework | Django 5.2 |
| Auth | django-allauth (email/password + social ready) |
| Session | Django sessions (expires on browser close) |
| Payments | Stripe (Checkout + webhooks) |
| Database | SQLite (file volume) |
| Static files | WhiteNoise |
| Media files | Local filesystem (/media) |
| Email | SMTP |
| Reverse proxy | Caddy (auto-TLS) |
| WSGI server | Gunicorn (3 workers) |
| Container | Docker + Docker Compose |
| Process manager | Docker (single container) |
