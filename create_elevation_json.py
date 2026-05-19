import csv
import json
import os

input_file = 'docs/data/elevation.csv'
output_file = 'docs/data/elevation.json'

data = []

if not os.path.exists(input_file):
    print(f"Error: {input_file} not found")
    exit(1)

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
    json.dump(data, f, indent=4)

print(f"Successfully created {output_file} with {len(data)} entries")
