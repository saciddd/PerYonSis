"""
ADMS/Push Protokolü - HTTP Endpoint'leri
=========================================

Bu modül, ZKTeco/Perkotek tabanlı cihazların ADMS (Push) protokolü
üzerinden Django sunucusuna veri göndermesi için gereken HTTP
endpoint'lerini içerir.

Protokol Akışı:
1. Cihaz periyodik olarak GET /iclock/getrequest ile komut polling yapar
2. Cihaz POST /iclock/cdata ile yoklama/operasyon loglarını gönderir
3. Cihaz POST /iclock/devicecmd ile komut sonuçlarını bildirir

Cihaz Konfigürasyonu:
- Sunucu Adresi: http://SUNUCU_IP:PORT/cardcontrol
- Cihaz menüsünden: Comm. → Cloud Server / ADMS
"""

import logging
import os
from datetime import datetime

from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import Cihaz, CihazLog, CihazKullanici, ADMSKomutKuyrugu, ADMSHamLog

logger = logging.getLogger(__name__)

# Debug: Dosyaya log yazma (cihazdan istek gelip gelmediğini görmek için)
ADMS_LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'adms_debug.log')

def _adms_debug_log(message):
    """Her ADMS isteğini dosyaya yazar — debug amaçlı."""
    try:
        with open(ADMS_LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Yardımcı Fonksiyonlar
# ---------------------------------------------------------------------------

def _get_cihaz_by_sn(seri_no):
    """
    Seri numarasına göre cihazı bulur.
    Bulunamazsa None döner ve log yazar.
    """
    if not seri_no:
        logger.warning("ADMS: İstek SN parametresi içermiyor.")
        return None

    try:
        return Cihaz.objects.get(seri_no=seri_no, adms_aktif=True)
    except Cihaz.DoesNotExist:
        logger.warning(f"ADMS: Tanımsız veya inaktif cihaz SN={seri_no}")
        return None


def _parse_attlog(line):
    """
    ATTLOG satırını parse eder.
    Format: PIN\tTimestamp\tVerifyStatus\tStatus\tWorkCode
    Örnek: 1001\t2026-04-29 10:00:00\t1\t0\t0\t0
    """
    fields = line.strip().split('\t')
    if len(fields) < 2:
        return None

    try:
        pin = fields[0].strip()
        timestamp_str = fields[1].strip()
        verify_status = int(fields[2].strip()) if len(fields) > 2 else 0
        status = int(fields[3].strip()) if len(fields) > 3 else 0

        # Timestamp formatı: YYYY-MM-DD HH:MM:SS
        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
        timestamp = timezone.make_aware(timestamp, timezone.get_current_timezone())

        return {
            'pin': pin,
            'timestamp': timestamp,
            'verify_status': verify_status,
            'status': status,
        }
    except (ValueError, IndexError) as e:
        logger.error(f"ADMS: ATTLOG parse hatası: {line!r} → {e}")
        return None


def _save_attlog_records(cihaz, records_text):
    """
    ATTLOG verilerini parse edip veritabanına kaydeder.
    Tekrar eden kayıtları (aynı user_id + timestamp) atlar.
    """
    lines = records_text.strip().split('\n')
    created_count = 0
    skipped_count = 0
    error_count = 0

    for line in lines:
        line = line.strip()
        if not line:
            continue

        parsed = _parse_attlog(line)
        if not parsed:
            error_count += 1
            continue

        # Mükerrer kontrolü
        exists = CihazLog.objects.filter(
            cihaz=cihaz,
            user_id=parsed['pin'],
            timestamp=parsed['timestamp']
        ).exists()

        if exists:
            skipped_count += 1
            continue

        CihazLog.objects.create(
            cihaz=cihaz,
            uid=0,  # ADMS üzerinden uid bilgisi gelmiyor, pin (user_id) kullanılır
            user_id=parsed['pin'],
            timestamp=parsed['timestamp'],
            status=parsed['status'],
            verification=parsed['verify_status'],
        )
        created_count += 1

    logger.info(
        f"ADMS ATTLOG [{cihaz.kapi_adi}]: "
        f"{created_count} yeni, {skipped_count} mükerrer, {error_count} hata"
    )
    return created_count, skipped_count, error_count


# ---------------------------------------------------------------------------
# ADMS Endpoint'leri
# ---------------------------------------------------------------------------

@csrf_exempt
@require_http_methods(["GET", "POST"])
def iclock_cdata(request):
    """
    /iclock/cdata endpoint'i
    
    GET: Cihaz ilk bağlantıda handshake / registry bilgisi gönderir.
    POST: Cihaz yoklama (ATTLOG) ve operasyon (OPERLOG) loglarını gönderir.
    
    Query Parametreleri:
        SN: Cihaz seri numarası
        table: Veri tablosu (ATTLOG, OPERLOG, USERINFO vb.)
        Stamp: Zaman damgası
    """
    # Debug: Gelen her isteği dosyaya yaz
    _adms_debug_log(
        f">>> CDATA {request.method} | Path={request.get_full_path()} | "
        f"IP={request.META.get('REMOTE_ADDR')} | "
        f"Headers={dict(request.headers)}"
    )

    seri_no = request.GET.get('SN', '')
    table = request.GET.get('table', '')
    stamp = request.GET.get('Stamp', '')

    _adms_debug_log(f"    CDATA parsed: SN={seri_no}, table={table}, Stamp={stamp}")

    logger.info(
        f"ADMS cdata [{request.method}]: SN={seri_no}, table={table}, "
        f"Stamp={stamp}"
    )

    if request.method == 'GET':
        # Handshake / İlk bağlantı
        # Bazı cihazlar ilk bağlantıda GET ile registry bilgisi gönderir
        cihaz = _get_cihaz_by_sn(seri_no)
        if cihaz:
            cihaz.son_heartbeat = timezone.now()
            cihaz.save(update_fields=['son_heartbeat'])
            logger.info(f"ADMS: Cihaz handshake başarılı: {cihaz.kapi_adi}")

        # Cihaz tanımsız olsa bile OK dönüyoruz (cihazın tekrar denemesini engellemek için)
        return HttpResponse("OK", content_type="text/plain")

    # POST: Veri alımı
    cihaz = _get_cihaz_by_sn(seri_no)

    try:
        body = request.body.decode('utf-8')
    except UnicodeDecodeError:
        body = request.body.decode('latin-1', errors='replace')

    logger.debug(f"ADMS cdata body: {body[:500]}")

    # Ham veriyi kaydet (debug amaçlı)
    if cihaz and body.strip():
        ham_log = ADMSHamLog.objects.create(
            cihaz=cihaz,
            tablo=table or 'BILINMIYOR',
            ham_veri=body,
            islem_durumu='BEKLEMEDE'
        )

        try:
            if table == 'ATTLOG':
                created, skipped, errors = _save_attlog_records(cihaz, body)
                ham_log.islem_durumu = 'ISLENDI'
                ham_log.save(update_fields=['islem_durumu'])

            elif table == 'OPERLOG':
                # Operasyon logları şimdilik sadece ham olarak kaydedilir
                ham_log.islem_durumu = 'ISLENDI'
                ham_log.save(update_fields=['islem_durumu'])
                logger.info(f"ADMS OPERLOG [{cihaz.kapi_adi}]: Ham veri kaydedildi")

            else:
                # Diğer tablolar (USERINFO, FPTEMPLATE vb.)
                ham_log.islem_durumu = 'ISLENDI'
                ham_log.save(update_fields=['islem_durumu'])
                logger.info(f"ADMS [{cihaz.kapi_adi}]: Bilinmeyen tablo={table}, ham veri kaydedildi")

        except Exception as e:
            ham_log.islem_durumu = 'HATA'
            ham_log.hata_mesaji = str(e)
            ham_log.save(update_fields=['islem_durumu', 'hata_mesaji'])
            logger.error(f"ADMS cdata işleme hatası: {e}")

    elif not cihaz:
        logger.warning(f"ADMS cdata: Tanımsız cihaz SN={seri_no}, veri kaydedilmedi")

    return HttpResponse("OK", content_type="text/plain")


@csrf_exempt
@require_http_methods(["GET"])
def iclock_getrequest(request):
    """
    /iclock/getrequest endpoint'i
    
    Cihaz periyodik olarak (genellikle 30-60 saniyede bir) bu endpoint'e
    GET isteği atarak bekleyen komut olup olmadığını kontrol eder.
    
    Query Parametreleri:
        SN: Cihaz seri numarası
    
    Yanıt:
        - Komut varsa: "C:<KomutID>:<KomutTipi> <Parametreler>"
        - Komut yoksa: "OK"
    """
    # Debug: Gelen her isteği dosyaya yaz
    _adms_debug_log(
        f">>> GETREQUEST {request.method} | Path={request.get_full_path()} | "
        f"IP={request.META.get('REMOTE_ADDR')}"
    )

    seri_no = request.GET.get('SN', '')
    _adms_debug_log(f"    GETREQUEST parsed: SN={seri_no}")

    cihaz = _get_cihaz_by_sn(seri_no)
    if not cihaz:
        # Tanımsız cihaza da OK döneriz (cihaz hata almasın)
        return HttpResponse("OK", content_type="text/plain")

    # Son heartbeat güncelle
    cihaz.son_heartbeat = timezone.now()
    cihaz.save(update_fields=['son_heartbeat'])

    # Bekleyen komutları kontrol et
    pending_commands = ADMSKomutKuyrugu.objects.filter(
        cihaz=cihaz,
        gonderildi=False
    ).order_by('olusturulma')

    if pending_commands.exists():
        # İlk bekleyen komutu gönder
        cmd = pending_commands.first()
        cmd_str = f"C:{cmd.komut_id}:{cmd.komut_tipi}"
        if cmd.parametreler:
            cmd_str += f" {cmd.parametreler}"

        # Komutu gönderildi olarak işaretle
        cmd.gonderildi = True
        cmd.gonderilme_zamani = timezone.now()
        cmd.save(update_fields=['gonderildi', 'gonderilme_zamani'])

        logger.info(f"ADMS getrequest [{cihaz.kapi_adi}]: Komut gönderildi → {cmd_str}")
        return HttpResponse(cmd_str, content_type="text/plain")

    return HttpResponse("OK", content_type="text/plain")


@csrf_exempt
@require_http_methods(["POST"])
def iclock_devicecmd(request):
    """
    /iclock/devicecmd endpoint'i
    
    Cihaz, bir komutu uyguladıktan sonra sonucu bu endpoint'e bildirir.
    """
    # Debug: Gelen her isteği dosyaya yaz
    _adms_debug_log(
        f">>> DEVICECMD {request.method} | Path={request.get_full_path()} | "
        f"IP={request.META.get('REMOTE_ADDR')}"
    )

    seri_no = request.GET.get('SN', '')

    logger.info(f"ADMS devicecmd: SN={seri_no}")

    try:
        body = request.body.decode('utf-8')
    except UnicodeDecodeError:
        body = request.body.decode('latin-1', errors='replace')

    logger.info(f"ADMS devicecmd body: {body[:500]}")

    cihaz = _get_cihaz_by_sn(seri_no)
    if cihaz:
        # Komut sonucunu ham log olarak kaydet
        ADMSHamLog.objects.create(
            cihaz=cihaz,
            tablo='DEVICECMD_RESPONSE',
            ham_veri=body,
            islem_durumu='ISLENDI'
        )

    return HttpResponse("OK", content_type="text/plain")


@csrf_exempt
def iclock_catchall(request, subpath=''):
    """
    Catch-all: Cihaz beklenmedik bir /iclock/ path'ine istek atarsa yakala ve logla.
    Debug amaçlı — hangi endpoint'e istek geldiğini görmek için.
    """
    _adms_debug_log(
        f">>> CATCHALL {request.method} | Path={request.get_full_path()} | "
        f"subpath={subpath} | IP={request.META.get('REMOTE_ADDR')} | "
        f"Headers={dict(request.headers)}"
    )
    try:
        body = request.body.decode('utf-8', errors='replace')
        if body:
            _adms_debug_log(f"    CATCHALL body: {body[:500]}")
    except Exception:
        pass

    return HttpResponse("OK", content_type="text/plain")

