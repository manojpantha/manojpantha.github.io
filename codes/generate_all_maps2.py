import branca
import folium
import geopandas as gpd

# 1. Load all geospatial/JSON files (including district.json)
area_gdf = gpd.read_file("Basin_office_area1.geojson")
point_gdf = gpd.read_file("basin_office_point1.json")
rivers_gdf = gpd.read_file("rivers_light.geojson")
district_gdf = gpd.read_file("district.json")

# 2. Ensure all data files use Latitude/Longitude (EPSG:4326)
for gdf in [area_gdf, point_gdf, rivers_gdf, district_gdf]:
  if gdf.crs != "EPSG:4326":
    gdf.to_crs("EPSG:4326", inplace=True)

# 3. Initialize the Folium map with no default background tiles
m = folium.Map(tiles=None)

# 4. Automatically fit the initial zoom/extent to the basin polygon
bounds = area_gdf.total_bounds  # [minx, miny, maxx, maxy]
m.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])

# 5. Add Basemaps & Empty/White Background Option
folium.TileLayer(
    tiles="",
    attr="Blank Background",
    name="Empty White Background",
    overlay=False,
    control=True,
).add_to(m)

folium.TileLayer(
    tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
    attr="Google",
    name="Google Hybrid",
    overlay=False,
    control=True,
).add_to(m)

folium.TileLayer(
    tiles="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}",
    attr="Google",
    name="Google Streets",
    overlay=False,
    control=True,
).add_to(m)

folium.TileLayer("OpenStreetMap", name="OpenStreetMap").add_to(m)

# 6. Add Full-Width Title, Separated Search Bar, Decreased Footer Size, and Custom CSS to reposition Layer Control
title_html = """
             <div style="position: fixed; top: 0; left: 0; width: 100%; z-index:9999; background: white; padding: 12px 0px; border-bottom: 2px solid #ccc; text-align: center; box-shadow: 0px 2px 5px rgba(0,0,0,0.1);">
                 <h3 style="margin: 0; font-size:22px;"><b>जलस्रोत तथा सिंचाइ व्यवस्थापन आयोजना - जलस्रोत तथा सिंचाइ बिभाग</b></h3>
             </div>
             <style>
                 /* Push the layer control down so it doesn't get hidden under the top banner */
                 .leaflet-top.leaflet-right {
                     top: 60px !important;
                 }
             </style>
             """

search_html = """
              <div style="position: fixed; top: 70px; left: 50%; transform: translateX(-50%); z-index:9999; background: white; padding: 8px 15px; border-radius: 5px; border: 1px solid grey; box-shadow: 0px 0px 8px rgba(0,0,0,0.2); text-align: center; font-size: 13px;">
                  <b>Search Coordinates:</b> 
                  Lat: <input type="text" id="latInput" placeholder="e.g. 27.7172" style="width: 90px; padding: 2px;"> 
                  Lon: <input type="text" id="lonInput" placeholder="e.g. 85.3240" style="width: 90px; padding: 2px;">
                  <button onclick="zoomToCustomPoint()" style="background: #28a745; color: white; border: none; padding: 3px 10px; border-radius: 3px; cursor: pointer; font-weight: bold;">Go</button>
                  <button onclick="clearCustomPoint()" style="background: #dc3545; color: white; border: none; padding: 3px 10px; border-radius: 3px; cursor: pointer; font-weight: bold; margin-left: 5px;">Clear</button>
              </div>
              """

footer_html = """
              <div style="position: fixed; bottom: 10px; left: 10px; z-index:9999; font-size:17.5px; background-color: white; padding: 6px; border: 1px solid grey; border-radius: 3px;">
              Created by: <b>Manoj Pantha , S.D.E , DWRI</b>
              </div>
              """

m.get_root().html.add_child(branca.element.Element(title_html))
m.get_root().html.add_child(branca.element.Element(search_html))
m.get_root().html.add_child(branca.element.Element(footer_html))

# ---------------------------------------------------------
# 7. Layers Added in Reversed Order (Points on top)
# ---------------------------------------------------------

# Office Points Layer
folium.GeoJson(
    point_gdf,
    name="Office Points",
    marker=folium.Marker(icon=folium.Icon(color="green", icon="info-sign")),
    popup=folium.GeoJsonPopup(fields=list(point_gdf.columns.drop("geometry"))),
).add_to(m)

# Rivers Layer
folium.GeoJson(
    rivers_gdf,
    name="Rivers",
    style_function=lambda x: {"color": "blue", "weight": 2.5},
    popup=folium.GeoJsonPopup(fields=list(rivers_gdf.columns.drop("geometry"))),
).add_to(m)

# Basin Area Layer
folium.GeoJson(
    area_gdf,
    name="Office Basin Area",
    style_function=lambda x: {
        "fillColor": "transparent",
        "color": "darkorange",
        "weight": 3,
        "fillOpacity": 0.0,
    },
    popup=folium.GeoJsonPopup(fields=list(area_gdf.columns.drop("geometry"))),
).add_to(m)

# ---------------------------------------------------------
# 8. District Layer & District Labels FeatureGroup (Unchecked by default)
# ---------------------------------------------------------
district_group = folium.FeatureGroup(name="District Boundaries", overlay=True)

folium.GeoJson(
    district_gdf,
    style_function=lambda x: {
        "fillColor": "transparent",
        "color": "red",
        "weight": 2.5,
        "fillOpacity": 0.0,
    },
    popup=folium.GeoJsonPopup(fields=list(district_gdf.columns.drop("geometry"))),
).add_to(district_group)

district_label_field = "District"

for _, row in district_gdf.iterrows():
  if district_label_field in row and (dist_name := row[district_label_field]):
    geom = row.geometry
    if geom and not geom.is_empty:
      cent = geom.representative_point()
      lat, lon = cent.y, cent.x
      div_icon = folium.DivIcon(
          html=f'<div style="font-size: 9pt; font-weight: bold; color: white; text-shadow: -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000; width: max-content;">{dist_name}</div>',
      )
      folium.Marker(location=[lat, lon], icon=div_icon).add_to(district_group)

district_group.add_to(m)

# ---------------------------------------------------------
# 9. Other Map Labels (Office Points & Rivers)
# ---------------------------------------------------------
labels_group = folium.FeatureGroup(name="Map Labels", overlay=True)

for _, row in point_gdf.iterrows():
  if "Name2" in row and (pd_val := row["Name2"]):
    lat, lon = row.geometry.y, row.geometry.x
    div_icon = folium.DivIcon(
        html=f'<div style="font-size: 10pt; font-weight: bold; color: black; background-color: rgba(255, 255, 255, 0.7); padding: 2px; border-radius: 3px; width: max-content;">{pd_val}</div>',
        icon_anchor=(-10, 10),
    )
    folium.Marker(location=[lat, lon], icon=div_icon).add_to(labels_group)

for _, row in rivers_gdf.iterrows():
  if "RIV_NAM" in row and row["RIV_NAM"]:
    riv_name = row["RIV_NAM"]
    geom = row.geometry
    if geom and not geom.is_empty:
      midpoint = geom.interpolate(0.5, normalized=True)
      lat, lon = midpoint.y, midpoint.x
      div_icon = folium.DivIcon(
          html=f'<div style="font-size: 9pt; font-style: italic; color: #1f78b4; text-shadow: 1px 1px 0px #fff; width: max-content;">{riv_name}</div>',
      )
      folium.Marker(location=[lat, lon], icon=div_icon).add_to(labels_group)

labels_group.add_to(m)

# 10. Layer Control
folium.LayerControl().add_to(m)

# 11. Custom JavaScript for Dynamic Coordinate Search, Clear Function, and Pink Balloon Marker
custom_js = """
<script>
var customMarker = null;

function zoomToCustomPoint() {
    var lat = parseFloat(document.getElementById('latInput').value);
    var lon = parseFloat(document.getElementById('lonInput').value);
    
    if (isNaN(lat) || isNaN(lon)) {
        alert("Please enter valid numeric latitude and longitude coordinates.");
        return;
    }
    
    var mapObj = null;
    for (var key in window) {
        if (window[key] instanceof L.Map) {
            mapObj = window[key];
            break;
        }
    }
    
    if (mapObj) {
        mapObj.setView([lat, lon], 14);
        
        if (customMarker) {
            mapObj.removeLayer(customMarker);
        }
        
        var distinctPinkIcon = L.divIcon({
            className: 'custom-pink-balloon',
            html: '<div style="background-color: #ff69b4; width: 24px; height: 24px; border-radius: 50% 50% 50% 0; transform: rotate(-45deg); left: -4px; top: -4px; position: relative; box-shadow: 0 3px 6px rgba(0,0,0,0.4); border: 2px solid white;"><div style="background: white; width: 8px; height: 8px; border-radius: 50%; position: absolute; top: 6px; left: 6px;"></div></div>',
            iconSize: [24, 24],
            iconAnchor: [12, 24],
            popupAnchor: [0, -24]
        });
        
        customMarker = L.marker([lat, lon], {icon: distinctPinkIcon}).addTo(mapObj);
        customMarker.bindPopup("<b>Custom Searched Location</b><br>Lat: " + lat + "<br>Lon: " + lon).openPopup();
    }
}

function clearCustomPoint() {
    var mapObj = null;
    for (var key in window) {
        if (window[key] instanceof L.Map) {
            mapObj = window[key];
            break;
        }
    }
    
    if (mapObj && customMarker) {
        mapObj.removeLayer(customMarker);
        customMarker = null;
    }
    
    document.getElementById('latInput').value = '';
    document.getElementById('lonInput').value = '';
}

window.addEventListener('load', function() {
    setTimeout(function() {
        var labels = document.querySelectorAll('.leaflet-control-layers-overlays label');
        labels.forEach(function(label) {
            if (label.innerText.includes('District Boundaries')) {
                var checkbox = label.querySelector('input[type="checkbox"]');
                if (checkbox && checkbox.checked) {
                    checkbox.click();
                }
            }
        });
    }, 400);
});
</script>
"""
m.get_root().html.add_child(folium.Element(custom_js))

# 12. Save
m.save("dwri.html")
print(
    "Map generated successfully with the layer control shifted safely below the"
    " banner!"
)