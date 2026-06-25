import arcpy
import os

# ------------------------------------------------------------------------------
# ArcPy Exercise 9
# Task 2.2: Cell phone reception coverage analysis
# Chosen route: Option A - use a helper field and a single buffer call
# ------------------------------------------------------------------------------

# Set the workspace
arcpy.env.workspace = os.path.expandvars(
    r"%userprofile%\Documents\PythonInQgisArcGis\exercise_arcpy_1.gdb"
)
arcpy.env.overwriteOutput = True


def build_coverage():

    # Project active_assets to a metric CRS so buffering happens in meters
    # (source data is in WGS 84 / degrees, EPSG:25832 is ETRS89 / UTM 32N)
    projected_fc = "active_assets_utm"
    metric_sr = arcpy.SpatialReference(25832)
    arcpy.management.Project("active_assets", projected_fc, metric_sr)

    # Add a helper field that holds the buffer distance per asset
    arcpy.management.AddField(projected_fc, "buffer_dist", "DOUBLE")

    # Calculate the buffer distance from the 'type' field
    expr = "dist(!type!)"
    codeblock = """
def dist(t):
    return {"mast": 300, "mobile_antenna": 50, "building_antenna": 100}.get(t, 0)
"""
    arcpy.management.CalculateField(
        projected_fc, "buffer_dist", expr, "PYTHON3", codeblock
    )

    # Buffer once, using the helper field as the (variable width) distance
    arcpy.analysis.Buffer(projected_fc, "coverage", "buffer_dist")

    print("Coverage feature class created successfully.")


def main():
    build_coverage()


if __name__ == "__main__":
    main()
