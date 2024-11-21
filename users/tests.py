from django.test import TestCase
from django.contrib.auth import get_user_model

# Create your tests here.


class UserCreationTest(TestCase):
    def test_create_user(self):
        """Test that a user can be created successfully."""
        User = get_user_model()
        user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword123'
        )

        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'testuser@example.com')
        self.assertTrue(user.check_password('testpassword123'))
        

class SuperuserCreationTest(TestCase):
    def test_create_superuser(self):
        """Test that a superuser can be created successfully."""
        User = get_user_model()
        superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpassword123'
        )

        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)
        
        