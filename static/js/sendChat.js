const inputBox = document.querySelector('.input-box');
const sendButton = document.querySelector('.send-button');
const chatHistoryContainer = document.querySelector('.chat-history');
sendButton.addEventListener('click', () => {
    if (inputBox.value.trim() !== '') {
        const chatHistory = document.querySelector('.chat-history');
        const replyMessage = document.createElement('div');
        const replyText = document.createElement('div');

        replyMessage.classList.add('message', 'right');
        replyText.classList.add('message-text');

        const trimmedText = inputBox.value.trim();
        replyText.innerText = trimmedText;
        replyMessage.appendChild(replyText);
        document.getElementById("audio").play();
        chatHistory.appendChild(replyMessage);

        inputBox.value = '';
        inputBox.focus();
        sendButton.focus();
        chatHistoryContainer.scrollTop = chatHistoryContainer.scrollHeight;
    }
});
inputBox.addEventListener('keydown', function (event) {
    if (event.keyCode === 13 && !event.shiftKey) {
        event.preventDefault();
        sendButton.click();
        document.querySelector('.input-box').focus();
    }
});
