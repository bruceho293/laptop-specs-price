from django.urls import path

from . import views

urlpatterns = [
    path('login/', views.UserLogin.as_view(), name='login'),
    path('register/', views.UserRegister.as_view(), name='register'),
    path('detail/', views.UserDetail.as_view(), name='detail'),
    
    # User authorization through Oauth 2
    # path('authorize/', views.authorize, name='authorize'),
    # path('token/', views.get_token, name='token'),
    # path('revoke-token/', views.revoke_token, name='revoke-token'),
]
