from django.contrib import admin
from django.urls import path
from accounting_system import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    # ADMIN
    path('admin/', admin.site.urls),
    # AUTH
    path('', auth_views.LoginView.as_view(template_name='accounting_system/auth.html',
                                          redirect_authenticated_user=True), name="login"),
    path('login/', auth_views.LoginView.as_view(template_name='accounting_system/auth.html',
                                                redirect_authenticated_user=True), name="login"),
    path('auth/', views.auth, name='auth'),
    path('logout/', views.logout_view, name='logout_view'),
    # CLIENTS
    path('clients/', views.clients, name='clients'),
    path('add-client/', views.add_client, name='add-client'),
    path('delete-client/', views.delete_client, name='delete-client'),
    # STAFF
    path('staff/', views.staff, name='staff'),
    path('add-manager/', views.add_manager, name='add-manager'),
    path('change-manager-form/', views.change_manager_form, name='change-manager-form'),
    path('change-manager/', views.change_manager, name='change-manager'),
    path('delete-manager/', views.delete_manager, name='delete-manager'),
    # TASKS
    path('tasks/', views.tasks, name='tasks'),
    # CALENDAR
    path('calendar/', views.calendar, name='calendar'),
    # SERVICE
    path('service/', views.service, name='service'),
    path('delete-service/', views.delete_service, name='delete-service'),
    path('add-service-for-client-form/', views.add_service_for_client_form, name='add-service-for-client-form'),
    # KKT
    path('kkt-service/', views.kkt_service, name='kkt-service'),
    path('add-kkt/', views.add_kkt, name='add-kkt'),
    path('delete-kkt/', views.delete_kkt, name='delete-kkt'),
    # FN
    path('fn-service/', views.fn_service, name='fn-service'),
    path('add-fn/', views.add_fn, name='add-fn'),
    path('delete-fn/', views.delete_fn, name='delete-fn'),
    # TO
    path('to-service/', views.to_service, name='to-service'),
    path('add-to/', views.add_to, name='add-to'),
    path('delete-to/', views.delete_to, name='delete-to'),
    # ECP
    path('ecp-service/', views.ecp_service, name='ecp-service'),
    path('add-ecp/', views.add_ecp, name='add-ecp'),
    path('delete-ecp/', views.delete_ecp, name='delete-ecp'),
    # OFD
    path('ofd-service/', views.ofd_service, name='ofd-service'),
    path('add-ofd/', views.add_ofd, name='add-ofd'),
    path('delete-ofd/', views.delete_ofd, name='delete-ofd'),
]
