from datetime import date
from dateutil.relativedelta import relativedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from ..models import Bildirim, PersonelListesi, UserBirim, Birim, Personel, PersonelListesiKayit
from PersonelYonSis.models import User
import calendar # calendar modülü eklendi
import json


def get_donemler():
    """Mevcut aydan -6 ay ile +2 ay arası dönem listesi"""
    today = date.today().replace(day=1)
    donemler = []
    for i in range(-6, 3):
        d = today + relativedelta(months=i)
        value = f"{d.year}/{d.month:02d}"
        label = f"{d.month:02d}/{d.year}" # Görüntülenecek format
        donemler.append({'value': value, 'label': label})
    return donemler


@login_required
def bildirimler(request):
    """Mesai ve İcap bildirimlerini birleşik görüntüler"""
    if not request.user.has_permission("mercis657.view_bildirim"):
        return HttpResponseForbidden("Yetkiniz yok.")

    selected_donem = request.GET.get("donem")
    if not selected_donem:
        today = date.today().replace(day=1)
        selected_donem = f"{today.year}/{today.month:02d}"

    year, month = map(int, selected_donem.split("/"))
    donem_baslangic = date(year, month, 1)

    # Kullanıcının yetkili olduğu birimleri al
    user_birimler = UserBirim.objects.filter(user=request.user).values_list('birim__BirimID', flat=True)
    birimler = Birim.objects.filter(BirimID__in=user_birimler)

    selected_birim_id = request.GET.get("birim_id")
    if selected_birim_id and int(selected_birim_id) in user_birimler:
        selected_birim = get_object_or_404(Birim, BirimID=selected_birim_id)
    else:
        selected_birim = birimler.first() # Varsayılan olarak ilk birimi seç

    personel_data_for_template = []

    if selected_birim:
        # Seçilen döneme ve birime ait PersonelListesi'ni bul
        personel_listesi_obj = PersonelListesi.objects.filter(
            birim=selected_birim, yil=year, ay=month
        ).first()

        if personel_listesi_obj:
            # PersonelListesi'ndeki tüm personelleri al
            personel_kayitlari = PersonelListesiKayit.objects.filter(liste=personel_listesi_obj).select_related('personel')
            personeller_in_list = [pk.personel for pk in personel_kayitlari]

            # Her personel için Bildirim verilerini topla
            for personel in personeller_in_list:
                bildirim = Bildirim.objects.filter(
                    PersonelListesi=personel_listesi_obj,
                    DonemBaslangic=donem_baslangic,
                    SilindiMi=False,
                ).first() # Personel listesi ve dönem başlangıcına göre bildirim
                
                daily_mesai_detay = {}
                daily_icap_detay = {}
                total_normal_fazla_mesai = 0
                total_bayram_fazla_mesai = 0
                total_riskli_normal_fazla_mesai = 0
                total_riskli_bayram_fazla_mesai = 0
                total_normal_icap = 0
                total_bayram_icap = 0
                onay_durumu = 0
                onaylayan_kullanici = None
                onay_tarihi = None
                bildirim_id = None
                calisma_gunleri = 0

                if bildirim:
                    bildirim_id = bildirim.BildirimID
                    onay_durumu = bildirim.OnayDurumu
                    onaylayan_kullanici = bildirim.OnaylayanKullanici
                    onay_tarihi = bildirim.OnayTarihi
                    
                    total_normal_fazla_mesai = bildirim.NormalFazlaMesai
                    total_bayram_fazla_mesai = bildirim.BayramFazlaMesai
                    total_riskli_normal_fazla_mesai = bildirim.RiskliNormalFazlaMesai
                    total_riskli_bayram_fazla_mesai = bildirim.RiskliBayramFazlaMesai
                    total_normal_icap = bildirim.NormalIcap
                    total_bayram_icap = bildirim.BayramIcap

                    if bildirim.MesaiDetay: # JSONField olduğu için kontrol et
                        daily_mesai_detay = {date_str: hours for date_str, hours in bildirim.MesaiDetay.items()}
                    if bildirim.IcapDetay:
                        daily_icap_detay = {date_str: hours for date_str, hours in bildirim.IcapDetay.items()}
                    calisma_gunleri = len(daily_mesai_detay) # Örnek: MesaiDetay dolu gün sayısı

                personel_data_for_template.append({
                    'personel': personel,
                    'bildirim_id': bildirim_id,
                    'normal_fazla_mesai': total_normal_fazla_mesai,
                    'bayram_fazla_mesai': total_bayram_fazla_mesai,
                    'riskli_normal_fazla_mesai': total_riskli_normal_fazla_mesai,
                    'riskli_bayram_fazla_mesai': total_riskli_bayram_fazla_mesai,
                    'toplam_fazla_mesai': total_normal_fazla_mesai + total_bayram_fazla_mesai + 
                                          total_riskli_normal_fazla_mesai + total_riskli_bayram_fazla_mesai,
                    'normal_icap': total_normal_icap,
                    'bayram_icap': total_bayram_icap,
                    'toplam_icap': total_normal_icap + total_bayram_icap,
                    'calisma_gunleri': calisma_gunleri,
                    'onay_durumu': onay_durumu,
                    'onaylayan_kullanici': onaylayan_kullanici,
                    'onay_tarihi': onay_tarihi,
                    'daily_mesai_detay': daily_mesai_detay,
                    'daily_icap_detay': daily_icap_detay,
                })
        
    # Ayın günlerini hazırla
    num_days = calendar.monthrange(year, month)[1]
    days = []
    for day_num in range(1, num_days + 1):
        current_date = date(year, month, day_num)
        is_weekend = current_date.weekday() >= 5  # Cumartesi (5) veya Pazar (6)
        is_holiday = False # ResmiTatil modelinden kontrol edilebilir
        days.append({
            'day_num': day_num,
            'full_date': current_date.strftime("%Y-%m-%d"),
            'is_weekend': is_weekend,
            'is_holiday': is_holiday,
        })

    # Yetki kontrolünü context'e ekle
    can_approve_notifications = request.user.has_permission("mercis657.change_bildirim")

    context = {
        "donemler": get_donemler(),
        "selected_donem": selected_donem,
        "birimler": birimler,
        "selected_birim": selected_birim,
        "personel_data": personel_data_for_template,
        "days": days,
        "current_month_label": calendar.month_name[month], # Ay adını şablonda göstermek için
        "current_year": year,
        "can_approve_notifications": can_approve_notifications,
    }
    return render(request, "mercis657/bildirimler.html", context)


@login_required
def bildirim_olustur(request, liste_id, donem):
    """Yeni bildirim oluştur"""
    if not request.user.has_permission("mercis657.add_bildirim"):
        return HttpResponseForbidden("Yetkiniz yok.")

    liste = get_object_or_404(PersonelListesi, pk=liste_id)
    year, month = map(int, donem.split("/"))
    donem_baslangic = date(year, month, 1)

    # Eğer bu personel listesi ve dönem için zaten bir bildirim varsa
    existing_bildirim = Bildirim.objects.filter(
        PersonelListesi=liste,
        DonemBaslangic=donem_baslangic,
        SilindiMi=False
    ).first()

    if existing_bildirim:
        if existing_bildirim.OnayDurumu == 1: # Onaylanmışsa hata ver
            messages.error(request, f"Bu dönem için zaten onaylanmış bir bildirim mevcut ve güncellenemez.")
        else: # Onaylanmamışsa güncelle
            # Burada fazla mesai ve icap detaylarını yeniden hesaplayıp güncelleyebilirsiniz.
            # Şimdilik varsayılan değerleri bırakıyorum ya da boş JSON ile güncelliyorum.
            existing_bildirim.OlusturanKullanici = request.user
            existing_bildirim.OnayDurumu = 0
            existing_bildirim.OnaylayanKullanici = None
            existing_bildirim.OnayTarihi = None
            existing_bildirim.MesaiDetay = {}
            existing_bildirim.IcapDetay = {}
            # Diğer fazla mesai/icap alanları sıfırlanabilir veya yeniden hesaplanabilir
            existing_bildirim.NormalFazlaMesai = 0
            existing_bildirim.BayramFazlaMesai = 0
            existing_bildirim.RiskliNormalFazlaMesai = 0
            existing_bildirim.RiskliBayramFazlaMesai = 0
            existing_bildirim.NormalIcap = 0
            existing_bildirim.BayramIcap = 0

            existing_bildirim.save()
            messages.info(request, f"Mevcut onaylanmamış bildirim güncellendi.")
        return redirect(reverse("mercis657:bildirimler") + f"?donem={donem}&birim_id={liste.birim.BirimID}")

    # Yeni bildirim oluştur
    bildirim = Bildirim.objects.create(
        PersonelListesi=liste,
        DonemBaslangic=donem_baslangic,
        OlusturanKullanici=request.user,
        OnayDurumu=0,  # Oluşturulduğunda beklemede
        SilindiMi=False,
        MesaiDetay={},
        IcapDetay={},
        NormalFazlaMesai=0,
        BayramFazlaMesai=0,
        RiskliNormalFazlaMesai=0,
        RiskliBayramFazlaMesai=0,
        NormalIcap=0,
        BayramIcap=0,
    )
    messages.success(request, f"Bildirim başarıyla oluşturuldu.")
    return redirect(reverse("mercis657:bildirimler") + f"?donem={donem}&birim_id={liste.birim.BirimID}")


@login_required
def bildirim_onayla(request, bildirim_id):
    """Bildirimi onayla"""
    bildirim = get_object_or_404(Bildirim, pk=bildirim_id, SilindiMi=False)
    if not request.user.has_permission("mercis657.change_bildirim"):
        return HttpResponseForbidden("Yetkiniz yok.")

    if bildirim.OnayDurumu == 1:
        messages.warning(request, "Bildirim zaten onaylanmış.")
        return redirect(reverse("mercis657:bildirimler") + f"?donem={bildirim.DonemBaslangic.year}/{bildirim.DonemBaslangic.month:02d}&birim_id={bildirim.PersonelListesi.birim.BirimID}")

    bildirim.OnayDurumu = 1
    bildirim.OnaylayanKullanici = request.user
    bildirim.OnayTarihi = date.today() # datetime.now() olarak güncellenebilir
    bildirim.save()

    messages.success(request, "Bildirim başarıyla onaylandı.")
    return redirect(reverse("mercis657:bildirimler") + f"?donem={bildirim.DonemBaslangic.year}/{bildirim.DonemBaslangic.month:02d}&birim_id={bildirim.PersonelListesi.birim.BirimID}")


@login_required
def bildirim_sil(request, bildirim_id):
    """Bildirimi soft delete yap"""
    bildirim = get_object_or_404(Bildirim, pk=bildirim_id, SilindiMi=False)
    if not request.user.has_permission("mercis657.delete_bildirim"):
        return HttpResponseForbidden("Yetkiniz yok.")

    if bildirim.OnayDurumu == 1:
        messages.error(request, "Onaylanmış bildirim silinemez.")
        return redirect(reverse("mercis657:bildirimler") + f"?donem={bildirim.DonemBaslangic.year}/{bildirim.DonemBaslangic.month:02d}&birim_id={bildirim.PersonelListesi.birim.BirimID}")


    bildirim.SilindiMi = True
    bildirim.save()
    messages.success(request, "Bildirim başarıyla silindi.")
    return redirect(reverse("mercis657:bildirimler") + f"?donem={bildirim.DonemBaslangic.year}/{bildirim.DonemBaslangic.month:02d}&birim_id={bildirim.PersonelListesi.birim.BirimID}")

@login_required
def bildirim_toplu_olustur(request, birim_id):
    pass

@login_required
def bildirim_toplu_onay(request, birim_id):
    pass

@login_required
def bildirim_tekil_onay(request, bildirim_id):
    pass

@login_required
def bildirim_toplu_onay_kaldir(request, birim_id):
    pass

@login_required
def bildirim_form(request, birim_id):
    pass

@login_required
def bildirim_kilit(request, bildirim_id):
    pass

@login_required
def bildirim_kilit_ac(request, bildirim_id):
    pass

@login_required
def toplu_kilit(request):
    pass

@login_required
def resmi_tatiller(request):
    pass

@login_required
def bildirim_excel(request):
    pass

@login_required
def tatil_ekle(request):
    pass

@login_required
def tatil_duzenle(request):
    pass

@login_required
def tatil_sil(request, tatil_id):
    pass

@login_required
def cizelge_form(request, birim_id):
    pass
