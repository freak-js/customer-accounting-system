"""customer_accounting_system URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from accounting_system import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', auth_views.LoginView.as_view(template_name='accounting_system/auth.html',
                                          redirect_authenticated_user=True), name="login"),
    path('login/', auth_views.LoginView.as_view(template_name='accounting_system/auth.html',
                                                redirect_authenticated_user=True), name="login"),
    path('auth/', views.auth, name='auth'),
    path('logout/', views.logout_view, name='logout_view'),
    path('clients/', views.clients, name='clients'),
    path('add-client/', views.add_client, name='add_client'),
    path('delete-client/', views.delete_client, name='delete_client'),
    path('staff/', views.staff, name='staff'),
    path('add-manager/', views.add_manager, name='add_manager'),
    path('delete-manager/', views.delete_manager, name='delete_manager'),
    path('tasks/', views.tasks, name='tasks'),
    path('calendar/', views.calendar, name='calendar'),
    path('service/', views.service, name='service'),
]
