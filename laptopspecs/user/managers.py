from django.db import models

from django.contrib.auth.models import User
from oauth2_provider.models import Application

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
        # application = Application.objects.create(
        #   name='{}-auth-application'.format(user.username),
        #   user=user, 
        #   authorization_grant_type='password', 
        #   client_type='confidential'
        # )
        self.create(user=user)
        # application.client_secret=self.get(user=user).oauth2_client_secret
        # application.save()
        return self