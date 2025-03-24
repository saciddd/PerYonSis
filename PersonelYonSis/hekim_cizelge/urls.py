from django.urls import path
from . import views

app_name = 'hekim_cizelge'  # Namespace tanımlaması

urlpatterns = [
    path('cizelge', views.cizelge, name='cizelge'),
    path('cizelge_kaydet/', views.cizelge_kaydet, name='cizelge_kaydet'),
    path('personeller', views.personeller, name='personeller'),
    path('personel_ekle_form/', views.personel_ekle_form, name='personel_ekle_form'),
    path('personel-ekle/', views.personel_ekle, name='personel_ekle'),
    path('personel_update/', views.personel_update, name='personel_update'),
    path('hizmet_tanimlari/', views.hizmet_tanimlari, name='hizmet_tanimlari'),
    path('add_hizmet/', views.add_hizmet, name='add_hizmet'),
    path('birim_tanimlari/', views.birim_tanimlari, name='birim_tanimlari'),
    path('add_birim/', views.add_birim, name='add_birim'),
    path('birim_yetkileri/<int:user_id>/', views.birim_yetkileri, name='birim_yetkileri'),
    path('birim_duzenle_form/<int:birim_id>/', views.birim_duzenle_form, name='birim_duzenle_form'),
    path('birim_duzenle/<int:birim_id>/', views.birim_duzenle, name='birim_duzenle'),
    path('mesai/onay/<int:mesai_id>/', views.mesai_onay, name='mesai_onay'),
    path('mesai/onay-durumu/<int:mesai_id>/', views.mesai_onay_durumu, name='mesai_onay_durumu'),
    path('onay-bekleyen-mesailer/', views.onay_bekleyen_mesailer, name='onay_bekleyen_mesailer'),
    path('toplu-onay/<int:birim_id>/', views.toplu_onay, name='toplu_onay'),
    path('auto_fill_default/', views.auto_fill_default, name='auto_fill_default'),
]

urlpatterns += [
    path('bildirimler/', views.bildirimler, name='bildirimler'),
    path('bildirim/olustur/<str:tip>/', views.bildirim_olustur, name='bildirim_olustur'),
    path('bildirim/listele/<int:yil>/<int:ay>/<int:birim_id>/', views.bildirim_listele, name='bildirim_listele'),
    path('bildirim/guncelle/<int:bildirim_id>/', views.bildirim_guncelle, name='bildirim_guncelle'),
    path('bildirim/sil/<int:bildirim_id>/', views.bildirim_sil, name='bildirim_sil'),
    path('bildirim/toplu-olustur/<int:birim_id>/', views.bildirim_toplu_olustur, name='bildirim_toplu_olustur'),
    path('bildirim/toplu-onay/<int:birim_id>/', views.bildirim_toplu_onay, name='bildirim_toplu_onay'),
    path('bildirim/form/<int:bildirim_id>/', views.bildirim_form, name='bildirim_form'),
    path('resmi-tatiller/', views.resmi_tatiller, name='resmi_tatiller'),
    path('tatil-ekle/', views.tatil_ekle, name='tatil_ekle'),
    path('tatil-sil/<int:tatil_id>/', views.tatil_sil, name='tatil_sil'),
]