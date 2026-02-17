from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Cihaz, CihazKullanici
from .forms import CihazForm
from .ZKBaglanti import list_users, add_user, delete_user, ZKConnectionError, ZKUser

def cihaz_list(request):
    cihazlar = Cihaz.objects.all()
    if request.method == 'POST':
        form = CihazForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cihaz başarıyla eklendi.')
            return redirect('cardcontrol:cihaz_list')
    else:
        form = CihazForm()
    
    return render(request, 'cardcontrol/cihaz_list.html', {'cihazlar': cihazlar, 'form': form})

def cihaz_sil(request, cihaz_id):
    cihaz = get_object_or_404(Cihaz, id=cihaz_id)
    cihaz.delete()
    messages.success(request, 'Cihaz silindi.')
    return redirect('cardcontrol:cihaz_list')

def kapi_yonetimi(request):
    cihazlar = Cihaz.objects.all()
    selected_cihaz = None
    users = []
    
    cihaz_id = request.GET.get('cihaz_id')
    if cihaz_id:
        selected_cihaz = get_object_or_404(Cihaz, id=cihaz_id)
        users = CihazKullanici.objects.filter(cihaz=selected_cihaz).order_by('name')

    return render(request, 'cardcontrol/kapi_yonetimi.html', {
        'cihazlar': cihazlar,
        'selected_cihaz': selected_cihaz,
        'users': users
    })

def cihaz_kullanici_ekle(request, cihaz_id):
    cihaz = get_object_or_404(Cihaz, id=cihaz_id)
    if request.method == 'POST':
        name = request.POST.get('name')
        card_id = request.POST.get('card_id')
        
        if not name or not card_id:
            messages.error(request, 'Ad Soyad ve Kart ID zorunludur.')
            return redirect(f'/cardcontrol/kapi-yonetimi/?cihaz_id={cihaz.id}')

        try:
            # 1. Cihaza ekle
            zk_user = add_user(
                name=name,
                card_id=card_id,
                ip=cihaz.ip,
                port=cihaz.port
            )
            
            # 2. Veritabanına kaydet (Eğer zaten yoksa)
            # ZKBaglanti'daki add_user yeni bir UID üretir ve döndürür.
            CihazKullanici.objects.create(
                cihaz=cihaz,
                uid=zk_user.uid,
                user_id=zk_user.user_id,
                name=zk_user.name,
                card=zk_user.card,
                privilege=zk_user.privilege
            )
            messages.success(request, f'{name} cihaza ve veritabanına eklendi.')
            
        except Exception as e:
            messages.error(request, f'Hata oluştu: {str(e)}')
    
    return redirect(f'/cardcontrol/kapi-yonetimi/?cihaz_id={cihaz.id}')

def cihaz_kullanici_sil(request, cihaz_id):
    cihaz = get_object_or_404(Cihaz, id=cihaz_id)
    if request.method == 'POST':
        kullanici_db_id = request.POST.get('kullanici_db_id')
        kullanici = get_object_or_404(CihazKullanici, id=kullanici_db_id, cihaz=cihaz)
        
        try:
            # 1. Cihazdan sil
            delete_user(
                uid=kullanici.uid,
                user_id=kullanici.user_id,
                ip=cihaz.ip,
                port=cihaz.port
            )
            
            # 2. Veritabanından sil
            kullanici.delete()
            messages.success(request, 'Kullanıcı silindi.')
            
        except Exception as e:
            messages.error(request, f'Hata oluştu: {str(e)}')

    return redirect(f'/cardcontrol/kapi-yonetimi/?cihaz_id={cihaz.id}')

def cihaz_sync(request, cihaz_id):
    """Cihazdaki kullanıcıları çeker ve DB ile eşitler."""
    cihaz = get_object_or_404(Cihaz, id=cihaz_id)
    try:
        device_users = list_users(ip=cihaz.ip, port=cihaz.port)
        
        # Cihazdaki kullanıcıları DB'ye ekle/güncelle
        for u in device_users:
            CihazKullanici.objects.update_or_create(
                cihaz=cihaz,
                uid=u.uid,
                defaults={
                    'user_id': u.user_id,
                    'name': u.name,
                    'card': u.card,
                    'privilege': u.privilege
                }
            )
        
        # Opsiyonel: Cihazda olmayıp DB'de olanları silebiliriz veya işaretleyebiliriz.
        # Şimdilik sadece cihaz -> DB yönünde ekleme/güncelleme yapıyoruz.
        
        messages.success(request, f'Senkronizasyon tamamlandı. Toplam {len(device_users)} kullanıcı bulundu.')
    except Exception as e:
        messages.error(request, f'Senkronizasyon hatası: {str(e)}')

    return redirect(f'/cardcontrol/kapi-yonetimi/?cihaz_id={cihaz.id}')
