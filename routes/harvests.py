from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import models
import schemas

router = APIRouter(prefix="/api/batches", tags=["harvests"])


@router.get("/{batch_id}/harvests", response_model=List[schemas.HarvestResponse])
def get_harvests(batch_id: int, db: Session = Depends(get_db)):
    """Get all harvests for a batch, ordered by flush_number"""
    # Verify batch exists
    batch = db.query(models.Batch).filter(models.Batch.batch_id == batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch with id {batch_id} not found"
        )
    
    harvests = db.query(models.Harvest)\
        .filter(models.Harvest.batch_id == batch_id)\
        .order_by(models.Harvest.flush_number).all()
    
    return harvests


@router.post("/{batch_id}/harvests", response_model=schemas.HarvestResponse, status_code=status.HTTP_201_CREATED)
def create_or_update_harvest(batch_id: int, harvest: schemas.HarvestCreate, db: Session = Depends(get_db)):
    """Create a new harvest record. If a harvest with the same flush_number exists, update it."""
    # Verify batch exists
    batch = db.query(models.Batch).filter(models.Batch.batch_id == batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch with id {batch_id} not found"
        )
    
    try:
        # Check if harvest for this flush_number already exists
        existing_harvest = db.query(models.Harvest)\
            .filter(
                models.Harvest.batch_id == batch_id,
                models.Harvest.flush_number == harvest.flush_number
            ).first()
        
        if existing_harvest:
            # Update existing harvest
            for key, value in harvest.dict(exclude_unset=True).items():
                setattr(existing_harvest, key, value)
            db.commit()
            db.refresh(existing_harvest)
            return existing_harvest
        else:
            # Create new harvest
            harvest_data = harvest.dict()
            db_harvest = models.Harvest(batch_id=batch_id, **harvest_data)
            db.add(db_harvest)
            db.commit()
            db.refresh(db_harvest)
            return db_harvest
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating/updating harvest: {str(e)}"
        )

