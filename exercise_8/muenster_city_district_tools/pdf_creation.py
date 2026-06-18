# -*- coding: utf-8 -*-
import os
from qgis.core import QgsProject
from qgis.utils import iface
from .statistics import Statistics

def create_pdf_profile(feature, output_path):
    """
    Erstellt ein PDF-Profil für einen einzelnen Stadtbezirk.
    Inklusive automatischem Zoom und Kartenexport.
    """
    stats = Statistics()
    
    # 1. Daten über die Statistics-Engine berechnen
    profile = stats.build_profile_dict(feature)
    
    # 2. QGIS-Karte temporär exportieren
    # Holt den Bezirks-Layer und setzt ihn aktiv
    layers = QgsProject.instance().mapLayersByName("Muenster_City_Districts")
    if not layers:
        raise ValueError("Layer 'Muenster_City_Districts' nicht in QGIS gefunden!")
    layer = layers[0]
    iface.setActiveLayer(layer)
    
    # Zoomt die QGIS-Ansicht direkt auf das ausgewählte Feature
    layer.selectByIds([feature.id()])
    iface.mapCanvas().zoomToSelected(layer)
    iface.mapCanvas().refresh()
    
    # Pfad für das temporäre Kartenbild im Projektverzeichnis erzeugen
    image_path = os.path.join(QgsProject.instance().homePath(), "temp_district_map.png")
    iface.mapCanvas().saveAsImage(image_path)
    
    try:
        # Nutzung von ReportLab zur PDF-Erstellung
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Titel (Vorgabe: Name des Bezirks im Titel)
        title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=22, spaceAfter=15)
        story.append(Paragraph(f"Stadtbezirk-Profil: {profile['name']}", title_style))
        story.append(Spacer(1, 10))
        
        # Text-Informationen (Vorgabe: Alle geforderten Attribute)
        text_content = (
            f"<b>Übergeordneter Bezirk (P_District):</b> {profile['parent']}<br/>"
            f"<b>Berechnete Fläche:</b> {profile['area']} km² (Ellipsoidisch)<br/>"
            f"<b>Anzahl Haushalte:</b> {profile['households']}<br/>"
            f"<b>Anzahl Flurstücke (Parcels):</b> {profile['parcels']}<br/>"
            f"<b>Anzahl Schulen:</b> {profile['schools']}<br/>"
            f"<b>Anzahl Schwimmbäder:</b> {profile['pools']}"
        )
        body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=12, leading=18)
        story.append(Paragraph(text_content, body_style))
        story.append(Spacer(1, 20))
        
        # Kartenbild einbetten (Vorgabe: Map Image included)
        if os.path.exists(image_path):
            story.append(Image(image_path, width=400, height=300))
            
        doc.build(story)
        
    finally:
        # Wichtig: Temporäres Bild löschen, damit kein Müll zurückbleibt
        if os.path.exists(image_path):
            try:
                os.remove(image_path)
            except:
                pass