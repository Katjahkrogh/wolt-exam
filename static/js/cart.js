const cartModal = document.getElementById("cartModal");
const cartOpen = document.querySelector("#cart");
const cartClose = document.querySelector("#cartClose");

const cartNumber = document.querySelector("#cartNumber");
const cartItemsContainer = document.querySelector("#cartItems");
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
        const itemId = this.id.split("-")[1]; // ikke split med - da det forkorte 
        addToCart(itemId, this);

        // Close the modal containing the clicked button
        const parentModal = this.closest("dialog");
        if (parentModal) {
            parentModal.close();
        }
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

    updateCart();
}

function updateCart() {
    cartItemsContainer.innerHTML = "";

    if (cartItems.length === 0) {
        cartItemsContainer.innerHTML = "<p>Your cart is empty.</p>";
        return;
    }

    cartItems.forEach((item, index) => {
        const cartItemElement = document.createElement("div");
        cartItemElement.classList.add("cart-item");
        cartItemElement.innerHTML = `
                <div class="d-flex flex-row j-content-between a-items-center">
                    <div class="d-flex flex-col">
                        <h3 class="ma-0">${item.title}</h3>
                        <p class="text-c-grey4">${item.price}</p>
                    </div>
                    <button class="remove-btn rounded-full bg-c-grey2" hover="bg-c-grey3" data-index="${index}">
                        <img src="/static/img/trash.svg" class="w-4 h-100%"></img>
                    </button>
                </div>
            `;
        cartItemsContainer.appendChild(cartItemElement);
        });

        // Attach event listeners to remove buttons
        const removeBtns = cartItemsContainer.querySelectorAll(".remove-btn");
        removeBtns.forEach((btn) => {
        btn.addEventListener("click", function () {
            const index = this.getAttribute("data-index");
            removeFromCart(index);
        });
    });
}

