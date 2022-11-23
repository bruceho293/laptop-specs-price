"""laptopspecs URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls.static import static
from django.conf.urls import handler404
from django.conf import settings
from django.shortcuts import redirect
from django.urls import path, include, re_path
from django.views.static import serve

from rest_framework import routers
from oauth2_provider import views as oauth2_views

from laptop import views

router = routers.DefaultRouter()
router.register(r'laptops', views.LaptopViewSet, basename='laptop')
router.register(r'components', views.ComponentViewSet, basename='component')

# Oauth 
# OAuth2 provider endpoints
oauth2_endpoint_views = [
    path('authorize/', oauth2_views.AuthorizationView.as_view(), name='authorize'),
    path('token/', oauth2_views.TokenView.as_view(), name='token'),
    path('revoke-token/', oauth2_views.RevokeTokenView.as_view(), name='revoke-token'),
]

if settings.DEBUG:
    # OAuth2 Application Management endpoints
    oauth2_endpoint_views += [
        path('applications/', oauth2_views.ApplicationList.as_view(), name='list'),
        path('applications/register/', oauth2_views.ApplicationRegistration.as_view(), name='register'),
        path('applications/<pk>/', oauth2_views.ApplicationDetail.as_view(), name='detail'),
        path('applications/<pk>/delete/', oauth2_views.ApplicationDelete.as_view(), name='delete'),
        path('applications/<pk>/update/', oauth2_views.ApplicationUpdate.as_view(), name='update'),
    ]

    # OAuth2 Token Management endpoints
    oauth2_endpoint_views += [
        path('authorized-tokens/', oauth2_views.AuthorizedTokensListView.as_view(), name='authorized-token-list'),
        path('authorized-tokens/<pk>/delete/', oauth2_views.AuthorizedTokenDeleteView.as_view(),
            name="authorized-token-delete"),
    ]

# Final URLs 
urlpatterns = [
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    path('accounts/', admin.site.urls, name="admin"),
    path('o/', include((oauth2_endpoint_views, 'oauth2_provider'), namespace='oath2_provider')),
    path('user/', include('user.urls'), name="user"),
    path('laptop/', include('laptop.urls')),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/', include(router.urls), name='api'),
    path('', views.homepage, name="homepage"),
]

urlpatterns += static(prefix=settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler404 = views.error_404_not_found