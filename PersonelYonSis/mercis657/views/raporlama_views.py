from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from PersonelYonSis.views import get_user_permissions
from ..models import Bildirim, Kurum, PersonelListesi, UserBirim, Birim, Personel, PersonelListesiKayit, Mesai, ResmiTatil, Mesai_Tanimlari, Izin, UstBirim
from PersonelYonSis.models import User
import calendar # calendar modülü eklendi
import json
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db import transaction
from django.db.models import Count, Prefetch
from decimal import Decimal
from mercis657.utils import hesapla_fazla_mesai


def raporlama(request):
    bildirimler_by_birim = None
    donem = None
    kurum = None
    idare = None
    excel_url = None
    error_message = None
    info_message = None
    birimler_json = None
    birimler = Birim.objects.all()
    kurumlar = Kurum.objects.all()
    idareler = UstBirim.objects.all()

    # Form yerine GET parametrelerini doğrudan al
    donem_str = request.GET.get('donem')
    kurum = request.GET.get('kurum')
    idare = request.GET.get('idare')
    durum = request.GET.get('durum')  # "1", "0" veya ""

    toplam_kayit = 0

    # Dönem parametresi varsa veriyi çek
    if donem_str:
        try:
            # 'YYYY-MM' formatındaki stringi ayın ilk günü olan date objesine çevir
            donem = datetime.strptime(donem_str, "%Y-%m").date()

            bildirimler_query = Bildirim.objects.select_related(
                'Personel',
                'PersonelListesi__birim',
            ).filter(
                 DonemBaslangic=donem
            )

            if kurum:
                bildirimler_query = bildirimler_query.filter(
                    PersonelListesi__birim__KurumAdi=kurum
                )
            if idare:
                bildirimler_query = bildirimler_query.filter(
                    PersonelListesi__birim__IdareAdi=idare
                )

            if durum == "1":
                bildirimler_query = bildirimler_query.filter(OnayDurumu=1)
            elif durum == "0":
                bildirimler_query = bildirimler_query.filter(OnayDurumu=0)

            # Birimlere göre grupla ve her birim altındaki çalışmaları Prefetch ile çek
            #            birim_ids_with_calisma = bildirimler_query.values_list('PersonelListesi__birim', flat=True).distinct()
#
#            birimler_with_bildirimler = Birim.objects.filter(BirimID__in=birim_ids_with_calisma).prefetch_related(
#                Prefetch(
#                    'bildirim_set',
#                    queryset=bildirimler_query.order_by('Personel__PersonelName'),
#                    to_attr='bildirimler'
#                )
#            ).order_by('BirimAdi')
#                # Birimleri JSON'a çevir
#            birimler_json = json.dumps([
#                {'BirimID': b.BirimID, 'BirimAdi': b.BirimAdi} for b in birimler_with_bildirimler
#            ])
#            bildirimler_by_birim = []
#            for birim in birimler_with_bildirimler:
#                if birim.bildirimler:
#                    kesinlesmis = sum(1 for c in birim.bildirimler if c.OnayDurumu == 1)
#                    beklemede = sum(1 for c in birim.bildirimler if c.OnayDurumu == 0)
#                    bildirimler_by_birim.append({
#                        'birim': birim,
#                        'bildirimler': birim.bildirimler,
#                        'personel_sayisi': len(set([c.Personel.PersonelID for c in birim.bildirimler])),
#                        'kesinlesmis_sayisi': kesinlesmis,
#                        'beklemede_sayisi': beklemede,
#                    })
            # Bildirimleri çek ve PersonelListesi__birim'e göre grupla (Birim modelinde doğrudan bildirim_set yok)
            birim_ids_with_calisma = list(bildirimler_query.values_list('PersonelListesi__birim', flat=True).distinct())

            birimler_with_bildirimler = Birim.objects.filter(BirimID__in=birim_ids_with_calisma).order_by('BirimAdi')

            # Bildirimleri sıralı çek ve Python tarafında birim id'lerine göre grupla
            bildirimler_list = list(bildirimler_query.order_by('Personel__PersonelName').select_related('Personel', 'PersonelListesi'))
            bildirimler_map = {}
            for b in bildirimler_list:
                try:
                    birim_obj = getattr(b.PersonelListesi, 'birim', None)
                    birim_id = birim_obj.BirimID if birim_obj is not None else None
                except Exception:
                    birim_id = None
                if birim_id is None:
                    continue
                bildirimler_map.setdefault(birim_id, []).append(b)

            # Birimleri JSON'a çevir
            birimler_json = json.dumps([
                {'BirimID': b.BirimID, 'BirimAdi': b.BirimAdi} for b in birimler_with_bildirimler
            ])

            bildirimler_by_birim = []
            for birim in birimler_with_bildirimler:
                items = bildirimler_map.get(birim.BirimID, [])
                if items:
                    kesinlesmis = sum(1 for c in items if c.OnayDurumu == 1)
                    beklemede = sum(1 for c in items if c.OnayDurumu == 0)
                    bildirimler_by_birim.append({
                        'birim': birim,
                        'bildirimler': items,
                        'personel_sayisi': len(set([getattr(c.Personel, 'PersonelID', None) for c in items])),
                        'kesinlesmis_sayisi': kesinlesmis,
                        'beklemede_sayisi': beklemede,
                    })

            toplam_kayit = sum(len(birim['bildirimler']) for birim in bildirimler_by_birim)

            # Excel indirme linki oluştur
            if bildirimler_by_birim:
                 excel_url = reverse('hizmet_sunum_app:export_raporlama_excel')
                 excel_url += f'?donem={donem.strftime("%Y-%m")}'

                 if kurum:
                     excel_url += f'&kurum={kurum}'
                 if durum:
                     excel_url += f'&durum={durum}'
                 if idare:
                     excel_url += f'&idare={idare}'

            if toplam_kayit == 0:
                 info_message = "Seçilen dönem ve kuruma ait hizmet sunum çalışması bulunamadı."

        except ValueError:
             error_message = "Geçersiz dönem formatı seçildi."
        except Exception as e:
            # Hata yönetimi
            error_message = f"Rapor oluşturulurken bir hata oluştu: {str(e)}"
            print(f"Raporlama Hatası: {e}") # Konsola yazdır (geliştirme için)
    else:
        # İlk sayfa yüklemesi veya dönem seçilmemişse
        info_message = "Lütfen bir dönem ve isteğe bağlı kriterlerinizi seçerek raporlayın."

    user_permissions = get_user_permissions(request.user)
    context = {
        # 'form': form, # Form kaldırıldı
        'bildirimler_by_birim': bildirimler_by_birim,
        'birimler': birimler, # Kurum seçimi için tüm birimleri geçiyoruz (kurum listesi çekmek için)
        'birimler_json': birimler_json,
        'kurumlar': kurumlar, # Kurum seçimi için tüm kurumları geçiyoruz
        'idareler': idareler,
        'selected_donem': donem_str, # Şablona dönemin string halini gönderelim ki selectbox'ta seçili kalsın
        'selected_kurum': kurum,
        'selected_idare': idare,
        'selected_durum': durum,
        'excel_url': excel_url,
        # 'is_form_valid': is_form_valid, # Form kaldırıldı
        'error_message': error_message,
        'info_message': info_message,
        'toplam_kayit': toplam_kayit,
        'user_permissions': user_permissions,
    }
    return render(request, 'mercis657/raporlama.html', context)

def export_raporlama_excel(request):
    donem_str = request.GET.get('donem')
    kurum = request.GET.get('kurum')
    idare = request.GET.get('idare')

    if not donem_str:
        messages.error(request, "Lütfen bir dönem seçin.")
        return redirect('hizmet_sunum_app:raporlama')

    try:
        donem = datetime.strptime(donem_str, "%Y-%m").date()
    except ValueError:
         messages.error(request, "Geçersiz dönem formatı.")
         return redirect('hizmet_sunum_app:raporlama')

    bildirimler_query = HizmetSunumCalismasi.objects.select_related(
        'PersonelId',
        'CalisilanBirimID'
    ).filter(
        Donem=donem
    )

    if kurum:
        bildirimler_query = bildirimler_query.filter(
            CalisilanBirimID__KurumAdi=kurum
        )
    if idare:
        bildirimler_query = bildirimler_query.filter(
            CalisilanBirimID__IdareAdi=idare
        )

    bildirimler = bildirimler_query.order_by(
        'CalisilanBirimID__BirimAdi',
        'PersonelId__PersonelSoyadi',
        'PersonelId__PersonelAdi',
        'HizmetBaslangicTarihi'
    )

    if not bildirimler.exists():
        messages.warning(request, "Seçilen filtreye uygun veri bulunamadı.")
        return redirect('hizmet_sunum_app:raporlama')

    # Şablon dosyasını aç
    template_path = os.path.join(settings.STATIC_ROOT, 'excels', 'HizmetSunumSablon.xlsx')

    # Şablon dosyasının varlığını kontrol et
    if not os.path.exists(template_path):
         messages.error(request, f"Excel şablon dosyası bulunamadı: {template_path}")
         return redirect('hizmet_sunum_app:raporlama')

    wb = openpyxl.load_workbook(template_path)
    ws = wb.active

    # Verileri yaz (2. satırdan başla)
    row = 2
    for calisma in bildirimler:
        personel = calisma.PersonelId
        birim = calisma.CalisilanBirimID

        ws.cell(row=row, column=1, value=personel.TCKimlikNo)
        ws.cell(row=row, column=2, value=personel.PersonelAdi)
        ws.cell(row=row, column=3, value=personel.PersonelSoyadi)
        ws.cell(row=row, column=4, value=calisma.HizmetBaslangicTarihi)
        ws.cell(row=row, column=5, value=calisma.HizmetBitisTarihi)
        ws.cell(row=row, column=6, value=birim.BirimAdi)
        ws.cell(row=row, column=7, value=calisma.OzelAlanKodu)
        ws.cell(row=row, column=10, value=birim.KurumAdi)
        ws.cell(row=row, column=11, value=birim.IdareAdi)
        # Sütun eklenirse devam ettir
        if calisma.Sorumlu:
            sorumlu_alan = None
            if calisma.OzelAlanKodu:
                try:
                    sorumlu_alan = HizmetSunumAlani.objects.get(AlanKodu=calisma.OzelAlanKodu)
                except HizmetSunumAlani.DoesNotExist:
                    sorumlu_alan = None
            # SorumluAtanabilir True ise 1, False ise 0 yaz
            if sorumlu_alan is not None and hasattr(sorumlu_alan, "SorumluAtanabilir"):
                ws.cell(row=row, column=8, value=1 if sorumlu_alan.SorumluAtanabilir else 0)
            else:
                ws.cell(row=row, column=8, value="")
        else:
            ws.cell(row=row, column=8, value=0)
        ws.cell(row=row, column=9, value=1 if calisma.Sertifika else 0)
        row += 1

    # Excel dosyasını kaydet
    output = BytesIO()
    wb.save(output)
    output.seek(0)

    # HTTP response oluştur
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    file_name = f"hizmet_sunum_rapor_{donem_str}.xlsx"
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    return response
