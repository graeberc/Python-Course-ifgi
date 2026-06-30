import arcpy
import os

# ------------------------------------------------------------------------------
# ArcPy Exercise 10
# Task 1: Find the nearest bus stop
# ------------------------------------------------------------------------------

# Set the workspace
arcpy.env.workspace = os.path.expandvars(
    r"C:\Users\cedri\OneDrive\Desktop\UNI\PythonInQGIS&ArcGIS\Session10\arcpy_2.gdb"
)
arcpy.env.overwriteOutput = True

# Input feature class (contains ONE point)
input_fc = r"C:\Users\cedri\OneDrive\Desktop\UNI\PythonInQGIS&ArcGIS\Session10\arcpy_2.gdb\input_point"

# Feature class containing the bus stops
near_features = "stops_ms_mitte"

# Output datasets (new projected copies)
input_proj = "input_point_utm"
stops_proj = "stops_utm"

# Define coordinate system
sr = arcpy.SpatialReference(25832)

# Project both layers
arcpy.management.Project(input_fc, input_proj, sr)
arcpy.management.Project(near_features, stops_proj, sr)

# Run the Near tool
# This adds the fields NEAR_DIST and NEAR_FID to input_fc
arcpy.analysis.Near(
    input_proj,
    stops_proj,
    distance_unit="Meters"
)

# Read the distance and ObjectID of the nearest bus stop
distance = None
near_fid = None

with arcpy.da.SearchCursor(input_proj, ["NEAR_DIST", "NEAR_FID"]) as cursor:
    for row in cursor:
        distance = row[0]
        near_fid = row[1]

# Look up the name of the nearest bus stop
stop_name = ""

where_clause = f"OBJECTID = {near_fid}"

with arcpy.da.SearchCursor(
        stops_proj,
        ["OBJECTID", "name"],
        where_clause) as cursor:

    for row in cursor:
        stop_name = row[1]

# Display the results
arcpy.AddMessage(f"Distance: {round(distance, 2)} meters")
arcpy.AddMessage(f"Nearest bus stop: {stop_name}")