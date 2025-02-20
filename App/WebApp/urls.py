from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views, tables

urlpatterns = [

    path('', views.index, name='index'),  # Login Page
    path('login', views.userLogin, name='userLogin'),
    path('Dashboard', views.Dashboard, name='Dashboard'),
    path('TaxSlab', views.TaxSlab, name='TaxSlab'),
    path('verify', views.verify, name='verify'),
    path('InventoryForm', views.InventoryForm, name='InventoryForm'),
    path('InventoryList', views.InventoryList, name='InventoryList'),
    path('OutGoingStock', views.OutGoingStock, name='OutGoingStock'),
    path('OutGoingStockList', views.OutGoingStockList, name='OutGoingStockList'),

    path('CreatePromotions', views.CreatePromotions, name='CreatePromotions'),

    path('PromotedEmployeeList', views.PromotedEmployeeList, name='PromotedEmployeeList'),

    path('Logout', views.Logout, name='Logout'),
    path('DispositionList', views.getDispositionList, name='DispositionList'),
    path('AddEditDisposition', views.AddEditDisposition, name='AddEditDisposition'),
    path('RetiredTransferredEmployee', views.RetiredTransferredEmployee, name='RetiredTransferredEmployee'),

    path('Search', views.Search, name='Search'),
    path('Zone', views.Zone, name='Zone'),
    path('Sanction_Strength', views.Sanction_Strength, name='Sanction_Strength'),

    path('Strength', views.Strength, name='Strength'),
    path('TransferPosting', views.EmployeeTransferPosting, name='TransferPosting'),
    path('ManageTransferPosting', views.ManageEmployeeTransferPosting, name='ManageTransferPosting'),
    path('LeaveApplication',views.submitLeaveApplication, name='submitLeaveApplication'),
    path('ManageLeaveApplication',views.ManageEmployeeLeaveApplication, name='ManageLeaveApplication'),
    path('EmployeeExplanation', views.EmployeeExplanation, name='EmployeeExplanation'),
    path('ManageEmployeeExplanation', views.ManageEmployeeExplanation, name='ManageEmployeeExplanation'),

    path('get_employee_leave_data/<int:emp_id>/', views.get_employee_leave_data, name='get_employee_leave_data'),
    path('get_employee_unit_data/<int:emp_id>/', tables.get_employee_unit_data_table, name='get_employee_unit_data_table'),
    path('get_employee_exp_data/<int:emp_id>/', tables.get_employee_exp_data_table, name='get_employee_exp_data_table'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)