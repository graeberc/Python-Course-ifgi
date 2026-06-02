# -----------------------------------------------------------
# Exercise 6.1 Reading and creating data
# This script reads the CSV file standard_land_value_muenster
# and creates a completely new in-memory vector layer called
# temp_standard_land_value_muenster.
# The layer holds three fields:
#   - standard_land_value (float)
#   - type (string)
#   - district (string)
# and the geometry is created from the WKT column.
# -----------------------------------------------------------

import os

from qgis.PyQt.QtCore import QVariant
from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsField,
    QgsFeature,
    QgsGeometry,
    QgsCoordinateReferenceSystem,
)

# -----------------------------------------------------------
# Configuration – adjust path if needed
# -----------------------------------------------------------
csv_path = os.path.expandvars(
    r"%userprofile%\documents\PythonInQgisArcGis\standard_land_value_muenster.csv"
)

# CRS of the data (Münster: ETRS89 / UTM zone 32N)
crs = QgsCoordinateReferenceSystem("EPSG:25832")

# -----------------------------------------------------------
# Create the in-memory layer
# -----------------------------------------------------------
layer = QgsVectorLayer("MultiPolygon", "temp_standard_land_value_muenster", "memory")
layer.setCrs(crs)

provider = layer.dataProvider()

# Add the three required fields
provider.addAttributes([
    QgsField("standard_land_value", QVariant.Double),
    QgsField("type", QVariant.String),
    QgsField("district", QVariant.String),
])
layer.updateFields()

# -----------------------------------------------------------
# Read the CSV file line by line and create features
# -----------------------------------------------------------
features = []

with open(csv_path, "r", encoding="utf-8") as csv_file:
    lines = csv_file.readlines()

# Skip the header line (index 0); iterate over the data lines
for line in lines[1:]:
    # Strip the trailing newline and split on the semicolon delimiter
    values = line.strip("\n").split(";")

    # CSV columns: standard_land_value ; type ; district ; geometry
    raw_value = values[0].strip().replace(",", ".")   # handle "8,5" → "8.5"
    land_type  = values[1].strip()
    district   = values[2].strip()
    wkt        = values[3].strip()

    # Create geometry from WKT
    geom = QgsGeometry.fromWkt(wkt)
    if geom.isNull():
        continue  # skip rows with invalid geometry

    # Build the feature
    feature = QgsFeature(layer.fields())
    feature.setGeometry(geom)
    feature.setAttribute("standard_land_value", float(raw_value) if raw_value else None)
    feature.setAttribute("type", land_type)
    feature.setAttribute("district", district)

    features.append(feature)

# Add all features to the layer and refresh its extent
provider.addFeatures(features)
layer.updateExtents()

# -----------------------------------------------------------
# Add the finished layer to the QGIS project (map / TOC)
# -----------------------------------------------------------
QgsProject.instance().addMapLayer(layer)

print(
    f"Created layer 'temp_standard_land_value_muenster' "
    f"with {layer.featureCount()} features."
)
