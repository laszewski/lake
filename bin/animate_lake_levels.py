import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import matplotlib.dates as mdates

def main():
    # Load the data
    print("Loading data...")
    df = pd.read_csv('level-all.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')

    # Extract year and a normalized date (day of year) for plotting
    df['year'] = df['timestamp'].dt.year
    # We use the timestamp but we will adjust the x-axis for each year
    
    years = sorted(df['year'].unique())
    
    # Setup the plot
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Global Y limits to keep the scale consistent across years
    y_min = df['level_ft'].min() - 0.5
    y_max = df['level_ft'].max() + 0.5
    ax.set_ylim(y_min, y_max)
    
    # X axis will be formatted as months
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    ax.set_title('Lake Level Seasonal Change', fontsize=16)
    ax.set_xlabel('Month', fontsize=12)
    ax.set_ylabel('Level (ft)', fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.7)

    line, = ax.plot([], [], lw=2, color='blue')
    year_text = ax.text(0.5, 0.9, '', transform=ax.transAxes, 
                        fontsize=20, fontweight='bold', ha='center', color='darkblue')

    def init():
        line.set_data([], [])
        year_text.set_text('')
        return line, year_text

    def update(year):
        # Filter data for the current year
        year_data = df[df['year'] == year]
        
        # To plot on a consistent X-axis (Jan-Dec), we shift the dates to a single reference year
        # We'll use 2000 as a reference year for the X-axis
        ref_year = 2000
        x_vals = year_data['timestamp'].apply(lambda x: x.replace(year=ref_year))
        y_vals = year_data['level_ft']
        
        line.set_data(x_vals, y_vals)
        
        # Set X limits to cover the whole year
        ax.set_xlim(pd.Timestamp(f'{ref_year}-01-01'), pd.Timestamp(f'{ref_year}-12-31'))
        
        year_text.set_text(f'Year: {year}')
        return line, year_text

    print(f"Creating animation for {len(years)} years...")
    # We animate over the list of unique years
    ani = FuncAnimation(fig, update, frames=years, 
                        init_func=init, blit=False, interval=500)

    # Save as GIF
    output_file = 'lake_level_animation.gif'
    print(f"Saving animation to {output_file}...")
    ani.save(output_file, writer='pillow', fps=2) # Lower FPS to make years readable
    print("Done!")

if __name__ == "__main__":
    main()