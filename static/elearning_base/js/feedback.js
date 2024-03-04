document.getElementById('feedbackForm').addEventListener('submit', function(e) {
    e.preventDefault();

    const formData = new FormData(this);
    const courseId = this.getAttribute('data-course-id');
    fetch(`/api/create_feedback/${courseId}/`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
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
        this.reset();
        location.reload();
    })
    .catch(function(error) {
        console.error('Error:', error);
    });
});