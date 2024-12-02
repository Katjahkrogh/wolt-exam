
document.addEventListener("DOMContentLoaded", function() {
    const modal = document.getElementById("modal"); 
    // Add event listener to all menuItem elements
    document.querySelector('#deleteBtn').addEventListener("click", function() {                 
        modal.showModal(); // Show the modal if it's found
    });

    document.querySelector("#modalClose").addEventListener("click", function () {
        modal.close(); // Show the modal if it's found
    });

}); 