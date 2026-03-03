from ik_core.models.personel import Personel
from django.db.models import Count, Q
from datetime import date

def run_dynamic_search(filters, is_active=None, group_by=None, explanation="", request=None):
    """
    LLM'den gelen filtreleri Django ORM sorgusuna çevirir.
    
    filters: dict -> ORM filter kwargs
    is_active: bool -> Sadece aktif olanları listelemek için True
    group_by: str -> "unvan__ad" gibi bir alana göre gruplama verisi
    explanation: str -> LLM'in bu aramayı neden yaptığına dair kısa not
    request: Request nesnesi (Raporlama/Excel için session'da tutmak üzere)
    """
    if request:
        request.session['jarvis_last_search'] = {
            "filters": filters,
            "is_active": is_active,
            "group_by": group_by
        }
    
    # 1. Temel Sorgu (Tüm Personel Üzerinden)
    try:
        queryset = Personel.objects.all()
        
        # Filtreleri uygula
        if filters:
            # Sadece LLM'in uydurabileceği geçersiz parametreleri yakalamak adına,
            # temel bir hata mekanizması koyuyoruz.
            try:
                queryset = queryset.filter(**filters).distinct()
            except Exception as fe:
                return f"Veritabanı filtreleme hatası (geçersiz alan adı vb.): {fe}"
        
        # 2. Önceden Yüklemeler (Performans için)
        queryset = queryset.prefetch_related('gecicigorev_set', 'ozel_durumu', 'unvan', 'brans', 'unvan_brans_eslestirme__kisa_unvan__ust_birim')
        
        # 3. Aktiflik / Pasiflik Durumu Filtreleme (Python bellek / iteration gerektirir)
        filtered_list = []
        for p in queryset:
            durum = p.durum or ""
            # is_active = True ise sadece "Aktif" içerenleri dahil et.
            # is_active = False ise "Aktif" İÇERMEYENLERİ (Pasif, Ayrıldı vb) dahil et.
            # is_active = None ise hepsini dahil et.
            if is_active is True:
                if "Aktif" in durum:
                    filtered_list.append(p)
            elif is_active is False:
                if "Aktif" not in durum:
                    filtered_list.append(p)
            else:
                filtered_list.append(p)
                
        # 4. Sayım ve Gruplama Analizi
        toplam_sayi = len(filtered_list)
        
        if toplam_sayi == 0:
            return f"Girdiğiniz kriterlere uyan hiçbir personel kaydı bulunamadı. Kriterler: {filters}, Sadece Aktifler: {is_active}"
            
        sonuc_metni = f"Toplam Bulunan Kişi Sayısı: {toplam_sayi}\n"
        
        if group_by:
            # Python üzerinde gruplama yapmak zorundayız çünkü filtered_list bir Python dizisi (list of objects)
            # queryset.values(...).annotate(Count(...)) yapamıyoruz çünkü 'is_active' filter'ını python'da yaptık.
            gruplar = {}
            for p in filtered_list:
                # Dinamik attribute okuma (örn: unvan__ad -> p.unvan.ad)
                val = eval_field_path(p, group_by)
                val_str = str(val) if val else "Belirtilmemiş"
                gruplar[val_str] = gruplar.get(val_str, 0) + 1
                
            # Grupları büyükten küçüğe sırala
            sirali_gruplar = sorted(gruplar.items(), key=lambda x: x[1], reverse=True)
            
            sonuc_metni += f"\n--- {group_by} Kırılımına Göre Dağılım ---\n"
            for g_adi, g_sayi in sirali_gruplar:
                sonuc_metni += f"- {g_adi}: {g_sayi} kişi\n"
        else:
            # Eğer gruplama yoksa, liste o kadar da uzun değilse (İlk 15), detaylarını ver.
            if toplam_sayi <= 15:
                sonuc_metni += "\nBulunan Personel Listesi:\n"
                for p in filtered_list:
                    unvan_str = p.unvan.ad if p.unvan else "Ünvansız"
                    brans_str = p.brans.ad if p.brans else ""
                    unvan_tam = f"{unvan_str} ({brans_str})" if brans_str else unvan_str
                    
                    birim_str = p.son_birim_kaydi or "Birim Kaydı Yok"
                    telefon_str = p.telefon or "Kayıtlı Değil"
                    durum_str = p.durum or ""
                    
                    sonuc_metni += f"- {p.ad} {p.soyad} | Ünvan/Branş: {unvan_tam} | Birim: {birim_str} | Telefon: {telefon_str} | Durum: {durum_str}\n"
            else:
                sonuc_metni += "\n(Çok fazla kayıt olduğu için personel isimleri gizlenmiştir, alt kırılım veya gruplama isteyebilirsiniz.)"

        return sonuc_metni
        
    except Exception as e:
        return f"[DYNAMIC_SEARCH_ERROR] Sistemsel hata oluştu: {str(e)}"

def eval_field_path(obj, path):
    """
    path = "unvan__ad" olan bir string'i obj.unvan.ad objesine dönüştürür.
    """
    parts = path.split('__')
    current = obj
    try:
        for part in parts:
            if current is None:
                return None
            current = getattr(current, part, None)
        return current
    except AttributeError:
        return "Bilinmeyen Alan"
