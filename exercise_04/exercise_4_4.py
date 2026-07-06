import processing
from qgis.core import QgsProject

# Load layers
schools = QgsProject.instance().mapLayersByName("Schools")[0]
districts = QgsProject.instance().mapLayersByName("Muenster_City_Districts")[0]

# Run Count Points in Polygon
result = processing.run("native:countpointsinpolygon", {
    'POLYGONS': districts,
    'POINTS': schools,
    'FIELD': 'NUMPOINTS',
    'OUTPUT': 'memory:'
})

# Get output layer
output_layer = result['OUTPUT']

# Print results
for feature in output_layer.getFeatures():
    district_name = feature["Name"]
    school_count = feature["NUMPOINTS"]
    print(f"{district_name}: {school_count}")