from django.db import models
from PersonelYonSis.models import User

class Birim(models.Model):
    BirimID = models.AutoField(primary_key=True)
    BirimAdi = models.CharField(max_length=100, unique=True)
    VarsayilanHizmet = models.ForeignKey(
        'Hizmet',
        on_delete=models.SET_NULL,
        null=True,
        related_name='varsayilan_birim_hizmetleri'
    )
    DigerHizmetler = models.ManyToManyField(
        'Hizmet',
        related_name='diger_birim_hizmetleri'
    )

    def __str__(self):
        return self.BirimAdi

class UserBirim(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="yetkili_birimler")
    birim = models.ForeignKey(Birim, on_delete=models.CASCADE, related_name="yetkili_kullanicilar")

    class Meta:
        unique_together = ('user', 'birim')  # Her kullanıcı-birim eşleşmesi benzersiz olmalı

    def __str__(self):
        return f"{self.user.username} - {self.birim.BirimAdi}"

class Hizmet(models.Model):
    STANDART = 'Standart'
    NOBET = 'Nöbet'
    ICAP = 'İcap'
    HIZMET_TIPLERI = [
        (STANDART, 'Standart'),
        (NOBET, 'Nöbet'),
        (ICAP, 'İcap'),
    ]

    HizmetID = models.AutoField(primary_key=True)
    HizmetName = models.CharField(max_length=100, unique=True)
    HizmetTipi = models.CharField(max_length=10, choices=HIZMET_TIPLERI)
    HizmetSuresiHaftaIci = models.IntegerField(
        help_text="Hafta içi hizmet süresi (dakika)",
        default=480  # 8 saat = 480 dakika
    )
    HizmetSuresiHaftaSonu = models.IntegerField(
        help_text="Hafta sonu hizmet süresi (dakika)", 
        null=True, 
        blank=True
    )
    MaxHekimSayisi = models.IntegerField(
        default=1, 
        help_text="Aynı gün için maksimum hekim sayısı"
    )
    NobetErtesiIzinli = models.BooleanField(
        default=False, 
        help_text="Nöbet ertesi izinli mi?"
    )

    def get_hizmet_suresi(self, tarih):
        """Verilen tarihe göre dakika cinsinden hizmet süresini döndürür"""
        from datetime import datetime
        tarih_obj = datetime.strptime(tarih, '%Y-%m-%d')
        is_weekend = tarih_obj.weekday() >= 5
        return self.HizmetSuresiHaftaSonu if (is_weekend and self.HizmetSuresiHaftaSonu) else self.HizmetSuresiHaftaIci

    def format_sure(self, dakika):
        """Dakikayı saat:dakika formatına çevirir"""
        if dakika is None:
            return "-"
        saat = dakika // 60
        kalan_dakika = dakika % 60
        return f"{saat:02d}:{kalan_dakika:02d}"

    def get_hafta_ici_sure_formatted(self):
        return self.format_sure(self.HizmetSuresiHaftaIci)

    def get_hafta_sonu_sure_formatted(self):
        return self.format_sure(self.HizmetSuresiHaftaSonu)

    def __str__(self):
        return f"{self.HizmetName} ({self.HizmetTipi})"

class Personel(models.Model):
    PersonelID = models.AutoField(primary_key=True)
    PersonelName = models.CharField(max_length=100)  # Ad Soyad
    PersonelTitle = models.CharField(max_length=50)  # Unvan (ör. Uzman Tabip)
    PersonelBranch = models.CharField(max_length=100)  # Branş (ör. İç Hastalıkları)
    birim = models.ManyToManyField(Birim, through='PersonelBirim')

    def __str__(self):
        return f"{self.PersonelName} ({self.PersonelTitle})"

class PersonelBirim(models.Model):
    personel = models.ForeignKey(Personel, on_delete=models.CASCADE)
    birim = models.ForeignKey(Birim, on_delete=models.CASCADE)

class Mesai(models.Model):
    MesaiID = models.AutoField(primary_key=True)
    Personel = models.ForeignKey('Personel', on_delete=models.CASCADE)
    MesaiDate = models.DateField(null=False)
    Hizmetler = models.ManyToManyField('Hizmet', related_name='mesai_hizmetleri')
    OnayDurumu = models.IntegerField(default=0)  # 0: Beklemede, 1: Onaylandı
    OnayTarihi = models.DateTimeField(null=True, blank=True)
    Onaylayan = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    Degisiklik = models.BooleanField(default=True)  # True: Değişiklik var, False: Değişiklik yok

    def __str__(self):
        return f"Mesai {self.MesaiDate} - {self.Personel.PersonelName}"

class MesaiKontrol:
    @staticmethod
    def nobet_ertesi_kontrol(personel_id, tarih):
        """Nöbet ertesi mesai kontrolü"""
        from datetime import datetime, timedelta
        tarih_obj = datetime.strptime(tarih, '%Y-%m-%d')
        onceki_gun = (tarih_obj - timedelta(days=1)).strftime('%Y-%m-%d')
        
        # Önceki gün nöbet var mı kontrol et
        onceki_gun_nobet = Mesai.objects.filter(
            Personel_id=personel_id,
            MesaiDate=onceki_gun,
            Hizmetler__HizmetTipi='Nöbet',
            Hizmetler__NobetErtesiIzinli=True
        ).exists()
        
        return not onceki_gun_nobet

    @staticmethod
    def hizmet_cakisma_kontrol(birim_id, tarih, hizmet_id):
        """Aynı hizmette başka hekim var mı kontrolü"""
        hizmet = Hizmet.objects.get(HizmetID=hizmet_id)
        if hizmet.HizmetTipi == 'Standart':
            return True  # Standart hizmetlerde çakışma kontrolü yok
            
        mevcut_mesai_sayisi = Mesai.objects.filter(
            Personel__personelbirim__birim_id=birim_id,
            MesaiDate=tarih,
            Hizmetler__HizmetID=hizmet_id
        ).count()
        
        return mevcut_mesai_sayisi < hizmet.MaxHekimSayisi

    @staticmethod
    def mesai_sure_hesapla(personel_id, tarih):
        """Günlük toplam mesai süresini hesapla"""
        from datetime import timedelta
        
        mesailer = Mesai.objects.filter(
            Personel_id=personel_id,
            MesaiDate=tarih
        ).prefetch_related('Hizmetler')
        
        standart_sure = timedelta()
        nobet_sure = timedelta()
        icap_sure = timedelta()
        
        for mesai in mesailer:
            for hizmet in mesai.Hizmetler.all():
                sure = hizmet.get_hizmet_suresi(tarih)
                if hizmet.HizmetTipi == 'Standart':
                    standart_sure = max(standart_sure, sure)
                elif hizmet.HizmetTipi == 'Nöbet':
                    nobet_sure += sure
                elif hizmet.HizmetTipi == 'İcap':
                    icap_sure += sure
        
        return {
            'standart': standart_sure,
            'nobet': nobet_sure,
            'icap': icap_sure,
            'toplam': standart_sure + nobet_sure  # İcap süresi toplama dahil edilmez
        }
