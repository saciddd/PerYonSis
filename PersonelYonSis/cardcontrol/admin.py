from django.contrib import admin
from .models import Cihaz, CihazKullanici

@admin.register(Cihaz)
class CihazAdmin(admin.ModelAdmin):
    list_display = ('kapi_adi', 'ip', 'port', 'aciklama')
    search_fields = ('kapi_adi', 'ip')

@admin.register(CihazKullanici)
class CihazKullaniciAdmin(admin.ModelAdmin):
    list_display = ('name', 'uid', 'user_id', 'card', 'cihaz', 'privilege')
    list_filter = ('cihaz', 'privilege')
    search_fields = ('name', 'user_id', 'card', 'uid')
