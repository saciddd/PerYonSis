from django.urls import path
from . import views
from .views import fazla_mesai_views, liste_views
from .views import personel_yonetim_views, cizelge_kontrol_views
# from .views import main_views

app_name = 'mercis657'  # Namespace tanımlaması

urlpatterns = [
    # Personel Yönetimi
    path('personel-yonetim/', personel_yonetim_views.personel_yonetim, name='personel_yonetim'),
    path('personel-sorgula/', personel_yonetim_views.personel_sorgula, name='personel_sorgula'),
    path('personel/<int:personel_id>/listeler/', personel_yonetim_views.personel_listeleri, name='personel_listeleri_kisi'),
    # Yeni eklenen URL pattern'leri
    path('birim/<int:birim_id>/listeler/', liste_views.birim_listeleri, name='birim_listeleri'),
    path('liste/<int:liste_id>/personeller/', liste_views.liste_personeller, name='liste_personeller'),
    path('liste/<int:liste_id>/personel/<int:personel_id>/sil/', liste_views.personel_cikar, name='personel_cikar'),
    path('liste/<int:liste_id>/sil/', liste_views.liste_sil, name='liste_sil'),
    
    # Mevcut URL pattern'leri
    path('cizelge', views.cizelge, name='cizelge'),
    path('cizelge_kaydet', views.cizelge_kaydet, name='cizelge_kaydet'),
    path('favori-mesai-kaydet/', views.favori_mesai_kaydet, name='favori_mesai_kaydet'),
    path('fazla-mesai-hesapla', fazla_mesai_views.fazla_mesai_hesapla, name='fazla_mesai_hesapla'),
    path('fazla-mesai-hesapla-toplu/', fazla_mesai_views.fazla_mesai_hesapla_toplu, name='fazla_mesai_hesapla_toplu'),
    path('vardiya-tanimlari/', fazla_mesai_views.vardiya_tanimlari, name='vardiya_tanimlari'),
    path('cizelge-kontrol/', cizelge_kontrol_views.cizelge_kontrol, name='cizelge_kontrol'),
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
    path('birim/<int:birim_id>/sil/', views.birim_sil, name='birim_sil'),
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
    path("yarim-zamanli-kaydet/<int:personel_id>/", views.yarim_zamanli_calisma_kaydet, name="yarim_zamanli_calisma_kaydet"),
    path('cizelge/yazdir/', views.cizelge_yazdir, name='cizelge_yazdir'),
    path('cizelge-onay/', views.cizelge_onay, name='cizelge_onay'),
    path('imza_cizelgeleri_yazdir/', views.imza_cizelgeleri_yazdir, name='imza_cizelgeleri_yazdir'),
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
    path('sabit-mesai-guncelle/', views.sabit_mesai_guncelle, name='sabit_mesai_guncelle'),
    
    # Stop işlemleri
    path('stop-ekle/<int:mesai_id>/', views.stop_ekle, name='stop_ekle'),
    path('stop-sil/<int:stop_id>/', views.stop_sil, name='stop_sil'),

    # Toplu işlemler
    path('toplu-islem/<int:liste_id>/<int:year>/<int:month>/', views.toplu_islem, name='toplu_islem'),
    path('toplu-radyasyon-ata/<int:liste_id>/', views.toplu_radyasyon_ata, name='toplu_radyasyon_ata'),
    path('toplu-sabit-mesai-ata/<int:liste_id>/', views.toplu_sabit_mesai_ata, name='toplu_sabit_mesai_ata'),
    path('toplu-mesai-ata/<int:liste_id>/<int:year>/<int:month>/', views.toplu_mesai_ata, name='toplu_mesai_ata'),
    path('toplu-mesai-degistir/<int:liste_id>/<int:year>/<int:month>/', views.toplu_mesai_degistir, name='toplu_mesai_degistir'),

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
    path('personel-listesi/<int:liste_id>/onceki-ay-siralamasi/', views.onceki_ay_siralamasi, name='onceki_ay_siralamasi'),

    # İlk Liste Bildirimi
    path('ilk-liste-olustur/<int:liste_id>/', views.ilk_liste_olustur, name='ilk_liste_olustur'),
    path('ilk-liste-onayla/<int:ilk_liste_id>/', views.ilk_liste_onayla, name='ilk_liste_onayla'),
    path('ilk-liste-onay-kaldir/<int:ilk_liste_id>/', views.ilk_liste_onay_kaldir, name='ilk_liste_onay_kaldir'),
    path('ilk-liste-detay/<int:liste_id>/', views.ilk_liste_detay, name='ilk_liste_detay'),

    # Vardiya Dağılımı
    path('vardiya-dagilim/', views.vardiya_dagilim, name='vardiya_dagilim'),
    path('vardiya-dagilim/search/', views.vardiya_dagilim_search, name='vardiya_dagilim_search'),
    path('vardiya-dagilim/kaydet/', views.vardiya_dagilim_kaydet, name='vardiya_dagilim_kaydet'),
    path('vardiya-dagilim/pdf/', views.vardiya_dagilim_pdf, name='vardiya_dagilim_pdf'),
    
    # Çalışma Statüsü Kontrolü
    path('calisma-statusu-list/<int:liste_id>/', views.get_calisma_statusu_list, name='get_calisma_statusu_list'),
    path('calisma-statusu-guncelle/<int:liste_id>/', views.update_calisma_statusu_list, name='update_calisma_statusu_list'),
]
