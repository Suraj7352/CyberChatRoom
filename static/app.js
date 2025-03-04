const socket = io.connect();

// Get username from the server-side
const username = '{{ current_user.username }}';  // Will be passed from Flask template

// Listen for incoming messages from the server
socket.on('chat message', function(data) {
    const chatBox = document.getElementById("chat-box");
    const messageElement = document.createElement("div");
    messageElement.textContent = `${data.username}: ${data.message}`;
    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight; // Scroll to the bottom
});

// Send a chat message
function sendMessage() {
    const messageInput = document.getElementById("message-input");
    const messageText = messageInput.value.trim();
    
    if (messageText && username) {
        const messageData = {
            username: username,
            message: messageText
        };

        // Emit the message to the server
        socket.emit('chat message', messageData);
        
        // Clear the message input
        messageInput.value = "";
    } else {
        alert("Please enter a message");
    }
}
