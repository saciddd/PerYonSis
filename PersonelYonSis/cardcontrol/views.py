from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Cihaz, CihazKullanici, CihazLog
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

def cihaz_guncelle(request, cihaz_id):
    cihaz = get_object_or_404(Cihaz, id=cihaz_id)
    if request.method == 'POST':
        form = CihazForm(request.POST, instance=cihaz)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cihaz güncellendi.')
        else:
            messages.error(request, 'Güncelleme hatası.')
    return redirect('cardcontrol:cihaz_list')

def kapi_yonetimi(request):
    cihazlar = Cihaz.objects.all()
    selected_cihaz = None
    users = []
    
    cihaz_id = request.GET.get('cihaz_id')
    query = request.GET.get('q', '')
    
    if cihaz_id:
        selected_cihaz = get_object_or_404(Cihaz, id=cihaz_id)
        qs = CihazKullanici.objects.filter(cihaz=selected_cihaz).order_by('name')
        
        if query:
            qs = qs.filter(
                Q(name__icontains=query) | 
                Q(user_id__icontains=query) | 
                Q(card__icontains=query)
            )
            
        paginator = Paginator(qs, 20) # 20 per page
        page_number = request.GET.get('page')
        users = paginator.get_page(page_number)

    return render(request, 'cardcontrol/kapi_yonetimi.html', {
        'cihazlar': cihazlar,
        'selected_cihaz': selected_cihaz,
        'users': users,
        'query': query
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
    fetch_new = request.GET.get('fetch', '0') == '1' # Cihazdan veri çekme parametresi
    
    # Filtre parametreleri
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    user_id_filter = request.GET.get('user_id')
    name_filter = request.GET.get('name')
    
    from datetime import datetime
    
    if cihaz_id:
        selected_cihaz = get_object_or_404(Cihaz, id=cihaz_id)
        
        if fetch_new:
            try:
                # 1. Saat Eşitleme
                sync_device_time(ip=selected_cihaz.ip, port=selected_cihaz.port)
                
                # 2. Depolama Durumu (Eğer fetch istendiyse)
                storage_info = get_storage_status_info(ip=selected_cihaz.ip, port=selected_cihaz.port)
                
                # 3. Logları Çek
                device_logs = get_attendance(ip=selected_cihaz.ip, port=selected_cihaz.port, timeout=30)
                
                # 4. DB'ye Kaydet (Bulk Create Ignore Conflicts for efficiency if possible, but SQLite needs careful handling)
                # Basit döngü ile yapalım, get_or_create yavaş olabilir ama güvenli.
                # User ID -> DB ID mapping gerek yok, sadece user_id string olarak yeterli.
                
                # Django'nun bulk_create ignore_conflicts=True (SQLite >= 3.24) destekler.
                log_objects = []
                existing_keys = set(CihazLog.objects.filter(cihaz=selected_cihaz).values_list('user_id', 'timestamp'))
                # Not: timestamp datetime objesi, timezone aware/naive dikkat etmek lazım. 
                # ZK library naive dönerse, settings TIME_ZONE'a göre aware yapmak gerekebilir.
                
                from django.utils.timezone import make_aware
                import pytz
                
                for log in device_logs:
                    # log.timestamp naive ise aware yapalım
                    ts = log.timestamp
                    if ts.tzinfo is None:
                         ts = make_aware(ts)
                    
                    key = (str(log.user_id), ts) # Key kontrolü
                    if key not in existing_keys:
                        log_objects.append(CihazLog(
                            cihaz=selected_cihaz,
                            uid=int(getattr(log, 'uid', 0) or 0),
                            user_id=str(log.user_id),
                            timestamp=ts,
                            status=int(log.status),
                            verification=int(log.punch)
                        ))
                        existing_keys.add(key) 
                
                if log_objects:
                    CihazLog.objects.bulk_create(log_objects, batch_size=500)
                    messages.success(request, f"{len(log_objects)} yeni kayıt veritabanına eklendi.")
                else:
                    messages.info(request, "Yeni kayıt bulunamadı.")

            except Exception as e:
                messages.error(request, f"Veri çekme hatası: {str(e)}")

        # DB'den Sorgula
        qs = CihazLog.objects.filter(cihaz=selected_cihaz).order_by('-timestamp')
        
        if start_date:
            qs = qs.filter(timestamp__gte=start_date)
        if end_date:
            qs = qs.filter(timestamp__lte=end_date)
            
        if user_id_filter:
            qs = qs.filter(user_id__icontains=user_id_filter)
            
        if name_filter:
            # İsimden user_id bulmamız lazım
            matching_user_ids = CihazKullanici.objects.filter(
                cihaz=selected_cihaz, 
                name__icontains=name_filter
            ).values_list('user_id', flat=True)
            qs = qs.filter(user_id__in=matching_user_ids)

        # Pagination
        paginator = Paginator(qs, 50) # 50 per page
        page_number = request.GET.get('page')
        logs_page = paginator.get_page(page_number)
        
        # User Name Mapping for current page
        page_user_ids = [log.user_id for log in logs_page]
        db_users = CihazKullanici.objects.filter(cihaz=selected_cihaz, user_id__in=page_user_ids)
        user_map = {u.user_id: u.name for u in db_users}
        
        # Log objelerine isim ekle (template'de kullanmak için)
        for log in logs_page:
            log.user_name = user_map.get(log.user_id, 'Bilinmeyen')
        
        logs = logs_page # Template variable name compatibility

    return render(request, 'cardcontrol/cihaz_loglari.html', {
        'cihazlar': cihazlar,
        'selected_cihaz': selected_cihaz,
        'logs': logs,
        'storage_info': storage_info
    })
