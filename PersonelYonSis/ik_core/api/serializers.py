# ik_core/api/serializers.py
from rest_framework import serializers
from ik_core.models import Personel

class PersonelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Personel
        fields = [
            'tc_kimlik_no', 'ad', 'soyad', 'sicil_no'
        ]
        extra_kwargs = {
            'tc_kimlik_no': {'required': True}
        }

    def create(self, validated_data):
        return Personel.objects.create(
            tc_kimlik_no=validated_data.get('tc_kimlik_no'),
            ad=validated_data.get('ad', ''),
            soyad=validated_data.get('soyad', ''),
            sicil_no=validated_data.get('sicil_no', '')
        )