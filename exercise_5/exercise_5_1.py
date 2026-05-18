# -----------------------------------------------------------
# Exercise 5.1 - Where is my next school?
# -----------------------------------------------------------

from qgis.PyQt.QtWidgets import QInputDialog, QMessageBox
from qgis.core import *

# Get QGIS main window
parent = iface.mainWindow()

# Access project layers
district_layer = QgsProject.instance().mapLayersByName("Muenster_City_Districts")[0]
school_layer = QgsProject.instance().mapLayersByName("Schools")[0]

# -----------------------------------------------------------
# Create sorted lsit of district names
# -----------------------------------------------------------
district_names = sorted([f["Name"] for f in district_layer.getFeatures()])

# Open dropdown dialog 
sDistrict, bOk = QInputDialog.getItem(
    parent,
    "District Names",
    "Select District:",
    district_names
)

# Handle cancel action
if not bOk:
    QMessageBox.warning(parent, "Schools", "User cancelled")

else:

    # Find selected district feature
    request = QgsFeatureRequest()
    request.setFilterExpression(f'"Name" = \'{sDistrict}\'')

    district_feature = next(district_layer.getFeatures(request))
    district_geom = district_feature.geometry()
    centroid_geom = district_geom.centroid()

    school_info = []
    school_ids = []

    # -------------------------------------------------------
    # Find schools inside district
    # -------------------------------------------------------
    for school in school_layer.getFeatures():

        school_geom = school.geometry()

        if school_geom.intersects(district_geom):

            school_ids.append(school.id())

            # Calculate distance directly from geometry
            distance_m = school_geom.distance(centroid_geom)
            distance_km = round(distance_m / 1000, 2)

            school_info.append((
                school["Name"],
                school["SchoolType"],   
                distance_km
            ))

    # Sort alphabetically by school name
    school_info.sort(key=lambda x: x[0])

    # Handle no schools found
    if not school_info:
        QMessageBox.information(
            parent,
            f"Schools in {sDistrict}",
            "No schools found."
        )

    else:

        msg = "\n".join([
            f"{name} ({stype}) - {dist} km"
            for name, stype, dist in school_info
        ])

        QMessageBox.information(
            parent,
            f"Schools in {sDistrict}",
            msg
        )

        # Select + zoom
        school_layer.removeSelection()
        school_layer.selectByIds(school_ids)
        iface.mapCanvas().zoomToSelected(school_layer)