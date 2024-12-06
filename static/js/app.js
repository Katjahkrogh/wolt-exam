document.addEventListener("DOMContentLoaded", function () {

const cartModal = document.getElementById("cartModal");
const cartOpen = document.querySelector("#cart");
const cartClose = document.querySelector("#cartClose");

// open close cart
cartOpen.addEventListener("click", function () {
    cartModal.showModal();
});

cartClose.addEventListener("click", function () {
    cartModal.close();
});


// Add to cart
const addToCartBtns = document.querySelectorAll("[id^='addToCart-']");
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
            if (data.redirect) {
            window.location.href = data.redirect;
            } else if (data.error) {
            console.error(data.error);
            } else {
            console.log(data.cart);
            console.log(data.message);
            }
        })
        .catch((error) => console.error("Error adding to cart:", error));
}

// Remove from cart
const removeItemBtns = document.querySelectorAll("[id^='remove-']");
removeItemBtns.forEach((btn) => {
    btn.addEventListener("click", function () {
        const itemId = this.id.replace("remove-", "");
        fetch(`/remove-from-cart/${itemId}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ item_pk: itemId }),
        })
        .then((response) => response.json())
        .then((data) => {
            if (data.success) {
            if (data.item_removed) {
                // Remove the item from the DOM if it was removed
                this.closest("#cartItem").remove();
            } else {
                // Update the quantity if the item was not removed
                const quantityElement =
                this.closest("#cartItem").querySelector("#quantity");
                if (quantityElement && data.new_quantity > 1) {
                quantityElement.textContent = `x ${data.new_quantity}`;
                } else {
                    quantityElement.textContent = "";
                }
            }
            } else {
            console.error(data.error);
            }
        })
        .catch((error) => console.error("Error removing item from cart:", error));
    });
});


function render_items(data) {
    data = JSON.parse(data);
    data.forEach((e) => {
    console.log(e);
    var marker = L.marker(e.coords).addTo(map);
    marker.bindPopup(e.popup);
    });
}


});
