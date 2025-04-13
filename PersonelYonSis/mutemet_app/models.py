from django.db import models
from PersonelYonSis.models import User
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.core.exceptions import ValidationError
from datetime import date, timedelta

def validate_tc_kimlik_no(value):
    if not value.isdigit() or len(value) != 11:
        raise ValidationError('TC Kimlik No 11 haneli olmalıdır.')

class Personel(models.Model):
    """Personel bilgileri"""
    DURUM_TIPLERI = [
        ('AKTIF', 'Aktif'),
        ('PASIF', 'Pasif'),
        ('AYRILDI', 'Kurumdan Ayrıldı'),
    ]

    personel_id = models.CharField(
        primary_key=True,
        max_length=11,
        validators=[validate_tc_kimlik_no],
        verbose_name='T.C. Kimlik No'
    )
    sicil_no = models.CharField(max_length=20, verbose_name='Sicil No')
    ad = models.CharField(max_length=50, verbose_name='Ad')
    soyad = models.CharField(max_length=50, verbose_name='Soyad')
    unvan = models.CharField(max_length=100, verbose_name='Unvan')
    brans = models.CharField(max_length=100, verbose_name='Branş')
    durum = models.CharField(max_length=10, choices=DURUM_TIPLERI, default='AKTIF', verbose_name='Durum')
    olusturan = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='olusturan_personeller')
    olusturma_tarihi = models.DateTimeField(auto_now_add=True)
    guncelleyen = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='guncelleyen_personeller')
    guncelleme_tarihi = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['ad', 'soyad']
        verbose_name = 'Personel'
        verbose_name_plural = 'Personeller'

    def __str__(self):
        return f"{self.ad} {self.soyad}"

    def save(self, *args, **kwargs):
        # Trim işlemleri
        self.ad = self.ad.strip()
        self.soyad = self.soyad.strip()
        self.unvan = self.unvan.strip()
        self.brans = self.brans.strip()
        super().save(*args, **kwargs)

class Sendika(models.Model):
    """Sendika tanımları"""
    sendika_id = models.AutoField(primary_key=True)
    sendika_adi = models.CharField(max_length=100, verbose_name='Sendika Adı')
    olusturan = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='olusturan_sendikalar')
    olusturma_tarihi = models.DateTimeField(auto_now_add=True)
    guncelleyen = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='guncelleyen_sendikalar')
    guncelleme_tarihi = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sendika_adi']
        verbose_name = 'Sendika'
        verbose_name_plural = 'Sendikalar'

    def __str__(self):
        return self.sendika_adi

    def save(self, *args, **kwargs):
        self.sendika_adi = self.sendika_adi.strip()
        super().save(*args, **kwargs)

class PersonelHareket(models.Model):
    """Personel hareketleri"""
    HAREKET_TIPLERI = [
        ('BASLAMA', 'Başlama'),
        ('IZIN', 'Ücretsiz İzin'),
        ('DONUS', 'İzin Dönüşü'),
        ('AYRILMA', 'Ayrılma'),
    ]

    hareket_id = models.AutoField(primary_key=True)
    personel = models.ForeignKey(Personel, on_delete=models.CASCADE)
    hareket_tipi = models.CharField(max_length=10, choices=HAREKET_TIPLERI)
    hareket_tarihi = models.DateField()
    aciklama = models.TextField(blank=True, null=True)
    olusturan = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='olusturan_personel_hareketleri')
    olusturma_tarihi = models.DateTimeField(auto_now_add=True)
    guncelleyen = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='guncelleyen_personel_hareketleri')
    guncelleme_tarihi = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-hareket_tarihi']
        verbose_name = 'Personel Hareketi'
        verbose_name_plural = 'Personel Hareketleri'

    def __str__(self):
        return f"{self.personel} - {self.hareket_tipi} ({self.hareket_tarihi})"

class SendikaUyelik(models.Model):
    """Sendika üyelik hareketleri"""
    HAREKET_TIPI_CHOICES = [
        ('UYELIK', 'Üyelik'),
        ('AYRILMA', 'Ayrılma'),
    ]

    uyelik_id = models.AutoField(primary_key=True)
    personel = models.ForeignKey(Personel, on_delete=models.CASCADE, related_name='sendika_hareketleri')
    hareket_tipi = models.CharField(max_length=10, choices=HAREKET_TIPI_CHOICES)
    hareket_tarihi = models.DateField()
    sendika = models.ForeignKey(Sendika, on_delete=models.CASCADE, related_name='sendika_uyelik_hareketleri')
    maas_donemi = models.DateField()  # Her zaman ayın 1'i olacak şekilde tutulacak
    aciklama = models.TextField(blank=True, null=True)
    olusturan = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='olusturulan_sendika_hareketleri')
    olusturma_tarihi = models.DateTimeField(auto_now_add=True)
    guncelleyen = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='guncellenen_sendika_hareketleri')
    guncelleme_tarihi = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.personel.FullName} - {self.get_hareket_tipi_display()} - {self.hareket_tarihi}"

    class Meta:
        verbose_name = 'Sendika Üyelik Hareketi'
        verbose_name_plural = 'Sendika Üyelik Hareketleri'
        ordering = ['-hareket_tarihi']

    def hesapla_maas_donemi(self, islem_tarihi=None, eski_sendika_var=False):
        """Maaş dönemini hesaplar"""
        if islem_tarihi is None:
            islem_tarihi = self.hareket_tarihi

        if eski_sendika_var:
            # Bir ay sonrası için hesaplama
            if islem_tarihi.month == 12:
                next_month = 1
                next_year = islem_tarihi.year + 1
            else:
                next_month = islem_tarihi.month + 1
                next_year = islem_tarihi.year
                
            islem_tarihi = date(next_year, next_month, islem_tarihi.day)

        # 15'inden önce ise aynı ay, sonra ise gelecek ay
        if islem_tarihi.day < 15:
            maas_ayi = islem_tarihi.month
            maas_yili = islem_tarihi.year
        else:
            if islem_tarihi.month == 12:
                maas_ayi = 1
                maas_yili = islem_tarihi.year + 1
            else:
                maas_ayi = islem_tarihi.month + 1
                maas_yili = islem_tarihi.year

        return date(maas_yili, maas_ayi, 1)  # Her zaman ayın 1'ini döndür

    def check_eski_sendika(self):
        """Belirtilen TC için son 1 ay içinde ayrılış kaydı var mı kontrol eder"""
        bir_ay_once = self.hareket_tarihi - timedelta(days=30)
        
        # Ayrılış kaydı kontrolü
        return SendikaUyelik.objects.filter(
            personel=self.personel,
            hareket_tipi='AYRILMA',
            hareket_tarihi__range=[bir_ay_once, self.hareket_tarihi]
        ).exists()

    def save(self, *args, **kwargs):
        # Üyelik ise eski sendika kontrolü yap
        eski_sendika_var = False
        if self.hareket_tipi == 'UYELIK':
            eski_sendika_var = self.check_eski_sendika()
        
        self.maas_donemi = self.hesapla_maas_donemi(eski_sendika_var=eski_sendika_var)
        super().save(*args, **kwargs)

class IcraTakibi(models.Model):
    """İcra takibi"""
    DURUM_TIPLERI = [
        ('AKTIF', 'Aktif'),
        ('PASIF', 'Pasif'),
        ('KAPANDI', 'Kapandı'),
    ]

    icra_id = models.AutoField(primary_key=True)
    personel = models.ForeignKey(Personel, on_delete=models.CASCADE)
    icra_no = models.CharField(max_length=50)
    icra_tarihi = models.DateField()
    icra_tutari = models.DecimalField(max_digits=10, decimal_places=2)
    durum = models.CharField(max_length=10, choices=DURUM_TIPLERI, default='AKTIF')
    aciklama = models.TextField(blank=True, null=True)
    olusturan = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='olusturan_icralar')
    olusturma_tarihi = models.DateTimeField(auto_now_add=True)
    guncelleyen = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='guncelleyen_icralar')
    guncelleme_tarihi = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-icra_tarihi']
        verbose_name = 'İcra Takibi'
        verbose_name_plural = 'İcra Takipleri'

    def __str__(self):
        return f"{self.personel} - {self.icra_no} ({self.icra_tarihi})"

class OdemeTakibi(models.Model):
    """Ödeme takibi"""
    ODEME_TIPLERI = [
        ('MAAS', 'Maaş'),
        ('AVANS', 'Avans'),
        ('IKRAMIYE', 'İkramiye'),
        ('DIGER', 'Diğer'),
    ]

    odeme_id = models.AutoField(primary_key=True)
    personel = models.ForeignKey(Personel, on_delete=models.CASCADE)
    odeme_tipi = models.CharField(max_length=10, choices=ODEME_TIPLERI)
    odeme_tarihi = models.DateField()
    odeme_tutari = models.DecimalField(max_digits=10, decimal_places=2)
    aciklama = models.TextField(blank=True, null=True)
    olusturan = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='olusturan_odemeler')
    olusturma_tarihi = models.DateTimeField(auto_now_add=True)
    guncelleyen = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='guncelleyen_odemeler')
    guncelleme_tarihi = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-odeme_tarihi']
        verbose_name = 'Ödeme Takibi'
        verbose_name_plural = 'Ödeme Takipleri'

    def __str__(self):
        return f"{self.personel} - {self.odeme_tipi} ({self.odeme_tarihi})"
