import arcpy


class ToolValidator:
    # Controls the dynamic dropdown behaviour of the script tool.
    # Parameter layout (see exercise guide, section 0):
    #   params[0] -> Input Point (Feature Set)       -> the clicked point
    #   params[1] -> Evaluate-against feature class   -> e.g. stops_ms_mitte
    #   params[2] -> Name Field (String)             -> dropdown, filled dynamically
    #   params[3] -> Name Value (String)             -> dropdown, filled dynamically

    def __init__(self):
        # Grab the parameter objects of the tool (0-based).
        self.params = arcpy.GetParameterInfo()

    def initializeParameters(self):
        # Runs once when the tool opens. Nothing to prepare here.
        return

    def updateParameters(self):
        # Runs every time a parameter changes.

        # 2c - Fill the Name Field dropdown from the chosen feature class.
        # Only run once the evaluate-against feature class (params[1]) is set.
        if self.params[1].altered and self.params[1].value:
            # Read the fields of the selected feature class.
            fields = arcpy.Describe(self.params[1].value).fields
            # Skip special fields (geometry, object id, ...) that make no sense
            # as a "name field" and would break the value extraction below.
            skip_types = ("Geometry", "OID", "Blob", "Raster", "GUID", "GlobalID")
            field_names = [f.name for f in fields if f.type not in skip_types]
            # Offer these field names as the dropdown for the Name Field parameter.
            self.params[2].filter.list = field_names

        # 2d - Fill the Name Value dropdown from the chosen field's unique values.
        # Only run once both the feature class and the name field are set.
        if self.params[1].altered and self.params[2].altered and self.params[2].value:
            fc = self.params[1].value
            field = self.params[2].value
            # A set comprehension over a SearchCursor gives the unique values.
            values = {row[0] for row in arcpy.da.SearchCursor(fc, [field])}
            # Offer the sorted unique values as the dropdown for Name Value.
            self.params[3].filter.list = sorted(str(v) for v in values)

        return

    def updateMessages(self):
        # No custom validation messages needed.
        return
