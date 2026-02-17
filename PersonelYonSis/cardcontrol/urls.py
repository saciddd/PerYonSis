from django.urls import path
from . import views

app_name = 'cardcontrol'

urlpatterns = [
    path('cihazlar/', views.cihaz_list, name='cihaz_list'),
    path('kapi-yonetimi/', views.kapi_yonetimi, name='kapi_yonetimi'),
    path('cihaz-kullanici-ekle/<int:cihaz_id>/', views.cihaz_kullanici_ekle, name='cihaz_kullanici_ekle'),
    path('cihaz-kullanici-sil/<int:cihaz_id>/', views.cihaz_kullanici_sil, name='cihaz_kullanici_sil'),
    path('cihaz-sync/<int:cihaz_id>/', views.cihaz_sync, name='cihaz_sync'),
]
