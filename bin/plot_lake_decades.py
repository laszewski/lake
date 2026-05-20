import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

def plot_decades():
    input_file = "level-all.csv"
    output_image = "docs/images/lake-level-decades.png"
    
    print(f"Loading data from {input_file}...")
    try:
        df = pd.read_csv(input_file)
    except FileNotFoundError:
        print(f"Error: {input_file} not found. Please run bin/level-download-all.py first.")
        return

    # Convert timestamp to datetime
    # The CSV format is [timestamp, level_ft]
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['year'] = df['timestamp'].dt.year
    df['day_of_year'] = df['timestamp'].dt.dayofyear
    df['decade'] = (df['year'] // 10) * 10

    # Group by decade and day of year to get the average level
    # This smooths the data and allows overlaying decades
    decade_averages = df.groupby(['decade', 'day_of_year'])['level_ft'].mean().unstack(level=0)

    plt.figure(figsize=(12, 6))
    
    # Define colors for decades
    colors = plt.cm.viridis(np.linspace(0, 1, len(decade_averages.columns)))
    
    for i, decade in enumerate(decade_averages.columns):
        plt.plot(decade_averages.index, decade_averages[decade], 
                 label=f"{int(decade)}s", color=colors[i], linewidth=2)

    plt.title("Average Lake Level Comparison by Decade", fontsize=14)
    plt.xlabel("Day of Year", fontsize=12)
    plt.ylabel("Lake Level (ft)", fontsize=12)
    plt.legend(title="Decade")
    plt.grid(True, linestyle='--', alpha=0.6)
    
    # Add credit line at the bottom right
    plt.figtext(0.9, 0.02, "prepared by Gregor von Laszewski, laszewski@gmail.com", 
                ha="right", fontsize=9, color="gray", style="italic")
    
    plt.tight_layout(rect=[0, 0.05, 1, 1])

    plt.savefig(output_image)
    print(f"Successfully saved comparison chart to {output_image}")

if __name__ == "__main__":
    plot_decades()