from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import Permission
from ..models import StatusUpdate, Course, CourseActivity, Enrollments, Notification, Feedback, LobbyMessage
from rest_framework import status
import os, shutil
from django.conf import settings
import json

User = get_user_model()

class TestCreateUserAPI(APITestCase):
    def setUp(self):
        self.create_user_url = reverse('create_user_api')

    def test_create_user_invalid_password(self):
        user_data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'is_teacher': False,
            'email': 'test@test.com',
            'date_of_birth': '2000-01-01',
            'bio': 'This is a test bio.',
            'password': 'testpassword',
        }
        response = self.client.post(self.create_user_url, user_data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_invalid_data(self):
        user_data = {
            'username': '',
            'first_name': 'Test',
            'last_name': 'User',
            'is_teacher': True,
            'email': '',
            'date_of_birth': '2000-01-01',
            'bio': 'This is a test bio.',
            'password': 'testpassword',
        }
        response = self.client.post(self.create_user_url, user_data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user(self):
        user_data = {
            'username': 'testuser2',
            'first_name': 'Test',
            'last_name': 'User',
            'is_teacher': False,
            'email': 'test2@test.com',
            'date_of_birth': '2000-01-01',
            'bio': 'This is a test bio.',
            'password': '178723Lopyystr!?#',
        }
        response = self.client.post(self.create_user_url, user_data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.first().username, 'testuser2')

#This unit test helped us amend a serializers validation to not let the user update the is_teacher field
class TestUpdateUserAPI(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword', email="test@test.com", is_teacher=False)
        self.client.force_authenticate(user=self.user)
        self.update_user_url = reverse('update_user_api', kwargs={'user_id': self.user.user_id})
    
    def test_update_user(self):
        user_data = {
            'username': 'updateduser',
            'first_name': 'Updated',
            'last_name': 'User',
            'email': 'updated@test.com',
            'date_of_birth': '2000-01-01',
            'bio': 'This is an updated test bio.'
        }
        response = self.client.patch(self.update_user_url, user_data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'updateduser')

    def test_update_user_unauthorized(self):
        other_user = User.objects.create_user(username='otheruser', password='otherpassword', email="other@test.com", is_teacher=False)
        other_user_url = reverse('update_user_api', kwargs={'user_id': other_user.user_id})
        response = self.client.patch(other_user_url, data={}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_update_is_teacher(self):
        user_data = {
            'is_teacher': True
        }
        response = self.client.patch(self.update_user_url, user_data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertEqual(self.user.is_teacher, False)


class TestDeleteUserAPI(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword', email="test@test.com", is_teacher=False)
        self.client.force_authenticate(user=self.user)
        self.update_user_url = reverse('delete_user_api', kwargs={'user_id': self.user.user_id})

    def test_delete_user(self):
        response = self.client.delete(self.update_user_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.count(), 0)

    def test_delete_user_unauthorized(self):
        other_user = User.objects.create_user(username='otheruser', password='otherpassword', email="test2@test.com", is_teacher=False)
        other_user_url = reverse('delete_user_api', kwargs={'user_id': other_user.user_id})
        response = self.client.delete(other_user_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class TestGetUserAPI(APITestCase):
    def setUp(self):
        self.student = User.objects.create_user(username='student', password='testpassword', email="test@test.com", is_teacher=False)
        self.teacher = User.objects.create_user(username='teacher', password='testpassword', email="teacher@test.com", is_teacher=True)
        self.other_student = User.objects.create_user(username='otherstudent', password='testpassword', email="otherstudent@test.com", is_teacher=False)

    def test_get_own_data_as_student(self):
        self.client.force_authenticate(user=self.student)
        url = reverse('get_user_api', kwargs={'user_id': self.student.user_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(data['username'], 'student')

    def test_get_other_student_data_as_student(self):
        self.client.force_authenticate(user=self.student)
        url = reverse('get_user_api', kwargs={'user_id': self.other_student.user_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_student_data_as_teacher(self):
        self.client.force_authenticate(user=self.teacher)
        url = reverse('get_user_api', kwargs={'user_id': self.student.user_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(data['username'], 'student')
    
class TestCreateStatusUpdateAPI(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword', email="test@test.com", is_teacher=False)
        self.client.force_authenticate(user=self.user)
        self.status_update_url = reverse('create_status_update')

    def test_create_status_update(self):
        response = self.client.post(self.status_update_url, {'status': 'This is a test status update.'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(StatusUpdate.objects.count(), 1)
        self.assertEqual(StatusUpdate.objects.first().status, 'This is a test status update.')
        self.assertEqual(StatusUpdate.objects.first().user, self.user)

    def test_create_status_update_unauthorized(self):
        # Test without authentication
        self.client.logout()
        response = self.client.post(self.status_update_url, {'status': 'This is a test status update.'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)  # Or the appropriate status code for unauthorized access
    
    def test_create_status_update_invalid_data(self):
        response = self.client.post(self.status_update_url, {'status': ''}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class TestCreateCourseAPI(APITestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(username='teacher', password='testpassword', email="teacher@test.com", is_teacher=True)
        self.student = User.objects.create_user(username='student', password='testpassword', email="student@test.com", is_teacher=False)
        self.course_url = reverse('create_course_api')

        permission = Permission.objects.get(codename='add_course')
        self.teacher.user_permissions.add(permission)

    def test_create_course_as_teacher(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.post(self.course_url, {'course_title': 'Test Course', 'description': 'Test Description'}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Course.objects.count(), 1)
        self.assertEqual(Course.objects.first().course_title, 'Test Course')

    def test_create_course_as_student(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.post(self.course_url, {'course_title': 'Test Course', 'description': 'Test Description'}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class TestCreateCourseActivityAPI(APITestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(username='teacher', password='testpassword', email="teacher@test.com", is_teacher=True)
        self.student = User.objects.create_user(username='student', password='testpassword', email="student@test.com", is_teacher=False)
        self.course = Course.objects.create(course_title='Test Course', description='Test Description', teacher=self.teacher)
        self.activity_data = {'activity_title': 'Test Activity', 'description': 'Test Description', 'activity_type': 'LECTURE'}
        self.activity_url = reverse('create_course_activity', kwargs={'course_id': self.course.course_id})

    def test_create_course_activity_as_teacher(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.post(self.activity_url, self.activity_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CourseActivity.objects.count(), 1)
        self.assertEqual(CourseActivity.objects.first().activity_title, 'Test Activity')

    def test_create_course_activity_as_student(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.post(self.activity_url, self.activity_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_course_activity_for_nonexistent_course(self):
        self.client.force_authenticate(user=self.teacher)
        nonexistent_course_url = reverse('create_course_activity', kwargs={'course_id': 999})
        response = self.client.post(nonexistent_course_url, self.activity_data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
class TestCreateCourseActivityMaterialAPI(APITestCase):
    @classmethod
    def tearDownClass(self):
        #Files created on the server during testing are deleted after the tests are done
        super().tearDownClass()
        dir1 = os.path.join(settings.MEDIA_ROOT, '1')
        dir2 = os.path.join(settings.MEDIA_ROOT, 'course_files', 'course_1')

        if os.path.exists(dir1):
            shutil.rmtree(dir1)
        if os.path.exists(dir2):
            shutil.rmtree(dir2)

    def setUp(self):
        self.teacher = User.objects.create_user(username='teacher', password='testpassword', email="teacher@test.com", is_teacher=True)
        self.student = User.objects.create_user(username='student', password='testpassword', email="student@test.com", is_teacher=False)
        self.course = Course.objects.create(course_title='Test Course', description='Test Description', teacher=self.teacher)
        self.activity = CourseActivity.objects.create(activity_title='Test Activity', description='Test Description', activity_type='LECTURE', course=self.course)
        self.material_data = {'material_title': 'Test Material', 'description': 'Test Description'} 
        self.material_url = reverse('create_course_activity_material', kwargs={'activity_id': self.activity.activity_id}) 

        self.file = SimpleUploadedFile("file.pdf", b"file_content", content_type="application/pdf")
        image_path = os.path.join(settings.BASE_DIR, 'elearning_base', 'test_files', 'profile1.jpg')
        with open(image_path, 'rb') as f:
            self.image = SimpleUploadedFile("profile1.jpg", f.read(), content_type="image/jpeg")

        self.material_data_with_file = {'material_title': 'Test Material', 'description': 'Test Description', 'file': self.file}
        self.material_data_with_image = {'material_title': 'Test Material', 'description': 'Test Description', 'image': self.image}
        self.material_data_with_video = {'material_title': 'Test Material', 'description': 'Test Description', 'video_link': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'}

    def test_create_course_activity_material_as_student(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.post(self.material_url, self.material_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_course_activity_material_for_nonexistent_activity(self):
        self.client.force_authenticate(user=self.teacher)
        nonexistent_activity_url = reverse('create_course_activity_material', kwargs={'activity_id': 999})
        response = self.client.post(nonexistent_activity_url, self.material_data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_course_activity_material_with_file_as_teacher(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.post(self.material_url, self.material_data_with_file)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['material_title'], self.material_data_with_file['material_title'])
        self.assertEqual(response.data['description'], self.material_data_with_file['description'])

    def test_create_course_activity_material_with_image_as_teacher(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.post(self.material_url, self.material_data_with_image)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['material_title'], self.material_data_with_image['material_title'])
        self.assertEqual(response.data['description'], self.material_data_with_image['description'])

    def test_create_course_activity_material_with_video_as_teacher(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.post(self.material_url, self.material_data_with_video)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['material_title'], self.material_data_with_video['material_title'])
        self.assertEqual(response.data['description'], self.material_data_with_video['description'])

class TestCreateFeedbackAPI(APITestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(username='teacher', password='testpassword', email="teacher@test.com", is_teacher=True)
        self.student = User.objects.create_user(username='student', password='testpassword', email="student@test.com", is_teacher=False)
        self.course = Course.objects.create(course_title='Test Course', description='Test Description', teacher=self.teacher)
        self.feedback_url = reverse('create_feedback', kwargs={'course_id': self.course.course_id})
        self.feedback_data = {'feedback': 'Great course!'}
    
        permission = Permission.objects.get(codename='add_feedback')
        self.student.user_permissions.add(permission)

    def test_create_feedback_as_student(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.post(self.feedback_url, self.feedback_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['feedback'], self.feedback_data['feedback'])

    def test_create_feedback_as_teacher(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.post(self.feedback_url, self.feedback_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

#REQUIRES REDIS SERVER TO BE RUNNING - since enrollment serializer relies on cached data
#could be better handled by retrieving the user and ocurse instance and sendign them to the serializer
class TestCreateEnrollmentAPI(APITestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(username='teacher', password='testpassword', email="teacher@test.com", is_teacher=True)
        self.student = User.objects.create_user(username='student', password='testpassword', email="student@test.com", is_teacher=False)
        self.course = Course.objects.create(course_title='Test Course', description='Test Description', teacher=self.teacher)
        self.enrollment_url = reverse('create_enrollment', kwargs={'course_id': self.course.course_id})

        permission = Permission.objects.get(codename='add_enrollments')
        self.student.user_permissions.add(permission)

    def test_create_enrollment_as_student(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.post(self.enrollment_url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_enrollment_as_teacher(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.post(self.enrollment_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class TestUpdateBlockedStatusAPI(APITestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(username='teacher', password='testpassword', email="teacher@test.com", is_teacher=True)
        self.student = User.objects.create_user(username='student', password='testpassword', email="student@test.com", is_teacher=False)
        self.course = Course.objects.create(course_title='Test Course', description='Test Description', teacher=self.teacher)
        self.enrollment = Enrollments.objects.create(student=self.student, course=self.course, blocked=False)
        self.blocked_url = reverse('update_blocked_status', kwargs={'enrollment_id': self.enrollment.enrollment_id})

    def test_update_blocked_status_as_teacher(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.patch(self.blocked_url, {})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.enrollment.refresh_from_db()
        self.assertTrue(self.enrollment.blocked)
    
    def test_update_blocked_status_as_teacher_unauthorized(self):
        other_teacher = User.objects.create_user(username='otherteacher', password='testpassword', email="otherreacher@test.com", is_teacher=True)
        self.client.force_authenticate(user=other_teacher)
        response = self.client.patch(self.blocked_url, {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_blocked_status_as_student(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.patch(self.blocked_url, {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
class TestUpdateNotificationReadAPI(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='testpassword', email="user1@test.com", is_teacher=False)
        self.user2 = User.objects.create_user(username='user2', password='testpassword', email="user2@test.com", is_teacher=False)
        self.notification = Notification.objects.create(recipient=self.user1, read=False)
        self.notification_url = reverse('update_notification_read', kwargs={'notification_id': self.notification.notification_id})

    def test_update_notification_read_as_recipient(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.patch(self.notification_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.read)

    def test_update_notification_read_as_non_recipient(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.patch(self.notification_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class TestGetStatusUpdateAPI(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user', password='testpassword', email="user@test.com")
        self.status_update1 = StatusUpdate.objects.create(user=self.user, status='Status Update 1')
        self.status_update2 = StatusUpdate.objects.create(user=self.user, status='Status Update 2')
        self.status_url = reverse('get_status_updates', kwargs={'user_id': self.user.user_id})

    def test_get_status_updates_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.status_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['status'], 'Status Update 1')
        self.assertEqual(data[1]['status'], 'Status Update 2')

    def test_get_status_updates_unauthenticated(self):
        response = self.client.get(self.status_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class TestGetEnrolledCoursesAPI(APITestCase):
    def setUp(self):
        self.student = User.objects.create_user(username='user', password='testpassword', email="user@test.com", is_teacher=False)
        self.teacher = User.objects.create_user(username='teacher', password='testpassword', email="teacher@test.com", is_teacher=True)
        self.course1 = Course.objects.create(course_title='Course 1', description='Description 1', teacher=self.teacher)
        self.course2 = Course.objects.create(course_title='Course 2', description='Description 2', teacher=self.teacher)
        self.enrollment1 = Enrollments.objects.create(student=self.student, course=self.course1)
        self.enrollment2 = Enrollments.objects.create(student=self.student, course=self.course2)
        self.enrollment_url = reverse('get_enrolled_courses', kwargs={'user_id': self.student.user_id})  # replace with your actual url name

    def test_get_enrolled_courses_authenticated(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.enrollment_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['course']['course_title'], 'Course 2')
        self.assertEqual(data[1]['course']['course_title'], 'Course 1')

    def test_get_enrolled_courses_unauthenticated(self):
        response = self.client.get(self.enrollment_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class TestGetCoursesTaughtAPI(APITestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(username='user', password='testpassword', email="user@test.com", is_teacher=True)
        self.course1 = Course.objects.create(course_title='Course 1', description='Description 1', teacher=self.teacher)
        self.course2 = Course.objects.create(course_title='Course 2', description='Description 2', teacher=self.teacher)
        self.courses_url = reverse('get_courses_taught', kwargs={'user_id': self.teacher.user_id})

    def test_get_courses_taught_authenticated(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(self.courses_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(len(data), 2)

    def test_get_courses_taught_unauthenticated(self):
        response = self.client.get(self.courses_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class TestGetSearchResultsAPI(APITestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(username='teacher', password='testpassword', email="teacher@test.com", is_teacher=True)
        self.student1 = User.objects.create_user(username='student', password='testpassword', email="student@test.com", is_teacher=False)
        self.student2 = User.objects.create_user(username='student2', password='testpassword', email="student2@test.com", is_teacher=False)
        self.course1 = Course.objects.create(course_title='Course 1', description='Description 1', teacher=self.teacher)
        self.course2 = Course.objects.create(course_title='Course 2', description='Description 2', teacher=self.teacher)
        self.course_search_url = reverse('get_search_results', kwargs={'search_query': 'Course'})
        self.student_search_url = reverse('get_search_results', kwargs={'search_query': 'student'})
        self.teacher_search_url = reverse('get_search_results', kwargs={'search_query': 'teacher'})

    def test_get_course_search_results_authenticated_teacher(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(self.course_search_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(len(data['courses']), 2)
        self.assertEqual(data['courses'][0]['course_title'], 'Course 1')
        self.assertEqual(data['courses'][1]['course_title'], 'Course 2')

    def test_get_course_search_results_authenticated_student(self):
        self.client.force_authenticate(user=self.student1)
        response = self.client.get(self.course_search_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(len(data['courses']), 2)
        self.assertEqual(data['courses'][0]['course_title'], 'Course 1')
        self.assertEqual(data['courses'][1]['course_title'], 'Course 2')

    def test_get_user_search_results_authenticated_teacher(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(self.student_search_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(len(data['students']), 2)
        self.assertEqual(data['students'][0]['username'], 'student')
        self.assertEqual(data['students'][1]['username'], 'student2')

    def test_get_user_search_results_authenticated_student(self):
        self.client.force_authenticate(user=self.student1)
        response = self.client.get(self.teacher_search_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(len(data['teachers']), 1)
        self.assertEqual(data['teachers'][0]['username'], 'teacher')

    def test_get_search_results_unauthenticated(self):
        response = self.client.get(self.course_search_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class TestGetCourseActivitiesWithMaterialsAPI(APITestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(username='teacher', password='testpassword', email="teacher@test.com", is_teacher=True)
        self.teacher2 = User.objects.create_user(username='teacher2', password='testpassword', email="teacher2@test.com", is_teacher=True)  
        self.student = User.objects.create_user(username='student', password='testpassword', email="student@test.com", is_teacher=False)
        self.course = Course.objects.create(course_title='Course 1', description='Description 1', teacher=self.teacher)
        self.enrollment = Enrollments.objects.create(course=self.course, student=self.student, blocked=False)
        self.activity = CourseActivity.objects.create(course=self.course, activity_title='Activity 1', description='Description 1')
        self.url = reverse('get_course_activities_with_materials', kwargs={'course_id': self.course.course_id})  # replace with your actual url name

    def test_get_course_activities_with_materials_authenticated_teacher(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['activity_title'], 'Activity 1')

    def test_get_course_activities_with_materials_authenticated_student(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['activity_title'], 'Activity 1')

    def test_get_course_activities_with_materials_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_course_activities_with_materials_not_enrolled(self):
        self.enrollment.delete()
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_get_course_activities_with_materials_not_course_creator(self):
        self.client.force_authenticate(user=self.teacher2)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class TestGetCourseFeedbackAPI(APITestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(username='teacher', password='testpassword', email="teacher@test.com", is_teacher=True)
        self.student = User.objects.create_user(username='student', password='testpassword', email="student@test.com", is_teacher=False)
        self.course = Course.objects.create(course_title='Course 1', description='Description 1', teacher=self.teacher)
        self.feedback = Feedback.objects.create(course=self.course, student=self.student, feedback='Great course!')
        self.feedback_url = reverse('get_course_feedback', kwargs={'course_id': self.course.course_id})

    def test_get_course_feedback_authenticated(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.feedback_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['feedback'], 'Great course!')

    def test_get_course_feedback_nonexistent_course(self):
        url = reverse('get_course_feedback', kwargs={'course_id': 999})
        self.client.force_authenticate(user=self.student)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_course_feedback_unauthenticated(self):
        response = self.client.get(self.feedback_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class TestGetEnrolledStudentsAPI(APITestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(username='teacher', password='testpassword', email="teacher@test.com", is_teacher=True)
        self.student = User.objects.create_user(username='student', password='testpassword', email="student@test.com", is_teacher=False)
        self.course = Course.objects.create(course_title='Course 1', description='Description 1', teacher=self.teacher)
        self.enrollment = Enrollments.objects.create(course=self.course, student=self.student, blocked=False)
        self.url = reverse('get_enrolled_students', kwargs={'course_id': self.course.course_id}) 

    def test_get_enrolled_students_authenticated_teacher(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['student']['username'], self.student.username)

    def test_get_enrolled_students_authenticated_not_teacher(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_enrolled_students_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_enrolled_students_nonexistent_course(self):
        url = reverse('get_enrolled_students', kwargs={'course_id': 999})
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class TestGetNotificationsAPI(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='testpassword', email="user1@test.com")
        self.user2 = User.objects.create_user(username='user2', password='testpassword', email="user2@test.com")
        self.notification = Notification.objects.create(recipient=self.user1, read=False)
        self.notification_url = reverse('get_notifications', kwargs={'user_id': self.user1.user_id})

    def test_get_notifications_authenticated(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.notification_url)
        data = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['notification_id'], self.notification.notification_id)

    def test_get_notifications_unauthenticated(self):
        response = self.client.get(self.notification_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_notifications_not_owner(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(self.notification_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_notifications_nonexistent_user(self):
        url = reverse('get_notifications', kwargs={'user_id': 999})
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class TestGetLatestMessagesAPI(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user', password='testpassword', email="user@test.com")
        self.lobby_messages = [LobbyMessage.objects.create(message=f'Message {i}', user=self.user) for i in range(15)]
        self.messages_url = reverse('get_latest_lobby_messages')  # replace with your actual url name

    def test_get_latest_lobby_messages_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.messages_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(len(data), 10)
        self.assertEqual(data[0]['message'], 'Message 14')

    def test_get_latest_lobby_messages_unauthenticated(self):
        response = self.client.get(self.messages_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class TestDeleteStatusUpdateAPI(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='testpassword', email="user1@test.com")
        self.user2 = User.objects.create_user(username='user2', password='testpassword', email="user2@test.com")
        self.status_update = StatusUpdate.objects.create(user=self.user1, status='Status update 1')
        self.delete_status_url = reverse('delete_status_update', kwargs={'status_id': self.status_update.status_id})

    def test_delete_status_update_authenticated_owner(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(self.delete_status_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_status_update_authenticated_not_owner(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.delete(self.delete_status_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_status_update_unauthenticated(self):
        response = self.client.delete(self.delete_status_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_status_update_nonexistent_status_update(self):
        url = reverse('delete_status_update', kwargs={'status_id': 999})
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class TestDeleteCourseActivityAPI(APITestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(username='teacher', password='testpassword', email="teacher@test.com", is_teacher=True)
        self.other_teacher = User.objects.create_user(username='other_user', password='testpassword', email="other_user@test.com", is_teacher=True)
        self.course = Course.objects.create(course_title='Course 1', description='Description 1', teacher=self.teacher)
        self.course_activity = CourseActivity.objects.create(course=self.course, activity_title='Activity 1')
        self.activity_url = reverse('delete_course_activity', kwargs={'activity_id': self.course_activity.activity_id})

    def test_delete_course_activity_authenticated_teacher(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.delete(self.activity_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_course_activity_authenticated_not_teacher(self):
        self.client.force_authenticate(user=self.other_teacher)
        response = self.client.delete(self.activity_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_course_activity_unauthenticated(self):
        response = self.client.delete(self.activity_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_course_activity_nonexistent_activity(self):
        url = reverse('delete_course_activity', kwargs={'activity_id': 999})
        self.client.force_authenticate(user=self.teacher)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)