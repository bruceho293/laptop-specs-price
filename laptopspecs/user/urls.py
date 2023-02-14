from django.urls import path

from . import views

urlpatterns = [
    path('token/', views.UserToken.as_view(), name='token'),
    path('revoke_token/', views.UserRevokeToken.as_view(), name='revoke-token'),
    path('register/', views.UserRegister.as_view(), name='register'),
    path('detail/<str:username>', views.UserDetail.as_view(), name='detail'),
    path('impression/', views.UserLikeDislike.as_view(), name='like-dislike'),

    path('test/', views.test, name='test')
]
