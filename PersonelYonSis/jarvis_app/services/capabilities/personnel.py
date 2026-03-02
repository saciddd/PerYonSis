from django.db.models import Q
from ik_core.models.personel import Personel
from datetime import date

def _search_personel(name):
    """Yardımcı fonksiyon: İsim veya soyisimle personel arar."""
    if not name:
        return []
    
    parts = name.split()
    query = Q()
    for part in parts:
        query &= (Q(ad__icontains=part) | Q(soyad__icontains=part))
    
    # Çok fazla sonuç dönmesini engellemek için limite edelim
    return Personel.objects.filter(query)[:5]

def get_person_department(name):
    personels = _search_personel(name)
    
    if not personels:
        return f"'{name}' isimli personel bulunamadı."
    
    results = []
    for p in personels:
        birim = p.son_birim_kaydi or "Birim kaydı yok"
        results.append(f"{p.ad} {p.soyad} - Birim: {birim}")
        
    if len(results) == 1:
        return results[0]
    else:
        return "Birden fazla kayıt bulundu: \n" + "\n".join(results)

def get_person_phone(name):
    personels = _search_personel(name)
    
    if not personels:
        return f"'{name}' isimli personel bulunamadı."
    
    results = []
    for p in personels:
        telefon = p.telefon or "Telefon kaydı yok"
        results.append(f"{p.ad} {p.soyad} - Telefon: {telefon}")
        
    if len(results) == 1:
        return results[0]
    else:
        return "Birden fazla kayıt bulundu: \n" + "\n".join(results)
