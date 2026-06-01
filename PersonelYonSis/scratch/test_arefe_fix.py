import os
import django
import sys
from decimal import Decimal
from datetime import date

# Django setup
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PersonelYonSis.settings')
django.setup()

from mercis657.models import ResmiTatil, Personel, PersonelListesi, PersonelListesiKayit, SabitMesai, Mesai
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
    
    # İcap kaydı oluştur
    Mesai.objects.filter(Personel=personel, MesaiDate=test_date).delete()
    mesai_icap = Mesai.objects.create(
        Personel=personel,
        MesaiDate=test_date,
        Icap=True,
        OnayDurumu=True
    )
    
    res = hesapla_fazla_mesai(plk, 2026, 5)
    res_sade = hesapla_fazla_mesai_sade(plk, 2026, 5)
    
    print(f"hesapla_fazla_mesai -> olması_gereken_sure: {res['olması_gereken_sure']}")
    print(f"hesapla_fazla_mesai_sade -> olması_gereken_sure (normalde hesaplanan): {res_sade}")
    print(f"Çalışma Günleri: {res['calisma_gunleri']}, Arefe Günleri: {res['arefe_gunleri']}")
    print(f"Normal İcap Süresi: {res['normal_icap']}, Bayram İcap Süresi: {res['bayram_icap']}, Toplam İcap: {res['toplam_icap']}")
    print(f"İcap Detayları: {res['icap_detay']}")
    
    # 2026 Mayıs ayında 31 gün var.
    # Hafta sonları: 2, 3, 9, 10, 16, 17, 23, 24, 30, 31 (10 gün)
    # Hafta içi gün sayısı: 21 gün.
    # Hafta içi resmi tatil gün sayısı: 7 gün.
    # Bu yüzden hafta içi resmi tatil olmayan gün sayısı: 14 gün.
    # expected_hours = 14 * 8.0 = 112.0 saat.
    # Eğer ArefeMi = True olduğu için arefe_arttirimi = 5.0 saat eklenirse, 117.0 saat olur (Bug'lı durum).
    # Bizim düzeltmemizle arefe_arttirimi = 0.0 olmalı ve 112.0 saat hesaplanmalıdır!
    
    print(f"\nBeklenen olması_gereken_sure: 112.0 saat.")
    
    # Assertions
    assert res['olması_gereken_sure'] == Decimal('112.0'), f"Error: {res['olması_gereken_sure']} != 112.0"
    assert res_sade == Decimal('-112.0'), f"Error: {res_sade} != -112.0"
    assert res['normal_icap'] == Decimal('5.0'), f"Error: {res['normal_icap']} != 5.0"
    assert res['bayram_icap'] == Decimal('19.0'), f"Error: {res['bayram_icap']} != 19.0"
    assert res['toplam_icap'] == Decimal('24.0'), f"Error: {res['toplam_icap']} != 24.0"
    print("SUCCESS: All assertions passed!")
    print("=== END OF TEST ===")

if __name__ == "__main__":
    try:
        run_test()
    except Exception as e:
        import traceback
        traceback.print_exc()
