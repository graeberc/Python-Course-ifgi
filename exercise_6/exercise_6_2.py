from qgis.PyQt.QtCore import QVariant
from qgis.core import QgsProject, QgsField

# -----------------------------------------------------------
# Load layers
# -----------------------------------------------------------

# Swimming pools layer
pool_layer = QgsProject.instance().mapLayersByName("public_swimming_pools")[0]

# District polygon layer
district_layer = QgsProject.instance().mapLayersByName("Muenster_City_Districts")[0]

provider = pool_layer.dataProvider()

# -----------------------------------------------------------
# Change values in colum "Type"
# -----------------------------------------------------------

fields = pool_layer.fields()

type_idx = fields.indexOf("Type")

for feature in pool_layer.getFeatures():

    old_type = feature["Type"]

    if old_type == "H":
        new_value = "Hallenbad"

    elif old_type == "F":
        new_value = "Freibad"

    else: 
        continue

    provider.changeAttributreValues(
        {
            feature.id(): {
                type_idx: new_value
            }
        }
    )

# -----------------------------------------------------------
# 2. Add new field "district"
# -----------------------------------------------------------

district_field = QgsField(
    "district",
    QVariant.String,
    len = 50
)

provider.addAttributes([district_field])
pool_layer.updateFields()

district_idx = pool_layer.fields().indexOf("district")

# -----------------------------------------------------------
# 3. Determine district for each pool
# -----------------------------------------------------------

for pool in pool_layer.getFeatures():

    pool_geom = pool.geometry()

    district_name = None

    for district in district_layer.getFeatures():

        district_geom = district.geometry()

        if district_geom.contains(pool_geom):

            # Replace "Name" with the actual
            # district name field if necessary
            district_name = district["Name"]
            break

    provider.changeAttributeValues(
        {
            pool.id(): {
                district_idx: district_name
            }
        }
    )

print("Finished updating the swimming pools data.")