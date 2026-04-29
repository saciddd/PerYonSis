from django.db import models
from django.utils import timezone


class Cihaz(models.Model):
    kapi_adi = models.CharField(max_length=100, verbose_name="Kapı Adı")
    ip = models.GenericIPAddressField(protocol='IPv4', verbose_name="IP Adresi")
    port = models.PositiveIntegerField(default=4370, verbose_name="Port")
    aciklama = models.TextField(blank=True, null=True, verbose_name="Açıklama")
    # ADMS/Push Protokolü alanları
    seri_no = models.CharField(
        max_length=100, blank=True, null=True, unique=True,
        verbose_name="Seri Numarası",
        help_text="Cihazın seri numarası (ADMS Push protokolünde SN parametresi)"
    )
    adms_aktif = models.BooleanField(
        default=False, verbose_name="ADMS Aktif",
        help_text="ADMS Push modu aktif mi?"
    )
    son_heartbeat = models.DateTimeField(
        blank=True, null=True, verbose_name="Son Heartbeat",
        help_text="Cihazdan gelen son getrequest zamanı"
    )

    def __str__(self):
        return f"{self.kapi_adi} ({self.ip})"

    @property
    def adms_cevrimici(self):
        """Son 2 dakika içinde heartbeat geldiyse çevrimiçi kabul et."""
        if not self.son_heartbeat:
            return False
        return (timezone.now() - self.son_heartbeat).total_seconds() < 120

    class Meta:
        verbose_name = "Cihaz"
        verbose_name_plural = "Cihazlar"


class CihazKullanici(models.Model):
    cihaz = models.ForeignKey(Cihaz, on_delete=models.CASCADE, related_name='kullanicilar', verbose_name="Cihaz")
    uid = models.PositiveIntegerField(verbose_name="UID")
    user_id = models.CharField(max_length=50, verbose_name="User ID")
    name = models.CharField(max_length=100, verbose_name="Ad Soyad")
    card = models.CharField(max_length=50, blank=True, null=True, verbose_name="Kart No")
    privilege = models.IntegerField(default=0, verbose_name="Yetki")

    class Meta:
        verbose_name = "Cihaz Kullanıcısı"
        verbose_name_plural = "Cihaz Kullanıcıları"
        unique_together = ('cihaz', 'uid')  # Bir cihazda aynı UID tekrar edemez.

    def __str__(self):
        return f"{self.name} - {self.cihaz.kapi_adi}"

class CihazLog(models.Model):
    cihaz = models.ForeignKey(Cihaz, on_delete=models.CASCADE, related_name='logs', verbose_name="Cihaz")
    uid = models.PositiveIntegerField(verbose_name="UID") # User ID ile eşleşebilir
    user_id = models.CharField(max_length=50, verbose_name="User ID", blank=True, null=True)
    timestamp = models.DateTimeField(verbose_name="Zaman")
    status = models.IntegerField(verbose_name="Durum", default=0) # Giriş/Çıkış vb.
    verification = models.IntegerField(verbose_name="Doğrulama Türü", default=0)

    class Meta:
        verbose_name = "Cihaz Logu"
        verbose_name_plural = "Cihaz Logları"
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['cihaz']),
        ]

    def __str__(self):
        return f"{self.cihaz.kapi_adi} - {self.timestamp}"


class ADMSKomutKuyrugu(models.Model):
    """
    Sunucudan cihaza gönderilmek üzere bekleyen komutlar.
    Cihaz /iclock/getrequest ile polling yaptığında bu kuyruktan komut alır.
    """
    KOMUT_TIPLERI = [
        ('CHECK', 'Saat Kontrolü'),
        ('REBOOT', 'Yeniden Başlat'),
        ('INFO', 'Cihaz Bilgisi Al'),
        ('CLEAR LOG', 'Log Temizle'),
        ('CLEAR DATA', 'Veri Temizle'),
        ('SET OPTION', 'Ayar Değiştir'),
    ]

    cihaz = models.ForeignKey(
        Cihaz, on_delete=models.CASCADE,
        related_name='komut_kuyrugu', verbose_name="Cihaz"
    )
    komut_id = models.PositiveIntegerField(verbose_name="Komut ID")
    komut_tipi = models.CharField(max_length=50, verbose_name="Komut Tipi")
    parametreler = models.TextField(blank=True, default='', verbose_name="Parametreler")
    olusturulma = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma")
    gonderildi = models.BooleanField(default=False, verbose_name="Gönderildi")
    gonderilme_zamani = models.DateTimeField(
        blank=True, null=True, verbose_name="Gönderilme Zamanı"
    )

    class Meta:
        verbose_name = "ADMS Komut Kuyruğu"
        verbose_name_plural = "ADMS Komut Kuyrukları"
        ordering = ['olusturulma']

    def __str__(self):
        durum = "✓" if self.gonderildi else "⏳"
        return f"{durum} [{self.cihaz.kapi_adi}] C:{self.komut_id}:{self.komut_tipi}"


class ADMSHamLog(models.Model):
    """
    Cihazdan gelen ham (raw) verileri saklar — debug ve denetim amaçlı.
    """
    ISLEM_DURUMLARI = [
        ('BEKLEMEDE', 'Beklemede'),
        ('ISLENDI', 'İşlendi'),
        ('HATA', 'Hata'),
    ]

    cihaz = models.ForeignKey(
        Cihaz, on_delete=models.CASCADE,
        related_name='ham_loglar', verbose_name="Cihaz"
    )
    tablo = models.CharField(
        max_length=50, verbose_name="Tablo",
        help_text="ATTLOG, OPERLOG, USERINFO vb."
    )
    ham_veri = models.TextField(verbose_name="Ham Veri")
    islem_durumu = models.CharField(
        max_length=20, choices=ISLEM_DURUMLARI,
        default='BEKLEMEDE', verbose_name="İşlem Durumu"
    )
    hata_mesaji = models.TextField(blank=True, default='', verbose_name="Hata Mesajı")
    olusturulma = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma")

    class Meta:
        verbose_name = "ADMS Ham Log"
        verbose_name_plural = "ADMS Ham Loglar"
        ordering = ['-olusturulma']
        indexes = [
            models.Index(fields=['islem_durumu']),
            models.Index(fields=['olusturulma']),
        ]

    def __str__(self):
        return f"[{self.tablo}] {self.cihaz.kapi_adi} - {self.olusturulma}"
