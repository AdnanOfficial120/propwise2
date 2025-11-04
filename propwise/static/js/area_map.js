// D:\propwise2\propwise\static\js\area_map.js

document.addEventListener('DOMContentLoaded', function() {

    // 1. Find the map <div> on the page
    const mapDiv = document.getElementById('area-map');

    // 2. If the map <div> doesn't exist on this page, stop.
    if (!mapDiv) {
        return;
    }

    // 3. Get all the data we passed from Django (from the 'data-*' attributes)
    const lat = mapDiv.dataset.lat;
    const lng = mapDiv.dataset.lng;
    const areaName = mapDiv.dataset.areaName;

    // We must 'parse' the amenities string back into a JavaScript list
    const amenities = JSON.parse(mapDiv.dataset.amenitiesJson);

    // 4. Initialize the Map (using the data we got)
    const map = L.map('area-map').setView([lat, lng], 14); // 14 is a good "neighborhood" zoom

    // 5. Add the OpenStreetMap Tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);

    // 6. Add the "Main" pin for the Area center
    L.marker([lat, lng])
        .addTo(map)
        .bindPopup(`<b>Center of ${areaName}</b>`)
        .openPopup();

    // 7. Loop through the amenities and add *new* pins
    amenities.forEach(function(amenity) {
        L.marker([amenity.lat, amenity.lng])
            .addTo(map)
            .bindPopup(`<b>${amenity.name}</b><br>${amenity.type}`);
    });
});