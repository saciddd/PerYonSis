from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from ..models import PersonelListesiKayit, PersonelListesi
from ..utils import hesapla_fazla_mesai

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