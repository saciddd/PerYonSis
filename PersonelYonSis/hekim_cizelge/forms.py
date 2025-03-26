from django import forms
from django.template.loader import render_to_string
from django.conf import settings
import pdfkit
from pathlib import Path
import os

class BildirimForm:
    """Bildirim formu PDF oluşturma sınıfı"""
    
    @staticmethod
    def create_pdf(bildirim):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
        elements = []

        # Başlık bilgileri
        header_data = [
            ['FAZLA ÇALIŞMA/İCAP NÖBETİ BİLDİRİM FORMU'],
            [f'Personel: {bildirim.Personel.PersonelName}'],
            [f'Birim: {bildirim.PersonelBirim.birim.BirimAdi}'],
            [f'Dönem: {bildirim.DonemBaslangic.strftime("%B %Y")}'],
            ['']
        ]

        # Çalışma detayları
        detail_data = [
            ['Normal Fazla Mesai:', f'{bildirim.NormalFazlaMesai:.2f} saat'],
            ['Bayram Fazla Mesai:', f'{bildirim.BayramFazlaMesai:.2f} saat'],
            ['Riskli Normal Fazla Mesai:', f'{bildirim.RiskliNormalFazlaMesai:.2f} saat'],  
            ['Riskli Bayram Fazla Mesai:', f'{bildirim.RiskliBayramFazlaMesai:.2f} saat'],
            ['Normal İcap:', f'{bildirim.NormalIcap:.2f} saat'],
            ['Bayram İcap:', f'{bildirim.BayramIcap:.2f} saat'],
            ['Toplam Fazla Mesai:', f'{bildirim.ToplamFazlaMesai:.2f} saat'],
            ['Toplam İcap:', f'{bildirim.ToplamIcap:.2f} saat']
        ]

        # Günlük detay tablosu
        daily_data = []
        daily_header = ['Gün', 'Mesai (saat)', 'İcap (saat)', 'Not']
        daily_data.append(daily_header)

        # Tüm günleri birleştir
        all_dates = set()
        if bildirim.MesaiDetay:
            all_dates.update(bildirim.MesaiDetay.keys())
        if bildirim.IcapDetay:
            all_dates.update(bildirim.IcapDetay.keys())

        for tarih in sorted(all_dates):
            mesai_sure = bildirim.MesaiDetay.get(tarih, 0) if bildirim.MesaiDetay else 0
            icap_sure = bildirim.IcapDetay.get(tarih, 0) if bildirim.IcapDetay else 0
            
            if mesai_sure > 0 or icap_sure > 0:
                daily_data.append([
                    tarih, 
                    f'{mesai_sure:.2f}' if mesai_sure > 0 else '-',
                    f'{icap_sure:.2f}' if icap_sure > 0 else '-',
                    ''
                ])

        # Tabloları oluştur
        header_table = Table(header_data, colWidths=[19*cm])
        detail_table = Table(detail_data, colWidths=[10*cm, 9*cm])
        daily_table = Table(daily_data, colWidths=[6*cm, 6*cm, 7*cm])

        # Stil tanımlamaları
        header_style = TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 14),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ])

        detail_style = TableStyle([
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
            ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ])

        daily_style = TableStyle([
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ])

        # Stilleri uygula
        header_table.setStyle(header_style)
        detail_table.setStyle(detail_style)
        daily_table.setStyle(daily_style)

        # Tabloları ekle
        elements.append(header_table)
        elements.append(detail_table)
        elements.append(daily_table)

        # PDF oluştur
        doc.build(elements)
        pdf = buffer.getvalue()
        buffer.close()
        
        return pdf

    @staticmethod
    def create_pdf_multiple(bildirimler):
        try:
            # Template context hazırla
            context = {
                'bildirimler': [
                    {
                        'personel': bildirim.PersonelBirim.personel.PersonelName,
                        'birim': bildirim.PersonelBirim.birim.BirimAdi,
                        'donem': bildirim.DonemBaslangic.strftime("%B %Y"),
                        'normal_mesai': float(bildirim.NormalFazlaMesai),
                        'bayram_mesai': float(bildirim.BayramFazlaMesai),
                        'riskli_normal': float(bildirim.RiskliNormalFazlaMesai),
                        'riskli_bayram': float(bildirim.RiskliBayramFazlaMesai),
                        'normal_icap': float(bildirim.NormalIcap),
                        'bayram_icap': float(bildirim.BayramIcap),
                        'toplam_mesai': float(bildirim.ToplamFazlaMesai),
                        'toplam_icap': float(bildirim.ToplamIcap),
                        'mesai_detay': sorted([
                            {'tarih': k, 'sure': v} 
                            for k, v in (bildirim.MesaiDetay or {}).items()
                            if v > 0
                        ], key=lambda x: x['tarih']),
                        'icap_detay_dict': bildirim.IcapDetay or {}
                    }
                    for bildirim in bildirimler
                ]
            }

            # HTML template render et
            html_string = render_to_string('hekim_cizelge/bildirim_form.html', context)

            # PDF ayarları
            options = {
                'page-size': 'A4',
                'orientation': 'Landscape',
                'margin-top': '1.0cm',
                'margin-right': '1.0cm',
                'margin-bottom': '1.0cm',
                'margin-left': '1.0cm',
                'encoding': "UTF-8",
                'enable-local-file-access': None,
            }

            # CSS dosyasının tam yolu
            css_path = str(Path(__file__).resolve().parent.parent / 'static' / 'css' / 'bildirim_form.css')
            
            # wkhtmltopdf yolunu doğrudan belirt
            config = pdfkit.configuration(wkhtmltopdf='C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')
            
            # PDF oluştur
            pdf = pdfkit.from_string(
                html_string, 
                False, 
                options=options,
                css=css_path,
                configuration=config
            )
            
            return pdf

        except Exception as e:
            raise Exception(f"PDF oluşturma hatası: {str(e)}")