function toggleMode() {
    var body = document.body;
    var button = document.getElementById("mode-button");
    var isDarkMode = body.classList.contains("dark-mode");

    if (isDarkMode) {
        body.classList.remove("dark-mode");
        body.style.transition = "background-color 0.4s ease-out, color 0.4s ease-out";
        button.textContent = "Dark Mode";
        localStorage.setItem("mode", "light");
    } else {
        body.classList.add("dark-mode");
        body.style.transition = "background-color 0.4s ease-out, color 0.4s ease-out";
        button.textContent = "Light Mode";
        localStorage.setItem("mode", "dark");
    }
}
var mode = localStorage.getItem("mode");
if (mode === "dark") {
    document.body.classList.add("dark-mode");
    document.getElementById("mode-button").textContent = "Light Mode";
} else {
    document.body.classList.remove("dark-mode");
    document.getElementById("mode-button").textContent = "Dark Mode";
}

