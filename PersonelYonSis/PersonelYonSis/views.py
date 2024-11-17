from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout as auth_logout
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import LoginForm
from .models import Role, Permission, RolePermission, User
from django.contrib.auth.decorators import login_required
from .models import Permission

def get_user_permissions(user):
    if user.is_authenticated:
        return RolePermission.objects.filter(Role__in=user.roles.all()).values_list('Permission__PermissionName', flat=True)
    return []

def index(request):
    if request.user.is_authenticated:
        permissions = get_user_permissions(request.user)
        return render(request, 'index.html', {'permissions': permissions})
    else:
        return render(request, "login.html")

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            return render(request, 'login.html', {'error': 'Geçersiz kullanıcı adı veya şifre.'})
    return render(request, 'login.html')

def logout(request):
    auth_logout(request)
    return redirect('login')

def kullanici_tanimlari(request):
    users = User.objects.all()
    roles = Role.objects.all()

    return render(request, 'kullanici_tanimlari.html', {
        'users': users,
        'roles': roles,
    })

# Kullanıcının rollerini güncelleme
def update_roles(request, user_id):
    user = User.objects.get(UserID=user_id)
    selected_roles = request.POST.getlist('roles')  # Çoklu roller alınıyor
    user.role.set(selected_roles)  # Rolleri güncelle
    messages.success(request, f"{user.Username} kullanıcısının rolleri güncellendi.")
    return redirect('kullanici_tanimlari')

def yeni_kullanici_form(request):
    roles = Role.objects.all()
    return render(request, 'yeni_kullanici_form.html', {'roles': roles})

def kullanici_duzenle_form(request, user_id):
    user = User.objects.get(pk=user_id)
    roles = Role.objects.all()
    return render(request, 'kullanici_duzenle_form.html', {'user': user, 'roles': roles})
def update_user(request, user_id):
    if request.method == 'POST':
        # Kullanıcıyı bul
        user = get_object_or_404(User, UserID=user_id)
        
        # Güncellenebilir alanlar
        fullname = request.POST['fullname']
        roles = request.POST.getlist('roles')  # Çoklu roller alınıyor
        print(roles)
        # Eğer boş dönüyorsa formu inceleyin
        if not roles:
            print("Roller listesi boş döndü!")
        # Kullanıcıyı güncelle
        user.FullName = fullname
        # Seçilen rollerin ID'lerine göre Role nesnelerini çek
        role_objects = Role.objects.filter(RoleID__in=roles)
        user.roles.set(role_objects)  # Yeni roller atanıyor

        # Kullanıcıyı kaydet
        user.save()

        # Başarı mesajı
        messages.success(request, f"{user.Username} kullanıcısının bilgileri güncellendi.")
        return redirect('kullanici_tanimlari')
    return redirect('kullanici_tanimlari')

# Kullanıcının aktiflik durumunu güncelleme
def update_active_status(request, user_id):
    user = User.objects.get(UserID=user_id)
    user.is_active = 'is_active' in request.POST  # Checkbox kontrolü
    user.save()
    messages.success(request, f"{user.Username} kullanıcısının durumu güncellendi.")
    return redirect('kullanici_tanimlari')

# Şifre sıfırlama
def reset_password(request, user_id):
    user = User.objects.get(UserID=user_id)
    user.password = '123'  # Şifreyi "123" olarak ayarlama
    user.save()
    messages.success(request, f"{user.Username} kullanıcısının şifresi sıfırlandı.")
    return redirect('kullanici_tanimlari')

# Yeni kullanıcı ekleme
def add_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        fullname = request.POST['fullname']
        roles = request.POST.getlist('roles')  # Çoklu roller alınıyor

        # Yeni kullanıcı oluştur
        user = User.objects.create(
            Username=username,
            FullName=fullname,
            is_active=True,  # Varsayılan olarak aktif
            is_staff=False,  # Admin değil
            is_superuser=False,  # Süper kullanıcı değil
            password='123'  # Varsayılan şifre "123"
        )
        user.roles.set(roles)  # Kullanıcının rollerini ekle

        messages.success(request, f"{user.Username} kullanıcısı başarıyla eklendi.")
        return redirect('kullanici_tanimlari')
    return redirect('kullanici_tanimlari')


def rol_tanimlari(request):
    # Sistemdeki tüm roller
    roles = Role.objects.all()

    # Seçili rolün bilgilerini ve yetkilerini almak için kontrol
    selected_role = None
    selected_role_permissions = []
    if 'role' in request.GET:
        selected_role = Role.objects.get(RoleID=request.GET['role'])
        selected_role_permissions = RolePermission.objects.filter(Role=selected_role).select_related('Permission')

    # Tüm yetkileri almak
    all_permissions = Permission.objects.all().order_by('PermissionName')

    # Yetki ekleme işlemi
    if request.method == 'POST':
        if 'role_name' in request.POST:
            # Yeni rol ekleme
            role_name = request.POST['role_name']
            Role.objects.create(RoleName=role_name)
            return redirect('rol_tanimlari')

        if 'add_permission' in request.POST:
            # Yetki ekleme
            role_id = request.POST['role_id']
            permission_id = request.POST['permission_id']
            RolePermission.objects.create(Role_id=role_id, Permission_id=permission_id)
            return redirect('rol_tanimlari')

        if 'remove_permission' in request.POST:
            # Yetki silme
            role_id = request.POST['role_id']
            permission_id = request.POST['permission_id']
            RolePermission.objects.filter(Role_id=role_id, Permission_id=permission_id).delete()
            return redirect('rol_tanimlari')

    return render(request, 'rol_tanimlari.html', {
        'roles': roles,
        'selected_role': selected_role,
        'selected_role_permissions': selected_role_permissions,
        'all_permissions': all_permissions
    })

def add_role(request):
    if request.method == 'POST':
        role_name = request.POST.get('role_name')
        
        # Eğer rol adı mevcutsa, yeni rol oluştur
        if role_name:
            new_role, created = Role.objects.get_or_create(RoleName=role_name)
            
            if created:
                messages.success(request, 'Yeni rol başarıyla eklendi.')
            else:
                messages.warning(request, 'Bu rol zaten mevcut.')

        return redirect('rol_tanimlari')

    # Eğer POST değilse, bu fonksiyon direk rol_tanimlari sayfasına yönlendirir
    return redirect('rol_tanimlari')

# Yetki ekleme ve silme fonksiyonları
def add_permission_to_role(request, role_id, permission_id):
    # İlk olarak RolePermission kaydının zaten mevcut olup olmadığını kontrol edin
    existing_permission = RolePermission.objects.filter(Role_id=role_id, Permission_id=permission_id).exists()

    if existing_permission:
        # Eğer zaten eklenmişse, bir hata mesajı göster
        messages.warning(request, 'Bu yetki zaten bu role atanmış.')
    else:
        try:
            # Yeni RolePermission ekleyin
            RolePermission.objects.create(Role_id=role_id, Permission_id=permission_id)
            messages.success(request, 'Yetki başarıyla eklendi.')
        except IntegrityError:
            messages.error(request, 'Yetki eklenirken bir hata oluştu.')
    
    # Seçili role geri yönlendirme
    return redirect(f'/rol-tanimlari/?role={role_id}')

def remove_permission(request, role_id, permission_id):
    RolePermission.objects.filter(Role_id=role_id, Permission_id=permission_id).delete()
    # Seçili role geri yönlendirme
    return redirect(f'/rol-tanimlari/?role={role_id}')


def yetki_tanimlari(request):
    # Tüm yetkileri al
    permissions = Permission.objects.all()

    if request.method == 'POST':
        permission_name = request.POST.get('permission_name')
        Permission.objects.create(PermissionName=permission_name)
        return redirect('yetki_tanimlari')

    return render(request, 'yetki_tanimlari.html', {'permissions': permissions})