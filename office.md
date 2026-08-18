<!DOCTYPE html>
<html>
<head>
    <title>GeoJSON from Google Drive on Google Maps</title>
    <style>
        #map {
            height: 100vh;
            width: 100%;
        }
        html, body {
            height: 100%;
            margin: 0;
            padding: 0;
        }
    </style>
</head>
<body>

    <div id="map"></div>

    <script>
        let map;

        function initMap() {
            // 1. Initialize the Google Map background
            map = new google.maps.Map(document.getElementById("map"), {
                zoom: 4,
                center: { lat: 37.0902, lng: -95.7129 }, // Change default center coordinates
                mapTypeId: "roadmap" // Options: roadmap, satellite, hybrid, terrain
            });

            // 2. Format your Google Drive file URL for direct download
            // Replace YOUR_FILE_ID with the actual sharing ID from Google Drive
            const fileId = "d/1ohcxO_rf3Gk6-7IJSnKzQDO15QbdT4Zz";
            const driveGeoJsonUrl = `https://drive.google.com/uc?export=download&id=${fileId}`;

            // 3. Load the GeoJSON file into the Google Maps Data Layer
            map.data.loadGeoJson(driveGeoJsonUrl);

            // 4. (Optional) Style your GeoJSON features
            map.data.setStyle({
                fillColor: "red",
                strokeColor: "blue",
                strokeWeight: 2
            });
        }
    </script>

    {/* Load the Google Maps JavaScript API with your API key */}
    <script async defer
        src="https://maps.googleapis.com/maps/api/js?key=YOUR_GOOGLE_MAPS_API_KEY&callback=initMap">
    </script>

</body>
</html>
