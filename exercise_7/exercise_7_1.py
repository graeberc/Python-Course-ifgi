import os
import time

from qgis.PyQt.QtCore import QCoreApplication

from qgis.core import (
    QgsProject,
    QgsFeatureRequest,
    QgsDistanceArea,
    QgsProcessingAlgorithm,
    QgsProcessingParameterEnum,
    QgsProcessingParameterFileDestination
)

from qgis.utils import iface

from reportlab.lib.pagesizes import letter

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image
)

from reportlab.lib.styles import getSampleStyleSheet

import matplotlib.pyplot as plt
import html

class CreateCityDistrictProfile(QgsProcessingAlgorithm):
    
    # ---------------------------------------------------------
    # Parameter keys (used internally by QGIS Processing framework)
    # ---------------------------------------------------------
    
    CITY_DISTRICTS = "CITY_DISTRICTS"
    CHOICE_LAYER = "CHOICE_LAYER"
    PDF_OUTPUT = "PDF_OUTPUT"
    
    # ---------------------------------------------------------
    # Basic Metadata required by QGIS Processing framework
    # ---------------------------------------------------------
    
    def tr(self, string):
        # Translation wrapper 
        return QCoreApplication.translate("Processing", string)
        
    def createInstance(self):
        # Required by QGIS: allows the algorithm to be instantiated
        return CreateCityDistrictProfile()
        
    def name(self):
        # Internal algorithm name
        return "createcitydistrictprofile"
        
    def displayName(self):
        # Human-readable name shown in Processing Toolbox
        return self.tr("Create City District Profile")
    
    def group(self):
        # Group/category in Processing Toolbox
        return self.tr("City District Tools")
        
    def groupId(self):
        # Internal group ID
        return "citydistricttools"
        
    def shortHelpString(self):
        # Tooltip/help text shown in Processing dialog
        return self.tr(
            "Creates a PDF profile for a selected Münster city district."
        )
        
    # ----------------------------------------------------------
    # Helper function: builds dropdown list for city districts
    # ----------------------------------------------------------
    
    def getCityDistrictsList(self):
        
        # Reads all district names from the layer:
        # "Muenster_City_Districts"
        # and returns them as a sorted list for UI selection.
        district_layer = QgsProject.instance().mapLayersByName(
            "Muenster_City_Districts"
        )[0]
        
        names = []
        
        # No filter request -> iterates over all features
        request = QgsFeatureRequest()
        
        for feature in district_layer.getFeatures(request):
            # Assumes attribute field is called "Name"
            names.append(feature["Name"])
            
        return sorted(names)

    # ----------------------------------------------------------
    # Helper function: builds a bar chart of facility types
    # ----------------------------------------------------------

    def createStatisticalChart(self, pointLayer, district_geom):

        # Counts features by type within the district and
        # produces a bar chart image. Returns the image path and
        # a status flag indicating whether a chart was created.

        # Choose the right column name based on which layer
        # we're dealing with
        type_col = (
            "SchoolType"
            if pointLayer.name() == "Schools"
            else "Type"
        )

        counts = {}

        for feature in pointLayer.getFeatures():
            if district_geom.intersects(feature.geometry()):
                val = feature[type_col]
                counts[val] = counts.get(val, 0) + 1

        if not counts:
            # No features -> no chart
            return "", False

        # -----------------------------------------------------
        # Color definitions
        # Since the layers have no color attribute, we assign a
        # fixed color to each known type. Each type value (the
        # text stored in "SchoolType" / "Type") is mapped to a
        # color here. Unknown/missing types fall back to grey.
        # -----------------------------------------------------
        color_map = {
            # School types
            "Grundschule": "#4C72B0",
            "Hauptschule": "#DD8452",
            "Realschule": "#55A868",
            "Gesamtschule": "#C44E52",
            "Gymnasium": "#8172B3",
            "Förderschule": "#937860",
            "Berufskolleg": "#DA8BC3",
            "Montessorischule": "#E377C2",
            "PRIMUS-Schule": "#7F7F7F",
            "PTA-Berufsfachschule": "#BCBD22",
            "Schule für Kranke": "#17BECF",
            "Sekundarschule": "#AEC7E8",
            "Waldorfschule": "#FFBB78",
            "Weiterbildungskolleg": "#98DF8A",
            # Pool types
            "H": "#4C72B0",
            "F": "#55A868",
        }

        default_color = "#808080"

        labels = list(counts.keys())
        values = list(counts.values())

        # Build a per-bar color list (one color per label)
        bar_colors = [
            color_map.get(label, default_color)
            for label in labels
        ]

        # Build and save the bar chart
        plt.bar(labels, values, color=bar_colors)
        plt.title("Distribution by type")
        plt.ylabel("Count")

        chart_path = os.path.join(
            QgsProject.instance().homePath(),
            "temp_chart.png"
        )

        plt.savefig(chart_path, dpi=150, bbox_inches="tight")

        # Clear the figure so the next run starts fresh
        plt.clf()
        plt.close()

        return chart_path, True

    # -----------------------------------------------------------
    # GUI / Parameter definition
    # -----------------------------------------------------------
    
    def initAlgorithm(self, config=None):
        
        # Defines user input parameters for the Processing tool.
        self.addParameter(
            QgsProcessingParameterEnum(
                self.CITY_DISTRICTS,
                "Choose a city district",
                options = self.getCityDistrictsList(),
                usesStaticStrings = True
            )
        )
        
        # Dropdown: choose which point dataset to analyze
        # (schools OR pools)
        self.addParameter(
            QgsProcessingParameterEnum(
                self.CHOICE_LAYER,
                "Include statistics for:",
                options =  ["Schools", "Pools"],
                usesStaticStrings = True
            )
        )
        
        # Output file path for generated PDF
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.PDF_OUTPUT,
                "Output PDF file",
                fileFilter="PDF files (*.pdf)"
            )
        )
        
    # ---------------------------------------------------
    # Core statistics engine
    # ---------------------------------------------------
    
    def createStatistics(self, cityDistrictName, chosenLayer):

        # Computes spatial statistics for a given district:
        # - Area (km²)
        # - Number of houses (point-in-polygon)
        # - Number of parcels (polygon intersection)
        # - Number of selected facilities (schools or pools)
        # - Captures a map screenshot of the selected district
        
        # Load required layers from QGIS project
        districts = QgsProject.instance().mapLayersByName(
            "Muenster_City_Districts"
        )[0]

        houses = QgsProject.instance().mapLayersByName(
            "House_Numbers"
        )[0]

        parcels = QgsProject.instance().mapLayersByName(
            "Muenster_Parcels"
        )[0]

        # Choose dataset based on user input
        if chosenLayer == "Schools":
            pointLayer = QgsProject.instance().mapLayersByName(
                "Schools"
            )[0]
        else:
            pointLayer = QgsProject.instance().mapLayersByName(
                "public_swimming_pools"
            )[0]
        
        # -----------------------------------------------------
        # Find the selected district feature using attribute filter
        # -----------------------------------------------------
        request = QgsFeatureRequest()
        request.setFilterExpression(
            f'"Name" = \'{cityDistrictName}\''
        )

        districtFeature = None

        for feature in districts.getFeatures(request):
            districtFeature = feature
            break

        if districtFeature is None:
            raise Exception("District not found.")

        districtGeom = districtFeature.geometry()

        # -----------------------------------------------------
        # Calculate area using QgsDistanceArea (geodesic aware)
        # -----------------------------------------------------
        da = QgsDistanceArea()
        da.setEllipsoid("ETRS89")

        area_km2 = round(
            da.measureArea(districtGeom) / 1000000,
            2
        )

        # -----------------------------------------------------
        # Count houses inside district polygon
        # Point-in-polygon test using .within()
        # -----------------------------------------------------
        count_houses = 0

        for house in houses.getFeatures():
            if house.geometry().within(districtGeom):
                count_houses += 1

        # -----------------------------------------------------
        # Count parcels intersecting district polygon
        # Uses intersects (more permissive than within)
        # -----------------------------------------------------
        count_parcels = 0

        for parcel in parcels.getFeatures():
            if parcel.geometry().intersects(districtGeom):
                count_parcels += 1

        # -----------------------------------------------------
        # Count selected POI layer (schools or pools)
        # -----------------------------------------------------
        count_choice = 0

        for feature in pointLayer.getFeatures():
            if feature.geometry().within(districtGeom):
                count_choice += 1

        # -----------------------------------------------------
        # Build bar chart of facility types within district
        # -----------------------------------------------------
        chart_path, has_chart = self.createStatisticalChart(
            pointLayer,
            districtGeom
        )

        # -------------------------
        # Map export (screenshot of selected district)
        # -------------------------

        iface.setActiveLayer(districts)
        
        # Select only the chosen district feature
        districts.select(districtFeature.id())
        
        # Zoom map canvas to selection extent
        iface.mapCanvas().zoomToSelected(districts)

        iface.mapCanvas().refresh()

        # Delay ensures rendering completes before screenshot
        time.sleep(5)
        
        # Save temporary image inside project folder
        image_path = os.path.join(
            QgsProject.instance().homePath(),
            "temp_map.png"
        )
        
        # Export current canvas view to image
        iface.mapCanvas().saveAsImage(image_path)
        
        # Clear selection to restore clean state
        districts.removeSelection()
        
        # Return all computed values for report generation
        return {
            "district_name": districtFeature["Name"],
            "parent_district": districtFeature["P_District"],
            "area_km2": area_km2,
            "count_houses": count_houses,
            "count_parcels": count_parcels,
            "count_choice": count_choice,
            "chosen_layer": chosenLayer,
            "image_path": image_path,
            "chart_path": chart_path,
            "has_chart": has_chart
        }

    # ---------------------------------------------------
    # PDF generation using ReportLab
    # ---------------------------------------------------
    def createPDF(self, cityDistrict, layerChoice, pdf_output):
        # Builds a structured PDF report containing:
        # - Title
        # - Map image
        # - Statistical summary text
        
        # Compute all required stats first
        data = self.createStatistics(
            cityDistrict,
            layerChoice
        )
        
        # Create PDF document container
        pdf = SimpleDocTemplate(pdf_output)
        
        # Standard ReportLab styles (Title, Normal, etc.)
        styles = getSampleStyleSheet()

        content = []

        # Title

        content.append(
            Paragraph(
                f"City District Profile: {cityDistrict}",
                styles["Title"]
            )
        )

        content.append(Spacer(1, 20))

        # Map

        map_image = Image(
            data["image_path"],
            width=350,
            height=200
        )

        content.append(map_image)

        content.append(Spacer(1, 20))

        # Statistics heading

        content.append(
            Paragraph(
                "<b>Statistics</b>",
                styles["Heading2"]
            )
        )

        content.append(Spacer(1, 6))

        content.append(
            Paragraph(
                f"<b>Parent District:</b> "
                f"{html.escape(str(data['parent_district']))}",
                styles["Normal"]
            )
        )

        content.append(Spacer(1, 4))

        content.append(
            Paragraph(
                f"<b>Area:</b> "
                f"{html.escape(str(data['area_km2']))} km²",
                styles["Normal"]
            )
        )

        content.append(Spacer(1, 4))

        content.append(
            Paragraph(
                f"<b>Households:</b> "
                f"{html.escape(str(data['count_houses']))}",
                styles["Normal"]
            )
        )

        content.append(Spacer(1, 4))

        content.append(
            Paragraph(
                f"<b>Parcels:</b> "
                f"{html.escape(str(data['count_parcels']))}",
                styles["Normal"]
            )
        )

        content.append(Spacer(1, 4))

        if data["count_choice"] == 0:

            content.append(
                Paragraph(
                    f"No {html.escape(data['chosen_layer'].lower())} "
                    f"in this district.",
                    styles["Normal"]
                )
            )

        else:

            content.append(
                Paragraph(
                    f"{html.escape(str(data['count_choice']))} "
                    f"{html.escape(data['chosen_layer'].lower())} "
                    f"located in this district.",
                    styles["Normal"]
                )
            )

        # Chart (only if features of the chosen type were found)

        if data["has_chart"]:

            content.append(Spacer(1, 20))

            chart_image = Image(
                data["chart_path"],
                width=350,
                height=200
            )

            content.append(chart_image)

        pdf.build(content)

        # delete temporary image

        if os.path.exists(data["image_path"]):
            os.remove(data["image_path"])

        # delete temporary chart image

        if data["has_chart"] and os.path.exists(data["chart_path"]):
            os.remove(data["chart_path"])

    # ---------------------------------------------------
    # Main algorithm
    # ---------------------------------------------------

    def processAlgorithm(
        self,
        parameters,
        context,
        feedback
    ):
        
        # Reads user inputs, runs PDF generation, and returns output path.
        city_district = self.parameterAsString(
            parameters,
            self.CITY_DISTRICTS,
            context
        )

        layer_choice = self.parameterAsString(
            parameters,
            self.CHOICE_LAYER,
            context
        )

        pdf_path = self.parameterAsFileOutput(
            parameters,
            self.PDF_OUTPUT,
            context
        )
        
        # Run full pipeline: stats → map → PDF
        self.createPDF(
            city_district,
            layer_choice,
            pdf_path
        )
        
        # Return result to QGIS Processing model
        return {
            self.PDF_OUTPUT: pdf_path
        }