from django.test import TestCase
from django.contrib.auth.models import User
from .models import StudentProfile, WebsiteCategory, Website, Subscription

class StudentProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
    
    def test_student_profile_creation(self):
        profile = StudentProfile.objects.get(user=self.user)
        self.assertEqual(profile.user.username, 'testuser')

class WebsiteModelTest(TestCase):
    def setUp(self):
        self.category = WebsiteCategory.objects.create(
            name='Образовательные',
            description='Образовательные сайты'
        )
        self.website = Website.objects.create(
            name='Тестовый сайт',
            url='https://example.com',
            category=self.category
        )
    
    def test_website_creation(self):
        self.assertEqual(self.website.name, 'Тестовый сайт')
        self.assertEqual(self.website.category.name, 'Образовательные')