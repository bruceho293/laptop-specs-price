from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.debug import sensitive_post_parameters

from dotenv import load_dotenv
import base64
import json
import os

load_dotenv()

from rest_framework import generics
from rest_framework import status as rest_status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope
from oauth2_provider.views import TokenView, RevokeTokenView
from oauth2_provider.models import get_access_token_model, get_refresh_token_model
from oauth2_provider.signals import app_authorized
from oauth2_provider.decorators import protected_resource

from user.serializers import UserProfileDetailSerializer, UserProfileRegisterSerializer
from user.models import UserProfile

@api_view(['GET'])
@permission_classes([TokenHasReadWriteScope])
@protected_resource()
def test(request):
    return Response(data="Hello World")

class UserDetail(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, TokenHasReadWriteScope]
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileDetailSerializer
    lookup_field = 'user__username'
    lookup_url_kwarg = 'username'

class UserRegister(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserProfileRegisterSerializer

@method_decorator(csrf_exempt, name="dispatch")
class UserLogin(TokenView):
    """
    Login request with username and password based on Oauth2 Resource Owner Password-based.
    Implemented based on TokenView from Djano Oauth2 Toolkit.
    With successful login, the client should have get a response with access token.
    """
    
    @method_decorator(sensitive_post_parameters("password"))
    def post(self, request, *args, **kwargs):
        
        # Get all necessary variables.
        data = request.POST
        username = data.get('username')
        password = data.get('password')
        client_id = data.get('client_id')

        # Check if the username exists.
        if not UserProfile.objects.prefetch_related('user').filter(user__username=username).exists():
            return HttpResponse(content=json.dumps({"error": "username \'{}\' does not exists.".format(username)}), status=rest_status.HTTP_404_NOT_FOUND)

        user = authenticate(request=request, username=username, password=password)
        
        if user is not None:
            # Successful Authentication.
            client_secret = os.environ.get('OAUTH2_CLIENT_SECRET')
            client = base64.b64encode('{}:{}'.format(client_id, client_secret).encode()).decode()
            
            request.META['HTTP_AUTHORIZATION'] = 'Basic {}'.format(client)

            # Oauth2 Token view
            url, headers, body, status = self.create_token_response(request)
            if status == 200:
                access_token = json.loads(body).get("access_token")
                if access_token is not None:
                    token = get_access_token_model().objects.get(token=access_token)
                    app_authorized.send(sender=self, request=request, token=token)
            response = HttpResponse(content=body, status=status)
    
            for k, v in headers.items():
                response[k] = v
            return response
        else:
            return HttpResponse(content=json.dumps({"error":"Invalid user credentials!"}), status=rest_status.HTTP_401_UNAUTHORIZED)

@method_decorator(csrf_exempt, name="dispatch")
class UserLogout(RevokeTokenView):
    """
    Logout API endpoint that revoke both Oauth2 Access Token and Refresh Token.
    """

    def post(self, request, *args, **kwargs):
        # TODO: Looking into why the tokens don't get modified in `revoke-token` (FIXED) 
        
        # Custom setup for authorization
        client_id = request.POST.get('client_id')
        client_secret = os.environ.get('OAUTH2_CLIENT_SECRET')
        client = base64.b64encode('{}:{}'.format(client_id, client_secret).encode()).decode()    
        request.META['HTTP_AUTHORIZATION'] = 'Basic {}'.format(client)

        # Check if the token is refresh token.
        token = request.POST.get('token')
        if not get_refresh_token_model().objects.filter(token=token).exists():
            return HttpResponse(content="Invalid token", status=rest_status.HTTP_404_NOT_FOUND)       

        url, headers, body, status = self.create_revocation_response(request)
        response = HttpResponse(content=body or "", status=status)

        for k, v in headers.items():
            response[k] = v
        return response

