# nobet_defteri/urls.py
from django.urls import path
from . import views

app_name = 'nobet_defteri'

urlpatterns = [
    path('', views.nobet_defteri_list, name='liste'),
    path('olustur/', views.nobet_defteri_olustur, name='olustur'),
    path('<int:defter_id>/', views.nobet_defteri_detay, name='detay'),
    path('<int:defter_id>/onayla/', views.nobet_defteri_onayla, name='onayla'),
]
