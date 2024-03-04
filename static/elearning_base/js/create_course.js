document.getElementById('createCourseForm').addEventListener('submit', function(e) {
    e.preventDefault();

    var formData = new FormData();
    formData.append('course_title', document.getElementById('id_course_title').value);
    formData.append('description', document.getElementById('id_description').value);
    var fileInput = document.getElementById('id_course_img');
    if (fileInput.files.length > 0) {
        formData.append('course_img', fileInput.files[0], fileInput.files[0].name);
    }
    
    fetch('/api/create_course/', {
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
        window.location.href = '/enrolled_taught_courses/';
    })
    .catch(function(error) {
        console.error('Error:', error);
    });
});