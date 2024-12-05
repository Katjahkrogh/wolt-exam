document.addEventListener("DOMContentLoaded", () => {
    const searchToggle = document.getElementById("searchToggle");
    const profileBtn = document.getElementById("profileBtn");
    const searchForm = document.getElementById("searchForm");
    const searchInput = document.getElementById("search");

    // Show search field and hide button
    searchToggle.addEventListener("click", () => {
        searchForm.classList.add("d-block");
        searchForm.classList.remove("d-none");
        profileBtn.classList.add("d-none");
        profileBtn.classList.remove("d-block");
        searchToggle.classList.add("d-none");
        searchInput.focus();
    });

    // If user search hide search field and show button
    document.addEventListener("click", (event) => {
        if (!searchForm.contains(event.target) && !searchToggle.contains(event.target)) {
            searchForm.classList.add("d-none");
            searchForm.classList.remove("d-block");
            searchToggle.classList.remove("d-none");
        }
    });
});