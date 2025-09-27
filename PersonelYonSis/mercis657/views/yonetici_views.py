from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Q
from datetime import date
from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import login_required

from ..models import Birim, PersonelListesi, PersonelListesiKayit, Kurum, UstBirim, Idareci


@login_required
def birim_listeleri(request):
    # 🔹 Dönem parametresi (YYYY/MM)
    selected_donem = request.GET.get("donem", "")
    selected_birim_adi = request.GET.get("birim_adi", "").strip()
    selected_kurum = request.GET.get("kurum", "")
    selected_ust_birim = request.GET.get("ust_birim", "")
    selected_idareci = request.GET.get("idareci", "")

    # 🔹 Dönem listesi: -6 ay ile +2 ay
    today = date.today().replace(day=1)
    donemler = []
    for i in range(-6, 3):
        d = today + relativedelta(months=i)
        value = f"{d.year}/{d.month:02d}"
        label = value
        donemler.append({"value": value, "label": label})

    # 🔹 Sorgu
    queryset = Birim.objects.select_related("Kurum", "UstBirim", "Idareci")

    if selected_birim_adi:
        queryset = queryset.filter(BirimAdi__icontains=selected_birim_adi)
    if selected_kurum:
        queryset = queryset.filter(Kurum_id=selected_kurum)
    if selected_ust_birim:
        queryset = queryset.filter(UstBirim_id=selected_ust_birim)
    if selected_idareci:
        queryset = queryset.filter(Idareci_id=selected_idareci)

    # 🔹 Seçili döneme göre PersonelListesi eşleştir
    yil, ay = None, None
    if selected_donem:
        try:
            yil, ay = map(int, selected_donem.split("/"))
        except:
            yil, ay = None, None

    birimler_data = []
    for idx, birim in enumerate(queryset, start=1):
        liste = None
        personel_sayisi = 0
        created_by = None
        if yil and ay:
            liste = PersonelListesi.objects.filter(birim=birim, yil=yil, ay=ay).first()
            if liste:
                personel_sayisi = PersonelListesiKayit.objects.filter(liste=liste).count()
                created_by = liste.created_by

        birimler_data.append({
            "sira": idx,
            "birim": birim,
            "liste": liste,
            "personel_sayisi": personel_sayisi,
            "created_by": created_by,
        })

    context = {
        "donemler": donemler,
        "selected_donem": selected_donem,
        "birimler_data": birimler_data,
        "kurumlar": Kurum.objects.all(),
        "ust_birimler": UstBirim.objects.all(),
        "idareciler": Idareci.objects.all(),
        "selected_kurum": selected_kurum,
        "selected_ust_birim": selected_ust_birim,
        "selected_idareci": selected_idareci,
        "selected_birim_adi": selected_birim_adi,
    }
    return render(request, "mercis657/birim_listeleri.html", context)
