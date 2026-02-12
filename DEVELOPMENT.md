# Development Guide

## Quick Start

### Using Docker (Recommended)

```bash
# Copy environment variables
cp .env.example .env

# Edit .env with your API keys
# Required: ANTHROPIC_API_KEY
# Optional: GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, APIFY_API_KEY

# Start all services
docker-compose up -d

# Access the application
# Frontend: http://localhost:5173
# Backend: http://localhost:8000/docs
# ML Service: http://localhost:8001/docs
```

### Manual Setup

#### 1. Database Setup
```bash
# Install PostgreSQL 15+
# Create database
createdb trendscout
psql trendscout -c "CREATE EXTENSION vector;"
```

#### 2. Backend Setup
```bash
cd server
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file
cp ../.env.example .env

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

#### 3. ML Service Setup
```bash
cd ml-service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start service
uvicorn app.main:app --reload --port 8001
```

#### 4. Frontend Setup
```bash
cd client
npm install
npm run dev
```

## Project Structure

```
trendscout-clone/
├── client/              # React frontend
│   ├── src/
│   │   ├── components/  # Reusable UI components
│   │   ├── pages/       # Page components
│   │   ├── services/    # API services
│   │   ├── store/       # Zustand state management
│   │   ├── types/       # TypeScript types
│   │   └── lib/         # Utility functions
│   └── package.json
├── server/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # API routes
│   │   ├── models/      # Database models
│   │   ├── services/    # Business logic
│   │   ├── core/        # Config & security
│   │   └── db/          # Database setup
│   └── requirements.txt
├── ml-service/          # ML microservice
│   ├── app/
│   │   ├── services/    # AI & ML services
│   │   └── models/      # ML models
│   └── requirements.txt
└── docker-compose.yml
```

## Key Features

### Authentication
- JWT-based authentication
- Password hashing with bcrypt
- User registration and login
- Protected routes

### Trends Analysis
- Search trending videos by keyword
- Platform filtering (TikTok, YouTube, Instagram)
- Video metadata storage
- Favorites system

### AI Script Generation
- Powered by Anthropic Claude
- Context-aware script generation
- Multiple style options
- Video analysis

### ML Capabilities
- CLIP model for semantic similarity
- Video content analysis
- Engagement prediction
- Competitor tracking

## API Endpoints

### Backend (Port 8000)
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user
- `POST /trends/search` - Search trends
- `GET /trends/videos` - Get trending videos
- `GET /scripts` - Get user scripts
- `GET /favorites` - Get favorites
- `GET /competitors` - Get competitors

### ML Service (Port 8001)
- `POST /generate/script` - Generate AI script
- `POST /analyze/video` - Analyze video
- `POST /similarity` - Compute text similarity
- `POST /find-similar` - Find similar videos

## Testing

### Backend Tests
```bash
cd server
pytest
```

### Frontend Tests
```bash
cd client
npm test
```

## Deployment

### Environment Variables
Required for production:
- `SECRET_KEY` - Strong secret key for JWT
- `DATABASE_URL` - PostgreSQL connection string
- `ANTHROPIC_API_KEY` - Claude API key

Optional:
- `GOOGLE_CLIENT_ID` - For Google OAuth
- `GOOGLE_CLIENT_SECRET` - For Google OAuth
- `APIFY_API_KEY` - For video data scraping

### Docker Deployment
```bash
# Build and deploy
docker-compose -f docker-compose.prod.yml up -d
```

## Troubleshooting

### Database Connection Issues
- Ensure PostgreSQL is running
- Check DATABASE_URL in .env
- Verify pgvector extension is installed

### ML Model Loading Issues
- Models are downloaded on first use
- Ensure sufficient disk space (~500MB)
- Check internet connection

### API Key Issues
- Verify ANTHROPIC_API_KEY is set
- Check API key permissions
- Ensure no extra whitespace in .env

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details
