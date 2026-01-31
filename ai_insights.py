
import pandas as pd

def generate_insights(observations, harvests):
    insights = []

    if len(harvests) == 0:
        return ["No harvest data yet. Monitor early growth signals."]

    df_obs = pd.DataFrame(observations)
    df_h = pd.DataFrame(harvests)

    avg_yield = df_h['flush_yield_kg'].mean()

    if df_obs['relative_humidity_percent'].std() > 10:
        insights.append("High humidity variability detected; this may impact pinning consistency.")

    if df_obs['ambient_temperature_celsius'].mean() > 26:
        insights.append("Average temperature is on the higher side; consider tighter temperature control.")

    if avg_yield < 0.7 * df_h['flush_yield_kg'].max():
        insights.append("Early yield underperformance compared to peak flush detected.")

    if not insights:
        insights.append("Batch conditions appear stable with no major anomalies detected.")

    return insights
