# Get the layer
layer = QgsProject.instance().mapLayersByName("Schools")[0]

# Get selected features
selected_features = layer.selectedFeatures()

# Output file path
output_file = "C:/Users/cedri/OneDrive/Desktop/Uni/PythonInQgisArcGis/SchoolReport.csv"

# Open CSV file for writing
with open(output_file, "w") as file:
    # Write header
    file.write("Name;X;Y\n")
    
    # Loop through selected features
    for feature in selected_features:
        # Get school name
        name = feature["Name"]
        
        # Get geometry and extract coordinates
        point = feature.geometry().asPoint()
        x = point.x()
        y = point.y()
        
        # Write to CSV
        file.write(f"{name};{x};{y}\n")
        
print("SchoolReport.csv created succesfully.")