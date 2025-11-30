from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from ..models import PersonelListesi, Mesai, Mesai_Tanimlari, Izin, SabitMesai, PersonelListesiKayit


@login_required
def cizelge_kontrol(request):
    """
    Çizelge hata kontrolü endpoint'i.
    
    Parameters:
        request.POST.liste_id (int): PersonelListesi ID
        request.POST.year (int): Yıl
        request.POST.month (int): Ay
    
    Returns:
        JsonResponse: 
        {
            "status": "success|error",
            "errors": [
                {
                    "type": str,
                    "message": str,
                    "personel_id": int,
                    "date": str,
                    "cell_selector": str
                }
            ]
        }
    """
    try:
        import json
        data = json.loads(request.body) if request.body else {}
        
        liste_id = int(data.get("liste_id"))
        year = int(data.get("year"))
        month = int(data.get("month"))

        if not all([liste_id, year, month]):
            raise ValidationError("Liste ID, yıl ve ay gerekli.")

        liste = PersonelListesi.objects.filter(pk=liste_id).first()
        if not liste:
            return JsonResponse({
                "status": "error",
                "message": "Personel listesi bulunamadı."
            }, status=404)

        errors = []
        
        # 24 saatlik mesai sonrası kontrolü
        errors.extend(_check_24_hour_mesai_rule(liste, year, month))
        
        # 5 gün boş bırakılmamalı kontrolü
        errors.extend(_check_5_day_empty_rule(liste, year, month))

        # Sabit mesai kontrolü ve güncellemesi
        errors.extend(sabit_mesai_kontrol(liste, year, month))

        return JsonResponse({
            "status": "success",
            "errors": errors
        })
    except ValidationError as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=400)
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": f"Hata: {str(e)}"
        }, status=500)


def _check_24_hour_mesai_rule(liste, year, month):
    """24 saatlik mesai sonrası kontrolü"""
    errors = []
    days_in_month = 31  # Max gün sayısı
    try:
        import calendar
        days_in_month = calendar.monthrange(year, month)[1]
    except:
        pass
    
    kayitlar = liste.kayitlar.select_related('personel').all()
    
    for kayit in kayitlar:
        personel = kayit.personel
        mesailer = Mesai.objects.filter(
            Personel=personel,
            MesaiDate__year=year,
            MesaiDate__month=month
        ).select_related('MesaiTanim')
        
        for mesai in mesailer:
            if mesai.MesaiTanim and mesai.MesaiTanim.SonrakiGuneSarkiyor:
                if mesai.MesaiTanim.Sure and mesai.MesaiTanim.Sure >= 24:
                    # Sonraki günü kontrol et
                    next_date = mesai.MesaiDate + timedelta(days=1)
                    
                    # Sonraki gün aynı ay içindeyse kontrol et
                    if next_date.year == year and next_date.month == month:
                        next_mesai = Mesai.objects.filter(
                            Personel=personel,
                            MesaiDate=next_date
                        ).first()
                        
                        if next_mesai and next_mesai.MesaiTanim and not next_mesai.Izin:
                            errors.append({
                                "type": "24_hour_mesai",
                                "message": f"{mesai.MesaiDate.strftime('%Y-%m-%d')} tarihli 24 saatlik mesai sonrası {next_date.strftime('%Y-%m-%d')} tarihinde mesai tanımlanmamalı",
                                "personel_id": personel.PersonelID,
                                "date": next_date.strftime('%Y-%m-%d'),
                                "cell_selector": f"td[data-date='{next_date.strftime('%Y-%m-%d')}'][data-personel-id='{personel.PersonelID}']"
                            })
    
    return errors


def _check_5_day_empty_rule(liste, year, month):
    """5 gün boş bırakılmamalı kontrolü"""
    errors = []
    import calendar
    days_in_month = calendar.monthrange(year, month)[1]
    
    kayitlar = liste.kayitlar.select_related('personel').all()
    
    for kayit in kayitlar:
        personel = kayit.personel
        
        # Önceki ayın son 4 gününü de kontrol et
        prev_month = month - 1
        prev_year = year
        if prev_month == 0:
            prev_month = 12
            prev_year = year - 1
        
        prev_days_in_month = calendar.monthrange(prev_year, prev_month)[1]
        start_check_date = date(prev_year, prev_month, max(1, prev_days_in_month - 3))
        end_check_date = date(year, month, days_in_month)
        
        # Tüm günleri kontrol et
        current_date = start_check_date
        consecutive_empty = 0
        empty_start = None
        
        while current_date <= end_check_date:
            # Hafta sonu ve resmi tatil kontrolü (basitleştirilmiş)
            weekday = current_date.weekday()
            is_weekend = weekday >= 5
            
            if not is_weekend:
                mesai = Mesai.objects.filter(
                    Personel=personel,
                    MesaiDate=current_date
                ).first()
                
                has_data = mesai and (mesai.MesaiTanim or mesai.Izin)
                
                if not has_data:
                    if consecutive_empty == 0:
                        empty_start = current_date
                    consecutive_empty += 1
                else:
                    if consecutive_empty >= 5:
                        errors.append({
                            "type": "5_day_empty",
                            "message": f"{personel.PersonelName} {personel.PersonelSurname} için {empty_start.strftime('%Y-%m-%d')} - {current_date.strftime('%Y-%m-%d')} arası {consecutive_empty} gün boyunca mesai verisi yok",
                            "personel_id": personel.PersonelID,
                            "date": empty_start.strftime('%Y-%m-%d'),
                            "cell_selector": f"td[data-date='{empty_start.strftime('%Y-%m-%d')}'][data-personel-id='{personel.PersonelID}']"
                        })
                    consecutive_empty = 0
                    empty_start = None
            
            current_date += timedelta(days=1)
        
        # Son kontrol: Eğer ay sonunda hala boş günler varsa
        if consecutive_empty >= 5:
            errors.append({
                "type": "5_day_empty",
                "message": f"{personel.PersonelName} {personel.PersonelSurname} için {empty_start.strftime('%Y-%m-%d')} - {end_check_date.strftime('%Y-%m-%d')} arası {consecutive_empty} gün boyunca mesai verisi yok",
                "personel_id": personel.PersonelID,
                "date": empty_start.strftime('%Y-%m-%d'),
                "cell_selector": f"td[data-date='{empty_start.strftime('%Y-%m-%d')}'][data-personel-id='{personel.PersonelID}']"
            })
    
    return errors


def sabit_mesai_kontrol(liste, year, month):
    """
    Personelin mesai saatlerine göre sabit mesai bilgisini günceller.
    """
    messages = []
    
    # Tüm sabit mesai tanımlarını al
    sabit_mesailer = SabitMesai.objects.all()
    sabit_mesai_map = {sm.aralik: sm for sm in sabit_mesailer}
    
    if not sabit_mesai_map:
        return messages
        
    kayitlar = liste.kayitlar.select_related('personel', 'sabit_mesai').all()
    
    for kayit in kayitlar:
        personel = kayit.personel
        
        # Personelin ilgili dönemdeki mesailerini kontrol et
        mesailer = Mesai.objects.filter(
            Personel=personel,
            MesaiDate__year=year,
            MesaiDate__month=month
        ).select_related('MesaiTanim')
        
        matched_sabit_mesai = None
        
        # Mesailer içinde sabit mesai aralığı ile eşleşen var mı?
        for mesai in mesailer:
            if mesai.MesaiTanim and mesai.MesaiTanim.Saat in sabit_mesai_map:
                matched_sabit_mesai = sabit_mesai_map[mesai.MesaiTanim.Saat]
                break
        
        # Eşleşme varsa ve mevcut kayıttan farklıysa güncelle
        if matched_sabit_mesai:
            if kayit.sabit_mesai != matched_sabit_mesai:
                kayit.sabit_mesai = matched_sabit_mesai
                kayit.save()
                
                messages.append({
                    "type": "info",
                    "message": f"{personel.PersonelName} {personel.PersonelSurname} isimli personelin sabit mesai kaydı {matched_sabit_mesai.aralik} olarak belirlendi",
                    "personel_id": personel.PersonelID,
                    "date": "",
                    "cell_selector": ""
                })
    
    return messages
