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


]