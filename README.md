# 🚀 AI-Powered Crypto Portfolio Tracker

A full-stack cryptocurrency portfolio management application with real-time price tracking, AI-powered investment insights, and automated portfolio valuation updates.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)
![Redis](https://img.shields.io/badge/Redis-7-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Features

### Core Functionality
- 🔐 **Secure Authentication** - JWT-based authentication with access and refresh tokens
- 💼 **Portfolio Management** - Create and manage multiple crypto portfolios
- 🪙 **Real-Time Pricing** - Live cryptocurrency prices via CoinGecko API
- 📊 **Portfolio Valuation** - Automatic calculation of portfolio value and profit/loss
- 🤖 **AI Investment Insights** - AI-powered analysis using Google Gemini and real-time news
- 📰 **News Integration** - Latest crypto news from NewsAPI
- ⏰ **Background Tasks** - Automated portfolio updates using Celery
- 📈 **Performance Tracking** - Track your investment performance over time

### Technical Features
- 🔄 **Async/Await** - Fully asynchronous backend for high performance
- 📊 **Observability** - Prometheus metrics integration
- 🗄️ **Database Migrations** - Alembic for database version control
- 🔒 **Password Security** - Bcrypt password hashing
- 🌐 **CORS Enabled** - Ready for frontend integration
- 📝 **API Documentation** - Auto-generated Swagger/OpenAPI docs

## 🏗️ Architecture

```
┌─────────────────┐
│   Frontend      │
│  (HTML/CSS/JS)  │
└────────┬────────┘
         │
    ┌────▼─────┐
    │  FastAPI │
    │  Backend │
    └────┬─────┘
         │
┌────────┴──────────┬──────────┬──────────┐
│                   │          │          │
┌───▼───┐  ┌────▼──┐   ┌──▼──────┐ ┌─▼────────┐
│Postgre│  │Redis  │   │CoinGecko│ │  Gemini  │
│  SQL  │  │       │   │   API   │ │   AI     │
└───────┘  └───┬───┘   └─────────┘ └──────────┘
               │
          ┌────▼────┐
          │ Celery  │
          │ Workers │
          └─────────┘
```

## 🛠️ Tech Stack

### Backend
- **Framework:** FastAPI 0.104.1
- **Database:** PostgreSQL 15
- **ORM:** SQLModel
- **Caching:** Redis 7
- **Background Tasks:** Celery 5.3.4
- **Authentication:** JWT (python-jose)
- **Password Hashing:** Bcrypt (passlib)
- **API Clients:** httpx, aiohttp
- **Observability:** Prometheus Client

### Frontend
- **HTML5/CSS3** - Modern, responsive design
- **Vanilla JavaScript** - ES6 modules, async/await
- **No framework** - Lightweight and fast

### External APIs
- **CoinGecko API** - Real-time cryptocurrency prices
- **News API** - Latest crypto news
- **Google Gemini AI** - Investment insights generation

### Infrastructure
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration

## 📋 Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional)
- Node.js (for frontend development server)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/crypto-portfolio-tracker.git
cd crypto-portfolio-tracker
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your API keys
```

### 3. Environment Variables

Create `backend/.env` with:

```env
# Database
DATABASE_URL=postgresql://crypto_user:crypto_password@localhost:5432/crypto_portfolio

# Redis
REDIS_URL=redis://localhost:6379

# JWT
JWT_SECRET_KEY=your-super-secret-key-change-this
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# External APIs
NEWSAPI_KEY=your_newsapi_key
GEMINI_API_KEY=your_gemini_api_key
COINGECKO_API_KEY=optional

# App Settings
DEBUG=true
```

### 4. Database Setup

**Using Docker:**

```bash
docker run --name crypto_postgres -e POSTGRES_DB=crypto_portfolio -e POSTGRES_USER=crypto_user -e POSTGRES_PASSWORD=crypto_password -p 5432:5432 -d postgres:15-alpine

docker run --name crypto_redis -p 6379:6379 -d redis:7-alpine
```

**Or install PostgreSQL and Redis locally**

### 5. Run Database Migrations

```bash
cd backend
alembic upgrade head
```

### 6. Start Backend Server

```bash
uvicorn app.main:app --reload --host localhost --port 8000
```

- Backend will be available at: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### 7. Start Celery Worker (Optional - for background tasks)

In a new terminal:

```bash
cd backend
venv\Scripts\activate  # or source venv/bin/activate
celery -A app.tasks.celery_app worker --loglevel=info --pool=solo
```

### 8. Start Celery Beat Scheduler (Optional)

In another terminal:

```bash
cd backend
venv\Scripts\activate
celery -A app.tasks.celery_app beat --loglevel=info
```

### 9. Start Frontend

```bash
cd frontend
python -m http.server 3000
```

Frontend will be available at: http://localhost:3000

## 📁 Project Structure

```
crypto-portfolio-tracker/
├── backend/
│   ├── app/
│   │   ├── models/           # Database models
│   │   ├── routers/          # API endpoints
│   │   ├── services/         # Business logic
│   │   ├── middleware/       # Custom middleware
│   │   ├── tasks/            # Celery background tasks
│   │   ├── utils/            # Utility functions
│   │   ├── config.py         # Configuration
│   │   ├── database.py       # Database connection
│   │   └── main.py           # FastAPI app
│   ├── alembic/              # Database migrations
│   ├── tests/                # Test files
│   ├── requirements.txt      # Python dependencies
│   └── .env                  # Environment variables
├── frontend/
│   ├── css/                  # Stylesheets
│   ├── js/                   # JavaScript modules
│   ├── assets/               # Images, fonts
│   ├── index.html            # Login page
│   ├── dashboard.html        # Dashboard
│   └── portfolio.html        # Portfolio details
├── docker-compose.yml        # Docker services
└── README.md
```

## 🔑 API Endpoints

### Authentication

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/me` - Get current user info

### Portfolio Management

- `GET /api/portfolio` - List all portfolios
- `POST /api/portfolio` - Create new portfolio
- `GET /api/portfolio/{id}` - Get portfolio details
- `GET /api/portfolio/{id}/holdings` - Get portfolio holdings
- `POST /api/portfolio/{id}/holdings` - Add coin to portfolio
- `GET /api/portfolio/{id}/valuation` - Get portfolio valuation

### Cryptocurrency Data

- `GET /api/coins/search?query={term}` - Search coins
- `GET /api/coins/{coin_id}/price` - Get coin price
- `GET /api/coins/{coin_id}/details` - Get coin details

### AI Insights

- `GET /api/ai/{coin_id}` - Get AI insights for a coin
- `GET /api/ai/portfolio/{portfolio_id}` - Get portfolio analysis

## 🎯 API Keys Setup

### 1. CoinGecko API (Optional - Free tier works without key)

- Visit: https://www.coingecko.com/en/api
- Sign up for free tier
- Add to .env: `COINGECKO_API_KEY=your_key`

### 2. News API (Required for AI insights)

- Visit: https://newsapi.org/register
- Sign up for free account (100 requests/day)
- Add to .env: `NEWSAPI_KEY=your_key`

### 3. Google Gemini API (Required for AI insights)

- Visit: https://aistudio.google.com/app/apikey
- Sign in with Google account
- Create API key (free tier: 60 requests/minute)
- Add to .env: `GEMINI_API_KEY=your_key`

## 🐳 Docker Deployment

### Full Stack with Docker Compose

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f
```

Services will be available at:

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- PostgreSQL: localhost:5432
- Redis: localhost:6379
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001

## 🌐 Deployment

### Render.com (Recommended for Free Tier)

**Backend Deployment:**

1. Create new Web Service
2. Connect GitHub repository
3. Root Directory: `backend`
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables

**Database:**

1. Create PostgreSQL database (free tier)
2. Copy Internal Database URL to backend env

**Frontend:**

1. Create Static Site
2. Publish Directory: `frontend`
3. Update `js/config.js` with backend URL

**Note:** Celery background tasks won't work on Render free tier (requires Redis + worker compute)

## 🧪 Testing

```bash
cd backend
pytest
```

## 📊 Background Tasks

Celery automatically runs these tasks:

- **Every 5 minutes:** Update coin prices cache
- **Every 15 minutes:** Update all portfolio valuations

Manual task trigger:

```python
from app.tasks.portfolio_tasks import update_all_portfolio_values
update_all_portfolio_values.delay()
```

## 🔐 Security Features

- Password hashing with bcrypt (12 rounds)
- JWT token-based authentication
- Access token expires in 30 minutes
- Refresh token expires in 7 days
- SQL injection protection (SQLModel/SQLAlchemy)
- CORS configuration
- Environment variable management

## 📈 Monitoring

Access Prometheus metrics at: http://localhost:8000/metrics

Available metrics:

- `http_requests_total` - Total HTTP requests
- `http_request_duration_seconds` - Request latency
- Custom portfolio metrics (when configured)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👤 Author

**Your Name**

- GitHub: [@your-username](https://github.com/your-username)
- LinkedIn: [Your Name](https://linkedin.com/in/your-profile)

## 🙏 Acknowledgments

- CoinGecko for cryptocurrency data
- Google Gemini AI for intelligent insights
- News API for cryptocurrency news
- FastAPI framework
- The open-source community

## 📞 Support

For support, email your-email@example.com or open an issue in the repository.

## 🗺️ Roadmap

- [ ] Mobile app (React Native)
- [ ] Price alerts via email/SMS
- [ ] Advanced charting and analytics
- [ ] Social features (share portfolios)
- [ ] Multi-currency support
- [ ] Tax reporting
- [ ] Hardware wallet integration
- [ ] DeFi protocol integration

---

⭐ **Star this repo if you find it helpful!**

Made with ❤️ using FastAPI and Modern Web Technologies
