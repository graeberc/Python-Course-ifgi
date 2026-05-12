import os
from qgis.core import QgsApplication,QgsVectorLayer, QgsProject

# Initialize QGIS
QgsApplication.setPrefixPath(r"C:\Program Files\QGIS 3.44.9", True)
qgs = QgsApplication([], False)
qgs.initQgis()

# Path to Muenster folder
folder_path = r"C:\Users\cedri\Downloads\Muenster\Muenster"

# Path to save project
project_path = r"C:\Users\cedri\OneDrive\Desktop\Uni\PythonInQgisArcGis\Python-Course-ifgi\exercise_4\myFirstProject.qgz"

# Create QGIS project instance
project = QgsProject.instance()

# Get all files in folder as complete paths
file_list = [os.path.join(folder_path, file) for file in os.listdir(folder_path)]

# Iterate through files
for file_path in file_list:

    # Only add shapefiles
    if file_path.endswith(".shp"):

        # Extract filename without extension
        layer_name = os.path.splitext(os.path.basename(file_path))[0]

        # Create layer
        layer = QgsVectorLayer(file_path, layer_name, "ogr")

        # Check if layer is valid
        if layer.isValid():
            project.addMapLayer(layer)
            print(f"Added: {layer_name}")
        else:
            print(f"Error loading: {file_path}")

# Sace project
project.write(project_path)

print("Project saved successfully!")
