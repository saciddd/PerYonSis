from django.urls import path
from . import views

app_name = 'mutemet_app'

urlpatterns = [
    path('', views.index, name='index'),
    path('personel-listesi/', views.personel_listesi, name='personel_listesi'),
    path('hareket-listesi/', views.hareket_listesi, name='hareket_listesi'),
    path('hareket-ekle/', views.hareket_ekle, name='hareket_ekle'),
    path('sendika-takibi/', views.sendika_takibi, name='sendika_takibi'),
    path('sendika-hareket-ekle/', views.sendika_hareket_ekle, name='sendika_hareket_ekle'),
    path('personel-ara/', views.personel_ara, name='personel_ara'),
    path('icra-takibi/', views.icra_takibi, name='icra_takibi'),
    path('odeme-takibi/', views.odeme_takibi, name='odeme_takibi'),

    # Sendika CRUD URL'leri
    path('sendika/modal/', views.get_sendika_modal_content, name='get_sendika_modal_content'),
    path('sendika/ekle/', views.sendika_ekle, name='sendika_ekle'),
    path('sendika/guncelle/<int:pk>/', views.sendika_guncelle, name='sendika_guncelle'),
    path('sendika/sil/<int:pk>/', views.sendika_sil, name='sendika_sil'),
    path('sendika/liste/json/', views.get_sendikalar_json, name='get_sendikalar_json'),
    path('sendika-hareket-sil/<int:pk>/', views.sendika_hareket_sil, name='sendika_hareket_sil'),

    # Icra Takibi and Icra Hareketleri URL'leri
    path('icra-takibi/', views.icra_takibi_list, name='icra_takibi_list'),
    path('icra-takibi/ekle/', views.icra_takibi_ekle, name='icra_takibi_ekle'),
    path('icra-hareketleri/<int:icra_id>/', views.icra_hareketleri_list, name='icra_hareketleri_list'),
    path('icra-hareketleri/ekle/<int:icra_id>/', views.icra_hareket_ekle, name='icra_hareket_ekle'),
]