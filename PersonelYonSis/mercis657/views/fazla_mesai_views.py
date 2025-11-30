from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from ..models import PersonelListesiKayit, PersonelListesi, Personel
from ..utils import hesapla_fazla_mesai, hesapla_fazla_mesai_sade, get_vardiya_tanimlari

@login_required
def fazla_mesai_hesapla(request):
    """
    Seçili liste ve dönem için fazla mesai hesaplamalarını yapar.
    
    Parameters:
        request.GET.year (int): Yıl
        request.GET.month (int): Ay
        request.GET.liste_id (int): PersonelListesi ID
    
    Returns:
        JsonResponse: 
        {
            "status": "success|error",
            "data": [{"personel_id": id, "fazla_mesai": float}, ...],
            "message": "error message if any"
        }
    """
    try:
        year = int(request.GET.get("year"))
        month = int(request.GET.get("month"))
        liste_id = int(request.GET.get("liste_id"))

        if not all([year, month, liste_id]):
            raise ValidationError("Yıl, ay ve liste ID gerekli.")

        # Resolve the PersonelListesi (safer) and iterate its kayitlar
        liste = PersonelListesi.objects.filter(pk=liste_id).first()
        if not liste:
            # No list found -> return empty success (matches other list endpoints)
            print(f"fazla_mesai_hesapla: PersonelListesi id={liste_id} bulunamadı")
            return JsonResponse({"status": "success", "data": []})

        kayitlar = liste.kayitlar.select_related('personel').all()

        sonuc = []
        for kayit in kayitlar:
            try:
                hesaplama = hesapla_fazla_mesai(kayit, year, month) or {}
                # hesapla_fazla_mesai returns keys 'normal_fazla_mesai' and 'bayram_fazla_mesai'
                normal = hesaplama.get('normal_fazla_mesai') or 0
                bayram = hesaplama.get('bayram_fazla_mesai') or 0
                # ensure Decimal -> float
                try:
                    normal_f = float(normal)
                except Exception:
                    normal_f = float(0)
                try:
                    bayram_f = float(bayram)
                except Exception:
                    bayram_f = float(0)

                toplam = normal_f + bayram_f
                sonuc.append({
                    "personel_id": kayit.personel.PersonelID,
                    "fazla_mesai": float(hesaplama.get('fazla_mesai')),
                    "normal_fazla_mesai": normal_f,
                    "bayram_fazla_mesai": bayram_f,
                })
            except Exception as e:
                print(f"fazla_mesai_hesapla: hata personel {getattr(kayit.personel, 'PersonelID', '?')}: {e}")
                continue

        return JsonResponse({
            "status": "success",
            "data": sonuc
        })
    except ValidationError as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=400)
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": f"Hesaplama hatası: {str(e)}"
        }, status=500)

@login_required
def fazla_mesai_hesapla_toplu(request):
    """
    Toplu fazla mesai hesaplama endpoint'i.
    
    Parameters:
        request.POST.personel_ids (list): Personel ID listesi
        request.POST.year (int): Yıl
        request.POST.month (int): Ay
        request.POST.liste_id (int): PersonelListesi ID
    
    Returns:
        JsonResponse: 
        {
            "status": "success|error",
            "data": [{"personel_id": id, "fazla_mesai": float}, ...],
            "message": "error message if any"
        }
    """
    try:
        import json
        data = json.loads(request.body) if request.body else {}
        
        personel_ids = data.get("personel_ids", [])
        year = int(data.get("year"))
        month = int(data.get("month"))
        liste_id = int(data.get("liste_id"))

        if not all([personel_ids, year, month, liste_id]):
            raise ValidationError("Personel ID listesi, yıl, ay ve liste ID gerekli.")

        liste = PersonelListesi.objects.filter(pk=liste_id).first()
        if not liste:
            return JsonResponse({
                "status": "error",
                "message": "Personel listesi bulunamadı."
            }, status=404)

        sonuc = []
        for personel_id in personel_ids:
            try:
                personel = Personel.objects.filter(PersonelID=int(personel_id)).first()
                if not personel:
                    continue
                
                kayit = PersonelListesiKayit.objects.filter(
                    liste=liste,
                    personel=personel
                ).first()
                
                if kayit:
                    fazla_mesai = hesapla_fazla_mesai_sade(kayit, year, month)
                    sonuc.append({
                        "personel_id": personel.PersonelID,
                        "fazla_mesai": float(fazla_mesai)
                    })
            except Exception as e:
                print(f"fazla_mesai_hesapla_toplu: hata personel {personel_id}: {e}")
                continue

        return JsonResponse({
            "status": "success",
            "data": sonuc
        })
    except ValidationError as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=400)
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": f"Hesaplama hatası: {str(e)}"
        }, status=500)


@login_required
def vardiya_tanimlari(request):
    """
    Vardiya tanımlarını döndürür.
    
    Returns:
        JsonResponse: 
        {
            "status": "success",
            "mesai_tanimlari": { id: { "gunduz": bool, "aksam": bool, "gece": bool } }
        }
    """
    try:
        tanimlar = get_vardiya_tanimlari()
        return JsonResponse({
            "status": "success",
            "mesai_tanimlari": tanimlar
        })
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": f"Hata: {str(e)}"
        }, status=500)