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

