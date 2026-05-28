# -----------------------------------------------------------
# Exercise 5.2 Geoguesser - Münster Style
# This script asks the user for WGS84 coordinates
# (latitude, longitude), transforms them into the
# CRS of the Münster district layer and checks
# whether the point lies inside a city district.
# -----------------------------------------------------------

from qgis.PyQt.QtWidgets import QInputDialog, QMessageBox
from qgis.core import *

# Get QGIS main window
parent = iface.mainWindow()

# Access district layer
district_layer = QgsProject.instance().mapLayersByName("Muenster_City_Districts")[0]

# Open input dialog for coordinates
sCoords, bOk = QInputDialog.getText(
    parent,
    "Coordinates",
    "Enter coordinates as latitude, longitude",
    text = "51.96066, 7.62476"
)
# Check if user cancelled the dialog
if not bOk:
    QMessageBox.warning(
        parent,
        "Geoguesser",
        "User cancelled"
    )
    
else:
    
    try:
        
        # Convert input string into numerical coordinates
        lat, lon = map(float, sCoords.split(","))
        
        # Create a WGS84 point geometry
        point_wgs84 = QgsPointXY(lon, lat)
        
        # Define source and target coordinate systems
        #
        # EPSG:4326 = WGS84
        # Target CRS = CRS of district layer
        source_crs = QgsCoordinateReferenceSystem("EPSG:4326")
        target_crs = district_layer.crs()
        
        # Create coordinate transformation
        transform = QgsCoordinateTransform(
            source_crs,
            target_crs,
            QgsProject.instance()
        )
        
        # Transform point into district layer CRS
        point_projected = transform.transform(point_wgs84)
        
        # Convert transformed point into QgsGeometry
        point_geom = QgsGeometry.fromPointXY(point_projected)
        
        # Variable to track whether a district was found
        found = False
        
        # Loop through all city districts and check
        # if the point lies inside one of them
        for district in district_layer.getFeatures():
            
            if point_geom.within(district.geometry()):
                
                QMessageBox.information(
                    parent,
                    "Geoguesser",
                    f"The coordinates are inside:\n{district['Name']}"
                )
                
                found = True
                break
        
        # If no district was found        
        if not found:
            QMessageBox.information(
                parent,
                "Geoguesser",
                "The coordinates are outside Münster."
            )

    # Handle invalid user input       
    except:
        QMessageBox.warning(
            parent,
            "Geoguesser",
            "Invalid coordinate format."
        )