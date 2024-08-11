from django.urls import path

from . import views

urlpatterns = [

    path('', views.index, name='index'),  # Login Page
    path('login', views.userLogin, name='userLogin'),
    path('Dashboard', views.Dashboard, name='Dashboard'),
    path('Logout', views.Logout, name='Logout'),
    path('DispositionList', views.getDispositionList, name='DispositionList'),
    path('TransferPosting', views.EmployeeTransferPosting, name='TransferPosting'),
    path('Search', views.Search, name='Search'),
    path('Zone', views.Zone, name='Zone'),
    path('Strength', views.Strength, name='Strength'),



]
