from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from database import get_db
import models
import schemas

router = APIRouter(prefix="/api/batches", tags=["batches"])


@router.get("", response_model=List[schemas.BatchResponse])
def get_all_batches(
    username: Optional[str] = Query(None, description="Filter batches by username"),
    db: Session = Depends(get_db)
):
    """Get all batches ordered by most recent first. Optionally filter by username."""
    query = db.query(models.Batch)
    
    if username:
        query = query.filter(models.Batch.username == username)
    
    batches = query.order_by(desc(models.Batch.created_at)).all()
    return batches


@router.get("/{batch_id}", response_model=schemas.BatchDetailResponse)
def get_batch(batch_id: int, db: Session = Depends(get_db)):
    """Get a single batch with all related observations and harvests"""
    batch = db.query(models.Batch).filter(models.Batch.batch_id == batch_id).first()
    
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch with id {batch_id} not found"
        )
    
    # Load observations and harvests (ordered)
    observations = db.query(models.DailyObservation)\
        .filter(models.DailyObservation.batch_id == batch_id)\
        .order_by(desc(models.DailyObservation.date)).all()
    
    harvests = db.query(models.Harvest)\
        .filter(models.Harvest.batch_id == batch_id)\
        .order_by(models.Harvest.flush_number).all()
    
    # Use Pydantic's model_validate for proper conversion
    # Create a dict with all batch data including relationships
    batch_dict = {
        "batch_id": batch.batch_id,
        "username": batch.username,
        "substrate_type": batch.substrate_type,
        "substrate_moisture_percent": batch.substrate_moisture_percent,
        "spawn_rate_percent": batch.spawn_rate_percent,
        "start_date": batch.start_date,
        "created_at": batch.created_at,
        "updated_at": batch.updated_at,
        "observations": observations,
        "harvests": harvests
    }
    
    # Use model_validate for Pydantic v2 compatibility
    return schemas.BatchDetailResponse.model_validate(batch_dict)


@router.post("", response_model=schemas.BatchResponse, status_code=status.HTTP_201_CREATED)
def create_batch(batch: schemas.BatchCreate, db: Session = Depends(get_db)):
    """Create a new batch"""
    try:
        db_batch = models.Batch(**batch.dict())
        db.add(db_batch)
        db.commit()
        db.refresh(db_batch)
        return db_batch
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating batch: {str(e)}"
        )

