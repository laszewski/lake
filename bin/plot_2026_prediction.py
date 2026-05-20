import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta, timezone

def plot_prediction():
    print("Loading data...")
    levels_df = pd.read_csv('level-all.csv')
    levels_df['timestamp'] = pd.to_datetime(levels_df['timestamp'])
    
    # Create a 'day_of_year' column for climatology
    levels_df['day_of_year'] = levels_df['timestamp'].dt.dayofyear
    levels_df['year'] = levels_df['timestamp'].dt.year

    current_year = 2026
    current_date = datetime(2026, 5, 20, tzinfo=timezone.utc)
    
    # 1. Calculate Daily Climatology (Historical Avg and Std)
    hist_data = levels_df[levels_df['year'] < current_year]
    daily_stats = hist_data.groupby('day_of_year')['level_ft'].agg(['mean', 'std']).reset_index()
    daily_stats.columns = ['day_of_year', 'hist_mean', 'hist_std']

    # 2. Analyze 2026 Trend so far
    data_2026 = levels_df[levels_df['year'] == current_year].sort_values('timestamp')
    actuals = data_2026[data_2026['timestamp'] <= current_date]
    
    # Calculate anomaly: average difference between actuals and historical mean for those days
    merged_actuals = actuals.merge(daily_stats, on='day_of_year')
    anomaly = (merged_actuals['level_ft'] - merged_actuals['hist_mean']).mean()
    print(f"Calculated 2026 Daily Anomaly: {anomaly:.2f} ft")

    # 3. Generate Full Year Timeline for 2026
    start_date = datetime(current_year, 1, 1, tzinfo=timezone.utc)
    end_date = datetime(current_year, 12, 31, tzinfo=timezone.utc)
    date_range = pd.date_range(start=start_date, end=end_date, tz='UTC')
    
    full_year_df = pd.DataFrame({'timestamp': date_range})
    full_year_df['day_of_year'] = full_year_df['timestamp'].dt.dayofyear
    
    # Merge with historical stats
    full_year_df = full_year_df.merge(daily_stats, on='day_of_year', how='left')
    
    # Prediction: Hist Mean + Anomaly
    full_year_df['predicted'] = full_year_df['hist_mean'] + anomaly
    full_year_df['upper_bound'] = full_year_df['predicted'] + full_year_df['hist_std']
    full_year_df['lower_bound'] = full_year_df['predicted'] - full_year_df['hist_std']

    # 4. Plotting
    plt.figure(figsize=(14, 7))
    
    # Plot Actuals
    plt.plot(actuals['timestamp'], actuals['level_ft'], color='blue', label='Actual 2026 Levels', linewidth=2)
    
    # Plot Prediction (from current_date onwards)
    pred_mask = full_year_df['timestamp'] >= current_date
    plt.plot(full_year_df.loc[pred_mask, 'timestamp'], 
             full_year_df.loc[pred_mask, 'predicted'], 
             color='red', linestyle='--', label='Predicted 2026 Levels', linewidth=2)
    
    # Plot Error Band (Std Dev)
    plt.fill_between(full_year_df.loc[pred_mask, 'timestamp'], 
                     full_year_df.loc[pred_mask, 'lower_bound'], 
                     full_year_df.loc[pred_mask, 'upper_bound'], 
                     color='red', alpha=0.2, label=r'$\pm 1$ Std Dev Error')

    # Reference Flood Stage
    plt.axhline(y=546.0, color='black', linestyle=':', label='Flood Stage (546 ft)')

    plt.title(f'Lake Level Prediction for {current_year} (Trend-Based)', fontsize=16)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Level (ft)', fontsize=12)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    plt.savefig('lake_prediction_2026_plot.png')
    print("Plot saved as lake_prediction_2026_plot.png")

if __name__ == "__main__":
    plot_prediction()