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
let map;
let marker;
let  lastLatitude =null;
let lastLongitude=null;
let stationaryStartTime=null;
const routeLatitude=14.4674;
const routeLongitude=78.8241;
const routeDeviationDistance=500;
function calculateStationaryTime(latitude, longitude) {

    if (lastLatitude === null || lastLongitude === null) {
        lastLatitude = latitude;
        lastLongitude = longitude;
        stationaryStartTime = Date.now();

        return 0;
    }

    const previousLocation = L.latLng(
        lastLatitude,
        lastLongitude
    );

    const currentLocation = L.latLng(
        latitude,
        longitude
    );

    const distance = previousLocation.distanceTo(
        currentLocation
    );

    // Consider the tourist stationary if movement is less than 10 meters
    if (distance < 10) {

        const stationaryTime =
            (Date.now() - stationaryStartTime) / 60000;

        return stationaryTime;

    } else {

        lastLatitude = latitude;
        lastLongitude = longitude;
        stationaryStartTime = Date.now();

        return 0;
    }
}
function calculateRouteDeviation(latitude, longitude) {

    const expectedLocation = L.latLng(
        routeLatitude,
        routeLongitude
    );

    const currentLocation = L.latLng(
        latitude,
        longitude
    );

    const distance = expectedLocation.distanceTo(
        currentLocation
    );

    return distance > routeDeviationDistance;
}
function isNightMovement(){
	const hour =new Date().getHours();
	return hour>=22 ||hour<6;
}
if ("geolocation" in navigator) {

    navigator.geolocation.watchPosition(
        function (position) {

            const latitude = position.coords.latitude;
            const longitude = position.coords.longitude;
	const speed =position.coords.speed || 0;
	const stationaryTime=calculateStationaryTime(latitude,longitude);	  
	const routeDeviation=calculateRouteDeviation(latitude,longitude);
	const nightMovement = isNightMovement();
 checkZone(latitude,longitude,speed,stationaryTime,routeDeviation,nightMovement);
            if (!map) {

                map = L.map("map").setView(
                    [latitude, longitude],
                    16
                );

                L.tileLayer(
                    "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
                    {
                        attribution: "&copy; OpenStreetMap contributors"
                    }
                ).addTo(map);

                marker = L.marker([latitude, longitude])
                    .addTo(map)
                    .bindPopup("Your current location")
                    .openPopup();
                     loadZones();
            } else {

                marker.setLatLng([latitude, longitude]);

                map.setView(
                    [latitude, longitude],
                    16
                );

            }
        },

        function (error) {
            console.error("GPS error:", error);
        }
    );

} else {
    console.error("Geolocation is not supported.");
}
async function loadZones() {
    try {
        const response = await fetch("http://127.0.0.1:8000/zones");
        const zones = await response.json();

        zones.forEach(function (zone) {

            let zoneColor = "green";

if (zone.zone_type === "RESTRICTED") {
    zoneColor = "orange";
}

if (zone.zone_type === "DANGER") {
    zoneColor = "red";
}

L.circle(
    [zone.latitude, zone.longitude],
    {
        radius: zone.radius,
        color: zoneColor,
        fillColor: zoneColor,
        fillOpacity: 0.25
    }
)
            .addTo(map)
            .bindPopup(
                "<strong>" + zone.zone_name + "</strong><br>" +
                "Type: " + zone.zone_type + "<br>" +
                "Risk: " + zone.risk_level + "<br>" +
                zone.description
            );
        });
	map.setView([zones[0].latitude,zones[0].longitude],14);
    } catch (error) {
        console.error("Unable to load zones:", error);
    }
}
async function checkZone(latitude, longitude,speed,stationaryTime,routeDeviation,nightMovement) {

    fetch("http://127.0.0.1:8000/zones")
        .then(response => response.json())
        .then(async zones => {

            let highestRiskZone = null;
            let highestRiskScore = -1;

            const riskScores = {
                LOW: 1,
                MEDIUM: 2,
                HIGH: 3,
                CRITICAL: 4
            };

            zones.forEach(function (zone) {

                const touristLocation = L.latLng(
                    latitude,
                    longitude
                );

                const zoneLocation = L.latLng(
                    zone.latitude,
                    zone.longitude
                );

                const distance =
                    touristLocation.distanceTo(zoneLocation);

                if (distance <= zone.radius) {

                    console.log(
                        "ZONE ALERT:",
                        zone.zone_name,
                        "Distance:",
                        Math.round(distance) + " meters"
                    );

                    const score =
                        riskScores[zone.risk_level] || 0;

                    if (score > highestRiskScore) {
                        highestRiskScore = score;
                        highestRiskZone = zone;
                    }
                }
            });

            if (highestRiskZone) {

    const safetyStatus =
        document.getElementById("safetyStatus");
    const riskLevel=document.getElementById("riskLevel");
    if (highestRiskZone.zone_type === "SAFE") {
        safetyStatus.textContent = "SAFE";
    }

    if (highestRiskZone.zone_type === "RESTRICTED") {
        safetyStatus.textContent = "RESTRICTED";
    }

    if (highestRiskZone.zone_type === "DANGER") {
        safetyStatus.textContent = "DANGER";
    }

    showZoneAlert(
        highestRiskZone,
        latitude,
        longitude
    );
const aiResult = await getAIRisk(
    highestRiskZone.risk_level,
    speed,
    stationaryTime,
    routeDeviation,
    nightMovement
);

if (aiResult) {
    console.log("ZONE AI RISK:", aiResult);
    riskLevel.textContent=aiResult.risk_level

}
}

        })
        .catch(error => {
            console.error("Zone detection error:", error);
        });
}
async function showZoneAlert(zone, latitude, longitude) {

    const alertBox = document.getElementById("alertBox");
    const touristId = localStorage.getItem("tourist_id");

    let icon = "✓";
    let message = "You are in a safe tourist area.";

    if (zone.zone_type === "RESTRICTED") {
        icon = "⚠️";
        message = "You have entered a restricted area. Please leave the zone.";
    }

    if (zone.zone_type === "DANGER") {
        icon = "🚨";
        message = "Danger zone detected. Move to a safe area immediately.";
    }

    // Show alert on dashboard
    alertBox.innerHTML = `
        <span>${icon}</span>

        <div>
            <strong>${zone.zone_name}</strong>

            <p>
                ${message}<br>
                Risk level: ${zone.risk_level}.
            </p>
        </div>
    `;

    // Save only actual risk zones to database
    if (zone.zone_type === "SAFE") {
        return;
    }

    try {

        const params = new URLSearchParams({
            tourist_id: touristId,
            latitude: latitude,
            longitude: longitude,
            alert_type: zone.zone_type + "_ZONE",
            risk_level: zone.risk_level,
            message: message
        });

        const response = await fetch(
            "http://127.0.0.1:8000/zone-alert?" + params.toString(),
            {
                method: "POST"
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Zone alert failed");
        }

        console.log("ZONE ALERT SAVED:", data);

    } catch (error) {

        console.error("Zone alert database error:", error);

    }
}
document.getElementById("sosBtn").addEventListener("click", function () {

    const touristId = localStorage.getItem("tourist_id");
    const alertBox = document.getElementById("alertBox");

    if (!touristId) {
        console.error("Tourist ID not found.");
        return;
    }

    alertBox.innerHTML = `
        <span>📍</span>

        <div>
            <strong>Getting your location...</strong>

            <p>
                Please wait while your emergency location is being detected.
            </p>
        </div>
    `;

    navigator.geolocation.getCurrentPosition(

        async function (position) {

            const latitude = position.coords.latitude;
            const longitude = position.coords.longitude;

            try {

                const params = new URLSearchParams({
                    tourist_id: touristId,
                    latitude: latitude,
                    longitude: longitude
                });

                const response = await fetch(
                    "http://127.0.0.1:8000/sos?" + params.toString(),
                    {
                        method: "POST"
                    }
                );

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.detail || "SOS request failed");
                }

                alertBox.innerHTML = `
                    <span>🚨</span>

                    <div>
                        <strong>EMERGENCY SOS ACTIVATED</strong>

                        <p>
                            Emergency alert created successfully.<br>
                            Risk level: CRITICAL<br>
                            Alert ID: ${data.alert_id}
                        </p>
                    </div>
                `;

                console.log("SOS ALERT CREATED:", data);

            } catch (error) {

                console.error("SOS error:", error);

                alertBox.innerHTML = `
                    <span>❌</span>

                    <div>
                        <strong>SOS FAILED</strong>

                        <p>
                            Unable to create emergency alert.
                        </p>
                    </div>
                `;
            }
        },

        function (error) {

            console.error("GPS error:", error);

            alertBox.innerHTML = `
                <span>⚠️</span>

                <div>
                    <strong>LOCATION ERROR</strong>

                    <p>
                        Unable to get your current location.
                        Please allow location access.
                    </p>
                </div>
            `;
        }
    );

});
async function getAIRisk(
    zoneRisk,
    speed,
    stationaryTime,
    routeDeviation,
    nightMovement
) {
    try {

        const params = new URLSearchParams({
            zone_risk: zoneRisk,
            speed: speed,
            stationary_time: stationaryTime,
            route_deviation: routeDeviation,
            night_movement: nightMovement
        });

        const response = await fetch(
            "http://127.0.0.1:8000/calculate-risk?" + params.toString(),
            {
                method: "POST"
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "AI risk calculation failed");
        }

        console.log("AI RISK RESULT:", data);

        return data;

    } catch (error) {

        console.error("AI risk error:", error);

        return null;
    }
}
