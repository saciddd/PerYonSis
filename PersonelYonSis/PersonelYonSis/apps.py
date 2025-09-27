from django.apps import AppConfig

class PersonelYonSisConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'PersonelYonSis'

    def ready(self):
        # Sinyallerin yüklenmesi için ready fonksiyonu zaten mevcut
        import PersonelYonSis.signals
