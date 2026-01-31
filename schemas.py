
from pydantic import BaseModel
from datetime import date

class BatchCreate(BaseModel):
    substrate_type: str
    substrate_moisture_percent: float
    spawn_rate_percent: float
    start_date: date

class ObservationCreate(BaseModel):
    date: date
    ambient_temperature_celsius: float
    relative_humidity_percent: float
    CO2_level: str
    light_hours_per_day: float

class HarvestCreate(BaseModel):
    flush_number: int
    flush_yield_kg: float
    total_batch_yield_kg: float
