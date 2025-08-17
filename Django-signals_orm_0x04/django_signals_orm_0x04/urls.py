"""
URL configuration for django_signals_orm_0x04 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path, include
from messaging import views as msg_views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'messages', msg_views.MessageViewSet, basename='message')
router.register(r'notifications', msg_views.NotificationViewSet, basename='notification')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('rest_framework.urls')),  # For login/logout
    path('api/conversations/<int:user_id>/', 
         msg_views.MessageViewSet.as_view({'get': 'conversation'}), 
         name='conversation'),
    path('api/delete-account/', 
         msg_views.delete_user, 
         name='delete_account'),
    path('api/', include(router.urls)),
]
