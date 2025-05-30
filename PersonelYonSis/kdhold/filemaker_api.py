from datetime import datetime
import fmrest
import json
import requests
requests.packages.urllib3.disable_warnings()

""" FileMaker Server API ile veri işlemleri 
Bu modül, FileMaker Server API'sini kullanarak veri işlemleri yapar.

Fonksiyonlar için gereken Filemaker Layout ve Field bilgileri şu şekildedir:
--------------------------------------------------------------
get_birimler: Birimler_API layout'unda BirimID ve BirimAdi alanları olmalıdır.
check_login: Kullanici_API layout'unda UserID ve UserPassword alanları olmalıdır.
get_personel_data: Personel_API layout'unda PersonelBirimID alanı olmalıdır.
get_mesai_data: Mesai_API layout'unda Personel ID ve Mesai Günü alanları olmalıdır.
get_schedule_data: Personel_API ve Mesai_API layout'larında gerekli alanlar olmalıdır.
get_mesai_tanimlari: MesaiTanimlari_API layout'unda Saat alanı olmalıdır.
update_schedule_data: Mesai_API layout'unda Mesai ID alanı olmalıdır.
--------------------------------------------------------------

"""

# Global değişkenler
user_cache = {}  # Kullanıcı bilgilerini tutacak cache

# FileMaker Server bilgileri
FILEMAKER_SERVER = "https://127.0.0.1"
DATABASE_NAME = "Mercis_Memur"
LAYOUT_NAME = "Personeller_API"

# Oturum açma bilgileri
USERNAME = "admin"
PASSWORD = "polat123"

# Sistemdeki birimleri getir
def get_birimler():
    # FileMaker sunucusuna bağlan
    fms = fmrest.Server(
        url=FILEMAKER_SERVER,
        user=USERNAME,
        password=PASSWORD,
        database=DATABASE_NAME,
        layout="Birimler_API",
        api_version='vLatest',
        verify_ssl=False  # SSL doğrulamasını devre dışı bırak
    )
    fms.login()

    # FileMaker sunucusundan veri sorgulamak için boş bir sorgu gönder
    query = [{'BirimID': '>0'}]
    records = fms.find(query)
    fms.logout()

    # Birimleri dict listesi olarak döndür
    birimler = []
    for record in records:
        birimler.append({
            "ID": record["BirimID"],
            "Name": record["BirimAdi"]
        })

    return birimler


# Kullanıcı girişini kontrol et
def check_login(tc, sifre):
    # FileMaker sunucusuna bağlan
    fms = fmrest.Server(
        url=FILEMAKER_SERVER,
        user=USERNAME,
        password=PASSWORD,
        database=DATABASE_NAME,
        layout="Kullanici_API",
        api_version='vLatest',
        verify_ssl=False
    )    
    fms.login()
    
    # Kullanıcı tablosundaki UserID ve UserPassword alanlarını kontrol et
    query = [{'UserID': tc, 'UserPassword': sifre}]
    records = fms.find(query)
    fms.logout()
    
    # Eğer kullanıcı kaydı varsa Yetkili Olduğu Birimler'i döndür
    if records:
        # Kullanıcı bilgilerini alın
        user_record = records[0]
        
        # Kullanıcı bilgilerini cache'e kaydet
        global user_cache
        user_cache = {
            "tc": user_record["UserID"],
            "username": user_record["UserName"],
        }
        
        # Her biri paragraf olarak ayrılmış olan birimleri listeye çevir
        birim = records[0]["Yetkili Olduğu Birimler"]
        birimler = birim.split("\r")
        # tüm birimleri çek
        all_birimler = get_birimler()
        # Yetkili birimlerin ID'lerinin ve isimlerinin listesini oluştur
        yetkili_birimler = []
        for birim_ismi in birimler:
            for b in all_birimler:
                if b["Name"] == birim_ismi:
                    yetkili_birimler.append(b)
        return yetkili_birimler
    else:
        return None

def check_session():
    """Mevcut oturum bilgilerini kontrol eder"""
    return bool(user_cache.get('username') and user_cache.get('tc'))

def refresh_session(tc, password):
    """Oturumu yeniler ve sonucu döndürür"""
    try:
        result = check_login(tc, password)
        return bool(result)
    except Exception as e:
        print(f"Session yenileme hatası: {e}")
        return False

# Personel verilerini getir
def get_personel_data(BirimID):
    # FileMaker sunucusuna bağlan
    fms = fmrest.Server(
        url=FILEMAKER_SERVER,
        user=USERNAME,
        password=PASSWORD,
        database=DATABASE_NAME,
        layout="Personel_API",
        api_version='vLatest',
        verify_ssl=False  # SSL doğrulamasını devre dışı bırak
    )    
    fms.login()

    # FileMaker sunucusundan veri sorgula
    query = [{'PersonelBirimID': BirimID}]
    records = fms.find(query)
    fms.logout()
    
    return records

# Mesai verilerini getir
def get_mesai_data(PersonelID, BaslangicTarihi, BitisTarihi):
    # FileMaker sunucusuna bağlan
    fms = fmrest.Server(
        url=FILEMAKER_SERVER,
        user=USERNAME,
        password=PASSWORD,
        database=DATABASE_NAME,
        layout='Mesai_API',
        api_version='vLatest',
        verify_ssl=False  # SSL doğrulamasını devre dışı bırak
    )    
    fms.login()

    # FileMaker sunucusundan veri sorgula
    query = [{'Personel ID': PersonelID, 'Mesai Günü': f"{BaslangicTarihi}...{BitisTarihi}"}]
    records = fms.find(query, limit=100)
            
    fms.logout()
    
    return records

# Schedule verilerini getir
def get_schedule_data(Birim_id, BaslangicTarihi, BitisTarihi):
    # get_personel_data ve get_mesai_data fonksiyonlarından faydalanarak tablo verisi hazırlanacak
    personeller = get_personel_data(Birim_id)
    schedule_data = []
    for personel in personeller:
        mesai_data = get_mesai_data(personel["PersonelID"], BaslangicTarihi, BitisTarihi)
        for mesai in mesai_data:
            schedule_data.append({
                "ID": mesai["Mesai ID"],
                "Name": personel["PersonelAdiSoyadi"],
                "ListeSirasi": personel["Liste Sırası"],
                "PersonelAciklama": personel["PersonelAciklama"],
                "Date": mesai["Mesai Günü"],
                "Data": mesai["Mesai Bilgileri"]
            })
    return schedule_data

# Tanımlanabilecek Mesai Verilerini çek
def get_mesai_tanimlari():
    # FileMaker sunucusuna bağlan
    fms = fmrest.Server(
        url=FILEMAKER_SERVER,
        user=USERNAME,
        password=PASSWORD,
        database=DATABASE_NAME,
        layout='MesaiTanimlari_API',
        api_version='vLatest',
        verify_ssl=False  # SSL doğrulamasını devre dışı bırak
    )
    fms.login()

    try:
        # FileMaker sunucusundan veri sorgula
        query = [{'Saat': '*'}]
        records = fms.find(query)

        # Mesai tanımlarını dict listesi olarak döndür
        mesai_tanimlari = []
        for record in records:
            try:
                mesai_tanimlari.append({
                    "Saat": record["Saat"]  # "Name" yerine "Saat" kullan
                })
            except KeyError as e:
                print(f"Kayıt yapısı hatası: {e} - Tam kayıt: {record}")
                continue

        return mesai_tanimlari

    except Exception as e:
        print(f"Mesai tanımları çekilirken hata: {e}")
        return []

    finally:
        fms.logout()

# Mesai verilerini güncelle
def update_schedule_data(record_id, updated_data, tc=None):
    """Mesai ID alanını kullanarak kayıt günceller."""
    if not check_session():
        raise SessionError("Oturum bilgisi bulunamadı")
    fms = fmrest.Server(
        url=FILEMAKER_SERVER,
        user=USERNAME,
        password=PASSWORD,
        database=DATABASE_NAME,
        layout='Mesai_API',
        api_version='vLatest',
        verify_ssl=False
    )
    fms.login()
    try:
        query = [{'Mesai ID': record_id}]
        records = fms.find(query)
        if not records:
            raise Exception(f"Kayıt bulunamadı: {record_id}")
        record = records[0]
        current_mesai = record['Mesai Bilgileri']
        current_log = record["Log"]
        current_onay = record["OnayDurumu"]
        talep_oncesi = record["TalepOncesi"]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if current_onay == "Onaylandı":
            if updated_data == talep_oncesi:
                new_log_entry = (
                    f"Değişiklik talebi: {current_mesai} - Vazgeçildi / "
                    f"{timestamp} - "
                    f"{user_cache['username']} - {user_cache['tc']}"
                )
                record["TalepOncesi"] = ""
            else:
                new_log_entry = (
                    f"Asıl Mesai: {current_mesai} - Talep edilen: {updated_data} / "
                    f"{timestamp} - "
                    f"{user_cache['username']} - {user_cache['tc']}"
                )
                record["TalepOncesi"] = current_mesai
        else:
            new_log_entry = (
                f"Öncesi: {current_mesai} - "
                f"Sonrası: {updated_data} / {timestamp} - "
                f"{user_cache['username']} - {user_cache['tc']}"
            )   
        new_log_entry += "\n"
        updated_log = f"{current_log}{new_log_entry}"
        record['Mesai Bilgileri'] = updated_data
        record['Log'] = updated_log
        success = fms.edit(record)
        if not success:
            raise Exception("Güncelleme başarısız oldu")
        return True
    except Exception as e:
        print(f"Güncelleme hatası: {e}")
        raise
    finally:
        fms.logout()
# Özel hata sınıfı ekleyelim
class SessionError(Exception):
    pass
