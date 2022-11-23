from django.contrib.auth import authenticate, login
from django.http import HttpRequest, HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse
from django.utils.http import urlencode

from rest_framework import generics, status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope

from user.serializers import UserProfileDetailSerializer, UserProfileRegisterSerializer
from user.models import UserProfile
from user.decorators import get_request_user
from django.contrib.auth.models import User

# Create your views here
@api_view(['GET'])
@get_request_user
def authorize(request):
    """
    Intermediate Custom Oauth2 Authorization Request.
    """
    data = {
      'user': str(request.user),
      'is_authenticated': request.user.is_authenticated
    }
    return Response(data=data)

@api_view(['POST'])
def get_token(request):
    """
    Intermediate Custom Oauth2 Token Request.
    """
    pass

@api_view(['POST'])
def revoke_token(request):
    """
    Intermediate Custom Oauth2 Authorization Request.
    """
    pass

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
            login(request=request, user=user)
            content = {
               'user': str(request.user),
               'is_authenticated': request.user.is_authenticated
            }
            return Response(content)
        else:
            return Response(data={"error":"Invalid user credentials!"}, status=status.HTTP_401_UNAUTHORIZED)

