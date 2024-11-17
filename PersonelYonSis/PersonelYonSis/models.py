from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

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
        return self.Username

