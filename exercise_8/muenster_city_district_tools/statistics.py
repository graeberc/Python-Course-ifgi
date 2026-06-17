from qgis.core import QgsProject, QgsDistanceArea


class Statistics:
    """
    Central statistics engine for the Münster City District plugin.
    All spatial computations are reused in:
    - Profile window
    - Export (CSV/PDF)
    """

    # -----------------------------------------------------------
    # AREA
    # -----------------------------------------------------------
    def get_area_km2(self, district_feature):
        """
        Calculates district area in km² using ellipsoidal method.
        (Required: must NOT use Shape_Area)
        """

        geom = district_feature.geometry()

        da = QgsDistanceArea()
        da.setEllipsoid("ETRS89")

        area_m2 = da.measureArea(geom)
        return round(area_m2 / 1_000_000, 2)

    # -----------------------------------------------------------
    # HOUSEHOLDS
    # -----------------------------------------------------------
    def count_households(self, district_feature):
        """
        Counts House_Numbers points inside district (point-in-polygon)
        """

        layer = QgsProject.instance().mapLayersByName("House_Numbers")[0]
        poly = district_feature.geometry()

        count = 0
        for f in layer.getFeatures():
            if f.geometry().within(poly):
                count += 1

        return count

    # -----------------------------------------------------------
    # PARCELS
    # -----------------------------------------------------------
    def count_parcels(self, district_feature):
        """
        Counts parcels intersecting district
        """

        layer = QgsProject.instance().mapLayersByName("Muenster_Parcels")[0]
        poly = district_feature.geometry()

        count = 0
        for f in layer.getFeatures():
            if f.geometry().intersects(poly):
                count += 1

        return count

    # -----------------------------------------------------------
    # SCHOOLS
    # -----------------------------------------------------------
    def count_schools(self, district_feature):
        """
        Counts schools within district
        """

        layer = QgsProject.instance().mapLayersByName("Schools")[0]
        poly = district_feature.geometry()

        count = 0
        for f in layer.getFeatures():
            if f.geometry().within(poly):
                count += 1

        return count

    # -----------------------------------------------------------
    # POOLS
    # -----------------------------------------------------------
    def count_pools(self, district_feature):
        """
        Counts public swimming pools within district
        """

        layer = QgsProject.instance().mapLayersByName("public_swimming_pools")[0]
        poly = district_feature.geometry()

        count = 0
        for f in layer.getFeatures():
            if f.geometry().within(poly):
                count += 1

        return count

    # -----------------------------------------------------------
    # OPTIONAL: helper (cleaner profile building)
    # -----------------------------------------------------------
    def build_profile_dict(self, district_feature):
        """
        Convenience method used by the plugin to avoid repeated calls.
        """

        return {
            "name": district_feature["Name"],
            "parent": district_feature["P_District"],
            "area": self.get_area_km2(district_feature),
            "households": self.count_households(district_feature),
            "parcels": self.count_parcels(district_feature),
            "schools": self.count_schools(district_feature),
            "pools": self.count_pools(district_feature),
        }