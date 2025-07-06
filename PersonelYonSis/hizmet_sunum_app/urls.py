from django.urls import path
from . import views, bildirim_views

app_name = 'hizmet_sunum_app'

urlpatterns = [
    # Ana bildirim sayfası
    path('bildirim/', views.bildirim, name='bildirim'),
    path('bildirimler/listele/<int:year>/<int:month>/<int:birim_id>/', views.bildirimler_listele, name='bildirimler_listele'),
    path('bildirimler/kaydet/', bildirim_views.bildirimler_kaydet, name='bildirimler_kaydet'),
    path('bildirimler/kesinlestir/', views.bildirimler_kesinlestir, name='bildirimler_kesinlestir'),
    path('bildirimler/kesinlestirmeyi-kaldir/', views.bildirimler_kesinlestirmeyi_kaldir, name='bildirimler_kesinlestirmeyi_kaldir'),
    path('bildirim/kesinlestir/', bildirim_views.bildirim_kesinlestir, name='bildirim_kesinlestir'),
    path('bildirim/kesinlestirmeyi-kaldir/', bildirim_views.bildirim_kesinlestirmeyi_kaldir, name='bildirim_kesinlestirmeyi_kaldir'),
    path('bildirim/<int:bildirim_id>/sil/', views.bildirim_sil, name='bildirim_sil'),
    path('bildirimler/yazdir/', views.bildirim_yazdir, name='bildirim_yazdir'),  # Query string ile (donem, birim_id)
    path('bildirimler/yazdir/<int:year>/<int:month>/<int:birim_id>/', views.bildirim_yazdir, name='bildirim_yazdir_parametreli'),
    
    # Birim işlemleri
    path('birim/<int:birim_id>/detay/', views.birim_detay, name='birim_detay'),
    path('birim/ekle/', views.birim_ekle, name='birim_ekle'),
    path('birim/<int:birim_id>/guncelle/', views.birim_guncelle, name='birim_guncelle'),
    path('birim/<int:birim_id>/sil/', views.birim_sil, name='birim_sil'),
    path('birim/<int:birim_id>/yetkililer/', views.birim_yetkililer, name='birim_yetkililer'),
    path('birim/<int:birim_id>/yetki-ekle/', views.birim_yetki_ekle, name='birim_yetki_ekle'),
    path('birim/<int:birim_id>/yetki-sil/', views.birim_yetki_sil, name='birim_yetki_sil'),
    
    # Personel işlemleri
    path('onceki-donem-personel/<str:donem>/<int:birim_id>/', 
         views.onceki_donem_personel, name='onceki_donem_personel'),
    path('personel/kaydet/', views.personel_kaydet, name='personel_kaydet'),

    path('raporlama/', views.raporlama, name='raporlama'),
    path('raporlama/excel/', views.export_raporlama_excel, name='export_raporlama_excel'),

    # Kullanıcı işlemleri
    path('kullanici/ara/', views.kullanici_ara, name='kullanici_ara'),

    path('birim-yonetim/', views.birim_yonetim, name='birim_yonetim'),
]
