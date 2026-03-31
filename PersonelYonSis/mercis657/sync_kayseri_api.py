import json
import requests

API_URL = "http://10.38.8.115:5000/api/v1/kayseri/mesai/sync"
API_KEY = "dkod_kayseri_7b3f9a2e1d5c8f4061e2b7a9d3c5f812"

def sync_kayseri_mesai(liste_id: int):
    """
    Kayseri entegrasyonu için senkron mesai gönderimi yapar ve API sonucunu döner.
    """
    try:
        from .models import PersonelListesi, Mesai
        
        try:
            liste = PersonelListesi.objects.select_related('birim').get(id=liste_id)
        except PersonelListesi.DoesNotExist:
            return {"durum": "HATA", "mesaj": "Personel listesi bulunamadı."}
            
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
            
        # Eğer gönderilecek hiç M1 veya M2 notlu kayıt yoksa işlemi atla
        if not mesailar_payload:
            return {"durum": "BOS", "mesaj": "Gönderilecek M1/M2 notu olan kayıt bulunamadı."}
            
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
        
        response = requests.post(API_URL, json=payload, headers=headers, timeout=15)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"durum": "HATA", "mesaj": f"API Bağlantı Hatası: HTTP {response.status_code}"}

    except requests.exceptions.Timeout:
         return {"durum": "HATA", "mesaj": "Sunucuya bağlanırken zaman aşımı meydana geldi."}
    except requests.exceptions.RequestException as e:
         return {"durum": "HATA", "mesaj": f"Sunucuya bağlanırken ağ hatası oluştu: {str(e)}"}
    except Exception as e:
         return {"durum": "HATA", "mesaj": f"Beklenmeyen bir hata oluştu: {str(e)}"}
