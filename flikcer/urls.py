"""flikcer URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path
from .epilepsy.views import get_number_of_triggers, poll_number_of_triggers, get_safe_video, poll_safe_video

urlpatterns = [
    path('num_triggers/', get_number_of_triggers, name='num_triggers'),
    path('num_triggers/poll/', poll_number_of_triggers, name='poll_num_triggers'),
    path('safe_video/', get_safe_video, name='safe_video'),
    path('safe_video/poll/', poll_safe_video, name='poll_safe_video'),
]
