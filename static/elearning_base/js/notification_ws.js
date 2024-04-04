//Notification websocker set up on base_authenticated to be accessible from anywhere when user is logged in
const notificationSocket = new WebSocket('wss://'+window.location.host+'/ws/notifications/');

notificationSocket.onopen = function (event) {
    console.log('Notification WebSocket connected.');
};

notificationSocket.onmessage = function (event) {
    const data = JSON.parse(event.data);
    console.log('Notification received:', data)

    if (data.message === 'New message in the public lobby'){
        const newMessageIndicator = document.getElementById('newMessagesIndicator');
        if (newMessageIndicator.classList.contains('hidden')) {
            newMessageIndicator.classList.remove('hidden');
        }
    } else{
        const newNotificationsIndicator = document.getElementById('newNotificationsIndicator'); 
        // Check if the indicator 'NEW' is hidden on left panel, if so, remove the hidden class
        if (newNotificationsIndicator.classList.contains('hidden')) {
            newNotificationsIndicator.classList.remove('hidden');
        }

        var newNotification = document.createElement('div');
        newNotification.className = "bg-green-500 text-white p-4 rounded-lg shadow-lg transition-opacity duration-1000 opacity-100";
        newNotification.style.position = "relative";
        newNotification.style.marginBottom = "15px";
        newNotification.innerHTML = `<strong>${data.title}</strong>: ${data.message}`;

        const notificationContainer = document.getElementById("notificationContainer");
        if (notificationContainer) {
            notificationContainer.appendChild(newNotification);
        } else {
            console.error('Notification container not found');
        }

        setTimeout(() => {
            newNotification.style.opacity = '0';
            setTimeout(() => newNotification.remove(), 1000); // Wait for fade out to finish before removing
        }, 5000);
    }
};

notificationSocket.onclose = function (event) {
    console.log('Notification WebSocket closed.');
}

notificationSocket.onerror = function (event) {
    console.error('Notification WebSocket error:', event);
}

document.addEventListener('DOMContentLoaded', function() {
    const userId = document.querySelector('button[data-user-id]').getAttribute('data-user-id');
    fetch(`/api/get_notifications/${userId}/`, {
        method: 'GET',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        const newNotification = document.getElementById('newNotificationsIndicator');
        if (data.length > 0) {
            newNotification.classList.remove('hidden');
        } else {
            newNotification.classList.add('hidden');
        }
    })
    .catch(error => console.error('Error:', error));
})