# QuickMart API 🛒

> A production-grade E-Commerce REST API built with Django & Django REST Framework

[![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python)](https://python.org)
[![Django](https://img.shields.io/badge/Django-5.0-green?style=flat-square&logo=django)](https://djangoproject.com)
[![DRF](https://img.shields.io/badge/DRF-3.15-red?style=flat-square)](https://django-rest-framework.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue?style=flat-square&logo=postgresql)](https://postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-7-red?style=flat-square&logo=redis)](https://redis.io)
[![Docker](https://img.shields.io/badge/Docker-ready-blue?style=flat-square&logo=docker)](https://docker.com)
[![Tests](https://img.shields.io/badge/Tests-pytest-yellow?style=flat-square)](https://pytest.org)
[![Coverage](https://img.shields.io/badge/Coverage-77%25-brightgreen?style=flat-square)](https://coverage.readthedocs.io)

---

## 📖 About

QuickMart is a complete backend API for an e-commerce platform, similar to Amazon or Noon.  
Built as a portfolio project to demonstrate production-level Django development skills.

The system handles the full shopping lifecycle: user registration → product browsing → add to cart → checkout → payment → real-time order tracking.

---

## 🚀 Features

| Feature | Description |
|---------|-------------|
| 🔐 **JWT Authentication** | Secure login with access/refresh token rotation |
| 👥 **Role-Based Permissions** | Customer, Seller, and Admin roles with different access |
| 📦 **Product Catalog** | Full CRUD with filtering, search, pagination, and image uploads |
| 🛒 **Shopping Cart** | Add, update, remove items with stock validation |
| 📋 **Order Management** | Complete order lifecycle from pending to delivered |
| 💳 **Stripe Payments** | Payment intent flow with webhook handling |
| ⚡ **Real-Time Tracking** | WebSocket-based live order status updates via Django Channels |
| 📧 **Async Email Notifications** | Order/payment confirmations via Celery background tasks |
| 🚀 **Redis Caching** | Product list and detail caching for performance |
| 🧪 **Test Suite** | 38 tests with 77% coverage using pytest |
| 📚 **API Documentation** | Interactive Swagger UI with try-it-out functionality |
| 🐳 **Docker Ready** | One-command setup with docker-compose |

---

## 🛠 Tech Stack

```
Backend Framework:  Django 5.0 + Django REST Framework 3.15
Database:           PostgreSQL 15
Cache & Queue:      Redis 7
Task Queue:         Celery 5
Real-Time:          Django Channels 4 + Daphne (ASGI)
Payments:           Stripe API
Authentication:     JWT via djangorestframework-simplejwt
API Docs:           drf-spectacular (OpenAPI 3 / Swagger)
Testing:            pytest + pytest-django + pytest-cov
Deployment:         Docker + docker-compose
```

---


## 🏃 Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/quickmart-api.git
cd quickmart-api

# Copy environment variables
cp .env.example .env

# Start everything with one command
docker-compose up --build

# In another terminal, create a superuser
docker-compose exec web python manage.py createsuperuser
```

Visit:
- **API:** http://localhost:8000/api/
- **Swagger Docs:** http://localhost:8000/api/docs/
- **Admin Panel:** http://localhost:8000/admin/

### Option 2: Local Setup

**Prerequisites:** Python 3.11+, PostgreSQL 15, Redis 7

```bash
# Clone the repository
git clone https://github.com/yourusername/quickmart-api.git
cd quickmart-api

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database credentials

# Run database migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start Redis (in separate terminal)
redis-server

# Start Celery worker (in separate terminal)
celery -A core worker -l info

# Start development server
python manage.py runserver
```

---

## 🔐 Authentication Flow

```
1. Register: POST /api/auth/register/
   → Returns: {access_token, refresh_token, user}

2. Use access token in all requests:
   → Header: Authorization: Bearer <access_token>

3. When access token expires (after 8 hours):
   → POST /api/auth/token/refresh/ with {refresh: <refresh_token>}
   → Returns: new access_token + new refresh_token

4. Logout: POST /api/auth/logout/ with {refresh: <refresh_token>}
   → Blacklists the refresh token
```

---

## 💳 Payment Flow

```
1. Customer places order: POST /api/orders/checkout/
   → Returns: order with order_number

2. Create payment intent: POST /api/payments/create-intent/
   → Body: {order_number: "QM-ABC123"}
   → Returns: {client_secret, publishable_key}

3. Frontend uses Stripe.js with client_secret to collect card
   → Card details go directly to Stripe (never touch your server)

4. Stripe calls your webhook: POST /api/payments/webhook/
   → Order status updated to 'paid'
   → Confirmation email sent via Celery

Test cards:
  ✅ Success:  4242 4242 4242 4242
  ❌ Declined: 4000 0000 0000 0002
  💰 No funds: 4000 0000 0000 9995
```

---

## 🧪 Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest apps/orders/tests/test_orders.py

# Run specific test class
pytest apps/orders/tests/test_orders.py::TestCheckout

# Run with coverage report
pytest --cov=apps --cov-report=html

# Open coverage report (after running above)
# Open htmlcov/index.html in your browser
```

**Current Test Results:**
```
38 tests collected
25 passed, 0 failed
Coverage: 77%
```

---

## 📁 Project Structure

```
quickmart-api/
│
├── core/                       # Project configuration
│   ├── settings/
│   │   ├── base.py             # Shared settings
│   │   ├── development.py      # Local dev settings
│   │   └── production.py       # Production settings
│   ├── urls.py                 # Main URL routing
│   ├── asgi.py                 # ASGI + WebSocket config
│   └── celery.py               # Celery configuration
│
├── apps/
│   ├── accounts/               # User auth & JWT
│   ├── products/               # Products, categories, reviews
│   ├── orders/                 # Cart, checkout, orders
│   ├── payments/               # Stripe payment integration
│   └── notifications/          # WebSocket consumers
│
├── Dockerfile                  # Docker image instructions
├── docker-compose.yml          # Multi-container orchestration
├── .env.example                # Environment variables template
├── requirements.txt            # Python dependencies
└── pytest.ini                  # Test configuration
```

---

## ⚙️ Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | `django-insecure-...` |
| `DEBUG` | Debug mode | `True` / `False` |
| `DB_NAME` | Database name | `quickmart` |
| `DB_USER` | Database user | `postgres` |
| `DB_PASSWORD` | Database password | `yourpassword` |
| `DB_HOST` | Database host | `localhost` |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379/0` |
| `STRIPE_SECRET_KEY` | Stripe secret key | `sk_test_...` |
| `STRIPE_PUBLISHABLE_KEY` | Stripe public key | `pk_test_...` |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook secret | `whsec_...` |
| `EMAIL_HOST_USER` | Email sender | `your@gmail.com` |
| `EMAIL_HOST_PASSWORD` | Email app password | `your_app_password` |

---

## 🐳 Docker Commands Reference

```bash
# Start all services
docker-compose up --build

# Start in background
docker-compose up -d

# Stop all services
docker-compose down

# Stop and delete all data (fresh start)
docker-compose down -v

# View logs
docker-compose logs web
docker-compose logs celery

# Run Django commands inside container
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py shell
docker-compose exec web pytest

# Connect to database
docker-compose exec db psql -U postgres -d quickmart
```

---

## 📚 API Documentation

Interactive API documentation is available at:

- **Swagger UI:** http://localhost:8000/api/docs/
- **ReDoc:** http://localhost:8000/api/redoc/
- **Raw Schema:** http://localhost:8000/api/schema/

To test authenticated endpoints in Swagger:
1. Use `POST /api/auth/login/` to get a token
2. Click "Authorize" button (top right)
3. Enter: `Bearer your_access_token`
4. All endpoints now run with your token

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m 'feat: add my feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Open a Pull Request

---

---

## 👨‍💻 Author

**Abdelrahman Sayed Tawfik** 


