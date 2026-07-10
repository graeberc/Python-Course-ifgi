from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtWebKitWidgets import QWebView

# Get the district name from the selected feature
district = "[%NAME%]"

# Build dynamic Wikipedia URL
url = QUrl("https://de.wikipedia.org/wiki/" + district.replace(" ","_"))

# Create web view window
view = QWebView()

# Load Wikipedia page
view.load(url)

# Show popup window
view.show()