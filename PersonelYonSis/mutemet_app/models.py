from django.db import models
from PersonelYonSis.models import User
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from ik_core.models import Personel  # Yeni Personel modelini buradan alıyoruz

def validate_tc_kimlik_no(value):
    if not value.isdigit() or len(value) != 11:
        raise ValidationError('TC Kimlik No 11 haneli olmalıdır.')

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
        ('GIRIS', 'Giriş'),
        ('CIKIS', 'Çıkış'),
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
            hareket_tipi='CIKIS',
            hareket_tarihi__range=[bir_ay_once, self.hareket_tarihi]
        ).exists()

    def save(self, *args, **kwargs):
        # Aynı anda iki sendika üyeliği engelle
        son_kayit = SendikaUyelik.objects.filter(personel=self.personel).order_by('-hareket_tarihi', '-uyelik_id').first()
        if son_kayit and son_kayit.hareket_tipi == 'GIRIS' and self.hareket_tipi == 'GIRIS':
            raise ValidationError('Bir kişi aynı anda iki sendikaya üye olamaz. Önce mevcut üyelikten çıkış yapılmalı.')
        # Üyelik ise eski sendika kontrolü yap
        eski_sendika_var = False
        if self.hareket_tipi == 'GIRIS':
            eski_sendika_var = self.check_eski_sendika()
        self.maas_donemi = self.hesapla_maas_donemi(eski_sendika_var=eski_sendika_var)
        super().save(*args, **kwargs)

class IcraTakibi(models.Model):
    DURUM_TIPLERI = [
        ('AKTIF', 'Aktif'),
        ('SIRADA', 'Sırada'),
        ('KAPANDI', 'Kapandı'),
    ]
    ICRA_TURLERI = [
        ('NAFAKA', 'Nafaka'),
        ('TAAHHUT', 'Taahhüt'),
        ('ICRA', 'İcra'),
    ]

    icra_id = models.AutoField(primary_key=True)
    personel = models.ForeignKey(Personel, on_delete=models.CASCADE)
    icra_vergi_dairesi_no = models.CharField(max_length=50, verbose_name='Vergi Dairesi No')
    icra_dairesi = models.CharField(max_length=100, verbose_name='İcra Dairesi')
    dosya_no = models.CharField(max_length=50, verbose_name='Dosya No')
    icra_dairesi_banka = models.CharField(max_length=100, verbose_name='Banka')
    icra_dairesi_hesap_no = models.CharField(max_length=50, verbose_name='Hesap No')
    alacakli = models.CharField(max_length=100, verbose_name='Alacaklı')
    alacakli_vekili = models.CharField(max_length=100, verbose_name='Alacaklı Vekili', blank=True, null=True)
    tarihi = models.DateField(verbose_name='İcra Tarihi')
    tutar = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Tutar')
    durum = models.CharField(max_length=10, choices=DURUM_TIPLERI, default='AKTIF', verbose_name='Durum')
    icra_turu = models.CharField(max_length=10, choices=ICRA_TURLERI, default='ICRA', verbose_name='İcra Türü')
    silme_isteyen = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='silme_istegi_icralar', verbose_name='Silme İsteyen'
    )

    class Meta:
        ordering = ['-tarihi']
        verbose_name = 'İcra Takibi'
        verbose_name_plural = 'İcra Takipleri'

    def __str__(self):
        return f"{self.personel} - {self.icra_dairesi} ({self.dosya_no})"

    @property
    def toplam_kesinti(self):
        # Eğer nesne henüz kaydedilmediyse ilişkili kayıtlar olamaz, 0 döndür
        if not self.pk:
            return 0
        return self.icrahareketleri_set.aggregate(total=models.Sum('kesilen_tutar'))['total'] or 0

    @property
    def kalan_borc(self):
        return float(self.tutar) - float(self.toplam_kesinti or 0)

    def save(self, *args, **kwargs):
        # Nesne kaydedilmeden toplam_kesinti hesaplanamaz, sadece güncellemede kontrol et
        if self.pk:
            if self.kalan_borc <= 0:
                self.durum = 'KAPANDI'
            elif self.durum == 'KAPANDI' and self.kalan_borc > 0:
                self.durum = 'AKTIF'
        super().save(*args, **kwargs)

class IcraHareketleri(models.Model):
    ODEME_TURU_CHOICES = [
        ('DENGE', 'Denge'),
        ('DENGE FARK', 'Denge Fark'),
        ('EK ÖDEME', 'Ek Ödeme'),
        ('ELDEN', 'Elden'),
        ('İKRAMİYE', 'İkramiye'),
        ('MAAŞ', 'Maaş'),
        ('NAFAKA', 'Nafaka'),
        ('SABİT', 'Sabit'),
        ('SABİT FARK', 'Sabit Fark'),
        ('TEMEL', 'Temel'),
        ('TEŞVİK', 'Teşvik'),
        ('TOPLU GİRİŞ', 'Toplu Giriş'),
    ]

    icra = models.ForeignKey(IcraTakibi, on_delete=models.CASCADE, related_name='icrahareketleri_set')
    kesilen_tutar = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Kesilen Tutar')
    kesildigi_donem = models.DateField(verbose_name='Kesildiği Dönem')
    odeme_turu = models.CharField(max_length=20, choices=ODEME_TURU_CHOICES, verbose_name='Ödeme Türü')

    class Meta:
        ordering = ['-kesildigi_donem']
        verbose_name = 'İcra Hareketi'
        verbose_name_plural = 'İcra Hareketleri'

    def __str__(self):
        return f"{self.icra} - {self.odeme_turu} ({self.kesildigi_donem})"

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

class SilinenIcraTakibi(models.Model):
    """Silinen icra kayıtlarının yedeği"""
    # Orijinal IcraTakibi alanları
    icra_id = models.IntegerField()
    personel = models.ForeignKey(Personel, on_delete=models.SET_NULL, null=True)
    icra_vergi_dairesi_no = models.CharField(max_length=50)
    icra_dairesi = models.CharField(max_length=100)
    dosya_no = models.CharField(max_length=50)
    icra_dairesi_banka = models.CharField(max_length=100)
    icra_dairesi_hesap_no = models.CharField(max_length=50)
    alacakli = models.CharField(max_length=100)
    alacakli_vekili = models.CharField(max_length=100, blank=True, null=True)
    tarihi = models.DateField()
    tutar = models.DecimalField(max_digits=10, decimal_places=2)
    durum = models.CharField(max_length=10)
    icra_turu = models.CharField(max_length=10)
    silme_isteyen = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='yedek_silme_isteyen')
    # Ekstra alanlar
    silen = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='silinen_icralari_silen')
    silinme_tarihi = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Silinen İcra Takibi'
        verbose_name_plural = 'Silinen İcra Takipleri'

    def __str__(self):
        return f"{self.personel} - {self.icra_dairesi} ({self.dosya_no}) [Silindi]"
