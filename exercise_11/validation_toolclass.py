import arcpy


class ToolValidator:
    # Parameter layout:
    #   params[0] -> Input Point
    #   params[1] -> Feature class to evaluate against
    #   params[2] -> Name Field (dropdown, filled dynamically)
    #   params[3] -> Name Value (dropdown, filled dynamically)

    def __init__(self):
        self.params = arcpy.GetParameterInfo()

    def initializeParameters(self):
        return

    def updateParameters(self):
        # Fill the Name Field dropdown with the fields of the chosen feature class
        if self.params[1].altered and self.params[1].value:
            fields = arcpy.Describe(self.params[1].value).fields
            skip_types = ("Geometry", "OID", "Blob", "Raster", "GUID", "GlobalID")
            field_names = [f.name for f in fields if f.type not in skip_types]
            self.params[2].filter.list = field_names

        # Fill the Name Value dropdown with the unique values of the chosen field
        if self.params[1].altered and self.params[2].altered and self.params[2].value:
            fc = self.params[1].value
            field = self.params[2].value
            values = {row[0] for row in arcpy.da.SearchCursor(fc, [field])}
            self.params[3].filter.list = sorted(str(v) for v in values)

        return

    def updateMessages(self):
        return
