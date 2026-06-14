from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import connection

class Command(BaseCommand):
    help = "Belirtilen uygulamanın (örneğin mercis657) tüm tablolarında sequence değerlerini sıfırlar."

    def add_arguments(self, parser):
        parser.add_argument(
            'app_label',
            type=str,
            help="Sequence'leri düzeltilecek uygulamanın adı (örnek: mercis657)",
        )

    def handle(self, *args, **options):
        app_label = options['app_label']
        app_config = apps.get_app_config(app_label)

        self.stdout.write(self.style.NOTICE(f"🔍 '{app_label}' uygulamasındaki tablolar taranıyor..."))
        with connection.cursor() as cursor:
            for model in app_config.get_models():
                table = model._meta.db_table
                pk_column = model._meta.pk.column

                # PostgreSQL için sequence düzeltme komutu
                sql = f"""
                    SELECT setval(
                        pg_get_serial_sequence('"{table}"', '{pk_column}'),
                        COALESCE((SELECT MAX("{pk_column}") FROM "{table}"), 1),
                        TRUE
                    );
                """

                try:
                    cursor.execute(sql)
                    self.stdout.write(self.style.SUCCESS(f"✅ {table} sequence düzeltildi."))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"⚠️ {table} için hata: {e}"))

        self.stdout.write(self.style.SUCCESS(f"\n🎯 Tüm '{app_label}' tablolarının sequence değerleri güncellendi."))
