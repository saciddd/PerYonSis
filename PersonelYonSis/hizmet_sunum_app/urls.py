from django.urls import path
from . import views

app_name = 'hizmet_sunum_app'

urlpatterns = [
    # Ana bildirim sayfası
    path('bildirim/', views.bildirim, name='bildirim'),
    path('bildirimler/listele/<int:year>/<int:month>/<int:birim_id>/', views.bildirimler_listele, name='bildirimler_listele'),
    
    # Birim işlemleri
    path('birim/<int:birim_id>/', views.birim_detay, name='birim_detay'),
    path('birim/ekle/', views.birim_ekle, name='birim_ekle'),
    path('birim/<int:birim_id>/guncelle/', views.birim_guncelle, name='birim_guncelle'),
    
    # Personel işlemleri
    path('onceki-donem-personel/<str:donem>/<int:birim_id>/', 
         views.onceki_donem_personel, name='onceki_donem_personel'),
    path('personel/kaydet/', views.personel_kaydet, name='personel_kaydet'),
]
