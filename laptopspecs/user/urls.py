from django.urls import path

from . import views

urlpatterns = [
    path('<str:username>/', views.UserDetail.as_view(), name='user-detail'),
    path('register/', views.UserRegister.as_view(), name='user-register'),
    # path('login/',),
    # path('logout/'),
]
