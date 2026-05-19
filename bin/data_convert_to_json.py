import csv
import json

input_file = 'elevation_converted.csv'
output_file = 'elevation_data.json'

data = []
with open(input_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        data.append({
            'loc': row['Location'],
            'lat': float(row['Latitude']),
            'lon': float(row['Longitude']),
            'elev': float(row['Elevation (ft)'])
        })

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(data, f)
