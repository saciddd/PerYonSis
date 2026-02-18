from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Cihaz, CihazKullanici
from .forms import CihazForm
from .ZKBaglanti import (
    list_users, add_user, delete_user,
    get_attendance, get_storage_status_info, sync_device_time,
    ZKConnectionError, ZKUser
)

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
        # Cihaz saatini eşitle
        sync_device_time(ip=cihaz.ip, port=cihaz.port)

        device_users = list_users(ip=cihaz.ip, port=cihaz.port)
        
        created_count = 0
        updated_count = 0

        # Cihazdaki kullanıcıları DB'ye ekle/güncelle
        for u in device_users:
            # Önce UID ile kontrol et
            # User ID ya da Card ID benzersizliğini de kontrol edebiliriz ama
            # burada temel anahtar UID (cihaz içindeki ID).
            
            # Eğer kullanıcı veritabanında varsa, İSMİNİ GÜNCELLEME.
            # Sadece yeni eklenenlerin ismini cihazdan al.
            
            user_inst, created = CihazKullanici.objects.get_or_create(
                cihaz=cihaz,
                uid=u.uid,
                defaults={
                    'user_id': u.user_id,
                    'name': u.name,
                    'card': u.card,
                    'privilege': u.privilege
                }
            )

            if created:
                created_count += 1
            else:
                # Kayıt varsa, isim HARİÇ diğer alanları güncelle (yetki, kart no, vb.)
                # Ancak kullanıcı 'ilgili kart numarası dbde varsa ismini değiştirmesin' dedi.
                # UID zaten eşleşti.
                
                changed = False
                if user_inst.user_id != u.user_id:
                    user_inst.user_id = u.user_id
                    changed = True
                if user_inst.card != u.card:
                    user_inst.card = u.card
                    changed = True
                if user_inst.privilege != u.privilege:
                    user_inst.privilege = u.privilege
                    changed = True
                
                # İsim güncellemesi YAPMIYORUZ.
                
                if changed:
                    user_inst.save()
                    updated_count += 1
        
        messages.success(request, f'Senkronizasyon tamamlandı. {created_count} yeni kullanıcı eklendi, {updated_count} kullanıcı güncellendi.')
    except Exception as e:
        messages.error(request, f'Senkronizasyon hatası: {str(e)}')

    return redirect(f'/cardcontrol/kapi-yonetimi/?cihaz_id={cihaz.id}')


def cihaz_loglari(request):
    cihazlar = Cihaz.objects.all()
    selected_cihaz = None
    logs = []
    storage_info = None
    
    cihaz_id = request.GET.get('cihaz_id')
    if cihaz_id:
        selected_cihaz = get_object_or_404(Cihaz, id=cihaz_id)
        try:
            # 1. Saat Eşitleme
            sync_device_time(ip=selected_cihaz.ip, port=selected_cihaz.port)
            
            # 2. Depolama Durumu
            storage_info = get_storage_status_info(ip=selected_cihaz.ip, port=selected_cihaz.port)
            
            # 3. Logları Çek (Timeout artırıldı: 30sn)
            # Log sayısı çoksa bu işlem uzun sürer.
            device_logs = get_attendance(ip=selected_cihaz.ip, port=selected_cihaz.port, timeout=30)
            
            # Logları tersten sırala (en yeni en üstte)
            device_logs.reverse()
            
            # 4. Kullanıcı isimlerini eşleştir
            # DB'den bu cihazın kullanıcılarını çek: user_id -> name
            db_users = CihazKullanici.objects.filter(cihaz=selected_cihaz)
            user_map = {u.user_id: u.name for u in db_users}
            
            logs = []
            for log in device_logs:
                # Log nesnesi muhtemelen bir obje, attribute olarak ekleyemeyebiliriz (slot vs varsa).
                # Bu yüzden dict'e çevirelim veya wrapper kullanalım.
                # pyzk log nesnesinin user_id. timestamp, status, punch özellikleri var.
                
                log_user_id = getattr(log, 'user_id', '')
                user_name = user_map.get(str(log_user_id), 'Bilinmeyen')
                
                logs.append({
                    'user_id': log_user_id,
                    'timestamp': log.timestamp,
                    'status': log.status,
                    'punch': log.punch,
                    'user_name': user_name
                })
            
            messages.success(request, f"{len(logs)} adet kayıt çekildi.")
            
        except Exception as e:
            messages.error(request, f"Veri çekme hatası: {str(e)}")

    return render(request, 'cardcontrol/cihaz_loglari.html', {
        'cihazlar': cihazlar,
        'selected_cihaz': selected_cihaz,
        'logs': logs,
        'storage_info': storage_info
    })
