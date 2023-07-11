const passwordInput = document.getElementById("user_pass1");
const confirmPasswordInput = document.getElementById("user_pass2");
const form = document.forms.register_form;

function verifyPasswords() {
  const password = passwordInput.value;
  const confirmPassword = confirmPasswordInput.value;

  if (password === confirmPassword) {
    confirmPasswordInput.setCustomValidity("");
  } else {
    confirmPasswordInput.setCustomValidity("Passwords do not match!");
  }
}

function onSubmit(event) {
  event.preventDefault();
  form.reportValidity();
  if (form.checkValidity()) {
    console.log("Form submitted!");
    form.submit();
  } else {
    console.log("Form not submitted! Please correct the errors.");
  }
}

passwordInput.addEventListener("input", verifyPasswords);
confirmPasswordInput.addEventListener("input", verifyPasswords);
form.addEventListener("submit", onSubmit);