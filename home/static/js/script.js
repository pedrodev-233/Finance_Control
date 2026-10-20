const passwordInput = document.querySelector("#password");
const passwordToggle = document.querySelector("#password-toggle");
const loginForm = document.querySelector("#login-form");
const formMessage = document.querySelector("#form-message");

passwordToggle.addEventListener("click", () => {
    const isPasswordHidden = passwordInput.type === "password";
    passwordInput.type = isPasswordHidden ? "text" : "password";
    passwordToggle.setAttribute("aria-pressed", String(isPasswordHidden));
    passwordToggle.setAttribute(
        "aria-label",
        isPasswordHidden ? "Ocultar senha" : "Mostrar senha",
    );
});

loginForm.addEventListener("submit", (event) => {
    event.preventDefault();
    formMessage.textContent =
        "A interface está pronta, mas a autenticação ainda não está conectada.";
});