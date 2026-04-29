from django.contrib import admin
from .models import Cihaz, CihazKullanici, CihazLog, ADMSKomutKuyrugu, ADMSHamLog

@admin.register(Cihaz)
class CihazAdmin(admin.ModelAdmin):
    list_display = ('kapi_adi', 'ip', 'port', 'seri_no', 'adms_aktif', 'son_heartbeat', 'adms_cevrimici_goster', 'aciklama')
    search_fields = ('kapi_adi', 'ip', 'seri_no')
    list_filter = ('adms_aktif',)
    list_editable = ('adms_aktif',)

    @admin.display(boolean=True, description="Çevrimiçi")
    def adms_cevrimici_goster(self, obj):
        return obj.adms_cevrimici

@admin.register(CihazKullanici)
class CihazKullaniciAdmin(admin.ModelAdmin):
    list_display = ('name', 'uid', 'user_id', 'card', 'cihaz', 'privilege')
    list_filter = ('cihaz', 'privilege')
    search_fields = ('name', 'user_id', 'card', 'uid')

@admin.register(CihazLog)
class CihazLogAdmin(admin.ModelAdmin):
    list_display = ('cihaz', 'user_id', 'timestamp', 'status', 'verification')
    list_filter = ('cihaz', 'status')
    search_fields = ('user_id',)
    date_hierarchy = 'timestamp'

@admin.register(ADMSKomutKuyrugu)
class ADMSKomutKuyruguAdmin(admin.ModelAdmin):
    list_display = ('cihaz', 'komut_id', 'komut_tipi', 'gonderildi', 'olusturulma', 'gonderilme_zamani')
    list_filter = ('cihaz', 'gonderildi', 'komut_tipi')
    readonly_fields = ('olusturulma', 'gonderilme_zamani')

@admin.register(ADMSHamLog)
class ADMSHamLogAdmin(admin.ModelAdmin):
    list_display = ('cihaz', 'tablo', 'islem_durumu', 'olusturulma')
    list_filter = ('cihaz', 'tablo', 'islem_durumu')
    readonly_fields = ('olusturulma',)
    search_fields = ('ham_veri',)
    date_hierarchy = 'olusturulma'

