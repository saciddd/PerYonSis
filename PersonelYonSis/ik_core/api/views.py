# ik_core/api/views.py
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http import JsonResponse
from ik_core.models import Personel

@csrf_exempt
def filemaker_personel_aktar(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Yalnızca POST desteklenir'}, status=405)

    # Token kontrolü
    api_key = request.headers.get('X-API-KEY') or request.GET.get('api_key')
    if api_key != settings.API_AUTH_KEY:
        return JsonResponse({'status': 'error', 'message': 'Geçersiz veya eksik API anahtarı'}, status=403)

    try:
        data = JSONParser().parse(request)

        if 'tc_kimlik_no' not in data:
            return JsonResponse({'status': 'error', 'message': 'TC Kimlik No zorunludur'}, status=400)

        personel, created = Personel.objects.update_or_create(
            tc_kimlik_no=data['tc_kimlik_no'],
            defaults={
                'ad': data.get('ad', ''),
                'soyad': data.get('soyad', ''),
                'sicil_no': data.get('sicil_no', '')
            }
        )

        return JsonResponse({
            'status': 'success',
            'created': created,
            'personel': {
                'tc_kimlik_no': personel.tc_kimlik_no,
                'ad': personel.ad,
                'soyad': personel.soyad,
                'sicil_no': personel.sicil_no
            }
        })

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    # tc_kimlik_no = request.data.get('tc_kimlik_no')

    # if not tc_kimlik_no:
    #     return Response({'status': 'error', 'message': 'tc_kimlik_no alanı zorunludur'}, status=400)

    # try:
    #     personel = Personel.objects.get(tc_kimlik_no=tc_kimlik_no)
    #     serializer = PersonelSerializer(personel, data=request.data, partial=True)
    #     action = 'updated'
    # except Personel.DoesNotExist:
    #     serializer = PersonelSerializer(data=request.data)
    #     action = 'created'

    # if serializer.is_valid():
    #     serializer.save()
    #     return Response({'status': 'success', 'action': action, 'personel': serializer.data})
    # else:
    #     return Response({'status': 'error', 'errors': serializer.errors}, status=400)