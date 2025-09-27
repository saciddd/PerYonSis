from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from ..models import Birim, UserBirim, Kurum, UstBirim, Idareci
import json
from django.contrib import messages
from django.contrib.auth import get_user_model
User = get_user_model()

def birim_yonetim(request):
    birimler = Birim.objects.select_related('Kurum', 'UstBirim', 'Idareci').all()
    birim_list = []
    for birim in birimler:
        yetkiler = UserBirim.objects.filter(birim=birim).select_related('user')
        yetkili_users = [
            {
                "username": y.user.Username,
                "full_name": y.user.FullName
            }
            for y in yetkiler
        ]
        birim_list.append({
            "id": birim.BirimID,
            "adi": birim.BirimAdi,
            "kurum": birim.Kurum.ad if birim.Kurum else "",
            "ust_birim": birim.UstBirim.ad if birim.UstBirim else "",
            "idareci": birim.Idareci.ad if birim.Idareci else "",
            "yetkili_sayisi": len(yetkili_users),
            "yetkililer": yetkili_users,
        })
    kurumlar = Kurum.objects.all()
    ust_birimler = UstBirim.objects.all()
    idareciler = Idareci.objects.all()
    return render(request, "mercis657/birim_yonetim.html", {
        "birimler": birim_list,
        "kurumlar": kurumlar,
        "ust_birimler": ust_birimler,
        "idareciler": idareciler,
    })

@csrf_exempt
def birim_ekle(request):
    if request.method == 'POST':
        ad = request.POST.get('BirimAdi')
        kurum_id = request.POST.get('Kurum') or None
        ust_id = request.POST.get('UstBirim') or None
        mudur_id = request.POST.get('idareci') or None
        if not ad:
            return JsonResponse({'status': 'error', 'message': 'Birim adı zorunlu.'})
        try:
            birim = Birim.objects.create(
                BirimAdi=ad,
                Kurum_id=kurum_id if kurum_id else None,
                UstBirim_id=ust_id if ust_id else None,
                Idareci_id=mudur_id if mudur_id else None
            )
            # Yeni eklenen birime mevcut kullanıcıyı yetkilendir
            UserBirim.objects.create(user=request.user, birim=birim)
            return JsonResponse({'status': 'success', 'birim_id': birim.BirimID})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Geçersiz istek.'})

@login_required
def birim_detay(request, birim_id):
    try:
        birim = get_object_or_404(Birim, BirimID=birim_id)
        # Kullanıcının bu birim için yetkisi var mı kontrol et
        if not UserBirim.objects.filter(user=request.user, birim=birim).exists():
             return JsonResponse({'status': 'error', 'message': 'Bu birim için yetkiniz yok.'}, status=403)

        data = {
            'BirimID': birim.BirimID,
            'BirimAdi': birim.BirimAdi,
            'Kurum': birim.Kurum.pk if birim.Kurum else None,
            'UstBirim': birim.UstBirim.pk if birim.UstBirim else None,
            'idareci': birim.Idareci.pk if birim.Idareci else None,
        }
        return JsonResponse({'status': 'success', 'data': data})
    except Birim.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Birim bulunamadı.'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@csrf_exempt # CSRF korumasını geçici olarak devre dışı bırakıyoruz, uygun token yönetimi eklenmeli
@require_POST
@login_required
def birim_guncelle(request, birim_id):
    try:
        birim = get_object_or_404(Birim, BirimID=birim_id)
        # Kullanıcının bu birim için yetkisi var mı kontrol et
        if not UserBirim.objects.filter(user=request.user, birim=birim).exists():
             return JsonResponse({'status': 'error', 'message': 'Bu birim için yetkiniz yok.'}, status=403)

        ad = request.POST.get('birimAdi')
        kurum_id = request.POST.get('Kurum') or None
        ust_id = request.POST.get('UstBirim') or None
        mudur_id = request.POST.get('idareci') or None

        if not ad:
            return JsonResponse({'status': 'error', 'message': 'Birim adı zorunlu.'})

        birim.BirimAdi = ad
        birim.Kurum_id = kurum_id
        birim.UstBirim_id = ust_id
        birim.Idareci_id = mudur_id
        birim.save()

        return JsonResponse({'status': 'success', 'message': 'Birim başarıyla güncellendi.'})
    except Birim.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Birim bulunamadı.'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@csrf_exempt # CSRF korumasını geçici olarak devre dışı bırakıyoruz, uygun token yönetimi eklenmeli
@require_POST
@login_required
def birim_sil(request, birim_id):
    try:
        birim = get_object_or_404(Birim, BirimID=birim_id)
         # Kullanıcının bu birim için yetkisi var mı kontrol et (isteğe bağlı: silme yetkisi farklı olabilir)
        if not UserBirim.objects.filter(user=request.user, birim=birim).exists():
             return JsonResponse({'status': 'error', 'message': 'Bu birim için yetkiniz yok.'}, status=403)

        birim.delete()
        return JsonResponse({'status': 'success', 'message': 'Birim başarıyla silindi.'})
    except Birim.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Birim bulunamadı.'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@csrf_exempt
def birim_yetki_ekle(request, birim_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            user = User.objects.get(Username=username)
            birim = Birim.objects.get(pk=birim_id)
            obj, created = UserBirim.objects.get_or_create(user=user, birim=birim)
            if created:
                messages.success(request, f"{user.FullName} kullanıcısına {birim.BirimAdi} birimi yetkisi verildi.")
                return JsonResponse({"status": "success"})
            else:
                return JsonResponse({"status": "error", "message": "Kullanıcı zaten yetkili."})
        except User.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Kullanıcı bulunamadı."})
        except Birim.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Birim bulunamadı."})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})
    return JsonResponse({"status": "error", "message": "Geçersiz istek."})

@csrf_exempt
@require_POST
def birim_yetki_sil(request, birim_id):
    # Yetki kontrolü
    if not request.user.has_permission("ÇS 657 Birim Yönetimi Sayfası"):
        if not UserBirim.objects.filter(user=request.user, birim_id=birim_id).exists():
            return JsonResponse({"status": "error", "message": "Bu birim için yetkiniz yok."}, status=403)
    
    try:
        body = json.loads(request.body)
        username = body.get('username')
        user = User.objects.get(Username=username)
        birim = Birim.objects.get(pk=birim_id)
        deleted, _ = UserBirim.objects.filter(user=user, birim=birim).delete()
        if deleted:
            messages.success(request, f"{user.FullName} kullanıcısının {birim.BirimAdi} birimi yetkisi kaldırıldı.")
            return JsonResponse({"status": "success"})
        else:
            return JsonResponse({"status": "error", "message": "Yetki bulunamadı."})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})
    
def birim_yetkililer(request, birim_id):
    # Birime atanmış kullanıcıları getir
    yetkiler = UserBirim.objects.filter(birim_id=birim_id).select_related('user')
    data = [
        {
            "username": y.user.Username,
            "full_name": y.user.FullName,
        }
        for y in yetkiler
    ]
    return JsonResponse({"status": "success", "data": data})

def kullanici_ara(request):
    username = request.GET.get('username', '').strip()
    try:
        user = User.objects.get(Username=username)
        data = {
            "username": user.Username,
            "full_name": user.FullName
        }
        return JsonResponse({"status": "success", "data": data})
    except User.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Kullanıcı bulunamadı."})


@csrf_exempt
def kurum_ekle(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        ad = data.get('ad', '').strip()
        if not ad:
            return JsonResponse({'status': 'error', 'message': 'Kurum adı zorunlu.'})
        if Kurum.objects.filter(ad=ad).exists():
            return JsonResponse({'status': 'error', 'message': 'Bu ad ile kurum zaten var.'})
        Kurum.objects.create(ad=ad)
        messages.success(request, f'{ad} isimli Kurum başarıyla eklendi.')
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

@csrf_exempt
def kurum_guncelle(request, pk):
    if request.method == 'POST':
        data = json.loads(request.body)
        ad = data.get('ad', '').strip()
        if not ad:
            return JsonResponse({'status': 'error', 'message': 'Kurum adı zorunlu.'})
        kurum = Kurum.objects.get(pk=pk)
        kurum.ad = ad
        kurum.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

@csrf_exempt
def kurum_sil(request, pk):
    if request.method == 'POST':
        try:
            kurum = Kurum.objects.get(pk=pk)
            kurum.delete()
            messages.success(request, f'{kurum.ad} isimli Kurum başarıyla silindi.')
            return JsonResponse({'status': 'success'})
        except Kurum.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Kurum bulunamadı.'})
    return JsonResponse({'status': 'error'})

@csrf_exempt
def ust_birim_ekle(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        ad = data.get('ad', '').strip()
        if not ad:
            return JsonResponse({'status': 'error', 'message': 'Üst birim adı zorunlu.'})
        if UstBirim.objects.filter(ad=ad).exists():
            return JsonResponse({'status': 'error', 'message': 'Bu ad ile üst birim zaten var.'})
        UstBirim.objects.create(ad=ad)
        messages.success(request, f'{ad} isimli Üst Birim başarıyla eklendi.')
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

@csrf_exempt
def ust_birim_guncelle(request, pk):
    if request.method == 'POST':
        data = json.loads(request.body)
        ad = data.get('ad', '').strip()
        if not ad:
            return JsonResponse({'status': 'error', 'message': 'Üst birim adı zorunlu.'})
        ust = UstBirim.objects.get(pk=pk)
        ust.ad = ad
        ust.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

@csrf_exempt
def ust_birim_sil(request, pk):
    if request.method == 'POST':
        try:
            ust = UstBirim.objects.get(pk=pk)
            ust.delete()
            messages.success(request, f'{ust.ad} isimli Üst Birim başarıyla silindi.')
            return JsonResponse({'status': 'success'})
        except UstBirim.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Üst birim bulunamadı.'})
    return JsonResponse({'status': 'error'})

@csrf_exempt
def idareci_ekle(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        ad = data.get('ad', '').strip()
        if not ad:
            return JsonResponse({'status': 'error', 'message': 'İdareci adı zorunlu.'})
        if Idareci.objects.filter(ad=ad).exists():
            return JsonResponse({'status': 'error', 'message': 'Bu ad ile idareci zaten var.'})
        Idareci.objects.create(ad=ad)
        messages.success(request, f'{ad} isimli İdareci başarıyla eklendi.')
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

@csrf_exempt
def idareci_guncelle(request, pk):
    if request.method == 'POST':
        data = json.loads(request.body)
        ad = data.get('ad', '').strip()
        if not ad:
            return JsonResponse({'status': 'error', 'message': 'İdareci adı zorunlu.'})
        idareci = Idareci.objects.get(pk=pk)
        idareci.ad = ad
        idareci.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

@csrf_exempt
def kurum_toggle_aktif(request, pk):
    if request.method == 'POST':
        try:
            kurum = Kurum.objects.get(pk=pk)
            kurum.aktif = not kurum.aktif
            kurum.save()
            messages.success(request, f"{kurum.ad} kurumunun durumu {'aktif' if kurum.aktif else 'pasif'} olarak güncellendi.")
            return JsonResponse({'status': 'success', 'aktif': kurum.aktif})
        except Kurum.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Kurum bulunamadı.'})
    return JsonResponse({'status': 'error'})

@csrf_exempt
def ust_birim_toggle_aktif(request, pk):
    if request.method == 'POST':
        try:
            ust = UstBirim.objects.get(pk=pk)
            ust.aktif = not ust.aktif
            ust.save()
            messages.success(request, f"{ust.ad} üst biriminin durumu {'aktif' if ust.aktif else 'pasif'} olarak güncellendi.")
            return JsonResponse({'status': 'success', 'aktif': ust.aktif})
        except UstBirim.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'İdare bulunamadı.'})
    return JsonResponse({'status': 'error'})

@csrf_exempt
def idareci_toggle_aktif(request, pk):
    if request.method == 'POST':
        try:
            idareci = Idareci.objects.get(pk=pk)
            idareci.aktif = not idareci.aktif
            idareci.save()
            messages.success(request, f"{idareci.ad} idarecisinin durumu {'aktif' if idareci.aktif else 'pasif'} olarak güncellendi.")
            return JsonResponse({'status': 'success', 'aktif': idareci.aktif})
        except Idareci.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'İdareci bulunamadı.'})
    return JsonResponse({'status': 'error'})

def kullanici_ara(request):
    username = request.GET.get('username', '').strip()
    try:
        user = User.objects.get(Username=username)
        data = {
            "username": user.Username,
            "full_name": user.FullName
        }
        return JsonResponse({"status": "success", "data": data})
    except User.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Kullanıcı bulunamadı."})