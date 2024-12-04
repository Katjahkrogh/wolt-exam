
document.addEventListener("DOMContentLoaded", function() {
    const modal = document.getElementById("modal"); 

    document.querySelector('#deleteBtn').addEventListener("click", function() {                 
        modal.showModal(); 
    });

    document.querySelector("#modalClose").addEventListener("click", function () {
        modal.close(); 
    });

}); 