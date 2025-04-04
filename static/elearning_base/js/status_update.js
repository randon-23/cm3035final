// Tracks status update form submission to make POST API call and show the updated list of status updates
document.getElementById('statusUpdateForm').addEventListener('submit', function(e) {
    e.preventDefault();
    fetch('/api/create_status_update/', {
        method: 'POST',
        body: JSON.stringify({
            'status': document.getElementById('id_status').value
        }),
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            'Content-Type': 'application/json',
        },
    })
    .then(response => {
        if (response.ok) {
            return response.json(); // For HTTP 201 Created
        } else if (response.status === 400) {
            return response.json().then(data => {
                throw data; // Throw the data to be caught in the catch block
            });
        } else {
            throw new Error('Something went wrong on server side.'); // For other server-side errors
        }
    })
    .then(data => {
        console.log('Success:', data);
        document.getElementById('statusUpdateForm').reset(); // Reset form fields
        // Optionally, reload the page or part of it to show the updated list of status updates
        location.reload();
    })
    .catch(function(error) {
        console.error('Error:', error);
    });
});

document.querySelectorAll('[id^="deleteStatusUpdateForm-"]').forEach(form =>{
    form.addEventListener('submit', function(e) {
        e.preventDefault();

        const statusUpdateId = form.getAttribute('data-status-update-id');
        fetch(`/api/delete_status_update/${statusUpdateId}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => {
            if (response.ok) {
                console.log('Status update deleted successfully');
                window.location.reload();
            } else {
                response.json().then(data => {
                    throw data;
                })
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error deleting status update');
        })
    })
})

