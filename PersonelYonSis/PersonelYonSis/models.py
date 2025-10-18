from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator
from django.utils.timezone import now

class Role(models.Model):
    RoleID = models.AutoField(primary_key=True)
    RoleName = models.CharField(max_length=100, null=False)
    class Meta:
        db_table = 'Roles'  # Veritabanındaki tablo adı

    def __str__(self):
        return self.RoleName

class Permission(models.Model):
    PermissionID = models.AutoField(primary_key=True)
    PermissionName = models.CharField(max_length=100, null=False)
    class Meta:
        db_table = 'Permissions'  # Veritabanındaki tablo adı

    def __str__(self):
        return self.PermissionName

class RolePermission(models.Model):
    Role = models.ForeignKey(Role, on_delete=models.CASCADE)
    Permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    class Meta:
        db_table = 'RolePermissions'  # Veritabanındaki tablo adı
        unique_together = (('Role', 'Permission'),)

class UserManager(BaseUserManager):
    def create_user(self, Username, Password=None, **extra_fields):
        if not Username:
            raise ValueError("Kullanıcı adı gereklidir")
        user = self.model(Username=Username, **extra_fields)
        user.set_password(Password)  # Şifreyi hash'ler
        user.save(using=self._db)
        return user

    def create_superuser(self, Username, Password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(Username, Password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    UserID = models.AutoField(primary_key=True)
    Username = models.CharField(max_length=100, unique=True)
    FullName = models.CharField(max_length=150)
    Email = models.EmailField(max_length=255, null=True, blank=True)
    Phone = models.CharField(
        max_length=10,
        validators=[RegexValidator(regex=r'^5\d{9}$', message="Telefon numarası 5xxxxxxxxx formatında olmalıdır.")],
        null=True,
        blank=True
    )
    TCKimlikNo = models.CharField(max_length=11, unique=True, null=True, blank=True)
    Organisation = models.CharField(max_length=255, null=True, blank=True)
    CreationTime = models.DateTimeField(default=now)
    roles = models.ManyToManyField('Role', blank=True)  # Bir kullanıcıya birden fazla rol atanabilir

    # Zorunlu alanlar ve kullanıcı adı alanı
    USERNAME_FIELD = 'Username'
    REQUIRED_FIELDS = ['FullName']  # Sadece gerekli alanlar

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    class Meta:
        db_table = 'Users'  # Veritabanındaki tablo adı

    def __str__(self):
        return self.FullName

    def has_permission(self, permission_name):
        """
        Checks if the user has a specific permission, either directly
        or through their assigned roles.
        """
        # Check direct permissions (if you implement direct user permissions later)
        # if self.permissions.filter(PermissionName=permission_name).exists():
        #     return True

        # Check permissions through roles
        if self.roles.filter(rolepermission__Permission__PermissionName=permission_name).exists():
            return True

        # Check if the user is a superuser (implicitly has all permissions)
        if self.is_superuser:
            return True

        return False
class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class AuditLog(models.Model):
    ACTION_CHOICES = [
        ("CREATE", "Create"),
        ("UPDATE", "Update"),
        ("DELETE", "Delete"),
        ("LOGIN", "Login"),
        ("LOGOUT", "Logout"),
    ]

    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    # Nerede yapıldı?
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    request_path = models.CharField(max_length=200, null=True, blank=True)
    request_method = models.CharField(max_length=10, null=True, blank=True)

    # Hangi model/nesne?
    app_label = models.CharField(max_length=100)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=50, null=True, blank=True)

    # Ne yapıldı?
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    changes = models.JSONField(null=True, blank=True)  # önce/sonra değişiklikler

    class Meta:
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"
        ordering = ['-timestamp']

    def __str__(self):
        user_str = str(self.user) if self.user else "Anonim"
        return f"[{self.timestamp:%Y-%m-%d %H:%M:%S}] {user_str} {self.action} {self.model_name}({self.object_id})"
