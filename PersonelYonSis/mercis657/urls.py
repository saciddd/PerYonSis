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
]