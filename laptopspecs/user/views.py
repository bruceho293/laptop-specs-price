from django.contrib.auth import authenticate, login
from django.http import HttpRequest, HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse
from django.utils.http import urlencode

from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope
from oauth2_provider.views import TokenView
from oauth2_provider.models import Application

from user.serializers import UserProfileDetailSerializer, UserProfileRegisterSerializer
from user.models import UserProfile
from django.contrib.auth.models import User
import base64

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
    
    def post(self, request, *args, **kwargs):
        """
        Login request with username and password.
        With successful login, the client should have get a response.
        The response should have the access token and refresh token.
        """
        
        # Get all necessary variables.
        data = request.data
        username = data.get('username')
        password = data.get('password')

        # Check if the username exists.
        if not UserProfile.objects.prefetch_related('user').filter(user__username=username).exists():
            return Response(data="username \'{}\' does not exists.", status=status.HTTP_404_NOT_FOUND)

        user = authenticate(request=request, username=username, password=password)
        
        if user is not None:
            # Successful Login.
            # Start Oauth2 Authorization.
            
            user_client = Application.objects.get(user=user)
            user_profile = UserProfile.objects.get(user=user)

            client_id = user_client.client_id,
            client_secret = user_profile.oauth2_client_secret
            client = base64.b64encode('{}:{}'.format(client_id, client_secret).encode()).decode()

            data = {
              "grant_type": user_client.authorization_grant_type,
              "username": username,
              "password": password,
            }

            request = HttpRequest()
            request.method = 'POST'
            request.data = data
            request.META['HTTP_AUTHORIZATION'] = 'Basic {}'.format(client)

            oauth_response = TokenView.as_view()(request)
            if oauth_response.status_code == 200:
                return Response(data=oauth_response.data, status=status.HTTP_200_OK)
            else:
                return oauth_response
        else:
            return Response(data={"error":"Invalid user credentials!"}, status=status.HTTP_401_UNAUTHORIZED)

