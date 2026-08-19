import geopandas as gpd

# Load your large rivers file
rivers = gpd.read_file('rivers.json')

# Simplify the geometry to drastically reduce file size while keeping map shape
rivers['geometry'] = rivers['geometry'].simplify(
    tolerance=0.0001, preserve_topology=True
)

# Save as a lightweight GeoJSON file
rivers.to_file('rivers_light.geojson', driver='GeoJSON')
print('Compressed successfully!')