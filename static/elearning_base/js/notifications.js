document.querySelectorAll('.toggle-read-status').forEach(button => {
    button.addEventListener('click', function() {
        const notificationId = this.getAttribute('data-notification-id');
        fetch(`/api/update_notification_read/${notificationId}/`, {
            method: 'PATCH',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'Content-Type': 'application/json',
            },
        })
        .then(response => {
            if (response.ok) {
                window.location.reload();
            } else {
                alert('Failed to update the notification read status.');
            }
        })
        .catch(error => console.error('Error:', error));
    });
});
