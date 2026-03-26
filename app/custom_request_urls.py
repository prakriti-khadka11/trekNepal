"""
URL patterns for Custom Package Request System
"""
from django.urls import path
from . import custom_request_views

urlpatterns = [
    # User URLs
    path('create/', custom_request_views.create_custom_request, name='create_custom_request'),
    path('my-requests/', custom_request_views.my_custom_requests, name='my_custom_requests'),
    path('request/<int:request_id>/', custom_request_views.view_custom_request, name='view_custom_request'),
    path('quote/<int:quote_id>/accept/', custom_request_views.accept_quote, name='accept_quote'),
    path('quote/<int:quote_id>/reject/', custom_request_views.reject_quote, name='reject_quote'),

    # Khalti payment for custom requests
    path('khalti/initiate/<int:quote_id>/', custom_request_views.khalti_initiate_custom, name='khalti_initiate_custom'),
    path('khalti/verify/', custom_request_views.khalti_verify_custom, name='khalti_verify_custom'),

    # Admin URLs
    path('admin/dashboard/', custom_request_views.admin_custom_requests, name='admin_custom_requests'),
    path('admin/request/<int:request_id>/', custom_request_views.admin_view_request, name='admin_view_request'),
    path('admin/request/<int:request_id>/create-quote/', custom_request_views.admin_create_quote, name='admin_create_quote'),
]
