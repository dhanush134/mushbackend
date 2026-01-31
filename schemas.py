from pydantic import BaseModel, Field, validator
from datetime import date, datetime
from typing import Optional, List
import re


# Batch Schemas
class BatchCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    substrate_type: str = Field(..., min_length=1, max_length=100)
    substrate_moisture_percent: float = Field(..., ge=0, le=100)
    spawn_rate_percent: float = Field(..., ge=0, le=100)
    start_date: date

    @validator('username')
    def validate_username(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Username cannot be empty')
        v = v.strip()
        if len(v) < 3 or len(v) > 50:
            raise ValueError('Username must be between 3 and 50 characters')
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username can only contain letters, numbers, underscores, and hyphens')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "substrate_type": "Straw",
                "substrate_moisture_percent": 60.0,
                "spawn_rate_percent": 5.0,
                "start_date": "2024-01-15"
            }
        }


class BatchResponse(BaseModel):
    batch_id: int
    username: str
    substrate_type: str
    substrate_moisture_percent: float
    spawn_rate_percent: float
    start_date: date
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BatchDetailResponse(BatchResponse):
    observations: List['ObservationResponse'] = []
    harvests: List['HarvestResponse'] = []

    class Config:
        from_attributes = True
        # Allow forward references
        populate_by_name = True


# Observation Schemas
class ObservationCreate(BaseModel):
    date: date
    ambient_temperature_celsius: Optional[float] = Field(None, ge=-10, le=50)
    relative_humidity_percent: Optional[float] = Field(None, ge=0, le=100)
    CO2_level: Optional[str] = None
    light_hours_per_day: Optional[float] = Field(None, ge=0, le=24)

    @validator('CO2_level')
    def validate_co2_level(cls, v):
        if v is not None and v not in ['low', 'medium', 'high']:
            raise ValueError("CO2_level must be 'low', 'medium', or 'high'")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "date": "2024-01-16",
                "ambient_temperature_celsius": 22.5,
                "relative_humidity_percent": 85.0,
                "CO2_level": "medium",
                "light_hours_per_day": 12.0
            }
        }


class ObservationResponse(BaseModel):
    observation_id: int
    batch_id: int
    date: date
    ambient_temperature_celsius: Optional[float]
    relative_humidity_percent: Optional[float]
    CO2_level: Optional[str]
    light_hours_per_day: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


# Harvest Schemas
class HarvestCreate(BaseModel):
    flush_number: int = Field(..., ge=1)
    flush_yield_kg: float = Field(..., ge=0)
    total_batch_yield_kg: Optional[float] = Field(None, ge=0)
    date: Optional[date] = None

    class Config:
        json_schema_extra = {
            "example": {
                "flush_number": 1,
                "flush_yield_kg": 2.5,
                "total_batch_yield_kg": 2.5,
                "date": "2024-01-20"
            }
        }


class HarvestResponse(BaseModel):
    harvest_id: int
    batch_id: int
    flush_number: int
    flush_yield_kg: float
    total_batch_yield_kg: Optional[float]
    date: date
    created_at: datetime

    class Config:
        from_attributes = True


# AI Insights Schemas
class InsightsResponse(BaseModel):
    warnings: List[str]
    anomalies: List[str]
    suggestions: List[str]
    trends: List[str]
    summary: str


# Batch Comparison Schemas
class BatchComparisonRequest(BaseModel):
    batch_ids: List[int] = Field(..., min_items=2)

    class Config:
        json_schema_extra = {
            "example": {
                "batch_ids": [1, 2, 3]
            }
        }


class YieldComparison(BaseModel):
    batch_id: int
    total_yield: float
    flushes: int


class AverageConditions(BaseModel):
    batch_id: int
    avg_temperature: Optional[float]
    avg_humidity: Optional[float]
    substrate_type: str


class BatchComparisonResponse(BaseModel):
    yield_comparison: List[YieldComparison]
    average_conditions: List[AverageConditions]
    insights: List[str]


# Update forward references for Pydantic v2 compatibility
# This ensures forward references in BatchDetailResponse are resolved
try:
    BatchDetailResponse.model_rebuild()
except Exception:
    # If model_rebuild fails (Pydantic v1), it's okay - forward refs will be resolved at runtime
    pass
