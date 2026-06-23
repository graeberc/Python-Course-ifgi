import arcpy

# ------------------------------------------------------------------------------
# ArcPy Exercise 9
# Task 2.1: Copy active assets
# ------------------------------------------------------------------------------

# Set the workspace
arcpy.env.workspace = r"C:\Users\cedri\OneDrive\Desktop\UNI\PythonInQGIS&ArcGIS\Session9\exercise_arcpy_1.gdb"
arcpy.env.overwriteOutput = True

def create_active_assets():

    # List all point feature classes in the geodatabase
    point_fcs = arcpy.ListFeatureClasses(feature_type="Point")

    # Fields to copy (geometry + attributes)
    fields = ["SHAPE@", "status", "type"]

    # Open insert cursor on the target feature class
    with arcpy.da.InsertCursor("active_assets", fields) as insert_cursor:

        # Loop through all point feature classes
        for fc in point_fcs:

            # Skip the target feature class to avoid reading from it
            if fc == "active_assets":
                continue

            print(f"Processing: {fc}")

            # Search only for rows where status = 'active'
            with arcpy.da.SearchCursor(
                fc,
                fields,
                where_clause = "status = 'active'"
            ) as search_cursor:
                
                # Copy each active row into active_assets
                for row in search_cursor:
                    insert_cursor.insertRow(row)
    
    print("All active assets have been copied successfully.")

def main():
    create_active_assets()

if __name__ == "__main__":
    main()