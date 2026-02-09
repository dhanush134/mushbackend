"""
Seed script to populate database with hardcoded mushroom farming data.
This script creates 3 batches (Dhanush, Rakesh, Gagan) with observations
from Nov 4, 2025 to Dec 10, 2025 and harvest data starting from day 23.
"""
import random
from datetime import date, timedelta
from typing import Tuple
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models

# Initialize database tables
models.Base.metadata.create_all(bind=engine)


def get_south_india_weather(day_offset: int) -> Tuple[float, float]:
    """
    Generate realistic South India weather (Nov-Dec period)
    Returns: (temperature_celsius, humidity_percent)
    """
    # South India Nov-Dec: Temperature 22-30°C, Humidity 60-90%
    # Add some variation based on day
    base_temp = 26.0
    base_humidity = 75.0
    
    # Add daily variation
    temp_variation = random.uniform(-3, 4)  # 23-30°C range
    humidity_variation = random.uniform(-15, 15)  # 60-90% range
    
    # Slight trend: cooler and more humid as we move into December
    if day_offset > 20:
        temp_variation -= 1.5
        humidity_variation += 5
    
    temperature = round(base_temp + temp_variation, 1)
    humidity = round(base_humidity + humidity_variation, 1)
    
    # Clamp values
    temperature = max(22.0, min(30.0, temperature))
    humidity = max(60.0, min(90.0, humidity))
    
    return temperature, humidity


def get_co2_level(temperature: float, humidity: float) -> str:
    """Determine CO2 level based on conditions"""
    if temperature > 28 and humidity > 85:
        return "high"
    elif temperature < 24 or humidity < 70:
        return "low"
    else:
        return "medium"


def seed_database(clear_existing: bool = False):
    """
    Main function to seed the database
    
    Args:
        clear_existing: If True, clears all existing data before seeding. 
                       If False, only seeds if the seeded batches don't exist.
    """
    # Use fixed seed for consistent data across deployments
    random.seed(42)
    
    db: Session = SessionLocal()
    
    try:
        # Check if seeded batches already exist
        existing_batches = db.query(models.Batch).filter(
            models.Batch.username.in_(["Dhanush", "Rakesh", "Gagan"])
        ).all()
        
        if existing_batches and not clear_existing:
            # Silently skip if batches exist (for production)
            return
        
        # Clear existing data if requested or if we're re-seeding
        if clear_existing or existing_batches:
            if clear_existing:
                print("Clearing existing data...")
            db.query(models.Harvest).delete()
            db.query(models.DailyObservation).delete()
            db.query(models.Batch).delete()
            db.commit()
        
        # Batch configuration
        batches_config = [
            {"name": "Dhanush", "substrate_type": "Straw", "substrate_moisture": 65.0},
            {"name": "Rakesh", "substrate_type": "Sawdust", "substrate_moisture": 70.0},
            {"name": "Gagan", "substrate_type": "Compost", "substrate_moisture": 68.0},
        ]
        
        # Common spawn rate for all batches
        spawn_rate = 5.0
        
        # Start date: November 4, 2025
        start_date = date(2025, 11, 4)
        end_date = date(2025, 12, 10)
        
        # Calculate number of days
        total_days = (end_date - start_date).days + 1
        harvest_start_day = 23  # Start adding harvest data from day 23 (Nov 27)
        
        batch_ids = []
        
        # Create batches (silent in production, verbose in script mode)
        if clear_existing or not existing_batches:
            print(f"Creating {len(batches_config)} batches...")
        
        # Create batches
        for batch_config in batches_config:
            batch = models.Batch(
                username=batch_config["name"],
                substrate_type=batch_config["substrate_type"],
                substrate_moisture_percent=batch_config["substrate_moisture"],
                spawn_rate_percent=spawn_rate,
                start_date=start_date
            )
            db.add(batch)
            db.flush()  # Get batch_id
            batch_ids.append(batch.batch_id)
            if clear_existing or not existing_batches:
                print(f"  Created batch: {batch_config['name']} (ID: {batch.batch_id})")
        
        db.commit()
        
        # Create observations and harvests for each batch
        for idx, batch_id in enumerate(batch_ids):
            batch_name = batches_config[idx]["name"]
            if clear_existing or not existing_batches:
                print(f"\nProcessing batch: {batch_name} (ID: {batch_id})")
            
            total_yield_kg = 0.0
            flush_number = 1
            
            # Harvest yield ranges for each batch (to vary between batches)
            # Dhanush: 1-3 kg, Rakesh: 2-4 kg, Gagan: 1.5-5 kg
            harvest_ranges = [
                (1.0, 3.0),   # Dhanush
                (2.0, 4.0),   # Rakesh
                (1.5, 5.0),   # Gagan
            ]
            min_harvest, max_harvest = harvest_ranges[idx]
            
            # Create observations for each day
            for day_offset in range(total_days):
                current_date = start_date + timedelta(days=day_offset)
                
                # Get weather data
                temperature, humidity = get_south_india_weather(day_offset)
                co2_level = get_co2_level(temperature, humidity)
                light_hours = random.uniform(10.0, 14.0)  # 10-14 hours of light
                
                # Create observation
                observation = models.DailyObservation(
                    batch_id=batch_id,
                    date=current_date,
                    ambient_temperature_celsius=temperature,
                    relative_humidity_percent=humidity,
                    CO2_level=co2_level,
                    light_hours_per_day=round(light_hours, 1)
                )
                db.add(observation)
                
                # Add harvest data starting from day 23
                if day_offset >= harvest_start_day:
                    days_since_harvest_start = day_offset - harvest_start_day
                    
                    # Define harvest schedule: first on day 23, then every 4-5 days
                    # This creates a more predictable pattern
                    harvest_days = [0, 4, 9, 14, 19, 24, 29]  # Days relative to harvest_start_day
                    
                    if days_since_harvest_start in harvest_days:
                        # Vary harvest amount based on conditions and batch
                        # Better conditions (temp 24-27, humidity 75-85) = better yield
                        condition_factor = 1.0
                        if 24 <= temperature <= 27 and 75 <= humidity <= 85:
                            condition_factor = 1.15
                        elif temperature > 28 or humidity < 70:
                            condition_factor = 0.85
                        
                        # Calculate harvest yield with some variation
                        base_yield = random.uniform(min_harvest, max_harvest)
                        harvest_yield = round(base_yield * condition_factor, 2)
                        harvest_yield = max(0.5, min(harvest_yield, max_harvest * 1.2))  # Clamp
                        
                        total_yield_kg += harvest_yield
                        
                        # Create harvest record
                        harvest = models.Harvest(
                            batch_id=batch_id,
                            flush_number=flush_number,
                            flush_yield_kg=harvest_yield,
                            total_batch_yield_kg=round(total_yield_kg, 2),
                            date=current_date
                        )
                        db.add(harvest)
                        flush_number += 1
                        
                        if clear_existing or not existing_batches:
                            print(f"  Day {day_offset + 1} ({current_date}): Harvest Flush {flush_number - 1} = {harvest_yield} kg")
            
            db.commit()
            if clear_existing or not existing_batches:
                print(f"  Completed: {batch_name} - {total_days} observations, {flush_number - 1} harvests, Total yield: {total_yield_kg:.2f} kg")
        
        if clear_existing or not existing_batches:
            print("\n" + "="*60)
            print("Database seeding completed successfully!")
            print("="*60)
            print(f"\nCreated batches:")
            for idx, batch_id in enumerate(batch_ids):
                batch = db.query(models.Batch).filter(models.Batch.batch_id == batch_id).first()
                obs_count = db.query(models.DailyObservation).filter(
                    models.DailyObservation.batch_id == batch_id
                ).count()
                harvest_count = db.query(models.Harvest).filter(
                    models.Harvest.batch_id == batch_id
                ).count()
                print(f"  - {batch.username}: {obs_count} observations, {harvest_count} harvests")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Starting database seeding...")
    print("="*60)
    seed_database(clear_existing=True)
    print("\nYou can now use the API endpoints to fetch this data:")
    print("  - GET /api/batches - Get all batches")
    print("  - GET /api/batches/{batch_id} - Get batch with observations and harvests")
    print("  - GET /api/batches/{batch_id}/observations - Get observations")
    print("  - GET /api/batches/{batch_id}/harvests - Get harvests")

