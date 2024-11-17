from django.urls import path
from . import views

app_name = 'hekim_cizelge'  # Namespace tanımlaması

urlpatterns = [
    path('cizelge', views.cizelge, name='cizelge'),
    path('personeller', views.personeller, name='personeller'),
    path('personel-ekle-form/', views.personel_ekle_form, name='personel_ekle_form'),
    path('personel-ekle/', views.personel_ekle, name='personel_ekle'),
    path('personel_update/', views.personel_update, name='personel_update'),
    path('hizmet_tanimlari/', views.hizmet_tanimlari, name='hizmet_tanimlari'),
    path('add_hizmet/', views.add_hizmet, name='add_hizmet'),
    path('birim_tanimlari/', views.birim_tanimlari, name='birim_tanimlari'),
    path('add_birim/', views.add_birim, name='add_birim'),


]