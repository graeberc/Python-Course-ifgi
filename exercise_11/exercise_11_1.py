import arcpy, time

# ------------------------------------------------------------------------------
# ArcPy Exercise 11
# Task 1: Find the nearest bus stop 
# ------------------------------------------------------------------------------

arcpy.env.overwriteOutput = True

try:
        
    # Parameter 0: clicked point
    input_fc = arcpy.GetParameterAsText(0)

    # Parameter 1: feature class to evaluate againsst
    near_fc = arcpy.GetParameterAsText(1)

    # Parameter 2: field containing the stop names
    name_field = arcpy.GetParameterAsText(2)

    # Parameter 3: selected stop name
    name_value = arcpy.GetParameterAsText(3)

    # Progress bar
    arcpy.SetProgressor("step", "Starting..", 0, 3, 1)

    # Create a filtered Layer
    arcpy.SetProgressorLabel("Building filtered layer...")
    arcpy.SetProgressorPosition(1)
    time.sleep(2)

    sql = f"{arcpy.AddFieldDelimiters(near_fc, name_field)} = '{name_value}'"

    arcpy.management.MakeFeatureLayer(
        near_fc,
        "near_lyr",
        sql
    )

    # Run Near
    arcpy.SetProgressorLabel("Running Near analysis...")
    arcpy.SetProgressorPosition(2)
    time.sleep(2)

    arcpy.analysis.Near(
        input_fc,
        "near_lyr",
        distance_unit = "Meters"
    )

    # Read the result 
    arcpy.SetProgressorLabel("Reading results...")
    arcpy.SetProgressorPosition(3)
    time.sleep(2)

    distance = None

    with arcpy.da.SearchCursor(input_fc, ["NEAR_DIST"]) as cursor:
        for row in cursor:
            distance = row[0]


    # Display the results
    if distance is not None:
        arcpy.AddMessage(f"Selected bus stop: {name_value}")
        arcpy.AddMessage(f"Distance: {round(distance, 2)} meters")
    else:
        arcpy.AddWarning("No nearest feature could be found.")

# ArcGIS geoprocessing errors
except arcpy.ExecuteError:
    arcpy.AddError(arcpy.getMessages(2))

# Other Python errors
except Exception as e:
    arcpy.AddError(f"Unexpected error: {e}")