from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from PersonelYonSis.models import Notification
User = get_user_model()

def notify_role_users(role_name, title, message):
    """
    Belirli bir role sahip tüm kullanıcılara bildirim gönderir.
    """
    recipients = User.objects.filter(roles__RoleName=role_name, is_active=True)
    for user in recipients:
        add_notify(user, title, message)

    # E-posta bildirimi şimdilik kapalı
    # for user in recipients:
    #     send_notification(user, title, message)


def notify_user(user, title, message):
    """
    Tek bir kullanıcıya bildirim gönderir.
    """
    add_notify(user, title, message)
    # E-posta bildirimi şimdilik kapalı
    # send_notification(user, title, message)

def add_notify(recipient, title, message):
    Notification.objects.create(
        recipient=recipient,
        title=title,
        message=message
    )


def send_notification(user, title, message):
    """
    Bildirimi gönderir. Şimdilik email, ileride SMS, Whatsapp vb. eklenebilir.
    """
    if user.email:
        send_mail(
            subject=title,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True
        )
    # TODO: Burada sms/whatsapp vb. için fonksiyonları tetikleyebilirsin
    print(f"[Bildirim] {user.FullName} → {title}: {message}")

