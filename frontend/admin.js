const touristId = 3;

let adminMap = null;
let touristMarker = null;


function initializeMap(latitude, longitude) {

    if (!adminMap) {

        adminMap = L.map("adminMap").setView(
            [latitude, longitude],
            15
        );

        L.tileLayer(
            "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
            {
                attribution: "&copy; OpenStreetMap contributors"
            }
        ).addTo(adminMap);
    }

    if (!touristMarker) {

        touristMarker = L.marker(
            [latitude, longitude]
        ).addTo(adminMap);

        touristMarker.bindPopup(
            "Tourist " + touristId
        );

    } else {

        touristMarker.setLatLng(
            [latitude, longitude]
        );
    }

    adminMap.setView(
        [latitude, longitude],
        15
    );
}


async function loadLatestLocation() {

    try {

        const response = await fetch(
            `http://127.0.0.1:8000/locations/${touristId}`
        );

        const locations = await response.json();

        if (!response.ok) {
            throw new Error(
                locations.detail || "Failed to load locations"
            );
        }

        if (locations.length === 0) {

            document.getElementById(
                "locationStatus"
            ).textContent =
                "No location data available.";

            return;
        }

        const latest = locations[0];

        document.getElementById(
            "touristId"
        ).textContent = latest.tourist_id;

        document.getElementById(
            "latitude"
        ).textContent = latest.latitude;

        document.getElementById(
            "longitude"
        ).textContent = latest.longitude;

        document.getElementById(
            "speed"
        ).textContent = latest.speed;

        document.getElementById(
            "timestamp"
        ).textContent = latest.timestamp;

        document.getElementById(
            "locationStatus"
        ).textContent =
            "Tourist location received successfully.";

        initializeMap(
            latest.latitude,
            latest.longitude
        );

        console.log(
            "LATEST LOCATION:",
            latest
        );

    } catch (error) {

        console.error(
            "Location loading error:",
            error
        );

        document.getElementById(
            "locationStatus"
        ).textContent =
            "Unable to load tourist location.";
    }
}


document.getElementById(
    "refreshBtn"
).addEventListener(
    "click",
    loadLatestLocation
);


loadLatestLocation();
async function loadAlerts() {

    const container =
        document.getElementById("alertsContainer");

    try {

        const response = await fetch(
            `http://127.0.0.1:8000/alerts/${touristId}`
        );

        const alerts = await response.json();

        if (!response.ok) {
            throw new Error(
                alerts.detail || "Failed to load alerts"
            );
        }

        if (alerts.length === 0) {
            container.textContent =
                "No safety alerts found.";
            return;
        }

        container.innerHTML = alerts.map(alert => `
            <div class="alert-item">
                <strong>${alert.alert_type}</strong>
                <span>Risk: ${alert.risk_level}</span>
                <p>${alert.message || "No message"}</p>
                <small>${alert.created_at}</small>
            </div>
        `).join("");

    } catch (error) {

        console.error("Alert loading error:", error);

        container.textContent =
            "Unable to load alerts.";
    }
}

loadAlerts();

setInterval(loadAlerts, 5000);
async function loadTourists() {
    const tableBody = document.getElementById("touristsBody");

    try {
        const response = await fetch(
            "http://127.0.0.1:8000/tourists"
        );

        const tourists = await response.json();

        if (!response.ok) {
            throw new Error(
                tourists.detail || "Failed to load tourists"
            );
        }

        if (tourists.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="4">No registered tourists found.</td>
                </tr>
            `;
            return;
        }

        tableBody.innerHTML = tourists.map(tourist => `
            <tr>
                <td>${tourist.tourist_id}</td>
                <td>${tourist.name}</td>
                <td>${tourist.email}</td>
                <td>${tourist.created_at}</td>
            </tr>
        `).join("");

    } catch (error) {
        console.error("Tourist loading error:", error);

        tableBody.innerHTML = `
            <tr>
                <td colspan="4">
                    Unable to load tourists.
                </td>
            </tr>
        `;
    }
}

loadTourists();
async function loadAIRisk() {
    try {
        const response = await fetch(
            `http://127.0.0.1:8000/tourist-risk/${touristId}`
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "AI risk calculation failed"
            );
        }

        document.getElementById("riskTouristId").textContent =
            data.tourist_id;

        document.getElementById("riskScore").textContent =
            data.risk_score;

        document.getElementById("riskLevel").textContent =
            data.risk_level;
	const riskElement = document.getElementById("riskLevel");

riskElement.className = "";

riskElement.classList.add(
    "risk-" + data.risk_level.toLowerCase()
);
       const riskMessage = document.getElementById("riskMessage");

if (data.risk_level === "LOW") {
    riskMessage.textContent =
        "LOW RISK — Tourist movement appears normal.";
} else if (data.risk_level === "MEDIUM") {
    riskMessage.textContent =
        "MEDIUM RISK — Continue monitoring the tourist.";
} else if (data.risk_level === "HIGH") {
    riskMessage.textContent =
        "HIGH RISK — Attention is required.";
} else if (data.risk_level === "CRITICAL") {
    riskMessage.textContent =
        "CRITICAL RISK — Immediate attention required.";
}

        console.log("REAL AI RISK:", data);

    } catch (error) {

        console.error("Admin AI risk error:", error);

        document.getElementById("riskMessage").textContent =
            "Unable to calculate AI risk.";
    }
}
loadAIRisk();
setInterval(loadAIRisk,5000);
async function loadDigitalIDVerification() {
    const digitalId = "ST-000003";

    try {
        const response = await fetch(
            `http://127.0.0.1:8000/digital-id/verify/${digitalId}`
        );

        const data = await response.json();

        document.getElementById("adminDigitalId").textContent =
            data.digital_id;

        const statusElement =
            document.getElementById("adminVerificationStatus");

        statusElement.textContent =
            data.verification_status;

        const message =
            document.getElementById("blockchainMessage");

        if (data.verification_status === "VALID") {
            message.textContent =
                "✓ Digital ID verified. Identity hash matches the stored record.";
        } else {
            message.textContent =
                "⚠ Digital ID verification failed. Identity data may have been tampered with.";
        }

    } catch (error) {
        console.error("Digital ID verification error:", error);

        document.getElementById("adminVerificationStatus").textContent =
            "ERROR";

        document.getElementById("blockchainMessage").textContent =
            "Unable to verify Digital ID.";
    }
}

loadDigitalIDVerification();
