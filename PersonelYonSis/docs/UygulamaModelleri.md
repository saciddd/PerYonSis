# Personel Modeli
- Personel tablosu, personellerin bilgilerini tutar. Personelin telefon numarası farklı bir tablodan alınmakta. Sizin veritabanı kontrolünüz TC kimlik numarası üzerinden yapılabilir. Mesai kayıtlarını yaparken personeli bulmak için get or create yaparız. T.C. kimlik numarası saklamıyorsanız telefon numarası üzerinden ilerleriz.

class Personel(models.Model):
    PersonelID = models.AutoField(primary_key=True)
    PersonelTCKN = models.BigIntegerField(unique=True)
    PersonelName = models.CharField(max_length=100, null=False)
    PersonelSurname = models.CharField(max_length=100, null=False)
    PersonelTitle = models.CharField(max_length=100, null=True)

    def __str__(self):
        return f"{self.PersonelName} ({self.PersonelTCKN})"

# Mesai Modeli
- Burada önemli alanlar MesaiTanim ve MesaiNotu olacaktır. Mesai başlangıcı ve süresini MesaiTanim'dan alacağız. Hangi mavi kod ekibinde görevli olduğunu MesaiNotu'ndan alacağız.

class Mesai(models.Model):
    MesaiID = models.AutoField(primary_key=True)
    Personel = models.ForeignKey('Personel', on_delete=models.CASCADE, related_name='mercis657_mesai_personel')
    MesaiDate = models.DateField(null=False)
    MesaiTanim = models.ForeignKey('Mesai_Tanimlari', on_delete=models.CASCADE, null=True, related_name='mercis657_mesai_tanimlari')
    Izin = models.ForeignKey('Izin', on_delete=models.SET_NULL, null=True, blank=True, related_name='mercis657_mesai_izin')
    Icap = models.BooleanField(default=False)
    OnayDurumu = models.BooleanField(default=True)
    OnayTarihi = models.DateTimeField(null=True, blank=True)
    Onaylayan = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='mercis657_mesai_onaylayan')
    Degisiklik = models.BooleanField(default=False)  # True: Değişiklik var, False: Değişiklik yok
    SistemdekiIzin = models.BooleanField(default=False)  # True: İzin var, False: İzin yok
    MesaiNotu = models.TextField(null=True, blank=True) # Personelin Hangi mavi kod ekibinde görevli olduğunu burada belirtilmekte. Örn: M1, M2
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='mercis657_mesai_ekleyen')
    
    RISKLI_TAM = 'full'
    RISKLI_NOBET = 'nobet'

    RISKLI_CHOICES = [
        (RISKLI_TAM, 'Tam Riskli'),
        (RISKLI_NOBET, 'Nöbet Riskli'),
    ]

    riskli_calisma = models.CharField(
        max_length=10,
        choices=RISKLI_CHOICES,
        default=None,
        null=True,
        blank=True
    )
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['Personel', 'MesaiDate'], name='unique_personel_mesaidate')
        ]
    
    def __str__(self):
        return f"{self.Personel.PersonelName} - {self.MesaiDate}"


### Aşağıdaki modeller size lazım olur mu bilmiyorum, duruma göre inceleyebilirsiniz.

# Birim Modeli

class Birim(models.Model):
    BirimID = models.AutoField(primary_key=True)
    BirimAdi = models.CharField(max_length=100)
    NormalNobetKodu = models.PositiveIntegerField(null=True, blank=True, default=1)
    BayramNobetKodu = models.PositiveIntegerField(null=True, blank=True)
    RiskliNormalNobetKodu = models.PositiveIntegerField(null=True, blank=True)
    RiskliBayramNobetKodu = models.PositiveIntegerField(null=True, blank=True)
    NormalGeceNobetKodu = models.PositiveIntegerField(null=True, blank=True)
    BayramGeceNobetKodu = models.PositiveIntegerField(null=True, blank=True)
    RiskliNormalGeceNobetKodu = models.PositiveIntegerField(null=True, blank=True)
    RiskliBayramGeceNobetKodu = models.PositiveIntegerField(null=True, blank=True)
    Pasif = models.BooleanField(default=False)

    Kurum = models.ForeignKey(Kurum, on_delete=models.SET_NULL, null=True, blank=True)
    UstBirim = models.ForeignKey(UstBirim, on_delete=models.SET_NULL, null=True, blank=True)
    Idareci = models.ForeignKey(Idareci, on_delete=models.SET_NULL, null=True, blank=True)
    Bina = models.ForeignKey(Bina, on_delete=models.SET_NULL, null=True, blank=True) # Burada kampüs bilgisi tutuluyor. Merkez kampüs, Erkiler Çocuk Hastanesi, Geriarti gibi...

    def __str__(self):
        return self.BirimAdi

# Personel Listesi Modeli

- Burada dönem bilgisi saklanıyor. Listeler aylık olarak tutuluyor.

class PersonelListesi(models.Model):
    birim = models.ForeignKey(Birim, on_delete=models.CASCADE, related_name='personel_listeleri')
    yil = models.PositiveIntegerField()
    ay = models.PositiveIntegerField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    aciklama = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('birim', 'yil', 'ay')
        verbose_name = 'Personel Listesi'
        verbose_name_plural = 'Personel Listeleri'

    def __str__(self):
        return f"{self.birim.BirimAdi} - {self.ay}/{self.yil}"


# Personel Listesi Kayıt Modeli

- Bu modelde hangi personelin hangi dönemde hangi birimde görevli olduğu bilgisi tutuluyor.

class PersonelListesiKayit(models.Model):
    liste = models.ForeignKey(PersonelListesi, on_delete=models.CASCADE, related_name='kayitlar')
    personel = models.ForeignKey('Personel', on_delete=models.CASCADE)
    radyasyon_calisani = models.BooleanField(default=False)
    sabit_mesai = models.ForeignKey(SabitMesai, null=True, blank=True, on_delete=models.SET_NULL)
    sira_no = models.PositiveIntegerField(null=True, blank=True)
    is_gunduz_personeli = models.BooleanField(
        default=True,
        help_text="True: Gündüz Personeli, False: Nöbetli Çalışan"
    )

    class Meta:
        unique_together = ('liste', 'personel')
        verbose_name = 'Personel Listesi Kayıt'
        verbose_name_plural = 'Personel Listesi Kayıtları'

    def __str__(self):
        return f"{self.liste} - {self.personel}"