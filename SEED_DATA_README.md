# Seed Data Script Usage

The database is **automatically seeded on startup** when you run the FastAPI server. No manual command needed!

The `seed_data.py` script creates:

- **3 Batches**: Dhanush, Rakesh, and Gagan
- **Daily Observations**: From November 4, 2025 to December 10, 2025 (37 days)
  - Temperature: 22-30°C (South India weather patterns)
  - Humidity: 60-90% (South India weather patterns)
  - CO2 levels: Based on temperature and humidity
  - Light hours: 10-14 hours per day
- **Harvest Data**: Starting from day 23 (November 27, 2025)
  - Harvests every 4-5 days
  - Yield varies by batch:
    - Dhanush: 1-3 kg per flush
    - Rakesh: 2-4 kg per flush
    - Gagan: 1.5-5 kg per flush
- **Same Spawn Rate**: 5.0% for all batches

## How to Use

### Automatic Seeding (Recommended)

The database is **automatically seeded on startup**. Just start the server:

```bash
uvicorn main:app --reload
```

The server will:
1. Check if seeded batches (Dhanush, Rakesh, Gagan) exist
2. If they don't exist, automatically seed the database
3. If they exist, skip seeding (preserves your data)

**No manual commands needed!** This works in both development and production deployments.

### Manual Re-seeding (Optional)

If you want to clear existing data and re-seed manually:

```bash
python seed_data.py
```

**Note**: The manual script will **delete all existing data** before seeding new data.

### Customizing the Script

To modify the seed data, edit `seed_data.py`:

- **Change batch names**: Modify `batches_config` list
- **Change date range**: Modify `start_date` and `end_date`
- **Change harvest start day**: Modify `harvest_start_day` (currently 23)
- **Change spawn rate**: Modify `spawn_rate` variable
- **Change harvest ranges**: Modify `harvest_ranges` list

## API Endpoints to Access Data

Once seeded, you can access the data using these endpoints:

### Get All Batches (Shows data by default)
```bash
GET http://localhost:8000/api/batches
```

### Get Specific Batch with All Data
```bash
GET http://localhost:8000/api/batches/1
GET http://localhost:8000/api/batches/2
GET http://localhost:8000/api/batches/3
```

### Get Observations for a Batch
```bash
GET http://localhost:8000/api/batches/1/observations
```

### Get Harvests for a Batch
```bash
GET http://localhost:8000/api/batches/1/harvests
```

### Filter by Username
```bash
GET http://localhost:8000/api/batches?username=Dhanush
GET http://localhost:8000/api/batches?username=Rakesh
GET http://localhost:8000/api/batches?username=Gagan
```

## Example Response

When you call `GET /api/batches`, you'll get:

```json
[
  {
    "batch_id": 1,
    "username": "Dhanush",
    "substrate_type": "Straw",
    "substrate_moisture_percent": 65.0,
    "spawn_rate_percent": 5.0,
    "start_date": "2025-11-04",
    "created_at": "2025-11-04T10:00:00",
    "updated_at": "2025-11-04T10:00:00"
  },
  ...
]
```

When you call `GET /api/batches/1`, you'll get the batch with all observations and harvests included.

## Frontend Integration

The API is ready for frontend integration. The CORS is configured to allow all origins, so you can call these endpoints from any frontend application.

Example frontend code (JavaScript):

```javascript
// Get all batches
const response = await fetch('http://localhost:8000/api/batches');
const batches = await response.json();

// Get specific batch with observations and harvests
const batchResponse = await fetch('http://localhost:8000/api/batches/1');
const batch = await batchResponse.json();
```

## Notes

- The script uses realistic South India weather patterns for November-December
- Harvest yields vary based on environmental conditions
- All batches have the same spawn rate (5.0%) as requested
- Harvest amounts vary between batches as requested

