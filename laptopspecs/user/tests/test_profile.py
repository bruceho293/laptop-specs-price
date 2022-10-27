from django.test import TestCase

from django.contrib.auth.models import User
from user.models import UserProfile, UserImpression
from laptop.models import Brand, Laptop

class ProfileTestCase(TestCase):
    def setUp(self):
        kwargs = {
          'username': "teddybear",
          'email': "teddybear@teddy.com",
          'password': "123456789",
        }
        UserProfile.custom_manager.create_user_profile(**kwargs)
    
    def test_user_creation_method(self):        
        self.assertTrue(User.objects.filter(username="teddybear").exists())
        self.assertTrue(User.objects.filter(email="teddybear@teddy.com").exists())

        user = User.objects.get(username="teddybear")
        self.assertTrue(user.is_active, "The user account should be active.")
        self.assertFalse(user.is_staff, "The user account does not have staff priviledges.")
        self.assertFalse(user.is_superuser, "The user account does not have superuser priviledges.")

        profile = UserProfile.objects.get(user=user)
        self.assertTrue(profile.user.is_active, "The user account should be active.")
        self.assertFalse(profile.user.is_staff, "The user account does not have staff priviledges.")
        self.assertFalse(profile.user.is_superuser, "The user account does not have superuser priviledges.")

        self.assertEquals(user.profile, profile, "The profile should be accessible by the user.")
    
    def test_user_impression(self):
        user = User.objects.get(username="teddybear")
        brand = Brand.objects.create(name="Brand 1")
        lt1 = Laptop.objects.create(name="Laptop 1", slug="laptop-1", brand=brand, price=1.0)
        lt2 = Laptop.objects.create(name="Laptop 2", slug="laptop-2", brand=brand, price=1.0)

        user.profile.imp_laptop.add(lt1, lt2)
        self.assertTrue(user.profile.like_laptop("Laptop 1"), "User should like laptop 1 by default.")
        self.assertTrue(user.profile.like_laptop("Laptop 2"), "User should like laptop 2 by default.")
        self.assertEquals(user.profile.like_laptop("Laptop 1"), 1, "User should like laptop 1 by default.")
        self.assertEquals(user.profile.like_laptop("Laptop 2"), 1, "User should like laptop 2 by default.")

        user_impression = UserImpression.objects.get(profile__user=user, laptop=lt2)
        user_impression.liked = False
        user_impression.save()
        self.assertTrue(user.profile.like_laptop("Laptop 1"), "User should like laptop 1 by default.")
        self.assertFalse(user.profile.like_laptop("Laptop 2"), "User should not like the updated laptop 2.")
        self.assertEquals(user.profile.like_laptop("Laptop 1"), 1, "User should like laptop 1 by default.")
        self.assertEquals(user.profile.like_laptop("Laptop 2"), 0, "User should not like the updated laptop 2.")

        UserImpression.objects.filter(profile__user=user, laptop=lt1).delete()
        self.assertFalse(user.profile.like_laptop("Laptop 2"), "User should not like the updated laptop 2.")
        self.assertEquals(user.profile.like_laptop("Laptop 1"), -1, "User should have no interest with laptop 1.")
        self.assertEquals(user.profile.like_laptop("Laptop 2"), 0, "User should not like the updated laptop 2.")
        

        