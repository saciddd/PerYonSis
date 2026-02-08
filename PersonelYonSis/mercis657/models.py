from decimal import Decimal
from django.db import models
from datetime import date, timedelta
from django.utils import timezone
from django.utils.timezone import now
from django.contrib.auth import get_user_model

User = get_user_model()

class Kurum(models.Model):
    ad = models.CharField(max_length=100, unique=True)
    aktif = models.BooleanField(default=True)

    def __str__(self):
        return self.ad

class UstBirim(models.Model):
    ad = models.CharField(max_length=100, unique=True)
    aktif = models.BooleanField(default=True)

    def __str__(self):
        return self.ad

class Idareci(models.Model):
    ad = models.CharField(max_length=100, unique=True)
    aktif = models.BooleanField(default=True)

    def __str__(self):
        return self.ad

class Bina(models.Model):
    ad = models.CharField(max_length=100)
    aktif = models.BooleanField(default=True)

    def __str__(self):
        return self.ad

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
    Bina = models.ForeignKey(Bina, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.BirimAdi


class UserBirim(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mercis657_birimleri')
    birim = models.ForeignKey(Birim, on_delete=models.CASCADE, related_name='mercis657_kullanicilari')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'birim')
        verbose_name = "Kullanıcı Birim Yetkisi"
        verbose_name_plural = "Kullanıcı Birim Yetkileri"

    def __str__(self):
        return f"{self.user.username} - {self.birim.BirimAdi}"

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

class SabitMesai(models.Model):
    aralik = models.CharField(max_length=20)
    ara_dinlenme = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    
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

class Personel(models.Model):
    PersonelID = models.AutoField(primary_key=True)
    PersonelTCKN = models.BigIntegerField(unique=True)
    PersonelName = models.CharField(max_length=100, null=False)
    PersonelSurname = models.CharField(max_length=100, null=False)
    PersonelTitle = models.CharField(max_length=100, null=True)

    def __str__(self):
        return f"{self.PersonelName} ({self.PersonelTCKN})"

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
    MesaiNotu = models.TextField(null=True, blank=True)
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

class MesaiYedek(models.Model):
    mesai = models.ForeignKey('Mesai', on_delete=models.CASCADE, related_name='yedekler')
    MesaiTanim = models.ForeignKey('Mesai_Tanimlari', on_delete=models.SET_NULL, null=True, blank=True, related_name='mercis657_mesaiyedek_tanim')
    Izin = models.ForeignKey('Izin', on_delete=models.SET_NULL, null=True, blank=True, related_name='mercis657_mesaiyedek_izin')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='mercis657_mesaiyedek_ekleyen')

    class Meta:
        verbose_name = "Mesai Yedeği"
        verbose_name_plural = "Mesai Yedekleri"

    def __str__(self):
        return f"Yedek: {self.mesai.Personel.PersonelName} - {self.mesai.MesaiDate}"


class Mesai_Tanimlari(models.Model):
    Saat = models.CharField(max_length=11)
    GunduzMesaisi = models.BooleanField(default=False)
    AksamMesaisi = models.BooleanField(default=False)
    GeceMesaisi = models.BooleanField(default=False)
    IseGeldi = models.BooleanField(default=False)
    SonrakiGuneSarkiyor = models.BooleanField(default=False)
    AraDinlenme = models.DecimalField(
        max_digits=4, decimal_places=2, null=True, blank=True,
        help_text="Mesai ara dinlenmesi saat cinsinden (örn: 1.5)"
    )
    GecerliMesai = models.BooleanField(default=True)
    CKYS_BTF_Karsiligi = models.CharField(max_length=100, null=True, blank=True)
    Sure = models.DecimalField(
        max_digits=4, decimal_places=2, null=True, blank=True,
        help_text="Mesai süresi saat cinsinden (örn: 9.5)"
    )
    GeceCalismaSure = models.DecimalField(
        max_digits=4, decimal_places=2,
        null=True, blank=True,
        help_text="20:00–08:00 arası gece çalışma süresi saat cinsinden (örn: 9.5)"
    )
    Renk = models.CharField(max_length=7, null=True)

    def calculate_sure(self):
        """Mesai süresini saat cinsinden (ondalıklı) hesapla."""
        start, end = self.Saat.split(' ')
        start_time = self._parse_time(start)
        end_time = self._parse_time(end)

        if self.SonrakiGuneSarkiyor:
            end_time += timedelta(hours=24)

        total_seconds = (end_time - start_time).total_seconds()
        hours = Decimal(total_seconds / 3600).quantize(Decimal("0.01"))

        # Ara dinlenme çıkar
        if self.AraDinlenme:
            hours -= self.AraDinlenme

        if hours < 0:
            hours = Decimal("0.00")

        self.Sure = hours
        return hours

    def _parse_time(self, time_str):
        """'HH:MM' formatında bir saat dilimini timedelta olarak döndürür."""
        hours, minutes = map(int, time_str.split(':'))
        return timedelta(hours=hours, minutes=minutes)
    
    def save(self, *args, **kwargs):
        self.Sure = self.calculate_sure()
        self.GeceCalismaSure = self.calculate_gece_suresi()
        super().save(*args, **kwargs)

    def calculate_gece_suresi(self):
        """
        20:00–08:00 arası gece çalışma süresini saat cinsinden hesaplar.
        Ara dinlenme hesaba katılmaz.
        """
        if not self.Saat:
            return Decimal("0.00")
            
        start_str, end_str = self.Saat.split(' ')
        start = self._parse_time(start_str)
        end = self._parse_time(end_str)

        # Mesai ertesi güne sarkıyorsa
        if self.SonrakiGuneSarkiyor or end <= start:
            end += timedelta(hours=24)

        # Gece aralıkları
        # 1. Günün başındaki gece (00:00 - 08:00)
        win1_start = timedelta(hours=0)
        win1_end = timedelta(hours=8)

        # 2. Akşam başlayan gece (20:00 - 08:00 ertesi gün => 20 - 32)
        win2_start = timedelta(hours=20)
        win2_end = timedelta(hours=32)

        def overlap(a_start, a_end, b_start, b_end):
            """İki zaman aralığının kesişim süresi (timedelta)"""
            latest_start = max(a_start, b_start)
            earliest_end = min(a_end, b_end)
            return max(timedelta(0), earliest_end - latest_start)

        gece_sure = timedelta(0)

        gece_sure += overlap(start, end, win1_start, win1_end)
        gece_sure += overlap(start, end, win2_start, win2_end)

        hours = Decimal(gece_sure.total_seconds() / 3600).quantize(Decimal("0.01"))

        if hours < 0:
            hours = Decimal("0.00")

        return hours

    def __str__(self):
        return f"{self.Saat} ({self.Sure} saat)"

class Izin(models.Model):
    ad = models.CharField(max_length=100, unique=False)
    kod = models.CharField(max_length=20, unique=False)
    fm_karsiligi = models.CharField(max_length=100)

    def __str__(self):
        return self.ad

class MazeretKaydi(models.Model):
    personel = models.ForeignKey('Personel', on_delete=models.CASCADE, related_name='mazeret_kayitlari')
    baslangic_tarihi = models.DateField()
    bitis_tarihi = models.DateField()
    gunluk_azaltim_saat = models.DecimalField(max_digits=4, decimal_places=2, help_text="Günlük azaltım saati (örn: 3.00, 1.50)")
    aciklama = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "Mazeret Kaydı"
        verbose_name_plural = "Mazeret Kayıtları"

    def __str__(self):
        return f"{self.personel.PersonelName} - {self.baslangic_tarihi} / {self.bitis_tarihi}"

class ResmiTatil(models.Model):
    TatilID = models.AutoField(primary_key=True)
    TatilTarihi = models.DateField()
    Aciklama = models.CharField(max_length=200)
    TatilTipi = models.CharField(
        max_length=10,
        choices=[('TAM', 'Tam Gün'), ('YARIM', 'Yarım Gün')],
        default='TAM'
    )
    BayramMi = models.BooleanField(default=False)
    ArefeMi = models.BooleanField(default=False)

    class Meta:
        ordering = ['TatilTarihi']

    def __str__(self):
        return f"{self.TatilTarihi.strftime('%d.%m.%Y')} - {self.Aciklama}"
    
class Bildirim(models.Model):
    BildirimID = models.AutoField(primary_key=True)
    PersonelListesi = models.ForeignKey(PersonelListesi, on_delete=models.CASCADE, related_name='mercis657_bildirimler')
    Personel = models.ForeignKey('Personel', on_delete=models.CASCADE, related_name='mercis657_bildirimler')
    DonemBaslangic = models.DateField()
    
    # Mesai süreleri (saat cinsinden)
    NormalFazlaMesai = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    BayramFazlaMesai = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    RiskliNormalFazlaMesai = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    RiskliBayramFazlaMesai = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Gece çalışma süreleri (saat cinsinden)
    GeceNormalFazlaMesai = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    GeceBayramFazlaMesai = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    GeceRiskliNormalFazlaMesai = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    GeceRiskliBayramFazlaMesai = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # İcap süreleri (saat cinsinden)
    NormalIcap = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    BayramIcap = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Günlük detaylar
    MesaiDetay = models.JSONField(null=True, blank=True)  # {date: MesaiTanim.Saat}
    IcapDetay = models.JSONField(null=True, blank=True)   # {date: MesaiTanim.Saat}
    
    # İşlem bilgileri
    OlusturanKullanici = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='mercis657_olusturan_bildirimler')
    OlusturmaTarihi = models.DateTimeField(auto_now_add=True)
    OnaylayanKullanici = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='mercis657_onaylayan_bildirimler')
    OnayTarihi = models.DateTimeField(null=True)
    OnayDurumu = models.IntegerField(default=0)  # 0: Bekliyor, 1: Onaylandı
    SilindiMi = models.BooleanField(default=False)
    MutemetKilit = models.BooleanField(default=False)  # Kilit durumu
    MutemetKilitUser = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='mercis657_mutemet_kilit_kullanicilar'
    )  # Kilitleyen kullanıcı
    MutemetKilitTime = models.DateTimeField(null=True, blank=True)  # Kilitleme zamanı

    class Meta:
        # Unique per person and period
        unique_together = [['Personel', 'DonemBaslangic']]

    @property
    def ToplamFazlaMesai(self):
        """Toplam fazla mesai saati"""
        return (self.NormalFazlaMesai + self.BayramFazlaMesai + 
                self.RiskliNormalFazlaMesai + self.RiskliBayramFazlaMesai +
                self.GeceNormalFazlaMesai + self.GeceBayramFazlaMesai +
                self.GeceRiskliNormalFazlaMesai + self.GeceRiskliBayramFazlaMesai)

    @property
    def ToplamIcap(self):
        """Toplam icap saati"""
        return self.NormalIcap + self.BayramIcap

class YarimZamanliCalisma(models.Model):
    personel = models.ForeignKey('Personel', on_delete=models.CASCADE, related_name="yarim_zamanli_donemler")
    baslangic_tarihi = models.DateField()
    bitis_tarihi = models.DateField(null=True, blank=True)
    aciklama = models.TextField(blank=True, null=True)

    # Günlere göre mesai planı
    # {"Pazartesi": [1, 2], "Çarşamba": [5]}  -> Mesai_Tanimlari id listesi
    haftalik_plan = models.JSONField()

    def __str__(self):
        return f"{self.personel} ({self.baslangic_tarihi} - {self.bitis_tarihi or 'devam'})"

class StopKaydi(models.Model):
    mesai = models.ForeignKey('Mesai', on_delete=models.CASCADE, related_name="mercis657_stoplar")
    StopBaslangic = models.TimeField()
    StopBitis = models.TimeField()
    Sure = models.PositiveIntegerField(null=True, blank=True)  # dakika/saat türüne göre
    Aciklama = models.TextField(blank=True,)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def hesapla_sure(self):
        """Stop süresini saat cinsinden hesaplar."""
        if self.StopBaslangic and self.StopBitis:
            if self.StopBitis > self.StopBaslangic:
                delta = self.StopBitis - self.StopBaslangic
            else:
                # Ertesi güne sarkıyorsa
                delta = (self.StopBitis + timedelta(days=1)) - self.StopBaslangic
            self.Sure = int(delta.total_seconds() // 3600)  # saat cinsinden
        else:
            self.Sure = 0
        return self.Sure

    def save(self, *args, **kwargs):
        self.hesapla_sure()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.mesai} stop: {self.Sure} saat"

class IlkListe(models.Model):
    PersonelListesi = models.ForeignKey(
        'PersonelListesi',
        on_delete=models.CASCADE,
        related_name='mercis657_ilk_liste'
    )

    # JSON snapshot
    Veriler = models.JSONField(null=True, blank=True)

    # İşlem bilgileri
    OlusturanKullanici = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, related_name='mercis657_olusturan_ilk_liste'
    )
    OlusturmaTarihi = models.DateTimeField(auto_now_add=True)

    OnaylayanKullanici = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='mercis657_onaylayan_ilk_liste'
    )
    OnayTarihi = models.DateTimeField(null=True, blank=True)
    OnayDurumu = models.BooleanField(default=False)

    class Meta:
        verbose_name = "İlk Liste Bildirimi"
        verbose_name_plural = "İlk Liste Bildirimleri"
        ordering = ['-OlusturmaTarihi']

    def __str__(self):
        return f"{self.PersonelListesi.birim} - {self.PersonelListesi.yil}/{self.PersonelListesi.ay} İlk Liste"

    def onayla(self, kullanici):
        """İlk listeyi onaylar ve bilgileri kaydeder."""
        self.OnayDurumu = True
        self.OnaylayanKullanici = kullanici
        self.OnayTarihi = timezone.now()
        self.save()

    def onay_kaldir(self, kullanici):
        """İlk listeyi onayını kaldırır ve bilgileri kaydeder."""
        self.OnayDurumu = False
        self.OnaylayanKullanici = kullanici
        self.OnayTarihi = timezone.now()
        self.save()

class UserMesaiFavori(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favori_mesaileri")
    mesai = models.ForeignKey(Mesai_Tanimlari, on_delete=models.CASCADE, related_name="favori_kullanicilar")

    class Meta:
        unique_together = ('user', 'mesai')
        verbose_name = "Favori Mesai"
        verbose_name_plural = "Favori Mesailer"

    def __str__(self):
        return f"{self.user} → {self.mesai.Saat}"

class MesaiKontrol(models.Model):
    mesai = models.ForeignKey('Mesai', on_delete=models.CASCADE, related_name='mesai_kontrolleri')
    kontrol = models.BooleanField(default=False)
    kontrol_tarihi = models.DateTimeField(auto_now_add=True)
    kontrol_yapan = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = 'Mesai Kontrol'
        verbose_name_plural = 'Mesai Kontrolleri'
        unique_together = ('mesai',)