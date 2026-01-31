from typing import List, Dict, Any, Optional
from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
import models


# Optimal ranges based on mushroom farming best practices
OPTIMAL_TEMPERATURE_MIN = 20.0
OPTIMAL_TEMPERATURE_MAX = 24.0
OPTIMAL_HUMIDITY_MIN = 80.0
OPTIMAL_HUMIDITY_MAX = 90.0
OPTIMAL_LIGHT_HOURS_MIN = 10.0
OPTIMAL_LIGHT_HOURS_MAX = 14.0


def generate_insights(batch_id: int, db: Session) -> Dict[str, List[str]]:
    """
    Generate comprehensive AI-powered insights for a batch based on patterns,
    anomalies, and trends. Uses statistical analysis and pattern detection.
    """
    # Get batch data
    batch = db.query(models.Batch).filter(models.Batch.batch_id == batch_id).first()
    if not batch:
        return {
            "warnings": [],
            "anomalies": [],
            "suggestions": [],
            "trends": [],
            "summary": "Batch not found."
        }
    
    # Get observations and harvests for this batch
    observations = db.query(models.DailyObservation)\
        .filter(models.DailyObservation.batch_id == batch_id)\
        .order_by(models.DailyObservation.date).all()
    
    harvests = db.query(models.Harvest)\
        .filter(models.Harvest.batch_id == batch_id)\
        .order_by(models.Harvest.flush_number).all()
    
    # Get historical data for comparison
    all_batches = db.query(models.Batch).all()
    all_harvests = db.query(models.Harvest).all()
    all_observations = db.query(models.DailyObservation).all()
    
    warnings = []
    anomalies = []
    suggestions = []
    trends = []
    
    # Analyze observations
    if observations:
        obs_analysis = _analyze_observations(observations, batch)
        warnings.extend(obs_analysis["warnings"])
        anomalies.extend(obs_analysis["anomalies"])
        suggestions.extend(obs_analysis["suggestions"])
        trends.extend(obs_analysis["trends"])
    
    # Analyze harvests
    if harvests:
        harvest_analysis = _analyze_harvests(
            harvests, 
            batch, 
            all_harvests,
            all_batches
        )
        warnings.extend(harvest_analysis["warnings"])
        suggestions.extend(harvest_analysis["suggestions"])
        trends.extend(harvest_analysis["trends"])
    
    # Generate summary
    summary = _generate_summary(batch, observations, harvests, warnings, anomalies, suggestions)
    
    return {
        "warnings": warnings,
        "anomalies": anomalies,
        "suggestions": suggestions,
        "trends": trends,
        "summary": summary
    }


def _analyze_observations(observations: List[models.DailyObservation], batch: models.Batch) -> Dict[str, List[str]]:
    """Analyze daily observations for patterns and anomalies"""
    warnings = []
    anomalies = []
    suggestions = []
    trends = []
    
    # Extract numeric values (filter None)
    temps = [o.ambient_temperature_celsius for o in observations if o.ambient_temperature_celsius is not None]
    humidities = [o.relative_humidity_percent for o in observations if o.relative_humidity_percent is not None]
    light_hours = [o.light_hours_per_day for o in observations if o.light_hours_per_day is not None]
    co2_levels = [o.CO2_level for o in observations if o.CO2_level is not None]
    
    # Temperature analysis
    if temps:
        avg_temp = sum(temps) / len(temps)
        temp_variance = max(temps) - min(temps) if len(temps) > 1 else 0
        
        if temp_variance > 5.0:
            warnings.append(
                f"Temperature variance detected: Daily temperature fluctuations exceed 5°C "
                f"(range: {min(temps):.1f}°C to {max(temps):.1f}°C), which may stress mycelium growth."
            )
        
        if avg_temp < OPTIMAL_TEMPERATURE_MIN:
            suggestions.append(
                f"Average temperature of {avg_temp:.1f}°C is below optimal range ({OPTIMAL_TEMPERATURE_MIN}-{OPTIMAL_TEMPERATURE_MAX}°C). "
                f"Consider increasing temperature to improve growth rates."
            )
        elif avg_temp > OPTIMAL_TEMPERATURE_MAX:
            suggestions.append(
                f"Average temperature of {avg_temp:.1f}°C is above optimal range ({OPTIMAL_TEMPERATURE_MIN}-{OPTIMAL_TEMPERATURE_MAX}°C). "
                f"Consider reducing temperature to prevent stress."
            )
        else:
            suggestions.append(
                f"Average temperature of {avg_temp:.1f}°C is optimal. Maintain this range for consistent yields."
            )
        
        # Temperature trend
        if len(temps) >= 3:
            recent_temps = temps[-3:]
            earlier_temps = temps[:3] if len(temps) >= 6 else temps[:len(temps)-3]
            if earlier_temps:
                recent_avg = sum(recent_temps) / len(recent_temps)
                earlier_avg = sum(earlier_temps) / len(earlier_temps)
                if recent_avg > earlier_avg + 1:
                    trends.append(f"Temperature trend: Increasing from {earlier_avg:.1f}°C to {recent_avg:.1f}°C over recent period.")
                elif recent_avg < earlier_avg - 1:
                    trends.append(f"Temperature trend: Decreasing from {earlier_avg:.1f}°C to {recent_avg:.1f}°C over recent period.")
    
    # Humidity analysis
    if humidities:
        avg_humidity = sum(humidities) / len(humidities)
        min_humidity = min(humidities)
        max_humidity = max(humidities)
        
        # Check for low humidity anomalies
        low_humidity_days = [o for o in observations if o.relative_humidity_percent and o.relative_humidity_percent < OPTIMAL_HUMIDITY_MIN]
        if low_humidity_days:
            for obs in low_humidity_days[:3]:  # Limit to first 3
                anomalies.append(
                    f"Humidity dropped to {obs.relative_humidity_percent:.0f}% on {obs.date}, "
                    f"significantly below optimal range ({OPTIMAL_HUMIDITY_MIN}-{OPTIMAL_HUMIDITY_MAX}%)."
                )
        
        if avg_humidity < OPTIMAL_HUMIDITY_MIN:
            suggestions.append(
                f"Consider increasing humidity to {OPTIMAL_HUMIDITY_MIN}-{OPTIMAL_HUMIDITY_MAX}% based on successful batches "
                f"with similar substrate types. Current average: {avg_humidity:.1f}%."
            )
        elif avg_humidity > OPTIMAL_HUMIDITY_MAX:
            suggestions.append(
                f"Humidity is above optimal range. Consider reducing to {OPTIMAL_HUMIDITY_MIN}-{OPTIMAL_HUMIDITY_MAX}% "
                f"to prevent contamination. Current average: {avg_humidity:.1f}%."
            )
        
        # Humidity trend
        if len(humidities) >= 7:
            recent_hum = humidities[-7:]
            earlier_hum = humidities[:7]
            recent_avg = sum(recent_hum) / len(recent_hum)
            earlier_avg = sum(earlier_hum) / len(earlier_hum)
            if recent_avg > earlier_avg + 5:
                trends.append(
                    f"Humidity trend: Increasing from {earlier_avg:.0f}% to {recent_avg:.0f}% over the past week, "
                    f"approaching optimal range."
                )
            elif recent_avg < earlier_avg - 5:
                trends.append(
                    f"Humidity trend: Decreasing from {earlier_avg:.0f}% to {recent_avg:.0f}% over the past week, "
                    f"moving away from optimal range."
                )
    
    # CO2 analysis
    if co2_levels:
        high_co2_count = sum(1 for level in co2_levels if level == 'high')
        if high_co2_count >= 5:
            consecutive_high = _check_consecutive_high_co2(observations)
            if consecutive_high:
                anomalies.append(
                    f"CO2 levels remained 'high' for {consecutive_high} consecutive days, "
                    f"which may indicate insufficient ventilation."
                )
                suggestions.append(
                    "Increase ventilation to reduce CO2 levels. High CO2 can inhibit fruiting body development."
                )
        
        if 'low' in co2_levels or 'medium' in co2_levels:
            suggestions.append("CO2 levels are within acceptable range. Maintain current ventilation practices.")
    
    # Light analysis
    if light_hours:
        avg_light = sum(light_hours) / len(light_hours)
        if OPTIMAL_LIGHT_HOURS_MIN <= avg_light <= OPTIMAL_LIGHT_HOURS_MAX:
            suggestions.append(
                f"Light exposure of {avg_light:.1f} hours/day aligns with best-performing batches. Continue this pattern."
            )
        elif avg_light < OPTIMAL_LIGHT_HOURS_MIN:
            suggestions.append(
                f"Light exposure of {avg_light:.1f} hours/day is below optimal. Consider increasing to "
                f"{OPTIMAL_LIGHT_HOURS_MIN}-{OPTIMAL_LIGHT_HOURS_MAX} hours/day."
            )
        else:
            suggestions.append(
                f"Light exposure of {avg_light:.1f} hours/day is above optimal. Consider reducing to "
                f"{OPTIMAL_LIGHT_HOURS_MIN}-{OPTIMAL_LIGHT_HOURS_MAX} hours/day."
            )
    
    return {
        "warnings": warnings,
        "anomalies": anomalies,
        "suggestions": suggestions,
        "trends": trends
    }


def _analyze_harvests(
    harvests: List[models.Harvest],
    batch: models.Batch,
    all_harvests: List[models.Harvest],
    all_batches: List[models.Batch]
) -> Dict[str, List[str]]:
    """Analyze harvest data for yield patterns and performance"""
    warnings = []
    suggestions = []
    trends = []
    
    if not harvests:
        return {"warnings": warnings, "suggestions": suggestions, "trends": trends}
    
    # Calculate batch totals
    total_yield = sum(h.flush_yield_kg for h in harvests)
    num_flushes = len(harvests)
    
    # Get historical averages for similar batches
    similar_batches = [b for b in all_batches if b.substrate_type == batch.substrate_type]
    similar_batch_ids = [b.batch_id for b in similar_batches]
    similar_harvests = [h for h in all_harvests if h.batch_id in similar_batch_ids]
    
    if similar_harvests:
        # Group by flush number
        flush_yields = {}
        for h in similar_harvests:
            if h.flush_number not in flush_yields:
                flush_yields[h.flush_number] = []
            flush_yields[h.flush_number].append(h.flush_yield_kg)
        
        # Compare first flush
        if 1 in flush_yields and harvests and harvests[0].flush_number == 1:
            avg_first_flush = sum(flush_yields[1]) / len(flush_yields[1])
            first_flush_yield = harvests[0].flush_yield_kg
            
            if first_flush_yield < 0.7 * avg_first_flush:
                percentage_below = ((avg_first_flush - first_flush_yield) / avg_first_flush) * 100
                warnings.append(
                    f"Early yield underperformance detected: First flush yield ({first_flush_yield:.1f} kg) is "
                    f"{percentage_below:.0f}% below historical average ({avg_first_flush:.1f} kg) for similar batches."
                )
    
    # Analyze flush progression
    if len(harvests) >= 2:
        yields = [h.flush_yield_kg for h in harvests]
        if yields[1] < yields[0] * 0.5:
            trends.append(
                f"Yield trend: Second flush ({yields[1]:.1f} kg) shows significant decline from first flush "
                f"({yields[0]:.1f} kg). This is normal but monitor substrate condition."
            )
        elif yields[1] > yields[0] * 0.8:
            trends.append(
                f"Yield trend: Strong second flush performance ({yields[1]:.1f} kg) relative to first flush "
                f"({yields[0]:.1f} kg). Excellent substrate condition."
            )
    
    # Project future yields
    if len(harvests) >= 1:
        first_flush = harvests[0].flush_yield_kg
        if len(harvests) == 1:
            # Estimate second flush based on typical patterns (usually 50-80% of first)
            projected_second = first_flush * 0.65
            projected_total = first_flush + projected_second + (projected_second * 0.6)  # Estimate third flush
            trends.append(
                f"Yield trend: First flush shows promise ({first_flush:.1f} kg). Historical data suggests "
                f"second flush may yield {projected_second:.1f}-{first_flush * 0.8:.1f} kg if conditions remain stable."
            )
            trends.append(
                f"Projected total yield: {projected_total:.1f}-{projected_total * 1.2:.1f} kg based on current trajectory."
            )
    
    return {
        "warnings": warnings,
        "suggestions": suggestions,
        "trends": trends
    }


def _check_consecutive_high_co2(observations: List[models.DailyObservation]) -> int:
    """Check for consecutive days with high CO2 levels"""
    max_consecutive = 0
    current_consecutive = 0
    
    for obs in observations:
        if obs.CO2_level == 'high':
            current_consecutive += 1
            max_consecutive = max(max_consecutive, current_consecutive)
        else:
            current_consecutive = 0
    
    return max_consecutive if max_consecutive >= 5 else 0


def _generate_summary(
    batch: models.Batch,
    observations: List[models.DailyObservation],
    harvests: List[models.Harvest],
    warnings: List[str],
    anomalies: List[str],
    suggestions: List[str]
) -> str:
    """Generate a comprehensive summary of the batch"""
    summary_parts = [f"Batch #{batch.batch_id}"]
    
    if not observations and not harvests:
        return f"{summary_parts[0]} has no data yet. Start recording observations and harvests to generate insights."
    
    # Add substrate info
    summary_parts.append(f"uses {batch.substrate_type} substrate")
    
    # Add key metrics
    if observations:
        temps = [o.ambient_temperature_celsius for o in observations if o.ambient_temperature_celsius is not None]
        humidities = [o.relative_humidity_percent for o in observations if o.relative_humidity_percent is not None]
        
        if temps:
            summary_parts.append(f"with average temperature of {sum(temps)/len(temps):.1f}°C")
        if humidities:
            summary_parts.append(f"and humidity averaging {sum(humidities)/len(humidities):.0f}%")
    
    # Add yield info
    if harvests:
        total_yield = sum(h.flush_yield_kg for h in harvests)
        summary_parts.append(f"Current yield: {total_yield:.1f} kg across {len(harvests)} flush(es)")
    
    # Add main concerns
    if warnings or anomalies:
        summary_parts.append("Main concerns:")
        if warnings:
            summary_parts.append(warnings[0].lower())
        if anomalies:
            summary_parts.append(anomalies[0].lower())
    else:
        summary_parts.append("shows promising early indicators with stable conditions")
    
    # Add key recommendation
    if suggestions:
        # Find humidity or temperature suggestions first
        key_suggestion = None
        for s in suggestions:
            if "humidity" in s.lower() or "temperature" in s.lower():
                key_suggestion = s
                break
        if not key_suggestion:
            key_suggestion = suggestions[0]
        summary_parts.append(f"Key recommendation: {key_suggestion}")
    
    # Add projection
    if harvests and len(harvests) == 1:
        first_flush = harvests[0].flush_yield_kg
        projected = first_flush * 2.5  # Rough estimate
        summary_parts.append(f"Projected total yield: {projected:.1f}-{projected * 1.2:.1f} kg based on current trajectory")
    
    return ". ".join(summary_parts) + "."


def compare_batches(batch_ids: List[int], db: Session) -> Dict[str, Any]:
    """Compare multiple batches and provide comparative insights"""
    if len(batch_ids) < 2:
        return {
            "yield_comparison": [],
            "average_conditions": [],
            "insights": ["At least 2 batches are required for comparison."]
        }
    
    # Get batches
    batches = db.query(models.Batch).filter(models.Batch.batch_id.in_(batch_ids)).all()
    if len(batches) != len(batch_ids):
        missing = set(batch_ids) - {b.batch_id for b in batches}
        return {
            "yield_comparison": [],
            "average_conditions": [],
            "insights": [f"Some batches not found: {missing}"]
        }
    
    yield_comparison = []
    average_conditions = []
    insights = []
    
    # Calculate yield comparison
    for batch in batches:
        harvests = db.query(models.Harvest)\
            .filter(models.Harvest.batch_id == batch.batch_id).all()
        
        total_yield = sum(h.flush_yield_kg for h in harvests) if harvests else 0.0
        num_flushes = len(harvests)
        
        yield_comparison.append({
            "batch_id": batch.batch_id,
            "total_yield": total_yield,
            "flushes": num_flushes
        })
    
    # Calculate average conditions
    for batch in batches:
        observations = db.query(models.DailyObservation)\
            .filter(models.DailyObservation.batch_id == batch.batch_id).all()
        
        temps = [o.ambient_temperature_celsius for o in observations if o.ambient_temperature_celsius is not None]
        humidities = [o.relative_humidity_percent for o in observations if o.relative_humidity_percent is not None]
        
        avg_temp = sum(temps) / len(temps) if temps else None
        avg_humidity = sum(humidities) / len(humidities) if humidities else None
        
        average_conditions.append({
            "batch_id": batch.batch_id,
            "avg_temperature": round(avg_temp, 1) if avg_temp else None,
            "avg_humidity": round(avg_humidity, 1) if avg_humidity else None,
            "substrate_type": batch.substrate_type
        })
    
    # Generate comparative insights
    if len(yield_comparison) >= 2:
        # Find best and worst yields
        yields_sorted = sorted(yield_comparison, key=lambda x: x["total_yield"], reverse=True)
        best = yields_sorted[0]
        worst = yields_sorted[-1]
        
        if best["total_yield"] > 0 and worst["total_yield"] > 0:
            percentage_diff = ((best["total_yield"] - worst["total_yield"]) / worst["total_yield"]) * 100
            best_substrate = next((c["substrate_type"] for c in average_conditions if c["batch_id"] == best["batch_id"]), "Unknown")
            worst_substrate = next((c["substrate_type"] for c in average_conditions if c["batch_id"] == worst["batch_id"]), "Unknown")
            
            insights.append(
                f"Batch #{best['batch_id']} ({best_substrate} substrate) outperformed "
                f"Batch #{worst['batch_id']} ({worst_substrate}) by {percentage_diff:.0f}% in total yield."
            )
        
        # Compare humidity
        if len(average_conditions) >= 2:
            hum_sorted = sorted([c for c in average_conditions if c["avg_humidity"]], 
                              key=lambda x: x["avg_humidity"], reverse=True)
            if len(hum_sorted) >= 2:
                high_hum = hum_sorted[0]
                low_hum = hum_sorted[-1]
                insights.append(
                    f"Higher average humidity ({high_hum['avg_humidity']:.1f}% vs {low_hum['avg_humidity']:.1f}%) "
                    f"correlates with better yields in this comparison."
                )
        
        # Compare temperature variance
        temp_vars = []
        for batch in batches:
            observations = db.query(models.DailyObservation)\
                .filter(models.DailyObservation.batch_id == batch.batch_id).all()
            temps = [o.ambient_temperature_celsius for o in observations if o.ambient_temperature_celsius is not None]
            if len(temps) > 1:
                temp_var = max(temps) - min(temps)
                temp_vars.append({"batch_id": batch.batch_id, "variance": temp_var})
        
        if len(temp_vars) >= 2:
            temp_vars_sorted = sorted(temp_vars, key=lambda x: x["variance"])
            stable = temp_vars_sorted[0]
            insights.append(
                f"Temperature variance was lower in Batch #{stable['batch_id']} "
                f"({stable['variance']:.1f}°C), suggesting more stable conditions."
            )
    
    return {
        "yield_comparison": yield_comparison,
        "average_conditions": average_conditions,
        "insights": insights
    }

