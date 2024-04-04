const chatSocket = new WebSocket('wss://'+window.location.host+'/ws/lobby/');

chatSocket.onopen = function (event) {
    console.log('Chat WebSocket connected.');
    if (typeof notificationSocket !== 'undefined') {
        if (notificationSocket.readyState === WebSocket.OPEN) {
            console.log('Notification WebSocket connected.');
            notificationSocket.send(JSON.stringify({
                command: 'leave_chat_notifications'
            }));
            console.log('Left chat notifications group');
        } else {
            notificationSocket.onopen = function(event) {
                console.log('Notification WebSocket connected.');
                notificationSocket.send(JSON.stringify({
                    command: 'leave_chat_notifications'
                }));
                console.log('Left chat notifications group');
            }
        }
    }
    else {
        console.error('Attempted to leave chat notifications gorup - Notification WebSocket not found');
    }
}

document.getElementById('sendMessage').addEventListener('click', function(event) {
    const messageInput = document.getElementById('messageInput');
    const message = messageInput.value;

    chatSocket.send(JSON.stringify({
        'message': message,
    }));

    messageInput.value = '';
})

chatSocket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    
    const lobbyContainer = document.getElementById('lobbyContainer');
    const currentUserUsername = lobbyContainer.getAttribute('data-username');

    const messageBubble = document.createElement('div');
    messageBubble.className = "p-2 my-2 rounded shadow max-w-1/2";

    if (data.username === currentUserUsername) {
        messageBubble.classList.add("self-end", "bg-blue-500", "text-white"); // Example styles for current user
    } else {
        messageBubble.classList.add("self-start", "bg-slate-400", "text-black"); // Example styles for other users
    }
    
    const messageContent = document.createElement('p');
    messageContent.className = 'text-sm';
    messageContent.textContent = data.message;

    const messageSender = document.createElement('p');
    messageSender.className = 'text-xs font-semibold';
    messageSender.textContent = `${data.username} ${data.is_teacher ? '(Teacher) says' : '(Student) says'}`;

    messageBubble.appendChild(messageSender);
    messageBubble.appendChild(messageContent);

    const chatMessagesContainer = document.getElementById("chatMessages");
    chatMessagesContainer.appendChild(messageBubble);
    chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
    
};

chatSocket.onclose = function(event) {
    console.log('Chat WebSocket closed.');
};

chatSocket.onerror = function(event) {
    console.error('Chat WebSocket error:', event);
};