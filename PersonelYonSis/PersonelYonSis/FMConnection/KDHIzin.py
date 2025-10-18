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

def sync_personel_to_filemaker(personel):
    """
    Django Personel kaydını FileMaker'a senkronize eder.
    Eğer kayıt varsa UPDATE, yoksa INSERT yapar.
    """
    global connection
    try:
        connection = pyodbc.connect(conn_str)
        cursor = connection.cursor()

        # 1️⃣ Kayıt var mı kontrol et
        check_sql = 'SELECT "TCKimlikNo" FROM Personeller WHERE "TCKimlikNo" = ?'
        cursor.execute(check_sql, (personel.tc_kimlik_no,))
        existing = cursor.fetchone()

        # Ortak alan listesi
        data = [
            int(personel.aday_memur or 0),
            personel.ad or "",
            personel.adres or "",
            personel.atama_karar_no or "",
            format_date_for_filemaker(personel.atama_karar_tarihi),
            personel.brans or "",
            personel.cinsiyet or "",
            format_date_for_filemaker(personel.dogum_tarihi),
            personel.durum or "",
            format_date_for_filemaker(personel.goreve_baslama_tarihi),
            personel.kadro_durumu or "",
            personel.ayrilma_nedeni or "",
            personel.ayrilma_detay or "",
            personel.memuriyet_durumu or "",
            format_date_for_filemaker(personel.memuriyete_baslama_tarihi),
            personel.sicil_no or "",
            personel.soyad or "",
            int(personel.tc_kimlik_no),
            personel.telefon or "",
            personel.teskilat or "",
            personel.unvan or "",
        ]

        if existing:
            # 2️⃣ Güncelleme işlemi
            update_sql = """
                UPDATE Personeller SET
                    "AdayMemur?"=?,
                    "Adi"=?,
                    "Adres"=?,
                    "AtamaKararNo"=?,
                    "AtamaKararTarihi"=?,
                    "Brans"=?,
                    "Cinsiyet"=?,
                    "Doğum Tarihi"=?,
                    "Durum"=?,
                    "GoreveBaslamaTarihi"=?,
                    "KadroDurumu"=?,
                    "KurumdanAyrilmaNedeni"=?,
                    "KurumdanAyrilmaNedeniDetay"=?,
                    "MemuriyetDurumu"=?,
                    "Memuriyete Başlama Tarihi"=?,
                    "SicilNo"=?,
                    "Soyadi"=?,
                    "TCKimlikNo"=?,
                    "Telefon"=?,
                    "Teşkilat"=?,
                    "Unvan"=?
                WHERE "TCKimlikNo"=?
            """
            cursor.execute(update_sql, data + [personel.tc_kimlik_no])
            print(f"🟡 Güncellendi: {personel.ad} {personel.soyad}")

        else:
            # 3️⃣ Yeni kayıt ekleme
            insert_sql = """
                INSERT INTO Personeller (
                    "AdayMemur?",
                    "Adi",
                    "Adres",
                    "AtamaKararNo",
                    "AtamaKararTarihi",
                    "Brans",
                    "Cinsiyet",
                    "Doğum Tarihi",
                    "Durum",
                    "GoreveBaslamaTarihi",
                    "KadroDurumu",
                    "KurumdanAyrilmaNedeni",
                    "KurumdanAyrilmaNedeniDetay",
                    "MemuriyetDurumu",
                    "Memuriyete Başlama Tarihi",
                    "SicilNo",
                    "Soyadi",
                    "TCKimlikNo",
                    "Telefon",
                    "Teşkilat",
                    "Unvan"
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(insert_sql, data)
            print(f"🟢 Eklendi: {personel.ad} {personel.soyad}")

        connection.commit()

    except pyodbc.Error as e:
        print(f"❌ FileMaker senkronizasyon hatası: {e}")

    finally:
        if connection:
            connection.close()
