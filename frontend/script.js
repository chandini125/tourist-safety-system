const registerForm = document.getElementById("registerForm");
const message = document.getElementById("message");

registerForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const touristData = {
        name: document.getElementById("name").value,
        email: document.getElementById("email").value,
        phone: document.getElementById("phone").value,
        emergency_contact: document.getElementById("emergency_contact").value,
        password: document.getElementById("password").value
    };

    message.textContent = "Creating your account...";

    try {
        const response = await fetch("http://127.0.0.1:8000/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(touristData)
        });

        const data = await response.json();

        if (response.ok) {
            message.textContent =
                "Account created successfully! Tourist ID: " +
                data.tourist_id;

            registerForm.reset();
        } else {
            message.textContent =
                data.detail || "Registration failed.";
        }

    } catch (error) {
        message.textContent =
            "Unable to connect to the server.";
        console.error(error);
    }
});


function scrollToRegister() {
    document.getElementById("register").scrollIntoView({
        behavior: "smooth"
    });
}
