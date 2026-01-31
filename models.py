from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, CheckConstraint, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Batch(Base):
    __tablename__ = "batches"
    
    batch_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    username = Column(String(50), nullable=False)
    substrate_type = Column(String, nullable=False)
    substrate_moisture_percent = Column(Float, nullable=False)
    spawn_rate_percent = Column(Float, nullable=False)
    start_date = Column(Date, nullable=False)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    observations = relationship("DailyObservation", back_populates="batch", cascade="all, delete-orphan")
    harvests = relationship("Harvest", back_populates="batch", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_batches_start_date', 'start_date'),
        Index('idx_batches_username', 'username'),
    )


class DailyObservation(Base):
    __tablename__ = "daily_observations"
    
    observation_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    batch_id = Column(Integer, ForeignKey("batches.batch_id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    ambient_temperature_celsius = Column(Float)
    relative_humidity_percent = Column(Float)
    CO2_level = Column(String, CheckConstraint("CO2_level IN ('low', 'medium', 'high')"))
    light_hours_per_day = Column(Float)
    created_at = Column(DateTime, server_default=func.current_timestamp())

    batch = relationship("Batch", back_populates="observations")
    
    __table_args__ = (
        UniqueConstraint('batch_id', 'date', name='uq_batch_date'),
        Index('idx_observations_batch_date', 'batch_id', 'date'),
    )


class Harvest(Base):
    __tablename__ = "harvests"
    
    harvest_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    batch_id = Column(Integer, ForeignKey("batches.batch_id", ondelete="CASCADE"), nullable=False)
    flush_number = Column(Integer, nullable=False)
    flush_yield_kg = Column(Float, nullable=False)
    total_batch_yield_kg = Column(Float)
    date = Column(Date, server_default=func.current_date())
    created_at = Column(DateTime, server_default=func.current_timestamp())

    batch = relationship("Batch", back_populates="harvests")
    
    __table_args__ = (
        UniqueConstraint('batch_id', 'flush_number', name='uq_batch_flush'),
        Index('idx_harvests_batch_id', 'batch_id'),
    )
