var form = document.forms['register_form'];
var pass1 = form.elements['password'];
var pass2 = form.elements['user_pass2'];

form.addEventListener('submit', function(event) {
    if (pass1.value !== pass2.value) {
        event.preventDefault();
        alert('Passwords do not match. Please re-type the password.');
    }
});