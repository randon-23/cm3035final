from django.test import TestCase
from django.db import IntegrityError, transaction
from models import *
from datetime import date, datetime

def create_common_objects():
    teacher=UserProfile.objects.create(username='teacher1', email='teacher1@gmail.com', is_teacher=True)
    student = UserProfile.objects.create(username='student1', email='student1@gmail.com', is_teacher=False)
    return teacher, student

class TestUserProfile(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.teacher, cls.student = create_common_objects()
    
    def test_teacher_user_creation(self):
        self.assertEqual(self.teacher.username, 'teacher1')
        self.assertEqual(self.teacher.email, 'teacher1@gmail.com')
        self.assertEqual(self.teacher.is_teacher, True)
        self.assertEqual(self.teacher.bio, '')
        self.assertEqual(self.teacher.date_of_birth, '')
        self.assertEqual(self.teacher.profile_img, '')
    
    def test_student_user_creation(self):
        self.assertEqual(self.student.username, 'student1')
        self.assertEqual(self.student.email, 'student1@gmail.com')
        self.assertEqual(self.student.is_teacher, False)
        self.assertEqual(self.student.bio, '')
        self.assertEqual(self.student.date_of_birth, '')
        self.assertEqual(self.student.profile_img, '')
    
    def test_unique_email(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            UserProfile.objects.create(username='teacher2', email='teacher1@gmail.com', is_teacher=True)
    
    def test_user_default_values(self):
        user2 = UserProfile.objects.create(username='user2', email='user2@gmail.com')
        self.assertFalse(user2.is_teacher)

    def test_str_representation(self):
        self.assertEqual(str(self.teacher), "User ID: 1\nUsername: teacher1\nIs Teacher? True")
        self.assertEqual(str(self.student), "User ID: 2\nUsername: student1\nIs Teacher? False")

    def test_email_format(self):
        with self.assertRaises(Exception):
            UserProfile.objects.create(username='user3', email='user3.com', is_teacher=False)
    
    def test_user_dob_format(self):
        user = UserProfile.objects.create(
            username="userwithdob", 
            email="userdob@example.com", 
            date_of_birth=date(2000, 23, 11)
        )
        self.assertEqual(user.date_of_birth, date(2000, 23, 11))

        user2 = UserProfile.objects.create(
            username="userwithdob2", 
            email="userdob2@example.com",
            date_of_birth="2000-23-11"
        )
        self.assertEqual(user2.date_of_birth, date(2000, 23, 11))

        user3 = UserProfile.objects.create(
            username="userwithdob3", 
            email="userdob3@example.com",
            date_of_birth="23/11/2000"
        )
        self.assertEqual(user3.date_of_birth, date(2000, 23, 11))

class TestCourse(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.teacher, cls.student = create_common_objects()
        cls.course = Course.objects.create(course_title='Course1', description='This is course 1', teacher=cls.teacher)
    
    def test_course_creation(self):
        self.assertEqual(self.course.course_title, 'Course1')
        self.assertEqual(self.course.description, 'This is course 1')
        self.assertEqual(self.course.teacher, self.teacher)

    def test_course_str_representation(self):
        self.assertEqual(str(self.course), "Course Title: Course1")
    
    def test_course_creation_by_student(self):
        with self.assertRaises(ValidationError):
            course_error =Course.objects.create(course_title='Course2', description='This is course 2', teacher=self.student)
            course_error.clean()
        
    def test_course_title_unique(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Course.objects.create(course_title='Course1', description='This is course 2', teacher=self.teacher)
    
    def test_course_timestamps(self):
        self.assertIsNotNone(self.course.created_at)
        self.assertIsNotNone(self.course.updated_at)

        self.assertIsInstance(self.course.created_at, datetime)
        self.assertIsInstance(self.course.updated_at, datetime)

    def test_course_updated_at_created_at(self):
        old_update_timestamp = self.course.updated_at
        create_timestamp = self.course.created_at
        self.course.description = 'Updating COURSE 1'
        self.course.save()
        self.course.refresh_from_db()

        self.assertEqual(self.course.created_at, create_timestamp)
        self.assertNotEqual(self.course.updated_at, old_update_timestamp)
        self.assertNotEqual(self.course.description, 'This is course 1') 

    def test_course_img(self)
