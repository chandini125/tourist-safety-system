const touristId = localStorage.getItem("tourist_id");
const touristName = localStorage.getItem("tourist_name");
const touristEmail = localStorage.getItem("tourist_email");

const nameElement = document.getElementById("touristName");
const idElement = document.getElementById("touristId");
const digitalIdElement = document.getElementById("digitalTouristId");

if (!touristId || !touristName) {
    window.location.href = "index.html";
} else {
    nameElement.textContent = touristName;

    idElement.textContent = touristId;

    digitalIdElement.textContent =
        "ST-" + String(touristId).padStart(6, "0");
}


document.getElementById("logoutBtn").addEventListener("click", function () {

    localStorage.removeItem("tourist_id");
    localStorage.removeItem("tourist_name");
    localStorage.removeItem("tourist_email");

    window.location.href = "index.html";
});
