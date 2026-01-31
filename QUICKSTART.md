# Quick Start Guide

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Step 1: Install Dependencies

Open a terminal in the `backend` directory and run:

```bash
pip install -r requirements.txt
```

If you're using a virtual environment (recommended):

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Configure Environment (Optional)

Create a `.env` file in the `backend` directory (optional - defaults will be used if not created):

```env
DATABASE_PATH=./mushroom_farming.db
PORT=8000
CORS_ORIGIN=http://localhost:5173
```

## Step 3: Run the Server

Start the FastAPI development server:

```bash
uvicorn main:app --reload
```

The `--reload` flag enables auto-reload on code changes (useful for development).

For production, use:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Step 4: Access the API

Once the server is running, you can access:

- **API Base URL**: http://localhost:8000
- **Interactive API Docs (Swagger)**: http://localhost:8000/docs
- **Alternative API Docs (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Testing the API

### Using Swagger UI (Easiest)

1. Go to http://localhost:8000/docs
2. Click on any endpoint to expand it
3. Click "Try it out"
4. Fill in the request body (if needed)
5. Click "Execute"

### Using curl

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

# Get all batches
curl "http://localhost:8000/api/batches"

# Get batch insights
curl "http://localhost:8000/api/batches/1/insights"
```

### Using Python requests

```python
import requests

# Create a batch
response = requests.post("http://localhost:8000/api/batches", json={
    "substrate_type": "Straw",
    "substrate_moisture_percent": 60.0,
    "spawn_rate_percent": 5.0,
    "start_date": "2024-01-15"
})
print(response.json())
```

## Troubleshooting

### Port Already in Use

If port 8000 is already in use, specify a different port:

```bash
uvicorn main:app --reload --port 8001
```

### Database Issues

If you encounter database errors, delete the existing database file and let it recreate:

```bash
# On Windows PowerShell
Remove-Item mushroom_farming.db

# On macOS/Linux
rm mushroom_farming.db
```

Then restart the server - it will create a fresh database.

### Import Errors

Make sure you're running commands from the `backend` directory where `main.py` is located.

### Missing Dependencies

If you get import errors, make sure all dependencies are installed:

```bash
pip install -r requirements.txt
```

## Next Steps

1. Explore the API documentation at `/docs`
2. Create some test batches
3. Add observations and harvests
4. Check out the AI insights feature
5. Compare different batches

