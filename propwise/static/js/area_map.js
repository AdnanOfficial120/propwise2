// D:\propwise2\propwise\static\js\area_map.js

document.addEventListener('DOMContentLoaded', function() {

    // 1. Find the map <div> on the page
    const mapDiv = document.getElementById('area-map');

    // 2. If the map <div> doesn't exist on this page, or has no data, stop.
    if (!mapDiv || !mapDiv.dataset.lat || !mapDiv.dataset.amenitiesJson) {
        console.log("Map <div> or data not found. Stopping map script.");
        return; 
    }

    // 3. Get all the data we passed from Django
    const lat = mapDiv.dataset.lat;
    const lng = mapDiv.dataset.lng;
    const areaName = mapDiv.dataset.areaName;

    let amenities = [];
    try {
        // This is the line that was failing before
        amenities = JSON.parse(mapDiv.dataset.amenitiesJson);
    } catch (e) {
        console.error("Could not parse amenities JSON:", e, mapDiv.dataset.amenitiesJson);
        return; // Stop if the JSON is broken
    }

    // 4. Initialize the Map (using the data we got)
    const map = L.map('area-map').setView([lat, lng], 14);

    // 5. Add the OpenStreetMap Tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);

    // 6. Add the "Main" pin for the Area center
    try {
        const mainIcon = L.AwesomeMarkers.icon({
            icon: 'star',
            markerColor: 'cadetblue',
            prefix: 'fa'
        });

        L.marker([lat, lng], { icon: mainIcon })
            .addTo(map)
            .bindPopup(`<b>Center of ${areaName}</b>`)
            .openPopup();
    } catch (e) {
        console.error("Leaflet.AwesomeMarkers (mainIcon) failed to load:", e);
    }


    // 7. Loop through amenities and add new ICON pins
    amenities.forEach(function(amenity) {

        // --- THIS IS THE CRITICAL FIX ---
        // We check that 'amenity' is a real object and has all the data we need
        // before we try to use it. This will prevent the 'undefined' crash.
        if (amenity && amenity.lat && amenity.lng && amenity.icon && amenity.color) {

            try {
                // Create a new custom icon for *each* amenity
                const amenityIcon = L.AwesomeMarkers.icon({
                    icon: amenity.icon,     // This was line 28/29
                    markerColor: amenity.color,
                    prefix: 'fa'
                });

                // Create the marker and pass in our new custom icon
                L.marker([amenity.lat, amenity.lng], { icon: amenityIcon })
                    .addTo(map)
                    .bindPopup(`<b>${amenity.name}</b><br>${amenity.type}`);
            } catch (e) {
                console.error("Leaflet.AwesomeMarkers (amenityIcon) failed:", e);
            }
        }
    });
});