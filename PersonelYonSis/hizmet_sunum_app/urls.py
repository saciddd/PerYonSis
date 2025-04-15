from django.urls import path
from . import views

app_name = 'hizmet_sunum_app'

urlpatterns = [
    path('bildirim/', views.bildirim, name='bildirim'),
]
