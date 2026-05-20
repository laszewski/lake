import pandas as pd
import numpy as np
from datetime import datetime

def predict_2026():
    print("Loading data for prediction...")
    levels_df = pd.read_csv('level-all.csv')
    levels_df['timestamp'] = pd.to_datetime(levels_df['timestamp'])
    levels_df['year'] = levels_df['timestamp'].dt.year
    levels_df['month'] = levels_df['timestamp'].dt.month

    current_year = 2026
    current_date = datetime(2026, 5, 20)
    current_month = current_date.month

    # 1. Calculate Historical Monthly Averages
    hist_monthly_avg = levels_df[levels_df['year'] < current_year].groupby('month')['level_ft'].mean()

    # 2. Calculate 2026 performance so far (Jan to May)
    data_2026 = levels_df[levels_df['year'] == current_year]
    data_2026_so_far = data_2026[data_2026['month'] <= current_month]
    
    if data_2026_so_far.empty:
        print("Not enough data for 2026 to make a trend-based prediction.")
        return

    avg_2026_so_far = data_2026_so_far['level_ft'].mean()
    
    # Average of historical averages for the same months
    hist_avg_so_far = hist_monthly_avg.loc[:current_month].mean()
    
    # The "Anomaly" - how much higher/lower is this year compared to average?
    anomaly = avg_2026_so_far - hist_avg_so_far
    print(f"2026 Anomaly: {anomaly:.2f} ft relative to historical average")

    # 3. Project the rest of the year
    # Projected Level = Historical Monthly Avg + Anomaly
    projected_levels = hist_monthly_avg + anomaly
    projected_peak = projected_levels.max()
    peak_month = projected_levels.idxmax()

    # 4. Flood Stage Analysis
    # Based on file names in the project, 546 ft seems to be a significant flood stage
    flood_stage = 546.0
    
    # Probability of exceeding flood stage based on historical peaks
    yearly_maxes = levels_df[levels_df['year'] < current_year].groupby('year')['level_ft'].max()
    flood_years = (yearly_maxes > flood_stage).sum()
    prob_flood = (flood_years / len(yearly_maxes)) * 100

    # Write results
    with open('flood_prediction_2026.txt', 'w') as f:
        f.write("=== 2026 FLOOD LEVEL PREDICTION ===\n")
        f.write(f"Current Date: {current_date.date()}\n")
        f.write(f"2026 Trend Anomaly: {anomaly:.2f} ft\n")
        f.write(f"Projected Peak Level: {projected_peak:.2f} ft\n")
        f.write(f"Expected Peak Month: {peak_month}\n")
        f.write(f"Reference Flood Stage: {flood_stage:.2f} ft\n")
        
        if projected_peak > flood_stage:
            f.write(f"RESULT: High Risk. Projected peak exceeds flood stage by {projected_peak - flood_stage:.2f} ft.\n")
        else:
            f.write(f"RESULT: Low Risk. Projected peak remains {flood_stage - projected_peak:.2f} ft below flood stage.\n")
            
        f.write(f"\nHistorical Flood Probability (Yearly): {prob_flood:.1f}%\n")
        f.write("\nNote: This is a simple linear anomaly projection based on seasonal averages.\n")

    print("Prediction complete. Results saved to flood_prediction_2026.txt")

if __name__ == "__main__":
    predict_2026()