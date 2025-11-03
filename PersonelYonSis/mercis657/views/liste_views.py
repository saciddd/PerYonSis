from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from ..models import Birim, PersonelListesi, PersonelListesiKayit

def has_list_management_permission(user):
    return user.has_permission('ÇS 657 Personel Liste Yönetimi')

@login_required
def birim_listeleri(request, birim_id):
    if not has_list_management_permission(request.user):
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)
    
    birim = get_object_or_404(Birim, BirimID=birim_id)
    listeler = PersonelListesi.objects.filter(birim=birim).values('id', 'ay', 'yil')
    return JsonResponse({'listeler': list(listeler)})

@login_required
def liste_personeller(request, liste_id):
    if not has_list_management_permission(request.user):
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)
    
    liste = get_object_or_404(PersonelListesi, id=liste_id)
    # The Personel model uses fields PersonelID, PersonelName, PersonelSurname
    personeller_qs = liste.kayitlar.select_related('personel').all().values(
        'personel__PersonelID', 'personel__PersonelName', 'personel__PersonelSurname'
    )
    return JsonResponse({
        'personeller': [
            {
                'id': p['personel__PersonelID'],
                'ad': p['personel__PersonelName'],
                'soyad': p['personel__PersonelSurname']
            }
            for p in personeller_qs
        ]
    })

@login_required
@require_http_methods(["POST"])
def personel_cikar(request, liste_id, personel_id):
    if not has_list_management_permission(request.user):
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)
    
    try:
        kayit = PersonelListesiKayit.objects.get(
            liste_id=liste_id,
            personel_id=personel_id
        )
        kayit.delete()
        return JsonResponse({
            'status': 'success',
            'message': 'Personel listeden çıkarıldı.'
        })
    except PersonelListesiKayit.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Kayıt bulunamadı.'
        }, status=404)

@login_required
@require_http_methods(["DELETE"])
def liste_sil(request, liste_id):
    if not has_list_management_permission(request.user):
        return JsonResponse({'status': 'error', 'message': 'Yetkiniz yok.'}, status=403)
    
    liste = get_object_or_404(PersonelListesi, id=liste_id)
    
    if liste.kayitlar.exists():
        return JsonResponse({
            'status': 'error',
            'message': 'Liste içinde personel bulunduğu için silinemez.'
        }, status=400)
    
    birim_id = liste.birim_id
    liste.delete()
    return JsonResponse({
        'status': 'success',
        'message': 'Liste başarıyla silindi.',
        'birim_id': birim_id
    })