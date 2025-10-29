from django.core.management.base import BaseCommand
from django.apps import apps
import csv
from openpyxl import Workbook

class Command(BaseCommand):
    help = "Tüm app ve modellerin listesini CSV veya Excel olarak dışa aktarır."

    def add_arguments(self, parser):
        parser.add_argument(
            '--format',
            choices=['csv', 'xlsx'],
            default='csv',
            help='Çıktı formatı: csv veya xlsx (varsayılan: csv)'
        )
        parser.add_argument(
            '--output',
            default='model_listesi',
            help='Çıktı dosyası adı (uzantısız)'
        )

    def handle(self, *args, **options):
        output = options['output']
        fmt = options['format']

        # Django'daki tüm yüklü uygulamaları al
        all_apps = apps.get_app_configs()

        model_data = []
        for app in all_apps:
            for model in app.get_models():
                model_data.append({
                    "App Label": app.label,
                    "App Name": app.name,
                    "Model": model.__name__,
                    "Table Name": model._meta.db_table,
                })

        if fmt == 'csv':
            filename = f"{output}.csv"
            with open(filename, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=model_data[0].keys())
                writer.writeheader()
                writer.writerows(model_data)
            self.stdout.write(self.style.SUCCESS(f"✅ CSV dosyası oluşturuldu: {filename}"))

        else:
            filename = f"{output}.xlsx"
            wb = Workbook()
            ws = wb.active
            ws.title = "Model Listesi"

            headers = list(model_data[0].keys())
            ws.append(headers)
            for row in model_data:
                ws.append(list(row.values()))

            wb.save(filename)
            self.stdout.write(self.style.SUCCESS(f"✅ Excel dosyası oluşturuldu: {filename}"))
