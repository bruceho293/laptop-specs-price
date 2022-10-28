from django.shortcuts import render

from rest_framework import generics, authentication, permissions
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope

from user.serializers import UserProfileSerializer
from user.models import UserProfile

# Create your views here.
class UserDetail(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated, TokenHasReadWriteScope]
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    lookup_field = 'user__username'
    lookup_url_kwarg = 'username'