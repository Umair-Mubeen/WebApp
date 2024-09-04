from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [

    path('', views.index, name='index'),  # Login Page
    path('login', views.userLogin, name='userLogin'),
    path('Dashboard', views.Dashboard, name='Dashboard'),
    path('Logout', views.Logout, name='Logout'),
    path('DispositionList', views.getDispositionList, name='DispositionList'),
    path('Search', views.Search, name='Search'),
    path('Zone', views.Zone, name='Zone'),
    path('Strength', views.Strength, name='Strength'),
    path('TransferPosting', views.EmployeeTransferPosting, name='TransferPosting'),
    path('ManageTransferPosting', views.ManageEmployeeTransferPosting, name='ManageTransferPosting'),
    path('LeaveApplication',views.submitLeaveApplication, name='submitLeaveApplication'),
    path('ManageLeaveApplication',views.ManageEmployeeLeaveApplication, name='ManageLeaveApplication'),
    path('get_employee_leave_data/<int:emp_id>/', views.get_employee_leave_data, name='get_employee_leave_data'),
    path('get_employee_unit_data/<int:emp_id>/', views.get_employee_unit_data, name='get_employee_unit_data'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
