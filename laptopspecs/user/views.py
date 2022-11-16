from django.http import HttpResponse
from django.shortcuts import render

from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import BasicAuthentication
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope

from user.serializers import UserProfileDetailSerializer, UserProfileRegisterSerializer
from user.models import UserProfile

# Create your views here.
class UserDetail(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, TokenHasReadWriteScope]
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileDetailSerializer
    lookup_field = 'user__username'
    lookup_url_kwarg = 'username'

class UserRegister(generics.CreateAPIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [AllowAny]
    serializer_class = UserProfileRegisterSerializer