from django.urls import path

from . import views

urlpatterns = [
    path('detail/<str:username>/', views.UserDetail.as_view(), name='user-detail'),
    path('register/', views.UserRegister.as_view(), name='user-register'),
    path('login/', views.UserLogin.as_view(), name='user-login'),
    # path('logout/'),
]
