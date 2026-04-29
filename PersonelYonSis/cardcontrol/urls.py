from django.urls import path
from . import views
from . import adms_views

app_name = 'cardcontrol'

urlpatterns = [
    path('cihazlar/', views.cihaz_list, name='cihaz_list'),
    path('cihaz-guncelle/<int:cihaz_id>/', views.cihaz_guncelle, name='cihaz_guncelle'),
    path('kapi-yonetimi/', views.kapi_yonetimi, name='kapi_yonetimi'),
    path('cihaz-kullanici-ekle/<int:cihaz_id>/', views.cihaz_kullanici_ekle, name='cihaz_kullanici_ekle'),
    path('cihaz-kullanici-sil/<int:cihaz_id>/', views.cihaz_kullanici_sil, name='cihaz_kullanici_sil'),
    path('cihaz-sync/<int:cihaz_id>/', views.cihaz_sync, name='cihaz_sync'),
    path('cihaz-loglari/', views.cihaz_loglari, name='cihaz_loglari'),
    path('cihaz-kullanici-excele-aktar/<int:cihaz_id>/', views.cihaz_kullanici_excele_aktar, name='cihaz_kullanici_excele_aktar'),
    path('api-kullanici-ekle/<int:cihaz_id>/', views.api_kullanici_ekle, name='api_kullanici_ekle'),

    # ADMS Monitoring Sayfaları
    path('adms-ham-loglar/', views.adms_ham_loglar, name='adms_ham_loglar'),
    path('adms-komut-kuyrugu/', views.adms_komut_kuyrugu, name='adms_komut_kuyrugu'),
    path('adms-komut-gonder/', views.adms_komut_gonder, name='adms_komut_gonder'),

    # ADMS/Push Protokol Endpointleri
    # Cihazda sunucu adresi: http://SUNUCU_IP:PORT/cardcontrol
    path('iclock/cdata', adms_views.iclock_cdata, name='iclock_cdata'),
    path('iclock/getrequest', adms_views.iclock_getrequest, name='iclock_getrequest'),
    path('iclock/devicecmd', adms_views.iclock_devicecmd, name='iclock_devicecmd'),
]

