from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import models
import schemas
from services import ai_insights

router = APIRouter(prefix="/api/batches", tags=["insights"])


@router.get("/{batch_id}/insights", response_model=schemas.InsightsResponse)
def get_batch_insights(batch_id: int, db: Session = Depends(get_db)):
    """Generate AI-powered insights for a batch based on patterns, anomalies, and trends"""
    # Verify batch exists
    batch = db.query(models.Batch).filter(models.Batch.batch_id == batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch with id {batch_id} not found"
        )
    
    return ai_insights.generate_insights(batch_id, db)


@router.post("/compare", response_model=schemas.BatchComparisonResponse)
def compare_batches(request: schemas.BatchComparisonRequest, db: Session = Depends(get_db)):
    """Compare multiple batches and provide comparative insights"""
    if len(request.batch_ids) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least 2 batch IDs are required for comparison"
        )
    
    return ai_insights.compare_batches(request.batch_ids, db)

