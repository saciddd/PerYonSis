import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Sertifika, Personel

@csrf_exempt
@login_required
def sertifika_guncelle(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            tc_kimlik_no = data.get('tc_kimlik_no')
            aciklama = data.get('sertifika_aciklamasi')
            baslangic = data.get('baslangic_tarihi')
            bitis = data.get('bitis_tarihi')
            alanda_kullaniliyor = data.get('alanda_kullaniliyor', False)

            if not all([tc_kimlik_no, aciklama, baslangic, bitis]):
                return JsonResponse({'status': 'error', 'message': 'Eksik veri gönderildi.'}, status=400)

            personel = Personel.objects.filter(TCKimlikNo=tc_kimlik_no).first()
            if not personel:
                return JsonResponse({'status': 'error', 'message': 'Personel bulunamadı.'}, status=404)

            sertifika, created = Sertifika.objects.update_or_create(
                personel=personel,
                defaults={
                    'sertifika_aciklamasi': aciklama,
                    'baslangic_tarihi': baslangic,
                    'bitis_tarihi': bitis,
                    'alanda_kullaniliyor': alanda_kullaniliyor
                }
            )

            return JsonResponse({'status': 'success', 'message': 'Sertifika güncellendi.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Geçersiz istek metodu.'}, status=405)

@login_required
def sertifikali_personeller_raporu(request):
    sertifikalar = Sertifika.objects.select_related('personel').all()
    
    return render(request, 'ik_core/sertifika_raporu.html', {
        'sertifikalar': sertifikalar
    })
