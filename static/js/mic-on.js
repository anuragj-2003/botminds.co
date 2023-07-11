let isRecording = false;
let recognition;

function toggleRecording() {
  const button = document.getElementById('start-button');
  if (isRecording) {
    recognition.stop();
    isRecording = false;
    button.style.backgroundColor = '';
    button.innerHTML = '<span class="material-symbols-outlined">settings_voice</span>';
  } else {
    recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'en-GB';
    recognition.interimResults = true;

    recognition.onresult = function (event) {
      const result = event.results[event.results.length - 1];
      const transcript = result[0].transcript;
      document.getElementById('user-input-text').value = transcript;
      const sendbtn = document.getElementById('send-button');
      setTimeout(function () {
        sendbtn.click();
      }, 3000);
      sendbtn.focus();
    };

    recognition.onend = function () {
      if (isRecording) {
        recognition.start();
      }
    };

    recognition.start();
    isRecording = true;
    button.style.backgroundColor = 'red';
    button.innerHTML = '<span class="material-symbols-outlined">stop</span>';
  }
}
