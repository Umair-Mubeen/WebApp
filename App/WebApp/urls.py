from django.urls import path

from . import views
from .views import *
urlpatterns = [

path('', views.index, name='index'),  # Login Page
path('login', views.userLogin, name='userLogin'),
path('Dashboard', views.Dashboard, name='Dashboard'),
path('Logout', views.Logout, name='Logout'),

]