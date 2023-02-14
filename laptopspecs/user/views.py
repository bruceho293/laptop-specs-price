from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.debug import sensitive_post_parameters

from dotenv import load_dotenv
import json

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

from user.serializers import UserProfileDetailSerializer, UserProfileRegisterSerializer, UserImpressionSerializer
from user.models import UserProfile, UserImpression
from user.decorators import get_client_credentials

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

class UserLikeDislike(generics.UpdateAPIView, generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, TokenHasReadWriteScope]
    queryset = UserImpression.objects.all()
    serializer_class = UserImpressionSerializer

class UserRegister(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserProfileRegisterSerializer

@method_decorator(csrf_exempt, name="dispatch")
class UserToken(TokenView):
    """
    User token request with username and password based on Oauth2 Resource Owner Password-based.
    Implemented based on TokenView from Djano Oauth2 Toolkit.
    With successful login, the client should have get a response with access token.
    """
    
    @method_decorator(sensitive_post_parameters("password"))
    @method_decorator(get_client_credentials)
    def post(self, request, *args, **kwargs):
        
        # Get all necessary variables.       
        data = request.POST
        username = data.get('username')
        password = data.get('password')
        grant_type = data.get('grant_type')

        # Check if the username exists when user logins.
        if grant_type != "refresh_token":
          if not UserProfile.objects.prefetch_related('user').filter(user__username=username).exists():
              return HttpResponse(content=json.dumps({"error": "username \'{}\' does not exists.".format(username)}), status=rest_status.HTTP_404_NOT_FOUND)

          user = authenticate(request=request, username=username, password=password)
        
          if user is None:
            return HttpResponse(content=json.dumps({"error":"Invalid user credentials!"}), status=rest_status.HTTP_401_UNAUTHORIZED)

        # Either the user is authenticated or the grant_type is "refresh_token"  
        url, headers, body, status = self.create_token_response(request)
        if status == 200:
            access_token = json.loads(body).get("access_token")
            if access_token is not None:
                token = get_access_token_model().objects.get(token=access_token)
                app_authorized.send(sender=self, request=request, token=token)
            # Remove some extra information about OAuth2 Tokens
            body = json.loads(body)
            body.pop("expires_in", None)
            body = json.dumps(body)
        
        response = HttpResponse(content=body, status=status)

        for k, v in headers.items():
            response[k] = v
        return response

@method_decorator(csrf_exempt, name="dispatch")
class UserRevokeToken(RevokeTokenView):
    """
    Logout API endpoint that revoke both Oauth2 Access Token and Refresh Token.
    """

    @method_decorator(get_client_credentials)
    def post(self, request, *args, **kwargs):
        # TODO: Looking into why the tokens don't get modified in `revoke-token` (FIXED) 
        
        # Check if the token is refresh token.
        token = request.POST.get('token')
        if not get_refresh_token_model().objects.filter(token=token).exists():
            return HttpResponse(content="Invalid token", status=rest_status.HTTP_404_NOT_FOUND)       

        url, headers, body, status = self.create_revocation_response(request)
        response = HttpResponse(content=body or "", status=status)

        for k, v in headers.items():
            response[k] = v
        return response

