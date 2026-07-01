# CuraSuite

**Healthcare Technology That Helps Your Practice Grow**

PhoenixRise Interactive Pvt. Ltd. | CuraSuite Ecosystem

---

## Quick Start

### Prerequisites
- Python 3.13+
- PostgreSQL 17+
- Redis 7+
- Docker Desktop (recommended)

### With Docker (recommended)

```bash
# 1. Clone the repository
git clone <repo-url> curasuite
cd curasuite

# 2. Configure environment
cp .env.example .env
# Edit .env with your values

# 3. Start services
docker compose up -d

# 4. Run migrations
docker compose exec web python manage.py migrate

# 5. Create superuser
docker compose exec web python manage.py createsuperuser

# 6. Visit http://localhost:8000
```

### Without Docker

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements-dev.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your local PostgreSQL and Redis credentials

# 4. Run migrations
python manage.py migrate

# 5. Create superuser
python manage.py createsuperuser

# 6. Run development server
python manage.py runserver
```

---

## Project Structure

```
curasuite/
├── config/                  # Django project config
│   ├── settings/
│   │   ├── base.py         # Shared settings
│   │   ├── development.py  # Local dev overrides
│   │   ├── staging.py      # Staging overrides
│   │   └── production.py   # Production (hardened)
│   ├── urls.py             # Root URL config
│   ├── wsgi.py             # WSGI entry point
│   └── celery.py           # Celery config
│
├── apps/                   # Django applications (one per domain)
│   ├── accounts/           # Custom User model, auth
│   ├── core/               # Base models, shared utilities
│   ├── cms/                # Page management
│   ├── blogs/              # Blog engine
│   ├── seo/                # SEO metadata, sitemap, redirects
│   ├── media/              # Media library
│   ├── products/           # Product catalog (CuraCMS, CuraLabs, CuraSuite)
│   ├── crm/                # Lead capture and pipeline
│   ├── forms/              # Form builder
│   ├── newsletter/         # Email campaigns
│   ├── integrations/       # External API integrations
│   └── ...
│
├── templates/              # Django templates
│   ├── base/               # Base layout templates
│   └── components/         # Reusable UI components
│
├── static/                 # Static assets
│   ├── css/
│   │   ├── tokens.css      # CuraSuite Design Tokens
│   │   └── base.css        # Reset, typography, utilities
│   └── js/
│       └── main.js         # Core JS (HTMX config, toast)
│
└── docs/                   # Technical documentation
```

---

## Tech Stack

| Layer       | Technology                          |
|-------------|-------------------------------------|
| Backend     | Python 3.13, Django 5.x             |
| Database    | PostgreSQL 17+                      |
| Cache/Queue | Redis 7, Celery                     |
| Frontend    | Django Templates, HTMX, Alpine.js   |
| Auth        | Email+Password, Argon2 hashing      |
| Deployment  | Docker, Gunicorn, NGINX, Cloudflare |

---

## Development Guidelines

- Business logic → `services.py`
- Read/query logic → `selectors.py`
- Domain validation → `validators.py`
- Background jobs → `tasks.py`
- Views stay thin — orchestrate only

See the [Engineering Standards](docs/) for full coding conventions.
