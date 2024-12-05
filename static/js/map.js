// Initialize the map
var map = L.map('map').setView([55.6800, 12.5660], 13);

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
                <article class="w-100% p-10 d-flex flex-col j-content-between overflow-hidden" hover="cursor-pointer scale-101 ts-500">
                <a href="${restaurant.url}" class="w-100%">
                    <div class="relative">
                        <img src="${restaurant.avatar_url}"
                            alt="${restaurant.name}" 
                            class="h-30 w-full obj-f-cover">
                    </div>
                    <div class="d-flex flex-row j-content-between a-items-center">
                        <div>
                            <h3 class="text-c-black mb-0">${restaurant.name}</h3>
                            <p class="text-c-grey4 text-90 ma-0">${restaurant.address}</p>
                        </div>
                    </div>
                </a>
                </article> 
            `);
        });
    } else {
        console.error("Error fetching restaurants:", data.error);
    }
}

// Call the function to load restaurants on map initialization
loadRestaurants();


