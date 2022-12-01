from django.urls import path

from . import views

urlpatterns = [
    path('login/', views.UserLogin.as_view(), name='login'),
    path('register/', views.UserRegister.as_view(), name='register'),
    path('detail/', views.UserDetail.as_view(), name='detail'),

    path('test/', views.test, name='test')
]
