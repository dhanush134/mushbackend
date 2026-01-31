
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models, schemas
import os
from ai_insights import generate_insights
from fastapi.middleware.cors import CORSMiddleware


models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mushroom Farming AI")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # OK for now, tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/batches")
def create_batch(batch: schemas.BatchCreate, db: Session = Depends(get_db)):
    b = models.Batch(**batch.dict())
    db.add(b)
    db.commit()
    db.refresh(b)
    return b

@app.get("/batches")
def list_batches(db: Session = Depends(get_db)):
    return db.query(models.Batch).all()

@app.post("/batches/{batch_id}/observations")
def add_observation(batch_id: int, obs: schemas.ObservationCreate, db: Session = Depends(get_db)):
    o = models.DailyObservation(batch_id=batch_id, **obs.dict())
    db.add(o)
    db.commit()
    return o

@app.post("/batches/{batch_id}/harvests")
def add_harvest(batch_id: int, h: schemas.HarvestCreate, db: Session = Depends(get_db)):
    hv = models.Harvest(batch_id=batch_id, **h.dict())
    db.add(hv)
    db.commit()
    return hv

@app.get("/batches/{batch_id}/insights")
def get_insights(batch_id: int, db: Session = Depends(get_db)):
    obs = db.query(models.DailyObservation).filter_by(batch_id=batch_id).all()
    harv = db.query(models.Harvest).filter_by(batch_id=batch_id).all()

    obs_data = [o.__dict__ for o in obs]
    harv_data = [h.__dict__ for h in harv]

    return generate_insights(obs_data, harv_data)
