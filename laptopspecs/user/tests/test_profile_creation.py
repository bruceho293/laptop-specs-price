from django.test import TestCase

from django.contrib.auth.models import User
from user.models import Profile


class UserCreationTestCase(TestCase):
    def test_user_creation_method(self):
        kwargs = {
          'username': "teddybear",
          'email': "teddybear@teddy.com",
          'password': "123456789",
        }
        profile = Profile.create_user_profile(**kwargs)
        
        self.assertTrue(User.objects.filter(username="teddybear").exists())
        self.assertTrue(User.objects.filter(email="teddybear@teddy.com").exists())

        user = User.objects.get(username="teddybear")
        self.assertTrue(user.is_active, "The user account should be active")
        self.assertFalse(user.is_staff, "The user account does not have staff priviledges")
        self.assertFalse(user.is_superuser, "The user account does not have superuser priviledges")
        