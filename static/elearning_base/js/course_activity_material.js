document.querySelectorAll('[id^="addMaterialBtn-"]').forEach(button => {
    button.addEventListener('click', function() {
        const courseActivityId = this.getAttribute('data-course-activity-id');
        if (document.getElementById(`addMaterialFormContainer-${courseActivityId}`).style.display == 'none') {
            document.getElementById(`addMaterialFormContainer-${courseActivityId}`).style.display = 'block';
        } else {
            document.getElementById(`addMaterialFormContainer-${courseActivityId}`).style.display = 'none';
        }
    })
})
document.querySelectorAll('[id^="addMaterialForm-"]').forEach(form => {
    form.addEventListener('submit', function(e) {
        e.preventDefault();

        const formData = new FormData(this);
        const courseActivityId = this.getAttribute('data-course-activity-id');
        fetch(`/api/create_course_activity_material/${courseActivityId}/`, {
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
});
document.querySelectorAll('[id^="deleteCourseActivityForm-"]').forEach(form => {
    form.addEventListener('submit', function(e) {
        e.preventDefault();

        const courseActivityId = this.getAttribute('data-course-activity-id');
        fetch(`/api/delete_course_activity/${courseActivityId}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
        })
        .then(response => {
            if (response.ok) {
                console.log('Course activity successfully deleted');
                window.location.reload();
            } else {
                response.json().then(data => {
                    throw data;
                });
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error deleting course activity.')
        })
    })
})