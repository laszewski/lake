import pandas as pd
import numpy as np
from datetime import datetime

def analyze_stats():
    print("Loading data...")
    # Load lake levels
    levels_df = pd.read_csv('level-all.csv')
    levels_df['timestamp'] = pd.to_datetime(levels_df['timestamp'])
    levels_df['year'] = levels_df['timestamp'].dt.year
    levels_df['month'] = levels_df['timestamp'].dt.month

    # Load elevations
    elevations_df = pd.read_csv('elevation.csv')

    # 1. General Statistics
    overall_min = levels_df['level_ft'].min()
    overall_max = levels_df['level_ft'].max()
    overall_avg = levels_df['level_ft'].mean()

    # 2. Yearly Statistics
    yearly_stats = levels_df.groupby('year')['level_ft'].agg(['min', 'max', 'mean']).reset_index()
    yearly_stats.columns = ['Year', 'Min_Level', 'Max_Level', 'Avg_Level']

    # 3. Monthly Seasonal Trends (Average across all years)
    monthly_stats = levels_df.groupby('month')['level_ft'].mean().reset_index()
    monthly_stats.columns = ['Month', 'Avg_Level']

    # 4. Rate of Change (ft per day)
    # Calculate difference between consecutive readings and divide by time difference in days
    levels_df = levels_df.sort_values('timestamp')
    time_diff = levels_df['timestamp'].diff().dt.total_seconds() / (24 * 3600)
    level_diff = levels_df['level_ft'].diff()
    rate_of_change = level_diff / time_diff
    max_rise = rate_of_change.max()
    max_fall = rate_of_change.min()

    # 5. Location-Specific Flood Probability
    # For each location, what % of time was lake level > elevation?
    flood_probs = []
    for index, row in elevations_df.iterrows():
        loc = row['Location']
        elev = row['Elevation (ft)']
        # Count how many readings were above this elevation
        flooded_count = (levels_df['level_ft'] > elev).sum()
        prob = (flooded_count / len(levels_df)) * 100
        flood_probs.append({'Location': loc, 'Elevation': elev, 'Flood_Probability_%': prob})
    
    flood_probs_df = pd.DataFrame(flood_probs)
    # Group by location to get average probability for that area
    loc_flood_stats = flood_probs_df.groupby('Location')['Flood_Probability_%'].mean().reset_index()

    # Write results to file
    with open('lake_statistics.txt', 'w') as f:
        f.write("=== LAKE LEVEL GENERAL STATISTICS ===\n")
        f.write(f"Overall Min: {overall_min:.2f} ft\n")
        f.write(f"Overall Max: {overall_max:.2f} ft\n")
        f.write(f"Overall Avg: {overall_avg:.2f} ft\n")
        f.write(f"Max Rise Rate: {max_rise:.2f} ft/day\n")
        f.write(f"Max Fall Rate: {max_fall:.2f} ft/day\n\n")

        f.write("=== YEARLY STATISTICS ===\n")
        f.write(yearly_stats.to_string(index=False))
        f.write("\n\n")

        f.write("=== MONTHLY SEASONAL AVERAGES ===\n")
        f.write(monthly_stats.to_string(index=False))
        f.write("\n\n")

        f.write("=== LOCATION FLOOD PROBABILITY (Avg per Location) ===\n")
        f.write(loc_flood_stats.to_string(index=False))
        f.write("\n")

    print("Analysis complete. Results saved to lake_statistics.txt")

if __name__ == "__main__":
    analyze_stats()