document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.toggle-block-status').forEach(button => {
        button.addEventListener('click', function() {
            const enrollmentId = this.getAttribute('data-enrollment-id');
            fetch(`/api/update_blocked_status/${enrollmentId}/`, {
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
                    alert('Failed to update the enrollment status.');
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });
});