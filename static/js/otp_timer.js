let timer;
function startTimer() {
    let seconds = 30;
    let btn = document.getElementById("generate-otp-btn");
    btn.disabled = true;
    timer = setInterval(function () {
        btn.innerHTML = "Resend in" + " : " + seconds;
        seconds--;
        if (seconds < 0) {
            clearInterval(timer);
            btn.innerHTML = "Resend OTP";
            btn.disabled = false;
        }
    }, 1000);
}