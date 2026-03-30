# Kayseri Devlet Hastanesi - Mesai Entegrasyon API

---

## Baglanti Bilgileri

**Endpoint:** `POST http://10.38.8.115:5000/api/v1/kayseri/mesai/sync`

**API Key (her istekte header olarak gonderilmeli):**
```
x-api-key: dkod_kayseri_7b3f9a2e1d5c8f4061e2b7a9d3c5f812
```

---

## Ne Yapmalisiniz

Mesai tablosunda bir degisiklik oldugunda (kayit ekleme, silme, guncelleme), ilgili birimin o donemdeki **tum mesai listesini** asagidaki formatta gonderin. Biz eski kayitlari silip yenilerini yazariz.

**Istek:**
```json
{
  "birimId": 5,
  "birimAdi": "Mavi Kod 1",
  "donem": "2026-03",
  "mesailar": [
    {
      "tckn": "12345678901",
      "tarih": "2026-03-15",
      "baslangic": "08:00",
      "bitis": "16:00",
      "mesaiNotu": "M1",
      "onayDurumu": true,
      "izinli": false
    },
    {
      "tckn": "98765432101",
      "tarih": "2026-03-15",
      "baslangic": "16:00",
      "bitis": "08:00",
      "mesaiNotu": "M2",
      "onayDurumu": true,
      "izinli": false
    }
  ]
}
```

---

## Alan Aciklamalari

**Ust seviye:**

| Alan | Tip | Aciklama |
|------|-----|----------|
| birimId | int | Sizin sisteminizdeki birim ID |
| birimAdi | string | Birim adi (Mavi Kod 1, Guvenlik vs.) |
| donem | string | Ay bilgisi, format: YYYY-MM |

**Mesai satirlari:**

| Alan | Tip | Zorunlu | Format | Aciklama |
|------|-----|---------|--------|----------|
| tckn | string | Evet | 11 hane | T.C. kimlik numarasi |
| tarih | string | Evet | YYYY-MM-DD | Mesai tarihi |
| baslangic | string | Evet | HH:mm | Mesai baslangic saati |
| bitis | string | Evet | HH:mm | Mesai bitis saati |
| mesaiNotu | string | Hayir | Serbest | Gorev notu (M1, M2 vs.) |
| onayDurumu | boolean | Hayir | true/false | Onaylanmis mi (varsayilan: true) |
| izinli | boolean | Hayir | true/false | Izinli mi (varsayilan: false) |

---

## Yanitlar

**Basarili:**
```json
{
  "durum": "BASARILI",
  "toplam": 3,
  "eklenen": 3,
  "silinen": 0
}
```

**Kismi basarili (bazi personeller eslesmedi):**
```json
{
  "durum": "KISMI",
  "toplam": 5,
  "eklenen": 3,
  "eslesmeyenler": [
    { "tckn": "99999999999", "sebep": "Personel bulunamadi" }
  ]
}
```

**Beklemede (ilk gonderimde bir kerelik):**
```json
{
  "durum": "BEKLEMEDE",
  "mesaj": "Birim sisteme kaydedildi. DahiKOD admini eslestirmeyi yaptiktan sonra tekrar gonderin."
}
```

> Ilk kez bir birim gonderdiginizde bu yaniti alirsiniz. Bizim tarafta eslestirme yapildiktan sonra ayni istegi tekrar gonderdiginizde mesailer islenir. Bu islem her birim icin sadece bir kez yasanir.

---

## Limitler

- Tek istekte en fazla **5000 kayit**
- Dakikada en fazla **30 istek**

---

## Notlar

- Gece nobetinde bitis < baslangic ise (ornek: 16:00-08:00) otomatik hesaplanir.
- onayDurumu=false veya izinli=true olan kayitlar islenmez.
- TC kimlik numarasi ile personel eslestirilir. Bulunamayanlar yanit icerisinde raporlanir.
- Ayni birim+donem tekrar gonderildiginde onceki kayitlar silinip yenileri yazilir.
