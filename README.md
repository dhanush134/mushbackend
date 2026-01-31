# Mushroom Farming Optimization API

A production-ready RESTful API backend for mushroom farming data management and AI-powered insights. Built with FastAPI, SQLAlchemy, and SQLite.

## Features

- **Batch Management**: Create and track mushroom farming batches with substrate information
- **Daily Observations**: Record environmental conditions (temperature, humidity, CO2, light)
- **Harvest Tracking**: Log flush yields and track total batch performance
- **AI-Powered Insights**: Statistical analysis and pattern detection for optimization recommendations
- **Batch Comparison**: Compare multiple batches to identify best practices

## Technology Stack

- **Framework**: FastAPI
- **Database**: SQLite (local file-based storage)
- **ORM**: SQLAlchemy
- **Validation**: Pydantic
- **AI Insights**: Statistical analysis and pattern detection (no external APIs required)

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file (optional, defaults are provided):
```env
DATABASE_PATH=./mushroom_farming.db
PORT=8000
CORS_ORIGIN=http://localhost:5173
```

3. Run the server:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Batch Endpoints

- `GET /api/batches` - Get all batches (ordered by most recent)
  - Query parameter: `?username=john_doe` - Filter batches by username
- `GET /api/batches/{batch_id}` - Get a single batch with observations and harvests
- `POST /api/batches` - Create a new batch (requires `username` field)

### Observation Endpoints

- `GET /api/batches/{batch_id}/observations` - Get all observations for a batch
- `POST /api/batches/{batch_id}/observations` - Create or update an observation (upsert by date)

### Harvest Endpoints

- `GET /api/batches/{batch_id}/harvests` - Get all harvests for a batch
- `POST /api/batches/{batch_id}/harvests` - Create or update a harvest (upsert by flush_number)

### Insights Endpoints

- `GET /api/batches/{batch_id}/insights` - Generate AI-powered insights for a batch
- `POST /api/batches/compare` - Compare multiple batches

## Database Schema

The database includes three main tables:

- **batches**: Batch information (username, substrate type, moisture, spawn rate, start date)
- **daily_observations**: Daily environmental readings (temperature, humidity, CO2, light)
- **harvests**: Harvest records (flush number, yield, date)

All tables include proper foreign key constraints, unique constraints, and indexes for optimal performance.

### Username Field

The `batches` table includes a `username` field to support multi-user functionality. Usernames must be:
- 3-50 characters long
- Contain only letters, numbers, underscores, and hyphens
- Required for all new batches

See `MIGRATION_GUIDE.md` for details on migrating existing databases.

## AI Insights Features

The insights engine provides:

1. **Pattern Detection**: Compares current batch metrics against historical averages
2. **Anomaly Detection**: Flags sudden changes and prolonged suboptimal conditions
3. **Yield Analysis**: Compares flush yields and projects future performance
4. **Optimization Suggestions**: Actionable recommendations based on successful historical batches
5. **Trend Analysis**: Identifies improving or declining patterns

## Error Handling

The API returns appropriate HTTP status codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request (validation errors)
- `404` - Not Found
- `500` - Internal Server Error

All errors include descriptive JSON messages.

## Development

### Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── database.py          # Database configuration
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── routes/              # API route handlers
│   │   ├── batches.py
│   │   ├── observations.py
│   │   ├── harvests.py
│   │   └── insights.py
│   └── services/            # Business logic
│       └── ai_insights.py
├── requirements.txt
├── .env
└── README.md
```

## Testing

Test the API using the interactive Swagger documentation at `/docs` or use tools like `curl` or Postman.

Example requests:

```bash
# Create a batch
curl -X POST "http://localhost:8000/api/batches" \
  -H "Content-Type: application/json" \
  -d '{
    "substrate_type": "Straw",
    "substrate_moisture_percent": 60.0,
    "spawn_rate_percent": 5.0,
    "start_date": "2024-01-15"
  }'

# Get insights
curl "http://localhost:8000/api/batches/1/insights"
```

## License

MIT
