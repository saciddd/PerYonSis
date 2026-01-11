from django.contrib import admin
from django.urls import include, path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
	path('', views.index, name='index'),
	path('istek/sil/<int:istek_id>/', views.istek_sil, name='istek_sil'),
	path('istek/guncelle/<int:istek_id>/', views.istek_guncelle, name='istek_guncelle'),
	path('iletisim/', views.iletisim, name='iletisim'),
	path('register/', views.register, name='register'),
	path('login/', views.custom_login, name='login'),
	path('logout/', views.logout, name='logout'),
	path('duyurular/', views.duyurular_list, name='duyurular_list'),
	path('duyurular/ekle/', views.duyuru_ekle, name='duyuru_ekle'),
	path('yetki-tanimlari/', views.yetki_tanimlari, name='yetki_tanimlari'),
	path('rol-tanimlari/', views.rol_tanimlari, name='rol_tanimlari'),
	path('add_role/', views.add_role, name='add_role'),  # Yeni rol ekleme
	path('add_permission_to_role/<int:role_id>/<int:permission_id>/', views.add_permission_to_role, name='add_permission_to_role'),  # Yetki ekleme
	path('remove_permission/<int:role_id>/<int:permission_id>/', views.remove_permission, name='remove_permission'),  # Yetki silme
	path('kullanici-tanimlari/', views.kullanici_tanimlari, name='kullanici_tanimlari'),
	path('add_user/', views.add_user, name='add_user'),
	path('update_roles/<int:user_id>/', views.update_roles, name='update_roles'),
	path('update_active_status/<int:user_id>/', views.update_active_status, name='update_active_status'),
	path('reset_password/<int:user_id>/', views.reset_password, name='reset_password'),
	path('yeni-kullanici-form/', views.yeni_kullanici_form, name='yeni_kullanici_form'),
	path('kullanici-duzenle-form/<int:user_id>/', views.kullanici_duzenle_form, name='kullanici_duzenle_form'),
	path('update-user/<int:user_id>/', views.update_user, name='update_user'),
	path('add_permission/', views.yetki_tanimlari, name='add_permission'),
	# Profil
	path('profil/', views.profile_view, name='profile'),
	path('profil/change-password/', views.profile_change_password, name='profile_change_password'),
	path('mercis657/', include('mercis657.urls')),
	path('mercis696/', include('mercis696.urls')),
	path('hekim_cizelge/', include('hekim_cizelge.urls')),
	path('mutemet/', include('mutemet_app.urls')),
	path('hizmet_sunum/', include('hizmet_sunum_app.urls')),
	path('nobet_defteri/', include('nobet_defteri.urls')),
	path('ik_core/', include('ik_core.urls')),
	path('admin/', admin.site.urls),
	# Bildirim işlemleri
	path('notifications/unread/', views.unread_notifications, name='unread_notifications'),
	path('notifications/read/', views.read_notifications, name='read_notifications'),
	path('notifications/read/<int:notif_id>/', views.read_notification, name='read_notification'),
	# Audit Log
	path('log/', views.audit_log_list, name='audit_log_list'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
if settings.DEBUG:
	urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)