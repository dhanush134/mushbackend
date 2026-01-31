
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Batch(Base):
    __tablename__ = "batches"
    batch_id = Column(Integer, primary_key=True, index=True)
    substrate_type = Column(String)
    substrate_moisture_percent = Column(Float)
    spawn_rate_percent = Column(Float)
    start_date = Column(Date)

    observations = relationship("DailyObservation", back_populates="batch")
    harvests = relationship("Harvest", back_populates="batch")

class DailyObservation(Base):
    __tablename__ = "observations"
    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("batches.batch_id"))
    date = Column(Date)
    ambient_temperature_celsius = Column(Float)
    relative_humidity_percent = Column(Float)
    CO2_level = Column(String)
    light_hours_per_day = Column(Float)

    batch = relationship("Batch", back_populates="observations")

class Harvest(Base):
    __tablename__ = "harvests"
    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("batches.batch_id"))
    flush_number = Column(Integer)
    flush_yield_kg = Column(Float)
    total_batch_yield_kg = Column(Float)

    batch = relationship("Batch", back_populates="harvests")
