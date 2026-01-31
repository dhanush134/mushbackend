from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from database import get_db
import models
import schemas

router = APIRouter(prefix="/api/batches", tags=["observations"])


@router.get("/{batch_id}/observations", response_model=List[schemas.ObservationResponse])
def get_observations(batch_id: int, db: Session = Depends(get_db)):
    """Get all observations for a batch, ordered by date (newest first)"""
    # Verify batch exists
    batch = db.query(models.Batch).filter(models.Batch.batch_id == batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch with id {batch_id} not found"
        )
    
    observations = db.query(models.DailyObservation)\
        .filter(models.DailyObservation.batch_id == batch_id)\
        .order_by(desc(models.DailyObservation.date)).all()
    
    return observations


@router.post("/{batch_id}/observations", response_model=schemas.ObservationResponse, status_code=status.HTTP_201_CREATED)
def create_or_update_observation(batch_id: int, obs: schemas.ObservationCreate, db: Session = Depends(get_db)):
    """Create a new daily observation. If an observation for the same date already exists, update it instead."""
    # Verify batch exists
    batch = db.query(models.Batch).filter(models.Batch.batch_id == batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch with id {batch_id} not found"
        )
    
    try:
        # Check if observation for this date already exists
        existing_obs = db.query(models.DailyObservation)\
            .filter(
                models.DailyObservation.batch_id == batch_id,
                models.DailyObservation.date == obs.date
            ).first()
        
        if existing_obs:
            # Update existing observation
            for key, value in obs.dict(exclude_unset=True).items():
                setattr(existing_obs, key, value)
            db.commit()
            db.refresh(existing_obs)
            return existing_obs
        else:
            # Create new observation
            db_obs = models.DailyObservation(batch_id=batch_id, **obs.dict())
            db.add(db_obs)
            db.commit()
            db.refresh(db_obs)
            return db_obs
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating/updating observation: {str(e)}"
        )

