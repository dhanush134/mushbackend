# Username Field Migration Guide

## Overview

The `username` field has been added to the `batches` table to support multi-user functionality. This allows tracking which user owns each batch.

## Changes Made

### 1. Database Model (`models.py`)
- Added `username` column (String(50), NOT NULL) to Batch model
- Added index on `username` for efficient filtering

### 2. API Schemas (`schemas.py`)
- Added `username` field to `BatchCreate` with validation:
  - Required field
  - Length: 3-50 characters
  - Format: Only letters, numbers, underscores, and hyphens
- Added `username` field to `BatchResponse` and `BatchDetailResponse`

### 3. API Routes (`routes/batches.py`)
- Updated `POST /api/batches` to accept username
- Updated `GET /api/batches` to include username in response
- Added optional `username` query parameter to filter batches: `GET /api/batches?username=john_doe`
- Updated `GET /api/batches/{batch_id}` to include username

## Migration Steps

### For Existing Databases

If you have an existing database with batches, run the migration script:

```bash
python migration_add_username.py
```

This script will:
1. Check if the username column already exists
2. Add the column if it doesn't exist
3. Set default username 'unknown' for existing batches
4. Verify the migration

**Note:** SQLite doesn't support adding NOT NULL columns directly. The column will be nullable in the database, but the application enforces NOT NULL for new batches. You should update existing batches with actual usernames.

### For New Databases

If you're starting fresh, simply delete the existing database file and let SQLAlchemy recreate it:

```bash
# On Windows PowerShell
Remove-Item mushroom_farming.db

# On macOS/Linux
rm mushroom_farming.db
```

Then restart the server - it will create the database with the new schema automatically.

## API Usage Examples

### Create Batch with Username

```bash
curl -X POST "http://localhost:8000/api/batches" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "substrate_type": "Straw",
    "substrate_moisture_percent": 60.0,
    "spawn_rate_percent": 5.0,
    "start_date": "2024-01-15"
  }'
```

### Get All Batches (Filtered by Username)

```bash
# Get all batches
curl "http://localhost:8000/api/batches"

# Get batches for specific user
curl "http://localhost:8000/api/batches?username=john_doe"
```

### Response Format

```json
{
  "batch_id": 1,
  "username": "john_doe",
  "substrate_type": "Straw",
  "substrate_moisture_percent": 60.0,
  "spawn_rate_percent": 5.0,
  "start_date": "2024-01-15",
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-15T10:00:00Z"
}
```

## Username Validation Rules

- **Required**: Yes
- **Min Length**: 3 characters
- **Max Length**: 50 characters
- **Allowed Characters**: Letters (a-z, A-Z), numbers (0-9), underscores (_), and hyphens (-)
- **Whitespace**: Automatically trimmed

### Invalid Usernames (will be rejected):
- `"ab"` (too short)
- `"user name"` (contains space)
- `"user@name"` (contains @)
- `"user.name"` (contains .)

### Valid Usernames:
- `"john_doe"`
- `"user123"`
- `"my-user"`
- `"test_user_2024"`

## Testing Checklist

- [x] Create batch with valid username - should succeed
- [x] Create batch without username - should fail with validation error
- [x] Create batch with invalid username format - should fail with validation error
- [x] Get all batches - should include username in response
- [x] Get single batch - should include username
- [x] Filter batches by username - should return only matching batches
- [x] Migration script runs successfully on existing database

## Backward Compatibility

**Important:** Existing batches will have `username: "unknown"` after migration. You should:

1. Run the migration script
2. Update existing batches with actual usernames (if you have user data)
3. Or keep "unknown" for legacy batches

The application will enforce username validation for all new batches going forward.

## Troubleshooting

### Error: "Username cannot be empty"
- Make sure you're sending the username field in the request body
- Check that the username is not just whitespace

### Error: "Username must be between 3 and 50 characters"
- Username is too short (less than 3 characters) or too long (more than 50 characters)
- Adjust the username length

### Error: "Username can only contain letters, numbers, underscores, and hyphens"
- Username contains invalid characters
- Remove special characters except underscores and hyphens

### Migration Error
- Make sure the database file exists
- Check that you have write permissions
- If migration fails, you may need to manually update the database or recreate it

