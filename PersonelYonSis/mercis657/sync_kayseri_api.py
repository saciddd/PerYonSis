import threading
import json
import requests
from django.db import close_old_connections

API_URL = "http://10.38.8.115:5000/api/v1/kayseri/mesai/sync"
API_KEY = "dkod_kayseri_7b3f9a2e1d5c8f4061e2b7a9d3c5f812"

def sync_kayseri_mesai_async(liste_id: int):
    """
    Kayseri entegrasyonu için asenkron mesai gönderimi başlatır.
    """
    thread = threading.Thread(target=_sync_mesai_task, args=(liste_id,))
    thread.daemon = True
    thread.start()

def _sync_mesai_task(liste_id: int):
    # Veritabanı bağlantılarının thread güvenliği için temizlenmesi
    close_old_connections()
    
    try:
        from .models import PersonelListesi, Mesai
        
        try:
            liste = PersonelListesi.objects.select_related('birim').get(id=liste_id)
        except PersonelListesi.DoesNotExist:
            return
            
        birim_id = liste.birim.BirimID
        birim_adi = liste.birim.BirimAdi
        donem = f"{liste.yil}-{liste.ay:02d}"
        
        # Listedeki personeller
        personel_ids = liste.kayitlar.values_list('personel_id', flat=True)
        
        # Sadece M1 ve M2 notuna sahip olan mesaileri çekeceğiz
        mesailer = Mesai.objects.filter(
            Personel_id__in=personel_ids,
            MesaiDate__year=liste.yil,
            MesaiDate__month=liste.ay,
            MesaiNotu__in=["M1", "M2"]
        ).select_related('Personel', 'MesaiTanim')
        
        mesailar_payload = []
        
        for m in mesailer:
            # baslangic ve bitis MesaiTanim objesinden alınır.
            baslangic = ""
            bitis = ""
            if m.MesaiTanim and m.MesaiTanim.Saat:
                try:
                    parts = m.MesaiTanim.Saat.split(' ')
                    if len(parts) >= 2:
                        baslangic = parts[0]
                        bitis = parts[1]
                    else:
                        baslangic = parts[0]
                        bitis = parts[0]
                except Exception:
                    pass
            
            # API zorunlu alanlarını kontrol et
            if not baslangic or not bitis:
                continue
                
            mesailar_payload.append({
                "tckn": str(m.Personel.PersonelTCKN),
                "tarih": m.MesaiDate.strftime("%Y-%m-%d"),
                "baslangic": baslangic,
                "bitis": bitis,
                "mesaiNotu": m.MesaiNotu,
                "onayDurumu": m.OnayDurumu,
                "izinli": bool(m.SistemdekiIzin or getattr(m, 'Izin_id', None))
            })
            
        payload = {
            "birimId": birim_id,
            "birimAdi": birim_adi,
            "donem": donem,
            "mesailar": mesailar_payload
        }
        
        headers = {
            "Content-Type": "application/json",
            "x-api-key": API_KEY
        }
        
        # Sadece hata fırlatmamasını sağlıyoruz.
        requests.post(API_URL, json=payload, headers=headers, timeout=10)

    except Exception as e:
        # Thread içindeki hataları sessizce yutuyoruz, projeyi kırmaması için
        pass
    finally:
        # Thread sonlanırken connections temizleyelim
        close_old_connections()
