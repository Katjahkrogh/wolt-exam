src = "https://unpkg.com/leaflet/dist/leaflet.js";

// Initialize the map
var map = L.map('map').setView([55.6845, 12.564148], 12);

// Add OpenStreetMap tile layer
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 20,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

function test(){
    var markerLocations = [
    { coords: [51.5, -0.09], popup: "Marker 1: London" },
    { coords: [48.8566, 2.3522], popup: "Marker 2: Paris" },
    { coords: [40.7128, -74.0060], popup: "Marker 3: New York" },
    { coords: [55.6845, 12.564148], popup: "Marker 4: Tokyo" }
    ];

    // Loop through the markerLocations array and add markers to the map
    markerLocations.forEach(function(location) {
        var marker = L.marker(location.coords).addTo(map);
        marker.bindPopup(location.popup);
    });
}

setTimeout(test, 3000)
        