import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

def main():
    print("Loading data...")
    df = pd.read_csv('level-all.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')
    df['year'] = df['timestamp'].dt.year

    # To plot on a consistent X-axis (Jan-Dec), we normalize dates to a reference year
    ref_year = 2000
    df['norm_date'] = df['timestamp'].apply(lambda x: x.replace(year=ref_year))
    
    years = sorted(df['year'].unique())
    
    # Create the initial frame (first year)
    first_year = years[0]
    df_first = df[df['year'] == first_year]
    
    fig = go.Figure(
        data=[go.Scatter(
            x=df_first['norm_date'], 
            y=df_first['level_ft'], 
            mode='lines', 
            line=dict(color='blue', width=2),
            name=str(first_year)
        )],
        layout=go.Layout(
            title='Lake Level Seasonal Change',
            xaxis=dict(title='Month', tickformat='%b'),
            yaxis=dict(title='Level (ft)', range=[df['level_ft'].min() - 0.5, df['level_ft'].max() + 0.5]),
            updatemenus=[{
                'type': 'buttons',
                'buttons': [{
                    'label': 'Play',
                    'method': 'animate',
                    'args': [None, {'frame': {'duration': 500, 'redraw': True}, 'fromcurrent': True}]
                }]
            }]
        ),
        frames=[go.Frame(
            data=[go.Scatter(x=df[df['year'] == y]['norm_date'], 
                             y=df[df['year'] == y]['level_ft'])],
            name=str(y)
        ) for y in years]
    )

    # Add slider
    sliders = [{
        'steps': [{
            'method': 'animate',
            'label': str(y),
            'args': [[str(y)], {
                'frame': {'duration': 300, 'redraw': True},
                'mode': 'immediate',
                'transition': {'duration': 0}
            }]
        } for y in years],
        'transition': {'duration': 300},
        'x': 0.1,
        'len': 0.9
    }]
    
    fig.update_layout(sliders=sliders)
    
    output_file = 'docs/lake_level_interactive.html'
    print(f"Saving interactive animation to {output_file}...")
    fig.write_html(output_file)
    print("Done!")

if __name__ == "__main__":
    main()