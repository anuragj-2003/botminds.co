const text_box = document.querySelector('.input-box');
document.querySelector("#clear-button").addEventListener("click", function () {
    document.querySelector(".chat-history").innerHTML = "";
    text_box.focus();

});
document.querySelector("#clear-btn").addEventListener("click", function () {
    document.querySelector(".chat-history").innerHTML = "";
    text_box.focus();
});