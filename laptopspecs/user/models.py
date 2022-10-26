from django.db import models
from django.contrib.auth.models import User

# Create your models here.
def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'user_{0}/{1}'.format(instance.user.id, filename)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to=user_directory_path)

    @classmethod
    def create_user_profile(cls, username, email, password):
        kwargs = {
          'username': username,
          'email': email,
          'password': password,
          'is_active': True,
          'is_staff': False,
          'is_superuser': False,
        }
        user = User.objects.create(**kwargs)
        profile = cls(user=user)
        return profile