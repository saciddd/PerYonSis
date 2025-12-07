from django.urls import path
from . import views, resmi_yazi_views
from ik_core.api import views as api_views

app_name = 'ik_core'

urlpatterns = [
    path('personeller/', views.personel_list, name='personel_list'),
    path('personel/export/', views.personel_export_xlsx, name='personel_export_xlsx'),
    path('gelen-giden-personel/', views.gelen_giden_personel_list, name='gelen_giden_personel_list'),
    path('personel/ekle/', views.personel_ekle, name='personel_ekle'),
    path('personel/<int:pk>/', views.personel_detay, name='personel_detay'),
    path('personel/<int:pk>/duzenle/', views.personel_duzenle, name='personel_duzenle'),
    path('personel/<int:pk>/ilisik-kesme/', views.ilisik_kesme_formu, name='ilisik_kesme_formu'),
    path('personel/<int:pk>/ayrilis-kaydet/', views.ayrilis_kaydet, name='ayrilis_kaydet'),
    path('personel/<int:pk>/aktiflestir/', views.personeli_aktiflestir, name='personeli_aktiflestir'),
    path('personel/<int:personel_id>/gecici-gorev-ekle/', views.gecici_gorev_ekle, name='gecici_gorev_ekle'),
    path('personel/<int:personel_id>/gecici-gorev-sil/<int:gorev_id>/', views.gecici_gorev_sil, name='gecici_gorev_sil'),
    path('kurum-tanimlari/', views.kurum_tanimlari, name='kurum_tanimlari'),
    path('unvan-brans-tanimlari/', views.unvan_branstanimlari, name='unvan_branstanimlari'),
    path('tanimlamalar/', views.tanimlamalar, name='tanimlamalar'),
    path('personel_kontrol/', views.personel_kontrol, name='personel_kontrol'),
    path('get_brans_by_unvan/', views.get_brans_by_unvan, name='get_brans_by_unvan'),
    path('unvan_eslestirme_kaydet/', views.unvan_eslestirme_kaydet, name='unvan_eslestirme_kaydet'),
    path('personel/<int:pk>/mazeret-sil/', views.mazeret_sil, name='mazeret_sil'),
    # Geçici Görevler
    path('gecici-gorevler/', views.gecici_gorevler, name='gecici_gorevler'),
    path('gecici-gorevler/bulk-kaydet/', views.gecici_gorev_bulk_kaydet, name='gecici_gorev_bulk_kaydet'),
    # Tebliğ işlemleri
    path('imza-tanimlari/', views.imza_tanimlari, name='imza_tanimlari'),
    path('teblig-tanimlari/', views.teblig_tanimlari, name='teblig_tanimlari'),
    path('teblig-imzasi/ekle/', views.teblig_imzasi_ekle, name='teblig_imzasi_ekle'),
    path('teblig-imzasi/sil/<int:pk>/', views.teblig_imzasi_sil, name='teblig_imzasi_sil'),
    path('teblig-metni/ekle/', views.teblig_metni_ekle, name='teblig_metni_ekle'),
    path('teblig-metni/sil/<int:pk>/', views.teblig_metni_sil, name='teblig_metni_sil'),
    path('teblig-islemleri/<int:personel_id>/', views.teblig_islemleri, name='teblig_islemleri'),
    path('teblig-metni/guncelle/<int:pk>/', views.teblig_metni_guncelle, name='teblig_metni_guncelle'),
    path('teblig-metni/get/<int:pk>/', views.teblig_metni_get, name='teblig_metni_get'),
    # Resmi Yazı
    path('resmi-yazi/<int:personel_id>/', resmi_yazi_views.resmi_yazi_olustur, name='resmi_yazi'),
    path('resmi-yazi-tanimlari/', resmi_yazi_views.resmi_yazi_tanimlari, name='resmi_yazi_tanimlari'),
    path('resmi-yazi-ekle/', resmi_yazi_views.resmi_yazi_ekle, name='resmi_yazi_ekle'),
    path('resmi-yazi-guncelle/<int:yazi_id>/', resmi_yazi_views.resmi_yazi_guncelle, name='resmi_yazi_guncelle'),
    path('resmi-yazi-sil/<int:yazi_id>/', resmi_yazi_views.resmi_yazi_sil, name='resmi_yazi_sil'),
    path('resmi-yazi-get/<int:pk>/', resmi_yazi_views.resmi_yazi_get, name='resmi_yazi_get'),
    # Birim yönetimi
    path('birim-yonetimi/', views.birim_yonetimi, name='birim_yonetimi'),
    path('bina-ekle/', views.bina_ekle, name='bina_ekle'),
    path('ust-birim-ekle/', views.ust_birim_ekle, name='ust_birim_ekle'),
    path('birim-ekle/', views.birim_ekle, name='birim_ekle'),
    path('get-birimler-by-bina/', views.get_birimler_by_bina, name='get_birimler_by_bina'),
    path('personel-birim-ekle/', views.personel_birim_ekle, name='personel_birim_ekle'),
    path('gorevlendirme-yazisi/<int:personel_birim_id>/', views.gorevlendirme_yazisi, name='gorevlendirme_yazisi'),
    # API endpoints
    path('api/personel_aktar/', api_views.filemaker_personel_aktar, name='filemaker_personel_aktar'),

]
