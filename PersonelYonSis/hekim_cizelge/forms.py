from django import forms
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.units import cm
from io import BytesIO

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
        if bildirim.BildirimTipi == 'MESAI':
            detail_data = [
                ['Normal Fazla Mesai:', f'{bildirim.NormalFazlaMesai:.2f} saat'],
                ['Bayram Fazla Mesai:', f'{bildirim.BayramFazlaMesai:.2f} saat'],
                ['Riskli Normal Fazla Mesai:', f'{bildirim.RiskliNormalFazlaMesai:.2f} saat'],  
                ['Riskli Bayram Fazla Mesai:', f'{bildirim.RiskliBayramFazlaMesai:.2f} saat'],
                ['Toplam:', f'{bildirim.ToplamFazlaMesai:.2f} saat']
            ]
        else:
            detail_data = [
                ['Normal İcap:', f'{bildirim.NormalIcap:.2f} saat'],
                ['Bayram İcap:', f'{bildirim.BayramIcap:.2f} saat'],
                ['Toplam:', f'{bildirim.ToplamIcap:.2f} saat']
            ]

        # Günlük detay tablosu
        daily_data = []
        daily_header = ['Gün', 'Süre (saat)', 'Not']
        daily_data.append(daily_header)

        detay = bildirim.MesaiDetay if bildirim.BildirimTipi == 'MESAI' else bildirim.IcapDetay
        for tarih, sure in detay.items():
            if sure > 0:
                daily_data.append([tarih, f'{sure:.2f}', ''])

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
