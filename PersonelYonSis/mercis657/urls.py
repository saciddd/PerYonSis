from django.urls import path
from . import views
# from .views import main_views

app_name = 'mercis657'  # Namespace tanımlaması

urlpatterns = [
    path('cizelge', views.cizelge, name='cizelge'),
    path('cizelge_kaydet', views.cizelge_kaydet, name='cizelge_kaydet'),
    path('export_excel/', views.excel_export, name='export_excel'),
    path('add_mesai_tanim/', views.add_mesai_tanim, name='add_mesai_tanim'),
    path('mesai_tanim_update/', views.mesai_tanim_update, name='mesai_tanim_update'),
    path('mesai-tanim-form/<int:pk>/', views.mesai_tanim_form, name='mesai_tanim_form'),
    path('delete-mesai-tanim/', views.delete_mesai_tanim, name='delete_mesai_tanim'),
    path('personel-listeleri/', views.personel_listeleri, name='personel_listeleri'),
    path('personel-listesi/olustur/', views.personel_listesi_olustur, name='personel_listesi_olustur'),
    path('personel-listesi/<int:liste_id>/', views.personel_listesi_detay, name='personel_listesi_detay'),
    path('personel-listesi/<int:liste_id>/ekle/', views.personel_ekle, name='personel_ekle'),
    path('personel-listesi/<int:liste_id>/cikar/<int:personel_id>/', views.personel_cikar, name='personel_cikar'),
    path('birim-yonetim/', views.birim_yonetim, name='birim_yonetim'),
    path('birim-ekle/', views.birim_ekle, name='birim_ekle'),
    path('birim/<int:birim_id>/yetki-ekle/', views.birim_yetki_ekle, name='birim_yetki_ekle'),
    path('birim/<int:birim_id>/yetki-sil/', views.birim_yetki_sil, name='birim_yetki_sil'),
    path('birim/<int:birim_id>/yetkililer/', views.birim_yetkililer, name='birim_yetkililer'),

    # Kullanıcı işlemleri
    path('kullanici/ara/', views.kullanici_ara, name='kullanici_ara'),

    # Birim Yönetimi API Endpoints
    path('birim/<int:birim_id>/detay/', views.birim_detay, name='birim_detay'),
    path('birim/<int:birim_id>/guncelle/', views.birim_guncelle, name='birim_guncelle'),

    path('kurum-ekle/', views.kurum_ekle, name='kurum_ekle'),
    path('kurum-guncelle/<int:pk>/', views.kurum_guncelle, name='kurum_guncelle'),
    path('kurum-toggle-aktif/<int:pk>/', views.kurum_toggle_aktif, name='kurum_toggle_aktif'),
    path('kurum-sil/<int:pk>/', views.kurum_sil, name='kurum_sil'),

    path('ust-birim-ekle/', views.ust_birim_ekle, name='ust_birim_ekle'),
    path('ust-birim-guncelle/<int:pk>/', views.ust_birim_guncelle, name='ust_birim_guncelle'),
    path('ust-birim-toggle-aktif/<int:pk>/', views.ust_birim_toggle_aktif, name='ust_birim_toggle_aktif'),
    path('ust-birim-sil/<int:pk>/', views.ust_birim_sil, name='ust_birim_sil'),

    path('onceki-donem-personel/<str:donem>/<int:birim_id>/', views.onceki_donem_personel, name='onceki_donem_personel'),
    path('personel/kaydet/', views.personel_kaydet, name='personel_kaydet'),
    path('cizelge/yazdir/', views.cizelge_yazdir, name='cizelge_yazdir'),
    path('cizelge-onay/', views.cizelge_onay, name='cizelge_onay'),
    path('mesai-onayla/<int:mesai_id>/', views.mesai_onayla, name='mesai_onayla'),
    path('mesai-reddet/<int:mesai_id>/', views.mesai_reddet, name='mesai_reddet'),
    path('toplu-onay/<int:birim_id>/<int:year>/<int:month>/', views.toplu_onay, name='toplu_onay'),
    path('tanimlamalar/', views.tanimlamalar, name='tanimlamalar'),

    path('idareci-toggle-aktif/<int:pk>/', views.idareci_toggle_aktif, name='idareci_toggle_aktif'),
    path('idareci-ekle/', views.idareci_ekle, name='idareci_ekle'),
    path('idareci-guncelle/<int:pk>/', views.idareci_guncelle, name='idareci_guncelle'),

    # İzin işlemleri
    path('izin-ekle/', views.izin_ekle, name='izin_ekle'),
    path('izin-guncelle/<int:pk>/', views.izin_guncelle, name='izin_guncelle'),
    
    # Personel profil ve mazeret işlemleri
    path('personel-profil/<int:personel_id>/<int:liste_id>/<int:year>/<int:month>/', views.personel_profil, name='personel_profil'),
    path('mazeret-ekle/', views.mazeret_ekle, name='mazeret_ekle'),
    path('mazeret-guncelle/<int:mazeret_id>/', views.mazeret_guncelle, name='mazeret_guncelle'),
    path('mazeret-sil/<int:mazeret_id>/', views.mazeret_sil, name='mazeret_sil'),
    path('radyasyon-toggle/<int:personel_id>/<int:liste_id>/', views.radyasyon_toggle, name='radyasyon_toggle'),
    path('hazir-mesai-ata/<int:personel_id>/<int:liste_id>/<int:year>/<int:month>/', views.hazir_mesai_ata, name='hazir_mesai_ata'),
    
    # Toplu işlemler
    path('toplu-islem/<int:liste_id>/<int:year>/<int:month>/', views.toplu_islem, name='toplu_islem'),
    path('toplu-radyasyon-ata/<int:liste_id>/', views.toplu_radyasyon_ata, name='toplu_radyasyon_ata'),
    path('toplu-mesai-ata/<int:liste_id>/<int:year>/<int:month>/', views.toplu_mesai_ata, name='toplu_mesai_ata'),

    # İzin çek
    path('izinleri-mesailere-isle/<int:liste_id>/', views.izinleri_mesailere_isle, name='izinleri_mesailere_isle'),

    # Bildirim işlemleri
    path('bildirimler/', views.bildirimler, name='bildirimler'),
    path('bildirim-onayla/<int:bildirim_id>/', views.bildirim_onayla, name='bildirim_onayla'),
    path('bildirim-sil/<int:bildirim_id>/', views.bildirim_sil, name='bildirim_sil'),
    # path('bildirim-toplu-onay-kaldir/<int:birim_id>/', views.bildirim_toplu_onay_kaldir, name='bildirim_toplu_onay_kaldir'),
    path('bildirim-form/<int:birim_id>/', views.bildirim_form, name='bildirim_form'),
    # path('bildirim-kilit/<int:bildirim_id>/', views.bildirim_kilit, name='bildirim_kilit'),
    # path('bildirim-kilit-ac/<int:bildirim_id>/', views.bildirim_kilit_ac, name='bildirim_kilit_ac'),
    
    # path('bildirim-excel/', views.bildirim_excel, name='bildirim_excel'),
    path('tatil-ekle/', views.tatil_ekle, name='tatil_ekle'),
    path('tatil-duzenle/', views.tatil_duzenle, name='tatil_duzenle'),
    path('tatil-sil/<int:tatil_id>/', views.tatil_sil, name='tatil_sil'),

    # API Endpoints
    path('bildirim/listele/<int:year>/<int:month>/<int:birim_id>/', views.bildirim_listele, name='bildirim_listele'),
    path('bildirim/olustur/', views.bildirim_olustur, name='bildirim_olustur'),
    path('bildirim/toplu-olustur/<int:birim_id>/', views.bildirim_toplu_olustur, name='bildirim_toplu_olustur'),
    path('bildirim/tekil-onay/<int:bildirim_id>/', views.bildirim_tekil_onay, name='bildirim_tekil_onay'),
    path('bildirim/toplu-onay/<int:birim_id>/', views.bildirim_toplu_onay, name='bildirim_toplu_onay'),
    
    # Riskli Bildirim Yönetimi
    path('bildirimler/<int:birim_id>/riskli-data/', views.riskli_bildirim_data, name='riskli_bildirim_data'),
    path('bildirimler/<int:birim_id>/update-risky/', views.update_risky_bildirim, name='update_risky_bildirim'),
    path('bildirimler/<int:birim_id>/convert-all-risky/', views.convert_all_to_risky, name='convert_all_to_risky'),

    # Raporlama
    path('raporlama/', views.raporlama, name='raporlama'),
    path('raporlama/excel/', views.export_raporlama_excel, name='export_raporlama_excel'),
    # Raporlama API endpoints
    path('raporlama/update-birim-kodlari-toplu/', views.update_birim_kodlari_toplu, name='update_birim_kodlari_toplu'),
    path('raporlama/kilit-tekil/', views.kilit_tekil, name='kilit_tekil'),
    path('raporlama/kilit-toplu/', views.kilit_toplu, name='kilit_toplu'),
    path('personel-cikar/<int:liste_id>/<int:personel_id>/', views.personel_cikar, name='personel_cikar'),
    path('liste_aciklama_kaydet/', views.liste_aciklama_kaydet, name='liste_aciklama_kaydet'),
    
    # Yönetici Görünümleri
    path('yonetici/birim-listeleri/', views.birim_listeleri, name='birim_listeleri'),
    path('personel-listesi/<int:liste_id>/sira-kaydet/', views.personel_listesi_sira_kaydet, name='personel_listesi_sira_kaydet'),
]
