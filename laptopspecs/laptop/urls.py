from django.urls import path
from . import views

app_name = 'laptop'

urlpatterns = [
    path('search/', views.LaptopSearchList.as_view(), name='laptop-search'),
    path('detail/<int:laptop_id>/<slug:slug>', views.LaptopInfo.as_view(), name='laptop-info'),
]