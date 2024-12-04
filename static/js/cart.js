const cartModal = document.getElementById("cartModal");
const cartOpen = document.querySelector("#cart");
const cartClose = document.querySelector("#cartClose");

const cartNumber = document.querySelector("#cartNumber");
const cartItems = [];

document.addEventListener("DOMContentLoaded", function () {
    cartOpen.addEventListener("click", function () {
    cartModal.showModal();
    });

    cartClose.addEventListener("click", function () {
    cartModal.close();
    });

    // Attach event listeners to dynamically generated Add to Cart buttons
    const addToCartBtns = document.querySelectorAll("[id^='addToCart-']");
    addToCartBtns.forEach((btn) => {
    btn.addEventListener("click", function () {
        const itemId = this.id.split("-")[1];
        addToCart(itemId, this); // Pass the clicked button and itemId
    });
    });
});

function addToCart(itemId, button) {
    console.log(`Added item with ID: ${itemId}`);

    // Increment the total cart number
    let totalItemsNumber = parseInt(cartNumber.innerHTML) || 0;
    totalItemsNumber++;
    cartNumber.innerHTML = totalItemsNumber;

    // store item in cartItems array
    const container = button.closest("[id^='modal-']");
    const itemTitle = container.querySelector("[id^='title-']").innerText;
    const itemPrice = container.querySelector("[id^='price-']").innerText;

    cartItems.push({
    id: itemId,
    title: itemTitle,
    price: itemPrice,
    });

    console.log("Cart Items:", cartItems);

}
