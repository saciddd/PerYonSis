from django.contrib import admin
from .models import UstBirim, Bina, Birim, PersonelBirim
from .models.personel import KisaUnvan, UnvanBransEslestirme

@admin.register(KisaUnvan)
class KisaUnvanAdmin(admin.ModelAdmin):
    list_display = ['ad', 'ust_birim']
    search_fields = ['ad']
    list_filter = ['ust_birim']

@admin.register(UnvanBransEslestirme)
class UnvanBransEslestirmeAdmin(admin.ModelAdmin):
    list_display = ['kisa_unvan', 'unvan', 'brans']
    search_fields = ['kisa_unvan__ad', 'unvan__ad', 'brans__ad']
    list_filter = ['kisa_unvan']

@admin.register(UstBirim)
class UstBirimAdmin(admin.ModelAdmin):
    list_display = ['ad']
    search_fields = ['ad']
    ordering = ['ad']

@admin.register(Bina)
class BinaAdmin(admin.ModelAdmin):
    list_display = ['ad', 'birim_sayisi']
    search_fields = ['ad']
    ordering = ['ad']

@admin.register(Birim)
class BirimAdmin(admin.ModelAdmin):
    list_display = ['ad', 'bina', 'ust_birim']
    list_filter = ['bina', 'ust_birim']
    search_fields = ['ad', 'bina__ad', 'ust_birim__ad']
    ordering = ['ust_birim__ad', 'ad']

@admin.register(PersonelBirim)
class PersonelBirimAdmin(admin.ModelAdmin):
    list_display = ['personel', 'birim', 'gecis_tarihi', 'sorumlu', 'created_by']
    list_filter = ['birim', 'sorumlu', 'gecis_tarihi', 'created_by']
    search_fields = ['personel__ad', 'personel__soyad', 'birim__ad']
    ordering = ['-gecis_tarihi', '-creation_timestamp']
    readonly_fields = ['creation_timestamp']
