from django.urls import path
from . import chatbot_views

urlpatterns = [
    path('', chatbot_views.chatbot_interface, name='chatbot_interface'),
    path('message/', chatbot_views.chatbot_message, name='chatbot_message'),
]