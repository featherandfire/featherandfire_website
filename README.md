Layer	Technology
Framework	Django 5.2
Auth	django-allauth (email/password + social account ready)
Auth backends	Django ModelBackend + allauth AuthenticationBackend
Session	Django sessions (expires on browser close)
Payments	Stripe (Checkout + webhooks)
Database	SQLite (via file volume)
Static files	WhiteNoise (served directly from Django)
Media files	Local filesystem (/media)
Email	SMTP (configurable via env)
App server	Gunicorn (3 workers)
Container	Docker + Docker Compose
Process manager	Docker (single container)
