from django.db import models

from django.contrib.auth.models import User

class UserProfileCustomManager(models.Manager):
    def create_user_profile(self, username, email, password):
        kwargs = {
          'username': username,
          'email': email,
          'password': password,
          'is_active': True,
          'is_staff': False,
          'is_superuser': False,
        }
        user = User.objects.create_user(**kwargs)
        self.create(user=user)
        return self