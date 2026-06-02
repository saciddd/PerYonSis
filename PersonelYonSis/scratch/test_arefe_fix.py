import os
import django
import sys
from decimal import Decimal
from datetime import date

# Django setup
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PersonelYonSis.settings')
django.setup()

from mercis657.models import ResmiTatil, Personel, PersonelListesi, PersonelListesiKayit, SabitMesai, Mesai, Mesai_Tanimlari
from mercis657.utils import hesapla_fazla_mesai, hesapla_fazla_mesai_sade

def run_test():
    print("=== START OF TEST ===")
    
    # 1. 26.05.2026 tarihindeki tatili kontrol et/oluştur
    test_date = date(2026, 5, 26)
    
    # Mevcut kaydı bul veya oluştur
    rt, created = ResmiTatil.objects.get_or_create(
        TatilTarihi=test_date,
        defaults={
            'Aciklama': 'Test Arefe Tam Gün Tatili',
            'TatilTipi': 'TAM',
            'BayramMi': False,
            'ArefeMi': True
        }
    )
    if not created:
        # Değerleri tam olarak test senaryosuna göre güncelle
        rt.TatilTipi = 'TAM'
        rt.BayramMi = False
        rt.ArefeMi = True
        rt.save()
        print(f"Mevcut ResmiTatil kaydı güncellendi: {rt}")
    else:
        print(f"Yeni ResmiTatil kaydı oluşturuldu: {rt}")

    # List all holidays in May 2026
    print("\nMayıs 2026'daki Tüm Resmi Tatiller:")
    for t in ResmiTatil.objects.filter(TatilTarihi__year=2026, TatilTarihi__month=5):
        print(f" - Tarih: {t.TatilTarihi}, Tip: {t.TatilTipi}, Bayram: {t.BayramMi}, Arefe: {t.ArefeMi}, Açıklama: {t.Aciklama}")


    # 2. Test personeli ve listesi bul/oluştur
    personel, p_created = Personel.objects.get_or_create(
        PersonelTCKN=99999999999,
        defaults={
            'PersonelName': 'Test',
            'PersonelSurname': 'Kullanici',
            'PersonelTitle': 'Test Unvani'
        }
    )
    
    from mercis657.models import Birim
    birim = Birim.objects.first()
    if not birim:
        birim = Birim.objects.create(BirimAdi="Test Birimi")

    liste, l_created = PersonelListesi.objects.get_or_create(
        birim=birim,
        yil=2026,
        ay=5,
        defaults={'aciklama': 'Test Listesi'}
    )

    plk, plk_created = PersonelListesiKayit.objects.get_or_create(
        liste=liste,
        personel=personel,
        defaults={
            'radyasyon_calisani': False,
            'is_gunduz_personeli': True
        }
    )

    # 3. Hesaplamayı çalıştır
    print("\n--- Hesaplama Sonucları ---")
    
    # Mesai tanımlarını bul/oluştur
    tanim_8_16 = Mesai_Tanimlari.objects.filter(Saat="08:00 16:00").first()
    if not tanim_8_16:
        tanim_8_16 = Mesai_Tanimlari.objects.create(
            Saat="08:00 16:00",
            GunduzMesaisi=True,
            CKYS_BTF_Karsiligi='Normal Mesai'
        )
    tanim_8_17 = Mesai_Tanimlari.objects.filter(Saat="08:00 17:00").first()
    if not tanim_8_17:
        tanim_8_17 = Mesai_Tanimlari.objects.create(
            Saat="08:00 17:00",
            GunduzMesaisi=True,
            CKYS_BTF_Karsiligi='Nobet'
        )

    # Mevcut mesaileri temizle (Mayıs 2026'daki tüm kayıtları sıfırlayalım ki temiz bir test olsun)
    Mesai.objects.filter(Personel=personel, MesaiDate__year=2026, MesaiDate__month=5).delete()
    
    # 25.05.2026 (08:00-16:00): İdari izin (08:00-16:00) olduğu için 0 saat fiili sayılmalı
    Mesai.objects.create(
        Personel=personel,
        MesaiDate=date(2026, 5, 25),
        MesaiTanim=tanim_8_16,
        OnayDurumu=True
    )
    
    # 26.05.2026 (08:00-17:00): İdari izin (08:00-13:00) olduğu için 5 saat düşülüp sadece 4 saat sayılmalı
    # Bu mesai aynı zamanda İcap da içersin (önceki testimiz için)
    Mesai.objects.create(
        Personel=personel,
        MesaiDate=date(2026, 5, 26),
        MesaiTanim=tanim_8_17,
        Icap=True,
        OnayDurumu=True
    )
    
    res = hesapla_fazla_mesai(plk, 2026, 5)
    res_sade = hesapla_fazla_mesai_sade(plk, 2026, 5)
    
    print(f"hesapla_fazla_mesai -> olması_gereken_sure: {res['olması_gereken_sure']}")
    print(f"hesapla_fazla_mesai_sade -> olması_gereken_sure: {res_sade}")
    print(f"Fiili Çalışma Süresi (Detaylı): {res['fiili_calisma_suresi']}")
    
    # Sadeleştirilmiş fiili çalışma süresini de sade metodun dönüşü olan fazla_mesai + olmasi_gereken_sure ile bulabiliriz
    fiili_sade = res_sade + res['olması_gereken_sure']
    print(f"Fiili Çalışma Süresi (Sadeleştirilmiş): {fiili_sade}")
    
    print(f"Çalışma Günleri: {res['calisma_gunleri']}, Arefe Günleri: {res['arefe_gunleri']}")
    print(f"Normal İcap Süresi: {res['normal_icap']}, Bayram İcap Süresi: {res['bayram_icap']}, Toplam İcap: {res['toplam_icap']}")
    print(f"İcap Detayları: {res['icap_detay']}")
    print(f"Fazla Mesai Detayları: Bayram Gündüz: {res['bayram_fazla_mesai']}, Normal Gündüz: {res['normal_fazla_mesai']}, Toplam FM: {res['fazla_mesai']}")
    
    print(f"\nBeklenen olması_gereken_sure (Pozitif): 125.0 saat (112.0 base + 8.0 + 5.0).")
    print(f"Beklenen fiili çalışma süresi: 4.0 saat (25 Mayıs'ta 8 saatin tamamı, 26 Mayıs'ta 5 saat idari izin düştü).")
    
    # Assertions (Pozitif)
    assert res['olması_gereken_sure'] == Decimal('125.0'), f"Error: {res['olması_gereken_sure']} != 125.0"
    
    # Sade metot fazla mesai = fiili_calisma - olması_gereken_sure = 4.0 - 125.0 = -121.0 olmalı
    assert res_sade == Decimal('-121.0'), f"Error: res_sade {res_sade} != -121.0"
    
    assert res['fiili_calisma_suresi'] == Decimal('4.0'), f"Error: fiili_calisma {res['fiili_calisma_suresi']} != 4.0"
    assert fiili_sade == Decimal('4.0'), f"Error: fiili_sade {fiili_sade} != 4.0"
    
    assert res['normal_icap'] == Decimal('5.0'), f"Error: {res['normal_icap']} != 5.0"
    assert res['bayram_icap'] == Decimal('19.0'), f"Error: {res['bayram_icap']} != 19.0"
    assert res['toplam_icap'] == Decimal('24.0'), f"Error: {res['toplam_icap']} != 24.0"
    print("SUCCESS: Positive assertions passed!")

    # 4. Negatif test için json'ı geçici olarak güncelle
    import json
    json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'mercis657', 'idari_izinler.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        original_data = json.load(f)
    
    try:
        # Negatif süreleri yaz
        negative_data = []
        for item in original_data:
            new_item = item.copy()
            new_item['eklenecek_saat'] = -item['eklenecek_saat'] # 8.0 -> -8.0, 5.0 -> -5.0
            negative_data.append(new_item)
            
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(negative_data, f, indent=2)
            
        print("\n--- Hesaplama Sonucları (Negatif eklenecek_saat) ---")
        res_neg = hesapla_fazla_mesai(plk, 2026, 5)
        res_sade_neg = hesapla_fazla_mesai_sade(plk, 2026, 5)
        
        print(f"hesapla_fazla_mesai -> olması_gereken_sure: {res_neg['olması_gereken_sure']}")
        print(f"hesapla_fazla_mesai_sade -> olması_gereken_sure (normalde hesaplanan): {res_sade_neg}")
        
        # Negatif case assertions:
        # olması_gereken_sure = 112.0 (base) - 8.0 - 5.0 = 99.0
        # res_sade_neg = 4.0 - 99.0 = -95.0
        assert res_neg['olması_gereken_sure'] == Decimal('99.0'), f"Error: {res_neg['olması_gereken_sure']} != 99.0"
        assert res_sade_neg == Decimal('-95.0'), f"Error: {res_sade_neg} != -95.0"
        print("SUCCESS: Negative assertions passed!")
        
    finally:
        # Orijinal json'ı geri yükle
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(original_data, f, indent=2)
            
    print("SUCCESS: All administrative leave assertions passed!")
    print("=== END OF TEST ===")

if __name__ == "__main__":
    try:
        run_test()
    except Exception as e:
        import traceback
        traceback.print_exc()
