# PersonelYonSis/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.forms.models import model_to_dict
from django.utils.timezone import now
from .models import AuditLog
from django.contrib.auth import get_user_model
from .middleware import get_current_request, get_current_user
from django.contrib.auth.signals import user_logged_in, user_logged_out
import datetime
from decimal import Decimal
import uuid

User = get_user_model()

def serialize_for_json(data):
    """Dict içindeki date/datetime/time objelerini stringe çevirir."""
    def convert(val):
        # handle Decimal (and similar) and UUID types which are not JSON serializable by default
        if isinstance(val, Decimal):
            return str(val)
        if isinstance(val, uuid.UUID):
            return str(val)
        if isinstance(val, (datetime.datetime, datetime.date, datetime.time)):
            return val.isoformat()
        if isinstance(val, dict):
            return {k: convert(v) for k, v in val.items()}
        if isinstance(val, list):
            return [convert(v) for v in val]
        return val
    return {k: convert(v) for k, v in data.items()}

def create_log(sender, instance, action, changes=None):
    """AuditLog kaydını oluşturan yardımcı fonksiyon"""
        
    # 🔹 Loglanacak modellerin listesi (app bazlı)
    ALLOWED_MODELS = {
        "mercis657": ["Birim", "UserBirim", "PersonelListesi", "SabitMesai", "PersonelListesiKayit", "Mesai", "MazeretKaydi", "ResmiTatil", "Bildirim", "YarimZamanliCalisma", "StopKaydi", "IlkListe"],  # sadece bu modeller loglansın
        "PersonelYonSis": ["Permission", "RolePermission", "User"],
        "mutemet_app": ["Sendika", "PersonelHareket", "SendikaUyelik", "IcraTakibi", "IcraHareketleri", "OdemeTakibi", "SilinenIcraTakibi"],
        "ik_core": ["Personel" "OzelDurum", "GeciciGorev", "PersonelBirim",],
        "nobet_defteri": ["NobetDefteri"],
        "sessions": ["Session"],
    }

    app_label = sender._meta.app_label
    model_name = sender.__name__

    # 🔸 Eğer model izinli listede değilse loglama
    if app_label not in ALLOWED_MODELS or model_name not in ALLOWED_MODELS[app_label]:
        return
    
    req = get_current_request()
    user = get_current_user()
    log_kwargs = {}

    if req:
        log_kwargs.update({
            "ip_address": req.META.get("REMOTE_ADDR"),
            "user_agent": req.META.get("HTTP_USER_AGENT"),
            "request_path": req.path,
            "request_method": req.method,
        })

    AuditLog.objects.create(
        user=user if user and user.is_authenticated else None,
        app_label=sender._meta.app_label,
        model_name=sender.__name__,
        object_id=str(getattr(instance, "pk", None)),
        action=action,
        changes=serialize_for_json(changes) if changes else None,
        **log_kwargs
    )

def log_auth_action(user, request, action):
    from .models import AuditLog
    AuditLog.objects.create(
        user=user if user and user.is_authenticated else None,
        app_label="auth",
        model_name="User",
        object_id=str(getattr(user, "pk", None)),
        action=action,
        changes=None,
        ip_address=request.META.get("REMOTE_ADDR"),
        user_agent=request.META.get("HTTP_USER_AGENT"),
        request_path=request.path,
        request_method=request.method,
    )

# CREATE & UPDATE
@receiver(post_save)
def log_save(sender, instance, created, **kwargs):
    if sender == AuditLog or sender == User:
        return
    action = "CREATE" if created else "UPDATE"
    create_log(sender, instance, action, model_to_dict(instance))

# DELETE
@receiver(post_delete)
def log_delete(sender, instance, **kwargs):
    if sender == AuditLog or sender == User:
        return
    create_log(sender, instance, "DELETE", None)

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    log_auth_action(user, request, "LOGIN")

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    log_auth_action(user, request, "LOGOUT")
