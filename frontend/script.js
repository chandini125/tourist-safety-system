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
const loginForm = document.getElementById("loginForm");
const loginMessage = document.getElementById("loginMessage");

loginForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const loginData = {
        email: document.getElementById("loginEmail").value,
        password: document.getElementById("loginPassword").value
    };

    loginMessage.textContent = "Signing in...";

    try {
        const response = await fetch("http://127.0.0.1:8000/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(loginData)
        });

        const data = await response.json();

        if (response.ok) {
            localStorage.setItem("tourist_id", data.tourist_id);
            localStorage.setItem("tourist_name", data.name);
            localStorage.setItem("tourist_email", data.email);

            window.location.href = "dashboard.html";
        } else {
            loginMessage.textContent =
                data.detail || "Login failed.";
        }

    } catch (error) {
        loginMessage.textContent =
            "Unable to connect to the server.";

        console.error(error);
    }
});
