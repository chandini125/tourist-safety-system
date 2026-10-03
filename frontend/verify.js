document.addEventListener("DOMContentLoaded", () => {
    const params = new URLSearchParams(window.location.search);
    const digitalIdFromUrl = params.get("id");

    if (digitalIdFromUrl) {
        document.getElementById("digitalId").value =
            digitalIdFromUrl;

        document.getElementById("verifyBtn").click();
    }
});
document.getElementById("verifyBtn").addEventListener("click", async function () {

    const digitalId =
        document.getElementById("digitalId").value.trim();

    const result =
        document.getElementById("result");

    if (!digitalId) {
        result.style.display = "block";
        result.textContent = "Please enter a Digital ID.";
        return;
    }

    result.style.display = "block";
    result.textContent = "Verifying Digital ID...";

    try {

        const response = await fetch(
            "http://10.53.116.242:8000/digital-id/verify/" +
            encodeURIComponent(digitalId)
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "Verification failed"
            );
        }

        if (data.verification_status === "VALID") {

            result.innerHTML = `
                <strong>✓ DIGITAL ID VERIFIED</strong>

                <p>
                    Tourist Name: ${data.tourist_name}<br>
                    Tourist ID: ${data.tourist_id}<br>
                    Digital ID: ${data.digital_id}<br>
                    Status: VALID
                </p>
            `;

        } else {

            result.innerHTML = `
                <strong>⚠ DIGITAL ID INVALID</strong>

                <p>
                    The identity data does not match
                    the original registered hash.
                </p>
            `;
        }

    } catch (error) {

        result.innerHTML = `
            <strong>Verification Error</strong>

            <p>${error.message}</p>
        `;
    }

});
