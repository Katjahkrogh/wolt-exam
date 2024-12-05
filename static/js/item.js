
document.addEventListener("DOMContentLoaded", function() {
    // Add event listener to all menuItem elements
    document.querySelectorAll('[id^="menuItem-"]').forEach(menuItem => {
            menuItem.addEventListener("click", function() {
            const itemId = menuItem.id.replace('menuItem-', '');                     
            const modal = document.getElementById('modal-' + itemId); // Get the corresponding modal by item ID

                if (modal) {
                    modal.showModal(); // Show the modal if it's found
                } else {
                    console.error('Modal not found for itemId: ' + itemId);
                }
            });
        });

    // Close the modal when the close button is clicked
    document.querySelectorAll('[id^="modalClose_"]').forEach(button => {
        button.addEventListener("click", function() {
            const itemId = button.id.replace('modalClose-', ''); // Extract itemId from the button's ID
            const modal = document.getElementById('modal-' + itemId); // Get the corresponding modal

            if (modal) {
                modal.close(); // Close the modal
            } else {
                console.error('Modal not found for itemId: ' + itemId);
            }
        });
    });
});
