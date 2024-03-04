document.getElementById('showCourseActivityForm').addEventListener('click', function() {
    if (document.getElementById('courseActivityFormContainer').style.display == 'none') {
        document.getElementById('courseActivityFormContainer').style.display = 'block';
    } else {
        document.getElementById('courseActivityFormContainer').style.display = 'none';
    }
})

document.getElementById('courseActivityForm').addEventListener('submit', function(e) {
    e.preventDefault();

    const formData = new FormData(this);
    const courseId = this.getAttribute('data-course-id');
    fetch(`/api/create_course_activity/${courseId}/`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else if (response.status === 400) {
            return response.json().then(data => {
                throw data;
            });
        } 
    })
    .then(data => {
        console.log('Success:', data);
        this.reset();
        location.reload();
    })
    .catch(function(error) {
        const errorField = Object.keys(error)[0];
        const errorMessage = error[errorField][0];
        alert(`Error: ${errorField} - ${errorMessage}`);
    });
});