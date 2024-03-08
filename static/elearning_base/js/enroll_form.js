document.getElementById('enrollForm').addEventListener('submit', function(e) {
    e.preventDefault(); 

    const url = this.action;
    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
    }).then(response => {
        if (response.ok) {
            location.reload();
        } else {
            throw new Error('Form submission failed');
        }
    }).catch(error => console.error('Error:', error));
});