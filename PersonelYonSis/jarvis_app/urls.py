from django.urls import path
from . import views

app_name = 'jarvis_app'

urlpatterns = [
    path('', views.chat_view, name='chat'),
    path('api/chat', views.api_chat, name='api_chat'),
]
