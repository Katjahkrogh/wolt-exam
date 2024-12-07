// Initialize the map
var map = L.map('map').setView([55.6800, 12.5660], 13.3);

// Add OpenStreetMap tile layer
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 20,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

// Fetch restaurants from Flask API
async function loadRestaurants() {
    const response = await fetch('/api/restaurants');
    const data = await response.json();

    if (data.restaurants) {
        data.restaurants.forEach(restaurant => {
            const marker = L.marker([restaurant.latitude, restaurant.longitude]).addTo(map);
            marker.bindPopup(`
                <a href="${restaurant.url}" class="w-100%">
                <article class="w-100% p-8 d-flex flex-col gap-4 j-content-between overflow-hidden" hover="cursor-pointer scale-101 ts-500">
                    <div>
                        <img src="${restaurant.avatar_url}"
                            alt="${restaurant.name}" 
                            class="h-30 w-full obj-f-cover rounded-md shadow-md">
                    </div>
                    <div>
                        <h3 class="text-c-black mb-0">${restaurant.name}</h3>
                        <p class="text-c-primary text-90 mt-0 pa-0">${restaurant.address}</p>
                    </div>
                </article> 
                </a>
            `);
        });
    } else {
        console.error("Error fetching restaurants:", data.error);
    }
}

// Call the function to load restaurants on map initialization
loadRestaurants();

