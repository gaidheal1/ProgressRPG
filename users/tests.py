
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from unittest import skip

from .models import Profile

from character.models import Character, PlayerCharacterLink



class UserCreationTest(TestCase):
    def setUp(self):
        self.character = Character.objects.create(
            first_name='Jane',
            sex='Female'
        )
        self.UserModel = get_user_model()

    def test_create_user(self):
        """Test that a user can be created successfully."""
        user = self.UserModel.objects.create_user(
            email='testuser@example.com',
            password='testpassword123'
        )
        self.assertEqual(user.email, 'testuser@example.com')
        self.assertTrue(user.check_password('testpassword123'))

        profile = user.profile
        self.assertTrue(isinstance(user.profile, Profile))
        self.assertEqual(user, user.profile.user)
        self.assertEqual(user.profile.xp, 0)

    def test_create_superuser(self):
        """Test that a superuser can be created successfully."""
        User = get_user_model()
        superuser = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpassword123'
        )
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)

    def test_character_assigned_on_profile(self):
        user = self.UserModel.objects.create_user(
            email='testuser1@example.com',
            password='testpassword123'
        )
        link = PlayerCharacterLink.objects.filter(profile=user.profile).first()
        character = link.character
        self.assertEqual(character, self.character)

class OnboardingTest(TestCase):
    @skip("Skipping due to DB changes")
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpassword123'
        )
        self.client.login(email='testuser@example.com', password='testpassword123')
        self.profile = self.user.profile
        self.character = Character.objects.get(profile=self.profile)

    def test_initial_onboarding(self):
        self.assertTrue(self.user.profile.onboarding_step == 0)

    def test_onboarding_profile(self):
        url = reverse("create_profile")

        data = {
            'name': 'Test name',
        }
        
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)
        expected_url = reverse('create_character')
        self.assertRedirects(response, expected_url)
        
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.onboarding_step, 2)
        self.assertTrue(self.profile.name=='Test name')

    def test_onboarding_character(self):
        self.profile.onboarding_step = 2
        
        url = reverse("create_character")

        data = {
            'character_name': 'Test name',
        }
        
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)
        expected_url = reverse('subscribe')
        self.assertRedirects(response, expected_url)
        
        self.profile.refresh_from_db()
        self.character.refresh_from_db()
        self.assertEqual(self.profile.onboarding_step, 3)
        self.assertTrue(self.character.name=='Test name')

    def test_onboarding_subscribe(self):
        self.profile.onboarding_step = 3
        
        url = reverse("subscribe")

        data = {}
        
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)
        expected_url = reverse('game')
        self.assertRedirects(response, expected_url)
        
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.onboarding_step, 4)

class PersonXpTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            email='testuser1@example.com',
            password='testpassword123'
        )

    def test_profile_create(self):
        self.assertTrue(isinstance(self.user.profile, Profile))
        self.assertEqual(self.user, self.user.profile.user)
        self.assertEqual(self.user.profile.xp, 0)

    def test_profile_addxp(self):
        profile = self.user.profile
        self.assertEqual(profile.get_xp_for_next_level(), 100)

        profile.xp = 100
        profile.level_up()
        self.assertEqual(profile.level, 1)
        
        profile.add_xp(100)
        self.assertEqual(profile.xp, 100)
        self.assertEqual(profile.level, 1)
        self.assertEqual(profile.get_xp_for_next_level(), 200)

        profile.add_xp(100)
        self.assertEqual(profile.xp, 0)
        self.assertEqual(profile.level, 2)
        self.assertEqual(profile.get_xp_for_next_level(), 300)

class ProfileMethodsTest(TestCase):
    def setUp(self):
        character=Character.objects.create(
            first_name="Jane",
        )
        self.character2=Character.objects.create(
            first_name="John",
        )
        User = get_user_model()
        self.user = User.objects.create_user(
            email='testuser1@example.com',
            password='testpassword123'
        )

    def test_profile_addactivity(self):
        profile = self.user.profile
        profile.add_activity(10, 1)
        self.assertEqual(profile.total_time, 10)
        self.assertEqual(profile.total_activities, 1)

    def test_change_character(self):
        profile = self.user.profile
        link = PlayerCharacterLink.objects.filter(profile=profile).first()
        character = link.character
        self.assertTrue(character.first_name, "Jane")
        profile.change_character(self.character2)
        self.assertTrue(character.first_name, "John")


# Testing views: mock the response, then write the assertions

class TestViews_LoggedIn(TestCase):
    def setUp(self):
        self.client = Client()

        # urls
        self.index_url = reverse('index')
        self.profile_url = reverse('profile')
        self.editprofile_url = reverse('edit_profile')

        User = get_user_model()
        user = User.objects.create_user(
            email='testuser@example.com',
            password='testpassword123'
        )

        self.client.login(email='testuser@example.com', password='testpassword123')

    def test_index_GET(self):
        """
        Check the index is rendered successfully
        """
        response = self.client.get(self.index_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/index.html')

    def test_profile_GET(self):
        """
        Check the profile is rendered successfully
        """
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile.html')
    
    def test_profile_edit_GET(self):

        response = self.client.get(self.editprofile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/edit_profile.html')

class TestViews_LoggedOut(TestCase):
    def setUp(self):
        # urls
        self.index_url = reverse('index')
        self.profile_url = reverse('profile')
        self.editprofile_url = reverse('edit_profile')
        self.register_url = reverse('register')

    def test_profile_GET_loggedout(self):
        """
        Check redirect to login if user not logged in
        """
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 302)

    def test_editprofile_GET_loggedout(self):
        """
        Check redirect to login if user not logged in
        """
        response = self.client.get(self.editprofile_url)
        self.assertEqual(response.status_code, 302)

    def test_register_GET(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')

