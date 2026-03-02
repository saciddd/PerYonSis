from ik_core.models.personel import Personel
from ik_core.models.BirimYonetimi import PersonelBirim
from django.db.models import Q
from datetime import date

def count_personnel_by_title(title_name):
    """Verilen ünvan (unvan veya branş) adına sahip personelleri durumlarına göre analiz eder."""
    if not title_name:
        return "Lütfen sorgulamak istediğiniz ünvan veya branş adını belirtin."
        
    # Unvan veya Branş adında arama yapıyoruz
    personeller = Personel.objects.filter(
        Q(unvan__ad__icontains=title_name) | Q(brans__ad__icontains=title_name)
    ).prefetch_related('gecicigorev_set', 'unvan', 'brans')
    
    if not personeller.exists():
        return f"Sistemde '{title_name}' ünvanı veya branşına sahip kayıtlı personel bulunamadı."
        
    aktif_kadrolu = 0
    aktif_gecici = 0
    pasif = 0
    
    for p in personeller:
        durum = p.durum or ""
        if durum == "Aktif (Kadrolu)":
            aktif_kadrolu += 1
        elif durum == "Aktif (Geçici)":
            aktif_gecici += 1
        elif durum == "Pasif":
            pasif += 1
            
    toplam_aktif = aktif_kadrolu + aktif_gecici
    
    if toplam_aktif == 0 and pasif == 0:
         return f"Kayıtlı '{title_name}' personeli var ancak hiçbiri aktif veya geçici görevde (pasif) değil."

    sonuc = f"{toplam_aktif} Aktif {title_name} var."
    if toplam_aktif > 0:
        detaylar = []
        if aktif_kadrolu > 0:
            detaylar.append(f"{aktif_kadrolu} tanesi kadrolu")
        if aktif_gecici > 0:
            detaylar.append(f"{aktif_gecici} tanesi geçici gelen personel")
        if detaylar:
            sonuc += f" Bunun {', '.join(detaylar)}."
            
    if pasif > 0:
        sonuc += f" Ayrıca {pasif} {title_name} geçici görevle başka kuruma/birime gittiği için pasif durumda."
        
    return sonuc

def count_unit_personnel(unit_name):
    """Birim adıyla arama yapıp o birimde çalışan aktif personel sayısını döner."""
    if not unit_name:
        return "Lütfen sorgulamak istediğiniz birim adını belirtin."
        
    # Python tarafında durum analizi yapmak personellerin güncel/aktif birimini bulmamızı sağlar
    # Tüm personelleri alıp son birimi `unit_name` içerenleri filtreleyeceğiz 
    # Veya direkt PersonelBirim'den en güncel kayıtları alabiliriz
    # Basit bir çözüm: Personelleri alıp `son_birim_kaydi` propertiesini kontrol etmek.
    
    # ORM kullanarak `PersonelBirim` tablosunda isim filtrelemesi yapıyoruz
    # İlk olarak birimleri (BirimTipi vs) kısmen eşleşen personelleri bulalım
    # Sadece aktif olanları sayalım.
    
    eslesen_birimler = PersonelBirim.objects.filter(birim__ad__icontains=unit_name).select_related('personel', 'birim').order_by('personel_id', '-gecis_tarihi')
    
    # Unique personel ID to keep only the latest record for each person
    latest_birim_map = {}
    for pb in eslesen_birimler:
        if pb.personel_id not in latest_birim_map:
            latest_birim_map[pb.personel_id] = pb

    aktif_sayisi = 0
    birim_tam_adi = ""
    
    for pb in latest_birim_map.values():
        p = pb.personel
        # Sadece Aktif durumu olanları ekle
        if 'Aktif' in (p.durum or ""):
            aktif_sayisi += 1
            birim_tam_adi = pb.birim.ad # örnek teşkil etmesi için atandı
            
    if aktif_sayisi == 0:
        return f"'{unit_name}' ile eşleşen birimde aktif personel bulunamadı veya birim bulunamadı."
        
    return f"'{birim_tam_adi}' (veya varyasyonları) biriminde toplam {aktif_sayisi} aktif personel görev yapmaktadır."
