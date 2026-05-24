Markdown
Copy
Code
Preview
<!-- 
  ╔══════════════════════════════════════════════════════════════╗
  ║                    QuickMart API 🛒                         ║
  ║     Production-Grade E-Commerce REST API                   ║
  ╚══════════════════════════════════════════════════════════════╝
-->

<p align="center">
  <img src="https://img.shields.io/badge/Django-5.0-green?logo=django" alt="Django">
  <img src="https://img.shields.io/badge/DRF-3.15-red?logo=django" alt="DRF">
  <img src="https://img.shields.io/badge/Python-3.11-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/PostgreSQL-15-blue?logo=postgresql" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/Redis-7-red?logo=redis" alt="Redis">
  <img src="https://img.shields.io/badge/Docker-Ready-blue?logo=docker" alt="Docker">
</p>

---

## 📖 About

QuickMart is a complete backend API for an e-commerce platform, similar to Amazon or Noon. Built as a portfolio project to demonstrate production-level Django development skills. The system handles the full shopping lifecycle: user registration → product browsing → add to cart → checkout → payment → real-time order tracking.

---

## 🚀 Features

| Feature | Description |
|---------|-------------|
| 🔐 JWT Authentication | Secure login with access/refresh token rotation |
| 👥 Role-Based Permissions | Customer, Seller, and Admin roles with different access |
| 📦 Product Catalog | Full CRUD with filtering, search, pagination, and image uploads |
| 🛒 Shopping Cart | Add, update, remove items with stock validation |
| 📋 Order Management | Complete order lifecycle from pending to delivered |
| 💳 Stripe Payments | Payment intent flow with webhook handling |
| ⚡ Real-Time Tracking | WebSocket-based live order status updates via Django Channels |
| 📧 Async Email Notifications | Order/payment confirmations via Celery background tasks |
| 🚀 Redis Caching | Product list and detail caching for performance |
| 🧪 Test Suite | 38 tests with 77% coverage using pytest |
| 📚 API Documentation | Interactive Swagger UI with try-it-out functionality |
| 🐳 Docker Ready | One-command setup with docker-compose |

---

## 🛠 Tech Stack

| Category | Technology |
|----------|-----------|
| **Backend Framework** | Django 5.0 + Django REST Framework 3.15 |
| **Database** | PostgreSQL 15 |
| **Cache & Queue** | Redis 7 |
| **Task Queue** | Celery 5 |
| **Real-Time** | Django Channels 4 + Daphne (ASGI) |
| **Payments** | Stripe API |
| **Authentication** | JWT via djangorestframework-simplejwt |
| **API Docs** | drf-spectacular (OpenAPI 3 / Swagger) |
| **Testing** | pytest + pytest-django + pytest-cov |
| **Deployment** | Docker + docker-compose |

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
In another terminal, create a superuser:
bash
Copy
docker-compose exec web python manage.py createsuperuser
Visit:
API: http://localhost:8000/api/
Swagger Docs: http://localhost:8000/api/docs/
Admin Panel: http://localhost:8000/admin/
Option 2: Local Setup
Prerequisites: Python 3.11+, PostgreSQL 15, Redis 7
bash
Copy
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
🔐 Authentication Flow
Table
Step	Action	Endpoint	Returns
1	Register	POST /api/auth/register/	{access_token, refresh_token, user}
2	Use token	All requests	Header: Authorization: Bearer <access_token>
3	Token expired	POST /api/auth/token/refresh/	{refresh: <refresh_token>} → new access_token + new refresh_token
4	Logout	POST /api/auth/logout/	{refresh: <refresh_token>} → blacklists the refresh token
💳 Payment Flow
Table
Step	Action	Details
1	Place order	POST /api/orders/checkout/ → Returns: order with order_number
2	Create payment intent	POST /api/payments/create-intent/ → Body: {order_number: "QM-ABC123"} → Returns: {client_secret, publishable_key}
3	Stripe.js	Frontend uses client_secret to collect card → Card details go directly to Stripe (never touch your server)
4	Webhook	Stripe calls POST /api/payments/webhook/ → Order status updated to 'paid' → Confirmation email sent via Celery
Test cards:
✅ Success: 4242 4242 4242 4242
❌ Declined: 4000 0000 0000 0002
💰 No funds: 4000 0000 0000 9995
🧪 Running Tests
bash
Copy
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
📁 Project Structure
plain
Copy
quickmart-api/
│
├── core/                          # Project configuration
│   ├── settings/
│   │   ├── base.py               # Shared settings
│   │   ├── development.py        # Local dev settings
│   │   └── production.py         # Production settings
│   ├── urls.py                   # Main URL routing
│   ├── asgi.py                   # ASGI + WebSocket config
│   └── celery.py                 # Celery configuration
│
├── apps/
│   ├── accounts/                 # User auth & JWT
│   ├── products/                 # Products, categories, reviews
│   ├── orders/                   # Cart, checkout, orders
│   ├── payments/                 # Stripe payment integration
│   └── notifications/            # WebSocket consumers
│
├── Dockerfile                    # Docker image instructions
├── docker-compose.yml            # Multi-container orchestration
├── .env.example                  # Environment variables template
├── requirements.txt              # Python dependencies
└── pytest.ini                    # Test configuration
⚙️ Environment Variables
Copy .env.example to .env and fill in your values:
bash
Copy
cp .env.example .env
Table
Variable	Description	Example
SECRET_KEY	Django secret key	django-insecure-...
DEBUG	Debug mode	True / False
DB_NAME	Database name	quickmart
DB_USER	Database user	postgres
DB_PASSWORD	Database password	yourpassword
DB_HOST	Database host	localhost
REDIS_URL	Redis connection URL	redis://localhost:6379/0
STRIPE_SECRET_KEY	Stripe secret key	sk_test_...
STRIPE_PUBLISHABLE_KEY	Stripe public key	pk_test_...
STRIPE_WEBHOOK_SECRET	Stripe webhook secret	whsec_...
EMAIL_HOST_USER	Email sender	your@gmail.com
EMAIL_HOST_PASSWORD	Email app password	your_app_password
🐳 Docker Commands Reference
bash
Copy
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
📚 API Documentation
Interactive API documentation is available at:
Swagger UI: http://localhost:8000/api/docs/
ReDoc: http://localhost:8000/api/redoc/
Raw Schema: http://localhost:8000/api/schema/
To test authenticated endpoints in Swagger:
Use POST /api/auth/login/ to get a token
Click "Authorize" button (top right)
Enter: Bearer your_access_token
All endpoints now run with your token
🤝 Contributing
Fork the repository
Create your feature branch: git checkout -b feature/my-feature
Commit your changes: git commit -m 'feat: add my feature'
Push to the branch: git push origin feature/my-feature
Open a Pull Request
👨‍💻 Author
Abdelrahman Sayed Tawfik
