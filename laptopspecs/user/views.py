from django.contrib.auth import authenticate

from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope

import json

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
    permission_classes = [AllowAny]
    serializer_class = UserProfileRegisterSerializer

class UserLogin(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request, format=None):
        """
        Login request with username and password.
        With successful login, the client should have get a response.
        The response should have the access token and refresh token.
        """
        
        # Get username and password.
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        # Check if the username exists.
        if not UserProfile.objects.prefetch_related('user').filter(user__username=username).exists():
            return Response(data="username \'{}\' does not exists.", status=status.HTTP_404_NOT_FOUND)

        user = authenticate(request=request, username=username, password=password)
        
        if user is not None:
            # Successful Login.
            # Start Oauth2 Authorization.
            pass
        else:
            return Response(data="Invalid user credentials !", status=status.HTTP_401_UNAUTHORIZED)
        


