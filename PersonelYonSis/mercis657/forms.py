# forms.py
from django import forms
from .models import Mesai_Tanimlari

class MesaiTanimForm(forms.ModelForm):
    class Meta:
        model = Mesai_Tanimlari
        fields = ['Saat', 'GunduzMesaisi', 'AksamMesaisi', 'GeceMesaisi', 'IseGeldi', 'SonrakiGuneSarkiyor', 'AraDinlenme', 'GecerliMesai', 'CKYS_BTF_Karsiligi']
