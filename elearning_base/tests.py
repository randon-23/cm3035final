from django.test import TestCase
from django.db import IntegrityError, transaction
from .models import *
from datetime import date, datetime
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from django.conf import settings
import os

# Create common objects for testing
def create_common_objects():
    teacher=UserProfile.objects.create(username='teacher1', email='teacher1@gmail.com', is_teacher=True)
    student = UserProfile.objects.create(username='student1', email='student1@gmail.com', is_teacher=False)
    return teacher, student

#Test for UserProfile model
class TestUserProfile(TestCase):
    @classmethod
    def setUpTestData(cls):
        image_path = os.path.join(settings.BASE_DIR, 'elearning_base', 'test_files', 'profile1.jpg')
        cls.teacher, cls.student = create_common_objects()
        with open(image_path, 'rb') as f:
            cls.image = SimpleUploadedFile("profile1.jpg", content=f.read(), content_type='image/jpeg')
    
    def test_teacher_user_creation(self):
        self.assertEqual(self.teacher.username, 'teacher1')
        self.assertEqual(self.teacher.email, 'teacher1@gmail.com')
        self.assertEqual(self.teacher.is_teacher, True)
        self.assertTrue(self.teacher.bio is None or self.teacher.bio == '')
        self.assertTrue(self.teacher.date_of_birth is None or self.teacher.date_of_birth == '')
        self.assertTrue(self.teacher.profile_img is None or self.teacher.profile_img == '')
    
    def test_student_user_creation(self):
        self.assertEqual(self.student.username, 'student1')
        self.assertEqual(self.student.email, 'student1@gmail.com')
        self.assertEqual(self.student.is_teacher, False)
        self.assertTrue(self.student.bio is None or self.student.bio == '')
        self.assertTrue(self.student.date_of_birth is None or self.student.date_of_birth == '')
        self.assertTrue(self.student.profile_img is None or self.student.profile_img == '')
            
    def test_unique_email(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            UserProfile.objects.create(username='teacher2', email='teacher1@gmail.com', is_teacher=True)
    
    def test_user_default_values(self):
        user2 = UserProfile.objects.create(username='user2', email='user2@gmail.com')
        self.assertFalse(user2.is_teacher)

    def test_str_representation(self):
        self.assertEqual(str(self.teacher), "Username: teacher1\nEmail: teacher1@gmail.com\nIs Teacher? True")
        self.assertEqual(str(self.student), "Username: student1\nEmail: student1@gmail.com\nIs Teacher? False")

    def test_email_format(self):
        with self.assertRaises(ValidationError):
            user_error = UserProfile.objects.create(username='user3', email='user3.com', is_teacher=False)
            user_error.clean()
    
    def test_user_dob_format(self):
        user = UserProfile.objects.create(
            username="userwithdob", 
            email="userdob@example.com", 
            date_of_birth=date(2000, 11, 23)
        )
        self.assertEqual(user.date_of_birth, date(2000, 11, 23))

        user2 = UserProfile.objects.create(
            username="userwithdob2",
            email="userdob2@example.com",
            date_of_birth=date(2000, 11, 23)
        )
        self.assertEqual(str(user2.date_of_birth), "2000-11-23")
        #TEST FOR IMPROPER DATE FORMATS I.E. NOT IN YYYY-MM-DD FORMAT SUCH AS 23/11/2000. THIS IS DONE
        #FORM VALIDATION OR CUSTOM MODEL CLEAN METHODS TO MANUALLY PARSE AND VALIDATE STRING INPUTS
        #TO TEST FOR VALIDATION ERROS DUE TO INCORRECT FORMATS YOU WOULD TYPICALLY DO THIS IN FORM TESTS
        #OR MODEL CLEAN METHODS 

    def test_user_profile_img(self):
        self.teacher.profile_img = self.image
        self.teacher.save()
        self.assertTrue(self.teacher.profile_img)

        self.student.profile_img = self.image
        self.student.save()
        self.assertTrue(self.student.profile_img)

#Test for Course model
class TestCourse(TestCase):
    @classmethod
    def setUpTestData(cls):
        image_path = os.path.join(settings.BASE_DIR, 'elearning_base', 'test_files', 'course1.jpg')
        cls.teacher, cls.student = create_common_objects()
        with open(image_path, 'rb') as f:
            cls.image = SimpleUploadedFile("course1.jpg", content=f.read(), content_type='image/jpeg')    
        cls.course = Course.objects.create(course_title='Course1', description='This is course 1', teacher=cls.teacher, course_img=cls.image)
        
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

    def test_course_img(self):
        self.assertTrue(self.course.course_img)

#Test for Tag model
class TestTag(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tag = Tag.objects.create(tag_name="Tag1")

    def test_tag_creation(self):
        self.assertEqual(self.tag.tag_name, "Tag1")

    def test_tag_str_representation(self):
        self.assertEqual(str(self.tag.tag_name), "Tag1")
    
class TestCourseTag(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.teacher, cls.student = create_common_objects()
        cls.course = Course.objects.create(course_title="Web Dev", description="This is a web development course", teacher=cls.teacher) 
        cls.tag = Tag.objects.create(tag_name="Web Development")
        cls.course_tag=CourseTag.objects.create(course=cls.course, tag=cls.tag)

    def test_creation(self):
        self.assertEqual(self.course_tag.course, self.course)
        self.assertEqual(self.course_tag.tag, self.tag)
    
    def test_uniqueness_together(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            CourseTag.objects.create(course=self.course, tag=self.tag)
    
    def test_string_representation(self):
        self.assertEqual(str(self.course_tag), "Course Title: Web Dev\nTag: Web Development")

#Test for Enrollments model
class TestEnrollments(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.teacher, cls.student = create_common_objects()
        cls.course = Course.objects.create(course_title='Course1', description='This is course 1', teacher=cls.teacher)
        cls.enrollment = Enrollments.objects.create(course=cls.course, student=cls.student)

    def test_creation(self):
        self.assertEqual(self.enrollment.course, self.course)
        self.assertEqual(self.enrollment.student, self.student)
    
    def test_enrollment_by_teacher(self):
        with self.assertRaises(ValidationError):
            enrollment_error = Enrollments.objects.create(course=self.course, student=self.teacher)
            enrollment_error.clean()
    
    def test_blocked_default_false(self):
        self.assertFalse(self.enrollment.blocked)
    
    def test_enrolled_at(self):
        self.assertIsNotNone(self.enrollment.enrolled_at)
        self.assertIsInstance(self.enrollment.enrolled_at, datetime)

    def test_string_representation(self):
        self.assertEqual(str(self.enrollment), "Username: student1\nEmail: student1@gmail.com\nIs Teacher? False\n\nCourse Title: Course1")

#Test for CourseActivity
class TestCourseActivity(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.teacher, cls.student = create_common_objects()
        cls.course = Course.objects.create(course_title='Course1', description='This is course 1', teacher=cls.teacher)
        cls.lecture = CourseActivity.objects.create(course=cls.course, activity_title='Lecture 1', description='This is lecture 1')

    def test_creation(self):
        self.assertEqual(self.lecture.course, self.course)
        self.assertEqual(self.lecture.activity_title, 'Lecture 1')
        self.assertEqual(self.lecture.description, 'This is lecture 1')
        self.assertIsNotNone(self.lecture.created_at)

    def test_activity_type_default_is_lecture(self):
        self.assertEqual(self.lecture.activity_type, 'LECTURE')

    def test_valid_activity_type_choices(self):
        lecture2 = CourseActivity.objects.create(course=self.course, activity_title='Lecture 2', description='This is lecture 2', activity_type='ASSIGNMENT')
        self.assertEqual(lecture2.activity_type, 'ASSIGNMENT')

        lecture3 = CourseActivity.objects.create(course=self.course, activity_title='Lecture 3', description='This is lecture 3', activity_type='EXAM')
        self.assertEqual(lecture3.activity_type, 'EXAM')    

    def test_invalid_activity_type_choices(self):
        with self.assertRaises(ValueError):
            lecture4_error = CourseActivity.objects.create(course=self.course, activity_title='Lecture 4', description='This is lecture 4', activity_type='FIELDTRIP')
            lecture4_error.clean()

    def test_uniqueness_together(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            CourseActivity.objects.create(course=self.course, activity_title='Lecture 1', description='Attempting to violate unique pairing constraint')

    def test_string_representation(self):
        self.assertEqual(str(self.lecture), "Course Title: Course1\nActivity Title: Lecture 1")

    def test_deadline_past(self):
        with self.assertRaises(ValidationError):
            self.lecture.deadline = timezone.make_aware(datetime(2021, 8, 31, 23, 59, 59))
            self.lecture.save()
            self.lecture.clean()

    def test_deadline_future_less_than_week(self):
        with self.assertRaises(ValidationError):
            self.lecture.deadline = timezone.make_aware(datetime.now() + timedelta(days=6))
            self.lecture.save()
            self.lecture.clean()
    
    def test_deadline_future_more_than_week(self):
        self.lecture.deadline = timezone.make_aware(datetime.now() + timedelta(days=8))
        self.lecture.save()
        self.lecture.clean()

#Tes for CourseActivityMaterial
class TestCourseActivityMaterial(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.teacher, cls.student = create_common_objects()
        cls.course = Course.objects.create(course_title='Course1', description='This is course 1', teacher=cls.teacher)
        cls.lecture = CourseActivity.objects.create(course=cls.course, activity_title='Lecture 1', description='This is lecture 1')
        cls.material = CourseActivityMaterial.objects.create(material_title='Material 1', description='This is material 1', course_activity=cls.lecture)
    
    def test_creation(self):
        self.assertEqual(self.material.material_title, 'Material 1')
        self.assertEqual(self.material.description, 'This is material 1')
        self.assertEqual(self.material.course_activity, self.lecture)
        self.assertIsNotNone(self.material.created_at)
        self.assertEqual(self.material.updated_at, self.material.created_at)

    def test_string_representation(self):
        self.assertEqual(str(self.material), "Course Title: Course1\nActivity Title: Lecture 1\nMaterial Title: Material 1")
    
    def test_file_upload(self):
        file_path=os.path.join(settings.BASE_DIR, 'elearning_base', 'test_files', 'test1.pdf')
        with open(file_path, 'rb') as f:
            self.material.file = SimpleUploadedFile("test1.pdf", content=f.read(), content_type='application/pdf')
            self.material.save()
            self.assertTrue(self.material.file)
    
    def test_foreign_key_deletion(self):
        self.lecture.delete()
        self.assertFalse(CourseActivityMaterial.objects.filter(material_id=self.material.material_id).exists())
    
    def test_valid_video_link(self):
        valid_url='https://www.example.com'
        self.material.video_link = valid_url
        self.material.save()
        self.assertEqual(self.material.video_link, valid_url)

    def test_invalid_video_link(self):
        invalid_url='example-com'
        self.material.video_link = invalid_url
        #Save not needed as that leads to the expected error being out of scope
        #Clean directly before saving or 
        #self.material.save()
        with self.assertRaises(ValidationError):
            #full_clean enforces field level validation and not only custom implemented clean methods
            self.material.full_clean()

#Test for Submission
class TestSubmission(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.teacher, cls.student = create_common_objects()
        cls.course = Course.objects.create(course_title='Course1', description='This is course 1', teacher=cls.teacher)
        cls.course_activity = CourseActivity.objects.create(course=cls.course, activity_title='Lecture 1', description='This is lecture 1')
        cls.file_path=os.path.join(settings.BASE_DIR, 'elearning_base', 'test_files', 'test1.pdf')

    def test_creation(self):
        with open(self.file_path, 'rb') as f:
            submission = Submission.objects.create(student=self.student, course_activity=self.course_activity, file=SimpleUploadedFile("test1.pdf", f.read(), content_type='application/pdf'))
        
        self.assertEqual(submission.student, self.student)
        self.assertEqual(submission.course_activity, self.course_activity)
        self.assertIsNotNone(submission.submitted_at)
        self.assertTrue(submission.file)
        self.assertIsNone(submission.grade)

    def test_teacher_submission(self):
        with open(self.file_path, 'rb') as f:
            with self.assertRaises(ValidationError):
                submission_error = Submission.objects.create(student=self.teacher, course_activity=self.course_activity, file=SimpleUploadedFile("test1.pdf", f.read(), content_type='application/pdf'))
                submission_error.clean()

    def test_valid_grade_format(self):
        with open(self.file_path, 'rb') as f:
            submission = Submission.objects.create(student=self.student, course_activity=self.course_activity, file=SimpleUploadedFile("test1.pdf", f.read(), content_type='application/pdf'))
            submission.grade = 85
            submission.save()
        self.assertEqual(submission.grade, 85)
    
    def test_invalid_grade_format_more_than_100(self):
        with open(self.file_path, 'rb') as f:
            submission = Submission.objects.create(student=self.student, course_activity=self.course_activity, file=SimpleUploadedFile("test1.pdf", f.read(), content_type='application/pdf'))
            with self.assertRaises(ValidationError):
                submission.grade = 100.5
                submission.clean()
        
    def test_invalid_grade_format_less_than_0(self):
        with open(self.file_path, 'rb') as f:
            submission = Submission.objects.create(student=self.student, course_activity=self.course_activity, file=SimpleUploadedFile("test1.pdf", f.read(), content_type='application/pdf'))
            with self.assertRaises(ValidationError):
                submission.grade = -1
                submission.clean()
    
    def test_submission_past_deadline(self):
        with open(self.file_path, 'rb') as f:
            submission = Submission.objects.create(student=self.student, course_activity=self.course_activity, file=SimpleUploadedFile("test1.pdf", f.read(), content_type='application/pdf'))
            self.course_activity.deadline = timezone.make_aware(datetime(2021, 8, 31, 23, 59, 59))
            self.course_activity.save()
            with self.assertRaises(ValidationError):
                submission.clean()
    
    def test_string_representation(self):
        with open(self.file_path, 'rb') as f:
            submission = Submission.objects.create(student=self.student, course_activity=self.course_activity, file=SimpleUploadedFile("test1.pdf", f.read(), content_type='application/pdf'))
        self.assertEqual(str(submission), "Username: student1\nEmail: student1@gmail.com\nIs Teacher? False\nCourse Title: Course1\nActivity Title: Lecture 1")
