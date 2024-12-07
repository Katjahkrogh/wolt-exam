document.addEventListener("DOMContentLoaded", function () {
    const cartModal = document.getElementById("cartModal");
    const cartOpen = document.querySelector("#cart");
    const cartClose = document.querySelector("#cartClose");
    const addToCartBtns = document.querySelectorAll("[id^='addToCart-']");
    const cartNumber = document.querySelector("#cartNumber");


    // Open close cart
    cartOpen.addEventListener("click", function () {
        cartModal.showModal();
    });

    cartClose.addEventListener("click", function () {
        cartModal.close();
    });


    // Fetch cart total from the server
    fetch("/cart-total")
        .then((response) => response.json())
        .then((data) => {
            if (cartNumber) {
            const totalItems = data.total_items || 0;
            cartNumber.textContent = totalItems;

            // Toggle visibility based on total items
            if (totalItems > 0) {
                cartNumber.classList.remove("d-none");
            } else {
                cartNumber.classList.add("d-none");
            }
            }
        })
        .catch((error) => {
            console.error("Error fetching cart total:", error);
        });


    // Add to cart
    addToCartBtns.forEach((btn) => {
        btn.addEventListener("click", function () {
            const itemId = this.id.replace("addToCart-", "");
            addToCart(itemId);

            // Close the modal containing the clicked button
            const parentModal = this.closest("dialog");
            if (parentModal) {
                parentModal.close();
            }
        });
    });

    function addToCart(itemId) {
        fetch("/add-to-cart", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ item_pk: itemId }),
        })
        .then((response) => response.json())
        .then((data) => {
            if (data.error) {
                console.error(data.error);
            } else if (data.cart) {
                updateCartDisplay(data.cart); // Update cart modal 
                console.log(data.message);
            }
        })
        .catch((error) => console.error("Error adding to cart:", error));
    }


    // Update cart content
    function updateCartDisplay(cart) {
        const cartItemsContainer = document.getElementById("cartItems");
        cartItemsContainer.innerHTML = ""; 

        const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);

        const orderBtn =
            document.getElementById("orderBtn");
        orderBtn.classList.remove("d-none");

        if (cartNumber) {
            cartNumber.textContent = totalItems;

            // Toggle visibility
            if (totalItems > 0) {
                cartNumber.classList.remove("d-none");
            } else {
                cartNumber.classList.add("d-none");
            }
        }

        // If the cart is empty, display the empty cart message
        if (totalItems === 0) {

            orderBtn.classList.add("d-none");

            cartItemsContainer.innerHTML = `
                <div class="d-flex flex-col j-content-center a-items-center gap-6">
                    <img src="/static/img/emptyCart.svg" alt="empty cart" class="w-50 h-100%">
                    <h2>Your cart is empty</h2>
                </div>
            `;

        } else {
            
            orderBtn.classList.remove("d-none");

            cart.forEach((item) => {
                const cartItem = document.createElement("div");
                cartItem.className = "d-flex flex-row j-content-between a-items-center";
                cartItem.innerHTML = `
                    <div class="d-flex gap-4 j-content-start a-items-start">
                        <img src="/static/dishes/${item.item_image}" alt="${item.item_title}" 
                            class="h-12 w-22 obj-f-cover rounded-sm">
                        <div class="d-flex flex-col j-content-center">
                            <h3 class="ma-0">${item.item_title}</h3>
                            <p class="text-c-primary ma-0">DKK ${item.total_item_price}</p>
                        </div>
                    </div>
                    <div class="d-flex gap-4 a-items-center">
                        ${
                        item.quantity > 1
                            ? `<p id="quantity" class="text-100 text-w-semibold mt-3">x ${item.quantity}</p>`
                            : ""
                        }
                        <button id="remove-${item.item_pk}" class="rounded-full bg-c-grey2" hover="bg-c-grey3">
                            <img src="/static/img/trash.svg" class="w-4 h-100%">
                        </button>
                    </div>
                `;
                cartItemsContainer.appendChild(cartItem);
            });
        }

        // Reattach event listeners for remove buttons
        setRemoveItemListeners();
    }


    // Remove from cart 
    function setRemoveItemListeners() {
        const currentRemoveItemBtns = document.querySelectorAll("[id^='remove-']");
        
        currentRemoveItemBtns.forEach((btn) => {
            btn.removeEventListener('click', removeItemHandler);
            btn.addEventListener('click', removeItemHandler);
        });
    }

    function removeItemHandler(e) {
        // getting itemId for the clicked btn
        const itemId = e.currentTarget.id.replace("remove-", "");
        removeFromCart(itemId);
    }

    function removeFromCart(itemId) {
        fetch(`/remove-from-cart/${itemId}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
        })
        .then((response) => response.json())
        .then((data) => {
            if (data.success) {
                updateCartDisplay(data.cart);
            } else {
                console.error(data.error);
            }
        })
        .catch((error) =>
            console.error("Error removing item from cart:", error)
        );
    }

    // set up event listeners to btns again
    setRemoveItemListeners();
});