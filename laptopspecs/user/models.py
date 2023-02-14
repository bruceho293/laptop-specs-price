from django.db import models

from django.contrib.auth.models import User

from laptop.models import Laptop
from user.managers import UserProfileCustomManager

# Create your models here.
def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'user_{0}/{1}'.format(instance.user.id, filename)

class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE, primary_key=True)
    avatar = models.ImageField(upload_to=user_directory_path, null=True, blank=True)
    imp_laptop = models.ManyToManyField(Laptop, related_name="laptop_impression", through="UserImpression", through_fields=('profile', 'laptop'))

    objects = models.Manager()
    custom_manager = UserProfileCustomManager()

    def __str__(self):
        return self.user.username + ' profile'

    def like_laptop(self, laptop_name):
        user_impression = UserImpression.objects.filter(profile=self, laptop__name=laptop_name)
        if user_impression.exists():
            return user_impression.get().liked
        return -1 # Uninterest 

class UserImpression(models.Model):
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    laptop = models.ForeignKey(Laptop, on_delete=models.CASCADE)
    liked = models.BooleanField(default=True)

    class Meta:
        constraints = [
          models.UniqueConstraint(fields=['profile', 'laptop'], name='unique_profile_laptop_impression'),
        ]