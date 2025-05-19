TESKILAT_DEGERLERI = [
    ("Sözleşmeli 4B (663 sayılı KHK 45A)", "Sözleşmeli 4B (663 sayılı KHK 45A)"),
    ("Döner Sermaye", "Döner Sermaye"),
    ("İşçi Personel (Genel Bütçe)", "İşçi Personel (Genel Bütçe)"),
    ("İşçi Personel 696 (Döner Sermaye)", "İşçi Personel 696 (Döner Sermaye)"),
    ("Sözleşmeli (4924)", "Sözleşmeli (4924)"),
    ("Taşra", "Taşra"),
]

EGITIM_DEGERLERI = [
    ("Okuryazar", "Okuryazar"),
    ("İlkokul", "İlkokul"),
    ("Ortaokul", "Ortaokul"),
    ("İlköğretim", "İlköğretim"),
    ("Lise", "Lise"),
    ("Önlisans", "Önlisans"),
    ("Lisans", "Lisans"),
    ("Yük. Öğr.(5 Yıl)", "Yük. Öğr.(5 Yıl)"),
    ("Lisans Sonrası 1 Yıl", "Lisans Sonrası 1 Yıl"),
    ("Yüksek Lisans", "Yüksek Lisans"),
    ("Diş Hekimliği", "Diş Hekimliği"),
    ("Tıp Fakültesi", "Tıp Fakültesi"),
    ("Tıpta Uzmanlık", "Tıpta Uzmanlık"),
]

ENGEL_DERECESI_DEGERLERI = [
    ("1.Derece Engelli (%80 ve üzeri)", "1.Derece Engelli (%80 ve üzeri)"),
    ("2.Derece Engelli (%60-79)", "2.Derece Engelli (%60-79)"),
    ("3.Derece Engelli (%40-59)", "3.Derece Engelli (%40-59)"),
]

MAZERET_DEGERLERI = [
    ("Saglik", "Sağlık"),
    ("Egitim", "Eğitim"),
    ("EsDurumu", "Eş Durumu"),
    ("AileBirligiDagilmasi", "Aile Birliğinin Dağılması"),
]

OZEL_DURUM_DEGERLERI = [
    ("Engelli", "Engelli"),
    ("Gazi", "Gazi"),
    ("SehitYakini", "Şehit Yakını"),
    ("BakmaklaYukumlu", "Bakmakla Yükümlü"),
]

AYRILMA_NEDENI_DEGERLERI = [
    ("Emeklilik", "Emeklilik"),
    ("Tayin", "Tayin"),
    ("TUS", "TUS"),
    ("Diger", "Diğer"),
]

# Burç tarihleri (gün ve ay ile)
BURC_DATES = [
    ("Koc", (3, 21), (4, 20)),
    ("Boga", (4, 21), (5, 21)),
    ("Ikizler", (5, 22), (6, 22)),
    ("Yengec", (6, 23), (7, 22)),
    ("Aslan", (7, 23), (8, 22)),
    ("Basak", (8, 23), (9, 22)),
    ("Terazi", (9, 23), (10, 22)),
    ("Akrep", (10, 23), (11, 21)),
    ("Yay", (11, 22), (12, 21)),
    ("Oglak", (12, 22), (1, 21)),
    ("Kova", (1, 22), (2, 19)),
    ("Balik", (2, 20), (3, 20)),
]

def get_burc_for_date(dt):
    m, d = dt.month, dt.day
    for burc, (start_m, start_d), (end_m, end_d) in BURC_DATES:
        if (m == start_m and d >= start_d) or (m == end_m and d <= end_d):
            return burc
        if start_m > end_m:  # Oğlak gibi yılbaşı burçları
            if (m == start_m and d >= start_d) or (m == end_m and d <= end_d):
                return burc
    return None
