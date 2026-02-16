from django.urls import path
from . import views, resmi_yazi_views, durum_belgesi_views, analiz_views, kampus_views, analiz_utils_views
from ik_core.api import views as api_views

app_name = 'ik_core'

urlpatterns = [
    path('personeller/', views.personel_list, name='personel_list'),
    path('personel/export/', views.personel_export_xlsx, name='personel_export_xlsx'),
    path('gelen-giden-personel/', views.gelen_giden_personel_list, name='gelen_giden_personel_list'),
    path('personel/ekle/', views.personel_ekle, name='personel_ekle'),
    path('personel/<int:pk>/', views.personel_detay, name='personel_detay'),
    path('personel/<int:personel_id>/isim-degistir/', views.personel_isim_degistir, name='personel_isim_degistir'),
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
    # Durum Belgesi
    path('durum-belgesi/<int:personel_id>/', durum_belgesi_views.durum_belgesi_olustur, name='durum_belgesi'),
    path('durum-belgesi-tanimlari/', durum_belgesi_views.durum_belgesi_tanimlari, name='durum_belgesi_tanimlari'),
    path('durum-belgesi-ekle/', durum_belgesi_views.durum_belgesi_ekle, name='durum_belgesi_ekle'),
    path('durum-belgesi-guncelle/<int:belge_id>/', durum_belgesi_views.durum_belgesi_guncelle, name='durum_belgesi_guncelle'),
    path('durum-belgesi-sil/<int:belge_id>/', durum_belgesi_views.durum_belgesi_sil, name='durum_belgesi_sil'),
    path('durum-belgesi-get/<int:pk>/', durum_belgesi_views.durum_belgesi_get, name='durum_belgesi_get'),
    # Birim yönetimi
    path('birim-yonetimi/', views.birim_yonetimi, name='birim_yonetimi'),
    path('birim-yonetimi/', views.birim_yonetimi, name='birim_yonetimi'),
    path('bina-ekle/', views.bina_ekle_duzenle, name='bina_ekle'), # Name yine bina_ekle kalsın, template değişmesin
    path('get-bina-detay/', views.get_bina_detay, name='get_bina_detay'),
    path('ust-birim-ekle/', views.ust_birim_ekle, name='ust_birim_ekle'),
    path('birim-ekle/', views.birim_ekle, name='birim_ekle'),
    path('get-birimler-by-bina/', views.get_birimler_by_bina, name='get_birimler_by_bina'),
    path('personel-birim-ekle/', views.personel_birim_ekle, name='personel_birim_ekle'),
    path('gorevlendirme-yazisi/<int:personel_birim_id>/', views.gorevlendirme_yazisi, name='gorevlendirme_yazisi'),
    # Analiz Sayfaları
    path('analiz/', analiz_views.dashboard_view, name='analiz_dashboard'),
    path('analiz/unvan/', analiz_views.unvan_analiz_view, name='unvan_analiz'),
    path('analiz/birim/', analiz_views.birim_analiz_view, name='birim_analiz'),
    path('analiz/modal/personel-list/', analiz_views.personel_list_modal_view, name='analiz_personel_list_modal'),
    path('analiz/personel-birim/update-aciklama/', analiz_utils_views.update_personel_birim_aciklama, name='update_personel_birim_aciklama'),
    path('analiz/kampus/', analiz_views.kampus_analiz_view, name='kampus_analiz'),
    # Kampüs Yönetimi
    path('yonetim/kampus/', kampus_views.kampus_tanimlari, name='kampus_tanimlari'),
    path('yonetim/kampus/duzenle/<int:pk>/', kampus_views.kampus_duzenle, name='kampus_duzenle'),
    path('yonetim/kampus/sil/<int:pk>/', kampus_views.kampus_sil, name='kampus_sil'),
    path('yonetim/kampus-koordinat/', kampus_views.kampus_koordinat_editor, name='kampus_koordinat_editor'),
    path('yonetim/bina-koordinat-kaydet/', kampus_views.bina_koordinat_kaydet, name='bina_koordinat_kaydet'),
    # API endpoints
    path('api/personel_aktar/', api_views.filemaker_personel_aktar, name='filemaker_personel_aktar'),

]
