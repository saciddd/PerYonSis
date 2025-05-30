from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from .forms import LoginForm, ScheduleForm
from .filemaker_api import check_login, get_schedule_data, get_mesai_tanimlari, update_schedule_data, refresh_session
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.decorators.http import require_POST
from datetime import datetime, timedelta
from calendar import monthrange
import calendar
import json
from django.conf import settings

@csrf_exempt
def m657_login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            authorized_units = check_login(username, password)
            
            if authorized_units:
                formatted_units = []
                for unit in authorized_units:
                    unit_data = {
                        'id': str(unit['ID']),
                        'name': str(unit['Name'])
                    }
                    formatted_units.append(unit_data)
                
                # Get current year and ±1 years
                current_year = datetime.now().year
                years = range(current_year - 1, current_year + 1)
                
                return render(request, 'schedule.html', {
                    'form': ScheduleForm(),
                    'authorized_units': formatted_units,
                    'tc': username,
                    'years': years
                })
            else:
                return HttpResponse("Invalid login credentials")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

@csrf_exempt
def m657_schedule_view(request):
    if request.method == 'POST':
        try:
            unit_id = request.POST.get('unit_id')
            start_date = datetime.strptime(request.POST.get('start_date'), '%Y-%m-%d').strftime('%m-%d-%Y')
            end_date = datetime.strptime(request.POST.get('end_date'), '%Y-%m-%d').strftime('%m-%d-%Y')
            
            schedule_data = get_schedule_data(unit_id, start_date, end_date)
            mesai_tanimlari = get_mesai_tanimlari()
            
            return render(request, 'schedule_edit.html', {
                'schedule_data': schedule_data,
                'mesai_tanimlari': mesai_tanimlari,
                'dates': [start_date, end_date]
            })
        except Exception as e:
            print(f"Error in schedule_view: {str(e)}")  # Hata ayıklama için log
            return HttpResponse(f"Error: {str(e)}")
    return redirect('login_view')

@csrf_exempt
def m657_update_schedule(request):
    if request.method == 'POST':
        record_id = request.POST.get('record_id')
        new_value = request.POST.get('value')
        success = update_schedule_data(record_id, new_value)
        return JsonResponse({'success': success})
    return JsonResponse({'success': False})

@csrf_protect
def m657_schedule_edit(request):
    try:
        unit_id = request.GET.get('unit_id')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        # Tarihleri datetime objesine çevir
        start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
        end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
        
        # FileMaker için tarihleri formatla (MM-DD-YYYY)
        fm_start_date = start_datetime.strftime('%m-%d-%Y')
        fm_end_date = end_datetime.strftime('%m-%d-%Y')
        
        print(f"Start date: {fm_start_date}, End date: {fm_end_date}")
        
        # FileMaker'dan verileri al
        raw_data = get_schedule_data(unit_id, fm_start_date, fm_end_date)
        mesai_tanimlari = get_mesai_tanimlari()
        
        # Personel bazında veriyi düzenle
        personel_data = {}
        for record in raw_data:
            name = record['Name']
            if name not in personel_data:
                personel_data[name] = {
                    'PersonelID': record['ID'],
                    'ListeSirasi': record['ListeSirasi'],  # Yeni alan
                    'PersonelAdiSoyadi': name,
                    'PersonelAciklama': record['PersonelAciklama'],  # Yeni alan
                    'mesai_data': {}
                }
            
            # Tarihi datetime objesine çevir
            record_date = datetime.strptime(record['Date'], '%m/%d/%Y')
            # Başlangıç tarihinden itibaren kaçıncı gün olduğunu hesapla
            day_number = (record_date - start_datetime).days + 1
            
            personel_data[name]['mesai_data'][day_number] = {
                'id': record['ID'],  # Mesai kaydının ID'si
                'value': record['Data']  # Mesai verisi
            }
        
        # Tarih aralığındaki gün sayısını hesapla
        total_days = (end_datetime - start_datetime).days + 1
        
        # Haftasonlarını belirle
        weekends = []
        current_date = start_datetime
        for day in range(total_days):
            if current_date.weekday() >= 5:  # 5: Cumartesi, 6: Pazar
                weekends.append(day + 1)  # 1'den başlayan gün numarası
            current_date += timedelta(days=1)
        IZIN_TURLERI = [
                        "Yıllık İzin", "İdari İzin", "Sendika İzni", "Resmi Tatil", 
                        "Sağlık Raporu", "Heyet Raporu", "Hastanede Yatış", 
                        "Şua İzni", "Refakat İzni", "Babalık İzni", "Ölüm İzni", "Evlilik İzni", "D. Öncesi", "D. Sonrası", "Ücretsiz İzin", "Mazeret İzni", "Görevlendirme", "Eğitim", "Emeklilik", "Ayrılış", "Başlangıç", "Atama Öncesi"
                        ]
        context = {
            'personeller': list(personel_data.values()),
            'mesai_tanimlari': mesai_tanimlari,
            'day_nums': range(1, total_days + 1),
            'weekends': weekends,
            'start_date': start_date,
            'end_date': end_date,
            'IZIN_TURLERI': IZIN_TURLERI
        }
        print(context['weekends'])       
        return render(request, 'schedule_edit.html', context)
        
    except Exception as e:
        print(f"Schedule edit error: {str(e)}")
        import traceback
        print("Full traceback:", traceback.format_exc())
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })

@csrf_protect 
def m657_cizelge_kaydet(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
        
    try:
        data = json.loads(request.body)
        tc = request.POST.get('tc')
        
        # Tek bir kayıt için gelen veriyi işle
        for key, change in data.items():
            record_id = change['id']
            updated_data = change['value']
            
            try:
                success = update_schedule_data(
                    record_id=record_id,
                    updated_data=updated_data,
                    tc=tc
                )
                
                if not success:
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Kayıt güncellenemedi: {record_id}'
                    })
                    
            except Exception as e:
                print(f"Kayıt güncelleme hatası: {e}, Kayıt: {change}")
                return JsonResponse({
                    'status': 'error',
                    'message': f'Kayıt güncellenirken hata oluştu: {str(e)}'
                })
                
        return JsonResponse({'status': 'success'})
        
    except Exception as e:
        print(f"Genel hata: {e}")
        return JsonResponse({
            'status': 'error',
            'message': f'İşlem sırasında hata oluştu: {str(e)}'
        })

@require_POST
@csrf_exempt
def m657_refresh_session_view(request):
    tc = request.POST.get('tc')
    password = request.POST.get('password')
    
    if not tc or not password:
        return JsonResponse({'success': False, 'message': 'Eksik bilgi'})
        
    success = refresh_session(tc, password)
    return JsonResponse({'success': success})
