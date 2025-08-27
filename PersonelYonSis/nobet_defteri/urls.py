# nobet_defteri/urls.py
from django.urls import path
from . import views

app_name = 'nobet_defteri'

urlpatterns = [
    path('', views.nobet_defteri_list, name='liste'),
    path('olustur/', views.nobet_defteri_olustur, name='olustur'),
    path('<int:defter_id>/', views.nobet_defteri_detay, name='detay'),
    path('<int:defter_id>/onayla/', views.nobet_defteri_onayla, name='onayla'),
    path('<int:defter_id>/olaylar/', views.nobet_defteri_olaylar_modal, name='olaylar_modal'),  # yeni eklenen
    path('pdf/<int:defter_id>/', views.nobet_defteri_pdf, name='pdf'),
    path('pdf_modal/<int:defter_id>/', views.nobet_defteri_pdf_modal, name='pdf_modal'),

    # App-level URLs
    path('kontrol-soru/', views.kontrol_soru_list, name='kontrol_soru_list'),
    path('kontrol-soru-ekle/', views.kontrol_soru_ekle, name='kontrol_soru_ekle'),
    path('kontrol-soru-guncelle/<int:pk>/', views.kontrol_soru_guncelle, name='kontrol_soru_guncelle'),
    path('kontrol-soru-sil/<int:pk>/', views.kontrol_soru_sil, name='kontrol_soru_sil'),
]
