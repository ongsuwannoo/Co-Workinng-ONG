"""main URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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

from process import views

urlpatterns = [
    path('', views.my_login, name='login'),
    path('index/', views.index, name='index'),
    path('admin/', admin.site.urls),
    path('login/', views.my_login, name='login'),
    path('create_member/', views.my_create_member, name='create_member'),
    path('logout/', views.my_logout, name='logout'),
    path('change_password/', views.change_password, name='change_password'),
    path('money/', views.money, name='money'),
    path('create_zone/', views.create_zone, name='create_zone'),
]
