from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.emergency_dashboard, name='emergency_dashboard'),
    path('menu/', views.emergency_menu, name='emergency_menu'),
    path('sos/', views.sos_alert, name='sos_alert'),
    path('status/<int:id>/', views.emergency_status, name='emergency_status'),
    path('history/', views.emergency_history, name='emergency_history'),
    path('contacts/', views.get_emergency_contacts, name='emergency_contacts'),
    path('contacts/manage/', views.emergency_contacts, name='emergency_contacts_manage'),
    path('hospitals/', views.nearby_hospitals, name='nearby_hospitals'),
    path('hospitals/api/', views.hospitals_api, name='hospitals_api'),
    path('map/', views.emergency_map, name='emergency_map'),
]
