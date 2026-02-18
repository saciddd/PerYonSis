from __future__ import annotations

"""
ZKBaglanti
==========

Bu modül, ZK (ZKTeco) tabanlı cihazlarla (örn. SC403) Django gibi
sunucu taraflı uygulamalarda kullanılmak üzere temel iletişim
fonksiyonlarını içerir.

Amaç:
- Her çağrıda otomatik olarak cihaza bağlanmak,
- İstenen işlemi yapmak (listele/ekle/sil),
- Ardından bağlantıyı güvenli şekilde sonlandırmak.

UI veya framework bağımsızdır; Django view'ları, DRF serializer'ları
vb. direkt bu fonksiyonları çağırabilir.
"""

from dataclasses import dataclass, asdict
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from zk import ZK, const


# Varsayılan cihaz ayarları.
# Django tarafında farklı ortamlar için override edebilirsiniz
# (örn. settings.py içinde ZK_... sabitleri ile).
DEFAULT_IP = None
DEFAULT_PORT = 4370
DEFAULT_TIMEOUT = 10
DEFAULT_PASSWORD = 0
DEFAULT_FORCE_UDP = True


@dataclass
class ZKUser:
    uid: int
    user_id: str
    name: str
    card: str
    privilege: int
    group_id: str

    @classmethod
    def from_device(cls, u: Any) -> "ZKUser":
        """Cihazdan dönen kullanıcı nesnesini normalize eder."""
        uid = int(getattr(u, "uid", 0) or 0)
        user_id = str(getattr(u, "user_id", "") or "")
        name = str(getattr(u, "name", "") or "")
        card_val = getattr(u, "card", getattr(u, "card_number", ""))  # geriye dönük uyumluluk
        card = str(card_val if card_val is not None else "")
        privilege = int(getattr(u, "privilege", 0) or 0)
        group_id = str(getattr(u, "group_id", "") or "")
        return cls(uid=uid, user_id=user_id, name=name, card=card, privilege=privilege, group_id=group_id)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ZKConnectionError(Exception):
    """Bağlantı veya cihaz seviyesi hatalar için genel exception."""


def _with_connection(
    fn,
    *,
    ip: str = DEFAULT_IP,
    port: int = DEFAULT_PORT,
    timeout: int = DEFAULT_TIMEOUT,
    password: int = DEFAULT_PASSWORD,
    force_udp: bool = DEFAULT_FORCE_UDP,
) -> Any:
    if ip is None:
        raise ValueError("Cihaz IP adresi belirtilmedi.")

    """
    Her çağrıda otomatik bağlan/çalıştır/kapat mantığı.

    Django view'ları genellikle tek bir istek içinde az sayıda
    cihaz çağrısı yapacağı için bu model basit ve güvenlidir.
    """
    try:
        zk = ZK(ip, port=port, timeout=timeout, password=password, force_udp=force_udp)
        conn = zk.connect()
    except Exception as e:  # noqa: BLE001
        raise ZKConnectionError(f"Cihaza bağlanırken hata oluştu: {e}") from e

    try:
        return fn(conn)
    finally:
        try:
            conn.disconnect()
        except Exception:
            # Bağlantı zaten kopmuş olabilir; HTTP cevabını bozmamak için swallow ediyoruz.
            pass


def _pick_available_uid(users: Sequence[Any]) -> int:
    """
    Cihazdaki mevcut kullanıcı listesine göre uygun bir UID seçer.

    UID genelde 1..65535 aralığında küçük integer olmalıdır.
    Kart ID / user_id ne kadar uzun olursa olsun UID bundan bağımsızdır.
    """
    used: set[int] = set()
    for u in users:
        try:
            used.add(int(getattr(u, "uid", 0)))
        except Exception:
            continue

    for cand in range(1, 65536):
        if cand not in used:
            return cand
    raise ZKConnectionError("Boş UID bulunamadı (UID havuzu dolu görünüyor).")


# ---------------------------------------------------------------------------
# Dışa açık temel fonksiyonlar
# ---------------------------------------------------------------------------

def list_users(
    *,
    ip: str = DEFAULT_IP,
    port: int = DEFAULT_PORT,
    timeout: int = DEFAULT_TIMEOUT,
    password: int = DEFAULT_PASSWORD,
    force_udp: bool = DEFAULT_FORCE_UDP,
) -> List[ZKUser]:
    """
    Cihazdaki tüm kullanıcıları döndürür.

    Django örneği:
        from .ZKBaglanti import list_users
        users = list_users()
        data = [u.to_dict() for u in users]
    """

    def op(conn):
        return conn.get_users()

    raw_users = _with_connection(op, ip=ip, port=port, timeout=timeout, password=password, force_udp=force_udp)
    return [ZKUser.from_device(u) for u in raw_users]


def add_user(
    name: str,
    card_id: str,
    *,
    ip: str = DEFAULT_IP,
    port: int = DEFAULT_PORT,
    timeout: int = DEFAULT_TIMEOUT,
    password: int = DEFAULT_PASSWORD,
    force_udp: bool = DEFAULT_FORCE_UDP,
) -> ZKUser:
    """
    Yeni kullanıcı ekler.

    Kurallar:
    - `card_id` ve `user_id` aynı olacak.
    - UID cihazdaki boş bir integer olarak OTOMATİK seçilecek.

    Django örneği (basit):
        from .ZKBaglanti import add_user
        user = add_user(name='Ali Veli', card_id='1234567')
    """
    card_id = str(card_id).strip()
    if not card_id:
        raise ValueError("card_id boş olamaz.")
    if not card_id.isdigit():
        raise ValueError("card_id sadece rakamlardan oluşmalıdır.")

    name = name.strip()
    if not name:
        raise ValueError("İsim boş olamaz.")

    user_id = card_id
    card = int(card_id)

    def op(conn):
        users = conn.get_users()
        uid = _pick_available_uid(users)

        conn.set_user(
            uid=uid,
            name=name,
            privilege=const.USER_DEFAULT,
            password="",
            group_id="",
            user_id=user_id,
            card=card,
        )
        try:
            conn.refresh_data()
        except Exception:
            # refresh_data her cihaz/firmware’de zorunlu değil; ekleme başarısız olsa bile
            # exception zaten üst katmanda görülecektir.
            pass

        # Bazı cihazlar yeni kullanıcıyı ancak tekrar get_users çağrısında net gösterir;
        # isterseniz tekrar sorgulayıp dönebiliriz.
        return ZKUser(uid=uid, user_id=user_id, name=name, card=str(card), privilege=const.USER_DEFAULT, group_id="")

    return _with_connection(op, ip=ip, port=port, timeout=timeout, password=password, force_udp=force_udp)


def delete_user(
    *,
    uid: Optional[int] = None,
    user_id: Optional[str] = None,
    ip: str = DEFAULT_IP,
    port: int = DEFAULT_PORT,
    timeout: int = DEFAULT_TIMEOUT,
    password: int = DEFAULT_PASSWORD,
    force_udp: bool = DEFAULT_FORCE_UDP,
) -> None:
    """
    Kullanıcı siler.

    - Tercihen hem `uid` hem `user_id` verilmesi daha güvenlidir.
    - En az bir tanesinin dolu olması gerekir.

    Django örneği:
        delete_user(uid=123)  # veya
        delete_user(user_id='1234567')
    """
    if uid is None and (user_id is None or str(user_id).strip() == ""):
        raise ValueError("Silme işlemi için en az uid veya user_id verilmelidir.")

    user_id_str = "" if user_id is None else str(user_id)

    def op(conn):
        conn.delete_user(uid=uid or 0, user_id=user_id_str)
        try:
            conn.refresh_data()
        except Exception:
            pass
        return True

    _with_connection(op, ip=ip, port=port, timeout=timeout, password=password, force_udp=force_udp)



def get_attendance(
    *,
    ip: str = DEFAULT_IP,
    port: int = DEFAULT_PORT,
    timeout: int = DEFAULT_TIMEOUT, # Uzun sürebilir, çağıran artırmalı
    password: int = DEFAULT_PASSWORD,
    force_udp: bool = DEFAULT_FORCE_UDP,
) -> List[Any]:
    """
    Cihazdaki katılım (giriş/çıkış) kayıtlarını getirir.
    """
    if ip is None:
        raise ValueError("Cihaz IP adresi belirtilmedi.")

    def op(conn):
        return conn.get_attendance()

    return _with_connection(op, ip=ip, port=port, timeout=timeout, password=password, force_udp=force_udp)

def get_storage_status_info(
    *,
    ip: str = DEFAULT_IP,
    port: int = DEFAULT_PORT,
    timeout: int = DEFAULT_TIMEOUT,
    password: int = DEFAULT_PASSWORD,
    force_udp: bool = DEFAULT_FORCE_UDP,
) -> Dict[str, Any]:
    """
    Cihazın depolama durumunu getirir.
    """
    if ip is None:
        raise ValueError("Cihaz IP adresi belirtilmedi.")
    
    def op(conn):
        # get_storage_status() genellikle bir string veya dict döner, kütüphaneye göre değişebilir
        # pyzk'da bu yöntem olmayabilir, extend_std_params ile bakabiliriz.
        # Ancak pyzk'da 'params' property'si veya get_extend_user_info vb. var.
        # Standart ZK kütüphanesinde conn.mid_get_device_status vb. olabilir. 
        # Fakat basitçe user count, log count alalım.
        
        # pyzk kütüphanesinde bu metod olmayabilir, varsa kullanırız.
        # Yoksa da basitçe user ve attendance sayısını manuel alabiliriz ama bu yavaş olur.
        # Genelde 'read_sizes' veya benzeri metod vardır.
        
        # Kullanıcı talebi: conn.get_storage_status() komutu ile... 
        # Demek ki kullanıcı pyzk kütüphanesinde bunun olduğunu biliyor veya varsayıyor.
        try:
             return conn.get_storage_status()
        except AttributeError:
             # Eğer metod yoksa fallback
             users = len(conn.get_users())
             att = len(conn.get_attendance())
             return {"users": users, "attendance": att, "status": "Fallback (counted)"}
    
    return _with_connection(op, ip=ip, port=port, timeout=timeout, password=password, force_udp=force_udp)

def sync_device_time(
    *,
    ip: str = DEFAULT_IP,
    port: int = DEFAULT_PORT,
    timeout: int = DEFAULT_TIMEOUT,
    password: int = DEFAULT_PASSWORD,
    force_udp: bool = DEFAULT_FORCE_UDP,
) -> None:
    """
    Cihaz saatini sunucu saati ile eşitler.
    """
    from datetime import datetime
    if ip is None:
        raise ValueError("Cihaz IP adresi belirtilmedi.")

    def op(conn):
        conn.set_time(datetime.now())
        return True

    _with_connection(op, ip=ip, port=port, timeout=timeout, password=password, force_udp=force_udp)


__all__ = [
    "ZKUser",
    "ZKConnectionError",
    "list_users",
    "add_user",
    "delete_user",
    "get_attendance",
    "get_storage_status_info",
    "sync_device_time",
    "DEFAULT_IP",
    "DEFAULT_PORT",
    "DEFAULT_TIMEOUT",
    "DEFAULT_PASSWORD",
    "DEFAULT_FORCE_UDP",
]

