import pandas as pd
import folium
from folium.plugins import MarkerCluster

# Read location data with coordinates
locations = pd.read_csv('data/location_point_unified_corrected.csv')

print('Columns:', locations.columns.tolist())
print('Total locations:', len(locations))
print()
print(locations.head())
