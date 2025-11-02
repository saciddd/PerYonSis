import datetime
from datetime import date, timedelta
import io
import pyodbc

# FileMaker veritabanı bağlantı bilgilerini değiştirin
server = '10.38.12.55'
database = 'KDH Izin'
username = 'admin'
password = 'polat123'
# ODBC bağlantı dizesini oluştur
conn_str = f'DRIVER={{FileMaker ODBC}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
# connection değişkenini tanımla
connection = None
#-----------------------

def IzinSorgula(baslangic, bitis):
    """
    2 Tarih arasındaki Tüm izinlerin sorgusu, Tarih formatını YYYY-MM-DD şeklinde ayarlayın.
    Örnek kullanım: IzinSorgula("2025-04-01", "2025-04-30")
    """
    global connection
    try:
        # Veritabanına bağlan
        connection = pyodbc.connect(conn_str)
        # Bağlantı üzerinden bir cursor oluştur
        cursor = connection.cursor()
        # SQL sorgunuzu burada çalıştırabilirsiniz
        sql = (f'SELECT "T.C. Kimlik No", "İzne Ayrılış Tarihi", "İzin Dönüşü", "İzin Türü" FROM Izinler WHERE "İzin Dönüşü" >= ? AND "İzne Ayrılış Tarihi" <= ?')
        cursor.execute(sql, (baslangic, bitis))
        # SQL sorgu sonuçlarını bir liste içine al
        rows = [list(row) for row in cursor.fetchall()]
        return rows
    except pyodbc.Error as e:
        print(f'Hata: {e}')
    finally:
        # Bağlantıyı kapat
        if connection:
            connection.close()

def format_date_for_filemaker(dt):
    """Tarih objesini FileMaker formatına (yyyy-aa-gg) dönüştürür."""
    if not dt:
        return None
    if isinstance(dt, date):
        return dt.strftime("%Y-%m-%d")
    return str(dt)

def sync_personel_to_filemaker(personel, silent=False):
    """
    Personel modelini FileMaker'daki 'Personeller' tablosuyla senkronize eder.
    TCKimlikNo eşleşiyorsa UPDATE, yoksa INSERT yapar.
    """
    global connection
    try:
        connection = pyodbc.connect(conn_str)
        cursor = connection.cursor()

        # FileMaker'da kayıt var mı kontrol et
        check_sql = 'SELECT "TCKimlikNo" FROM Personeller WHERE "TCKimlikNo" = ?'
        cursor.execute(check_sql, (personel.tc_kimlik_no,))
        existing = cursor.fetchone()

        # Tarih formatını FileMaker uyumlu hale getir (YYYY-MM-DD)
        def fmt_date(value):
            return value.strftime("%Y-%m-%d") if isinstance(value, date) else None

        cinsiyet_val = ""
        c = (personel.cinsiyet or "").strip().lower()
        if c in ("kadin", "kadın"):
            cinsiyet_val = "Kadın"
        elif c == "erkek":
            cinsiyet_val = "Erkek"

        data = {
            "AdayMemur?": int(personel.aday_memur or 0),
            "Adi": personel.ad or "",
            "Soyadi": personel.soyad or "",
            "Adres": personel.adres or "",
            "AtamaKararNo": personel.atama_karar_no or "",
            "AtamaKararTarihi": fmt_date(personel.atama_karar_tarihi),
            "Brans": personel.brans.ad if personel.brans else "",
            "Cinsiyet": cinsiyet_val,
            "Doğum Tarihi": fmt_date(personel.dogum_tarihi),
            "Durum": personel.durum or "",
            "GoreveBaslamaTarihi": fmt_date(personel.goreve_baslama_tarihi),
            "KadroDurumu": personel.kadro_durumu or "",
            "KurumdanAyrilmaNedeni": personel.ayrilma_nedeni or "",
            "KurumdanAyrilmaNedeniDetay": personel.ayrilma_detay or "",
            "MemuriyetDurumu": personel.memuriyet_durumu or "",
            "Memuriyete Başlama Tarihi": fmt_date(personel.memuriyete_baslama_tarihi),
            "SicilNo": personel.sicil_no or "",
            "Telefon": personel.telefon or "",
            "Teşkilat": personel.teskilat or "",
            "Unvan": personel.unvan.ad if personel.unvan else "",
            "TCKimlikNo": personel.tc_kimlik_no,
        }

        if existing:
            # UPDATE
            set_clause = ", ".join([f'"{k}" = ?' for k in data.keys()])
            sql = f'UPDATE Personeller SET {set_clause} WHERE "TCKimlikNo" = ?'
            cursor.execute(sql, list(data.values()) + [personel.tc_kimlik_no])
            action = "güncellendi"
        else:
            # INSERT
            columns = ", ".join([f'"{k}"' for k in data.keys()])
            placeholders = ", ".join(["?" for _ in data])
            sql = f'INSERT INTO Personeller ({columns}) VALUES ({placeholders})'
            cursor.execute(sql, list(data.values()))
            action = "eklenildi"

        connection.commit()
        message = f"🟢 FileMaker'a {personel.ad} {personel.soyad} {action}."
        if silent:
            print(message)
        return {"status": "success", "message": message}

    except pyodbc.Error as e:
        msg = f"❌ FileMaker senkronizasyon hatası: {e}"
        if silent:
            print(msg)
        return {"status": "error", "message": msg}

    finally:
        if connection:
            connection.close()
