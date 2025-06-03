from django.urls import path
from . import views

app_name = 'mercis657'  # Namespace tanımlaması

urlpatterns = [
    path('cizelge', views.cizelge, name='cizelge'),
    path('cizelge_kaydet', views.cizelge_kaydet, name='cizelge_kaydet'),
    path('export_excel/', views.excel_export, name='export_excel'),
    path('personeller', views.personeller, name='personeller'),
    path('personel-ekle-form/', views.personel_ekle_form, name='personel_ekle_form'),
    path('personel-ekle/', views.personel_ekle, name='personel_ekle'),
    path('personel_update/', views.personel_update, name='personel_update'),
    path('mesai_tanimlari/', views.mesai_tanimlari, name='mesai_tanimlari'),
    path('add_mesai_tanim/', views.add_mesai_tanim, name='add_mesai_tanim'),
    path('mesai_tanim_update/', views.mesai_tanim_update, name='mesai_tanim_update'),
    path('delete-mesai-tanim/', views.delete_mesai_tanim, name='delete_mesai_tanim'),
    path('personel-listeleri/', views.personel_listeleri, name='personel_listeleri'),
    path('personel-listesi/olustur/', views.personel_listesi_olustur, name='personel_listesi_olustur'),
    path('personel-listesi/<int:liste_id>/', views.personel_listesi_detay, name='personel_listesi_detay'),
    path('personel-listesi/<int:liste_id>/ekle/', views.personel_ekle, name='personel_ekle'),
    path('personel-listesi/<int:liste_id>/cikar/<int:personel_id>/', views.personel_cikar, name='personel_cikar'),
    path('birim-yonetim/', views.birim_yonetim, name='birim_yonetim'),
    path('birim-ekle/', views.birim_ekle, name='birim_ekle'),
    path('birim/<int:birim_id>/yetki-ekle/', views.birim_yetki_ekle, name='birim_yetki_ekle'),

    # Kullanıcı işlemleri
    path('kullanici/ara/', views.kullanici_ara, name='kullanici_ara'),

    # Birim Yönetimi API Endpoints
    path('birim/<int:birim_id>/detay/', views.birim_detay, name='birim_detay'),
    path('birim/<int:birim_id>/guncelle/', views.birim_guncelle, name='birim_guncelle'),
    path('birim/<int:birim_id>/sil/', views.birim_sil, name='birim_sil'),

    path('kurum-ekle/', views.kurum_ekle, name='kurum_ekle'),
    path('kurum-sil/<int:pk>/', views.kurum_sil, name='kurum_sil'),
    path('kurum-guncelle/<int:pk>/', views.kurum_guncelle, name='kurum_guncelle'),

    path('ust-birim-ekle/', views.ust_birim_ekle, name='ust_birim_ekle'),
    path('ust-birim-sil/<int:pk>/', views.ust_birim_sil, name='ust_birim_sil'),
    path('ust-birim-guncelle/<int:pk>/', views.ust_birim_guncelle, name='ust_birim_guncelle'),

    path('mudur-yrd-ekle/', views.mudur_yrd_ekle, name='mudur_yrd_ekle'),
    path('mudur-yrd-sil/<int:pk>/', views.mudur_yrd_sil, name='mudur_yrd_sil'),
    path('mudur-yrd-guncelle/<int:pk>/', views.mudur_yrd_guncelle, name='mudur_yrd_guncelle'),

    path('onceki-donem-personel/<int:year>/<int:month>/<int:birim_id>/', views.onceki_donem_personel, name='onceki_donem_personel'),
    path('personel/kaydet/', views.personel_kaydet, name='personel_kaydet'),
    path('cizelge/yazdir/', views.cizelge_yazdir, name='cizelge_yazdir'),
]
