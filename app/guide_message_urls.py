from django.urls import path
from . import guide_message_views

urlpatterns = [
    path('booking/<int:booking_id>/', guide_message_views.guide_chat, name='guide_chat'),
    path('booking/<int:booking_id>/send/', guide_message_views.send_message, name='send_guide_message'),
]
