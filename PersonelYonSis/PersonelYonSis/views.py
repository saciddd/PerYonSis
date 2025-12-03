from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout as auth_logout
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import LoginForm
from .models import Role, Permission, RolePermission, User, Notification, AuditLog, Duyuru, Istek
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from notifications.services import notify_role_users, notify_user
from django.core.paginator import Paginator
from django.db.models import Q
# Yeni eklenen importlar
from django.views.decorators.http import require_POST
from .forms import ProfileForm, PasswordChangeForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .middleware import get_current_request, get_current_user
import json

@login_required
def audit_log_list(request):
    logs = AuditLog.objects.select_related("user").all()

    # Filtreler
    date_start = request.GET.get("date_start")
    date_end = request.GET.get("date_end")
    user = request.GET.get("user")
    app_label = request.GET.get("app_label")
    model_name = request.GET.get("model_name")

    if date_start:
        logs = logs.filter(timestamp__date__gte=date_start)
    if date_end:
        logs = logs.filter(timestamp__date__lte=date_end)
    if user:
        logs = logs.filter(user__Username__icontains=user)
    if app_label:
        logs = logs.filter(app_label__icontains=app_label)
    if model_name:
        logs = logs.filter(model_name__icontains=model_name)

    paginator = Paginator(logs, 25)  # sayfa başı 25 kayıt
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # JSON verilerini güzel formatla decode et (yalnızca mevcut sayfadaki kayıtlar için)
    for log in page_obj:
        try:
            if log.changes:
                if isinstance(log.changes, str):
                    log.pretty_changes = json.dumps(json.loads(log.changes), indent=2, ensure_ascii=False)
                else:
                    log.pretty_changes = json.dumps(log.changes, indent=2, ensure_ascii=False)
            else:
                log.pretty_changes = None
        except Exception:
            log.pretty_changes = str(log.changes) if log.changes else None

    return render(request, "auditlog/audit_log_list.html", {
        "page_obj": page_obj
    })

def get_user_permissions(user):
	if user.is_authenticated:
		return RolePermission.objects.filter(Role__in=user.roles.all()).values_list('Permission__PermissionName', flat=True)
	return []

def build_duyuru_context(request):
	uygulama = (request.GET.get("uygulama") or "").strip()
	duyurular_qs = Duyuru.objects.select_related("olusturan").all()
	if uygulama:
		duyurular_qs = duyurular_qs.filter(uygulama=uygulama)

	uygulama_listesi = (
		Duyuru.objects.order_by("uygulama")
		.values_list("uygulama", flat=True)
		.distinct()
	)

	can_add_duyuru = False
	if request.user.is_authenticated:
		can_add_duyuru = request.user.has_permission("Genel Duyuru Ekleyebilir")

	return {
		"duyurular": list(duyurular_qs),
		"uygulama_listesi": uygulama_listesi,
		"aktif_uygulama": uygulama,
		"can_add_duyuru": can_add_duyuru,
	}

def index(request):
	if request.user.is_authenticated:
		if request.method == 'POST' and 'istek_ekle' in request.POST:
			istek_metni = request.POST.get('istek_metni')
			if istek_metni:
				Istek.objects.create(
					istek=istek_metni,
					talep_eden=request.user
				)
				messages.success(request, 'İsteğiniz başarıyla kaydedildi.')
				return redirect('index')
			else:
				messages.error(request, 'İstek metni boş olamaz.')

		permissions = get_user_permissions(request.user)
		istekler = Istek.objects.all().order_by('-talep_tarihi')
		
		context = {
			'permissions': permissions,
			'istekler': istekler
		}
		context.update(build_duyuru_context(request))
		return render(request, 'index.html', context)
	else:
		return render(request, "login.html")

@login_required
def istek_sil(request, istek_id):
	istek = get_object_or_404(Istek, id=istek_id)
	if istek.talep_eden == request.user:
		istek.delete()
		messages.success(request, 'İstek başarıyla silindi.')
	else:
		messages.error(request, 'Bu isteği silme yetkiniz yok.')
	return redirect('index')

@login_required
def istek_guncelle(request, istek_id):
	istek = get_object_or_404(Istek, id=istek_id)
	if request.user.has_permission("İstek Durumu Güncelleme"):
		if request.method == 'POST':
			yeni_durum = request.POST.get('durum')
			if yeni_durum:
				istek.tamamlanma_durumu = yeni_durum
				if yeni_durum == 'Tamamlandı':
					istek.tamamlanma_tarihi = now()
				else:
					istek.tamamlanma_tarihi = None
				istek.save()
				messages.success(request, 'İstek durumu güncellendi.')
			else:
				messages.error(request, 'Durum seçilmedi.')
	else:
		messages.error(request, 'Bu işlem için yetkiniz yok.')
	return redirect('index')

@login_required
def duyurular_list(request):
	context = build_duyuru_context(request)
	return render(request, "duyurular/index.html", context)

@login_required
@require_POST
def duyuru_ekle(request):
	if not request.user.has_permission("Genel Duyuru Ekleyebilir"):
		return JsonResponse({"status": "error", "message": "Bu işlem için yetkiniz yok."}, status=403)

	uygulama = (request.POST.get("uygulama") or "").strip()
	metin = (request.POST.get("duyuru_metni") or "").strip()

	if not uygulama or not metin:
		return JsonResponse({"status": "error", "message": "Tüm alanlar zorunludur."}, status=400)

	duyuru = Duyuru.objects.create(
		uygulama=uygulama,
		duyuru_metni=metin,
		olusturan=request.user
	)

	return JsonResponse({
		"status": "success",
		"message": "Duyuru eklendi.",
		"duyuru": {
			"uygulama": duyuru.uygulama,
			"duyuru_metni": duyuru.duyuru_metni,
			"olusturan": str(duyuru.olusturan) if duyuru.olusturan else "",
			"olusturma_tarihi": duyuru.olusturma_tarihi.strftime("%d.%m.%Y %H:%M"),
		}
	})

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

@login_required
def unread_notifications(request):
	notifs = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')
	data = [{
		'id': n.id,
		'title': n.title,
		'message': n.message,
		'created_at': n.created_at.strftime('%d.%m.%Y %H:%M')
	} for n in notifs]
	return JsonResponse({'notifications': data})

@login_required
def read_notifications(request):
	notifs = Notification.objects.filter(recipient=request.user, is_read=True).order_by('-created_at')[:10]
	data = [{
		'id': n.id,
		'title': n.title,
		'message': n.message,
		'created_at': n.created_at.strftime('%d.%m.%Y %H:%M')
	} for n in notifs]
	return JsonResponse({'notifications': data})

@csrf_exempt
@login_required
def read_notification(request, notif_id):
	Notification.objects.filter(id=notif_id, recipient=request.user).update(is_read=True)
	return JsonResponse({'status': 'ok'})

def kullanici_tanimlari(request):
	query = request.GET.get('q', '')
	page_number = request.GET.get('page', 1)
	users = User.objects.all()
	if query:
		users = users.filter(
			Q(Username__icontains=query) |
			Q(FullName__icontains=query) |
			Q(roles__RoleName__icontains=query)
		).distinct()
	users = users.order_by('-CreationTime')
	paginator = Paginator(users, 15)  # Sayfa başı 15 kayıt
	page_obj = paginator.get_page(page_number)
	roles = Role.objects.all()
	return render(request, 'kullanici_tanimlari.html', {
		'users': page_obj.object_list,
		'roles': roles,
		'page_obj': page_obj,
		'query': query,
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
		username = request.POST.get('username', '').strip()
		email = request.POST.get('email', '').strip()
		phone = request.POST.get('phone', '').strip()
		tckimlikno = request.POST.get('tckimlikno', '').strip()
		organisation = request.POST.get('organisation', '').strip()

		# Alan validasyonları ve unique kontrolleri
		errors = []
		if username and username != user.Username:
			if User.objects.filter(Username=username).exclude(UserID=user.UserID).exists():
				errors.append('Bu kullanıcı adı zaten kullanılıyor.')
		if tckimlikno:
			if User.objects.filter(TCKimlikNo=tckimlikno).exclude(UserID=user.UserID).exists():
				errors.append('Bu TCKimlikNo zaten kullanılıyor.')
		if phone:
			import re
			if not re.match(r'^5\d{9}$', phone):
				errors.append('Telefon numarası 5xxxxxxxxx formatında olmalıdır.')

		if errors:
			for err in errors:
				messages.error(request, err)
			return redirect('kullanici_tanimlari')

		# Kullanıcıyı güncelle
		user.FullName = fullname
		user.Username = username
		user.Email = email
		user.Phone = phone
		user.TCKimlikNo = tckimlikno
		user.Organisation = organisation
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

# İletişim
def iletisim(request):
	messages.warning(request, "Şu anda iletişime kapalıyız -.-")
	return redirect('index')

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
		notify_role_users(
			role_name="Admin",
			title="Yeni Kullanıcı Kaydı",
			message=f"{fullname} kullanıcı olarak sisteme eklendi."
		)

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
    if request.method == "POST":
        role_name = request.POST.get("role_name")
        if role_name:
            role = Role(RoleName=role_name)
            role.save()
            messages.success(request, 'Yeni rol başarıyla eklendi.')
        else:
            messages.warning(request, 'Rol adı boş olamaz.')
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

def register(request):
	"""User registration view."""
	if request.method == 'POST':
		username = request.POST.get('username')
		fullname = request.POST.get('fullname')
		password = request.POST.get('password')
		email = request.POST.get('email')
		phone = request.POST.get('phone')
		tckimlikno = request.POST.get('tckimlikno')
		organisation = request.POST.get('organisation')

		if not username or not password or not email or not phone or not tckimlikno:
			messages.error(request, "Tüm alanları doldurmanız gerekmektedir.")
			return redirect('register')

		if not phone.startswith('5') or len(phone) != 10:
			messages.error(request, "Telefon numarası 5xxxxxxxxx formatında olmalıdır.")
			return redirect('register')

		try:
			user = User.objects.create(
				Username=username,
				FullName=fullname,
				Email=email,
				Phone=phone,
				TCKimlikNo=tckimlikno,
				Organisation=organisation,
				is_active=False  # Set user as inactive
			)
			user.password = password  # Store raw password without hashing
			user.save()
			notify_role_users(
				role_name="Admin",
				title="Yeni Kullanıcı Kaydı",
				message=f"{username} kullanıcı olarak sisteme kaydoldu."
			)
			messages.success(request, "Kayıt başarılı! Hesabınız onaylandıktan sonra giriş yapabilirsiniz.")
			return redirect('login')
		except IntegrityError as e:
			if "Users.TCKimlikNo" in str(e):
				messages.error(request, "Kayıt sırasında bir hata oluştu: Bu T.C. Kimlik Numaralı kullanıcı zaten mevcut.")
			elif "Users.Username" in str(e):
				messages.error(request, "Kayıt sırasında bir hata oluştu: Bu kullanıcı adı zaten alınmış.")
			elif "Users.Email" in str(e):
				messages.error(request, "Kayıt sırasında bir hata oluştu: Bu e-posta adresi zaten kullanılıyor.")
			else:
				messages.error(request, f"Kayıt sırasında bir hata oluştu: {str(e)}")
			return redirect('register')
		except Exception as e:
			messages.error(request, f"Kayıt sırasında bir hata oluştu: {str(e)}")
			return redirect('register')

	return render(request, 'register.html')

def custom_login(request):
	"""Custom login view to handle inactive users and non-existent accounts."""
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		user = authenticate(request, username=username, password=password)

		if user is not None:
			if user.is_active:
				login(request, user)
				return redirect('index')  # Redirect to the main page
			else:
				messages.error(request, "Kullanıcınız henüz aktif edilmedi, sisteme giriş yapamazsınız.")
				return redirect('login')
		else:
			messages.error(request, "Kullanıcı adı veya şifre hatalı.")
			return redirect('login')

	return render(request, 'login.html')

# --------- PROFIL SAYFASI VE SIFRE DEGISTIRME ---------
@login_required
def profile_view(request):
	user: User = request.user
	if request.method == 'POST':
		form = ProfileForm(request.POST)
		if form.is_valid():
			full_name = form.cleaned_data['FullName']
			email = form.cleaned_data['Email']
			phone = form.cleaned_data['Phone']
			organisation = form.cleaned_data['Organisation']

			# email uniqueness
			if email and User.objects.filter(Email=email).exclude(UserID=user.UserID).exists():
				messages.error(request, 'Bu e-posta adresi başka bir kullanıcı tarafından kullanılıyor.')
			else:
				user.FullName = full_name
				user.Email = email
				user.Phone = phone
				user.Organisation = organisation
				user.save()
				messages.success(request, 'Profil bilgileriniz güncellendi.')
			return redirect('profile')
	else:
		initial = {
			'FullName': user.FullName,
			'Email': user.Email,
			'Phone': user.Phone,
			'Organisation': user.Organisation,
		}
		form = ProfileForm(initial=initial)

	return render(request, 'profile.html', {'form': form})

@login_required
@require_POST
def profile_change_password(request):
	user: User = request.user
	form = PasswordChangeForm(request.POST)
	if not form.is_valid():
		# Hata mesajlarını döndür
		for field, errs in form.errors.items():
			for e in errs:
				messages.error(request, e)
		return redirect('profile')

	old_password = form.cleaned_data['old_password']
	new_password = form.cleaned_data['new_password']

	# mevcut şifre kontrolü - hashlenmemiş şifreler için
	if user.password != old_password:
		messages.error(request, 'Mevcut şifre hatalı.')
		return redirect('profile')

	# Django password validators, daha güvenli bir şifre kontrolü yapılabilir. İleride aktif edilebilir.
	# try:
	# 	validate_password(new_password, user)
	# except ValidationError as ve:
	# 	for e in ve:
	# 		messages.error(request, e)
	# 	return redirect('profile')

	# Hashlenmemiş şifreler için doğrudan atama
	user.password = new_password
	user.save()
	messages.success(request, 'Şifreniz başarıyla güncellendi.')
	return redirect('profile')