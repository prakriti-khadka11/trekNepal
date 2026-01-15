from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.emergency_dashboard, name='emergency_dashboard'),
    path('menu/', views.emergency_menu, name='emergency_menu'),  # menu page
    path('sos/', views.sos_alert, name='sos_alert'),
    path('status/<int:id>/', views.emergency_status, name='emergency_status'),
    path('history/', views.emergency_history, name='emergency_history'),
]
