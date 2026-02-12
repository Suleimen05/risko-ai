# Quick Start Guide

Get TrendScout running in 5 minutes!

## Prerequisites

- [Docker](https://www.docker.com/get-started) & Docker Compose
- [Git](https://git-scm.com/)
- API Keys (at minimum, you need an [Anthropic API key](https://console.anthropic.com/))

## Step 1: Clone & Setup

```bash
# Navigate to project directory
cd trendscout-clone

# Copy environment template
cp .env.example .env
```

## Step 2: Configure API Keys

Edit the `.env` file and add your keys:

```env
# Required
ANTHROPIC_API_KEY=sk-ant-...

# Optional (can be added later)
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
APIFY_API_KEY=your-apify-key
```

## Step 3: Launch

```bash
# Start all services
docker-compose up -d

# Wait 30 seconds for services to initialize
```

## Step 4: Access

Open your browser:

- **Frontend**: [http://localhost:5173](http://localhost:5173)
- **Backend API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ML Service Docs**: [http://localhost:8001/docs](http://localhost:8001/docs)

## Step 5: Create Account

1. Go to http://localhost:5173
2. Click "Sign Up"
3. Enter your details
4. Start exploring trends!

## Common Issues

### Ports Already in Use

If you see "port already allocated" errors:

```bash
# Check what's using the ports
# Windows:
netstat -ano | findstr :5173
netstat -ano | findstr :8000
netstat -ano | findstr :8001

# macOS/Linux:
lsof -i :5173
lsof -i :8000
lsof -i :8001

# Either stop those services or change ports in docker-compose.yml
```

### Services Won't Start

```bash
# Check logs
docker-compose logs

# Restart services
docker-compose down
docker-compose up -d
```

### Database Issues

```bash
# Reset database
docker-compose down -v
docker-compose up -d
```

## Manual Setup (Without Docker)

If you prefer to run services individually:

### Terminal 1 - Database
```bash
# Start PostgreSQL (must be installed)
# Create database
createdb trendscout
psql trendscout -c "CREATE EXTENSION vector;"
```

### Terminal 2 - Backend
```bash
cd server
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Terminal 3 - ML Service
```bash
cd ml-service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

### Terminal 4 - Frontend
```bash
cd client
npm install
npm run dev
```

## Next Steps

- Explore the [Development Guide](DEVELOPMENT.md) for detailed information
- Check [README.md](README.md) for architecture details
- Review API documentation at http://localhost:8000/docs

## Getting Help

- **Issues**: Check existing GitHub issues
- **Documentation**: See DEVELOPMENT.md
- **API Docs**: http://localhost:8000/docs

---

Happy trending! 🚀
