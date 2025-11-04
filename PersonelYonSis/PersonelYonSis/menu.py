from .models import Permission

class MenuItem:
    def __init__(self, name, url, icon, permission=None, parent_menu=None, is_parent=False):
        self.name = name
        self.url = url
        self.icon = icon
        self.permission = permission  # Menüyü görüntülemek için gereken izin
        self.parent_menu = parent_menu
        self.is_parent = is_parent  # Varsayılan olarak alt menü
class Menu:
    def __init__(self, user):
        self.user = user
        self.items = self.build_menu()

    def build_menu(self):
        # Eğer kullanıcı giriş yapmamışsa menüyü boş döndür
        if not self.user.is_authenticated:
            return []

        items = [
            # Yönetim paneli ve Alt Menüleri
            MenuItem('Yönetim Paneli', '#', 'bi bi-incognito', 'Yeni Kullanıcı Tanımlama', is_parent=True),
            MenuItem('Kullanıcı Tanımları', 'kullanici_tanimlari', 'bi bi-octagon', 'Yeni Kullanıcı Tanımlama', parent_menu='Yönetim Paneli'),
            MenuItem('Rol Tanımları', 'rol_tanimlari', 'bi bi-octagon', 'Yeni Rol Tanımlama', parent_menu='Yönetim Paneli'),
            MenuItem('Yetki Tanımları', 'yetki_tanimlari', 'bi bi-octagon', 'Yeni Yetki Tanımlama', parent_menu='Yönetim Paneli'),
            MenuItem('Sistem Logları', 'audit_log_list', 'bi bi-octagon', 'Yeni Yetki Tanımlama', parent_menu='Yönetim Paneli'),
            # İnsan Kaynakları Modülü ve Alt Menüleri
            MenuItem('İK Modülü', '#', 'bi bi-person-lines-fill', 'İK Modülü', is_parent=True),
            MenuItem('Personel Tanımları', 'ik_core:personel_list', 'bi bi-octagon', 'İK Modülü', parent_menu='İK Modülü'),
            MenuItem('Geçici Görevler', 'ik_core:gecici_gorevler', 'bi bi-octagon', 'İK Modülü', parent_menu='İK Modülü'),
            MenuItem('Tanımlamalar', 'ik_core:tanimlamalar', 'bi bi-octagon', 'İK Modülü', parent_menu='İK Modülü'),
            MenuItem('Birim Yönetimi', 'ik_core:birim_yonetimi', 'bi bi-octagon', 'İK Modülü', parent_menu='İK Modülü'),
            # İzin Modülü ve Alt Menüleri
            MenuItem('İzin Modülü', '#', 'bi bi-calendar-check', 'İzin Modülü', is_parent=True),
            MenuItem('İzin Tanımları', 'kullanici_tanimlari', 'bi bi-octagon', 'İzin Modülü', parent_menu='İzin Modülü'),
            # Mutemetlik Modülü ve Alt Menüleri
            MenuItem('Mutemetlik Modülü', '#', 'bi bi-newspaper', 'Mutemetlik Modülü', is_parent=True),
            MenuItem('Personel Takibi', 'mutemet_app:personel_listesi', 'bi bi-octagon', parent_menu='Mutemetlik Modülü'),
            MenuItem('Sendika Takibi', 'mutemet_app:sendika_takibi', 'bi bi-octagon', parent_menu='Mutemetlik Modülü'),
            MenuItem('İcra Takibi', 'mutemet_app:icra_takibi', 'bi bi-octagon', parent_menu='Mutemetlik Modülü'),
            MenuItem('Sorgulamalar', 'mutemet_app:sorgulamalar', 'bi bi-octagon', parent_menu='Mutemetlik Modülü'),
            MenuItem('Hizmet Sunum Raporlama', 'hizmet_sunum_app:raporlama', 'bi bi-octagon', parent_menu='Mutemetlik Modülü'),
            MenuItem('Mercis 657 Raporlama', 'mercis657:raporlama', 'bi bi-octagon', parent_menu='Mutemetlik Modülü'),
            MenuItem('Hekim Bildirimleri', 'hekim_cizelge:mutemetlik_islemleri', 'bi bi-octagon', parent_menu='Mutemetlik Modülü'),
            # Nöbet Defteri Modülü ve Alt Menüleri
            MenuItem('Nöbet Defteri Modülü', '#', 'bi bi-journal-check', 'Nöbet Defteri Modülü', is_parent=True),
            MenuItem('Nöbet Defteri', 'nobet_defteri:liste', 'bi bi-octagon', parent_menu='Nöbet Defteri Modülü'),
            MenuItem('Tekniker Ziyaretleri', 'nobet_defteri:tekniker_ziyaretleri', 'bi bi-octagon', parent_menu='Nöbet Defteri Modülü'),
            MenuItem('Kontrol Formu Soruları', 'nobet_defteri:kontrol_soru_list', 'bi bi-octagon', 'Nöbet Defteri Soruları Düzenleme', parent_menu='Nöbet Defteri Modülü'),
            # Çizelge 657 ve Alt Menüleri
            MenuItem('Çizelge Sistemi 657', '#', 'bi bi-calendar3', 'ÇS 657 Çizelge Sayfası', is_parent=True),
            MenuItem('Çizelge', 'mercis657:cizelge', 'bi bi-octagon', 'ÇS 657 Çizelge Sayfası', parent_menu='Çizelge Sistemi 657'),
            MenuItem('Çizelge Onay', 'mercis657:cizelge_onay', 'bi bi-octagon', 'ÇS 657 Çizelge Onay', parent_menu='Çizelge Sistemi 657'),
            MenuItem('Bildirim İşlemleri', 'mercis657:bildirimler', 'bi bi-octagon', 'ÇS 657 Bildirim İşlemleri', parent_menu='Çizelge Sistemi 657'),
            MenuItem('Birim Yönetimi', 'mercis657:birim_yonetim', 'bi bi-octagon', 'ÇS 657 Birim Yönetimi Sayfası', parent_menu='Çizelge Sistemi 657'),
            MenuItem('Çizelge Yönetimi', 'mercis657:birim_listeleri', 'bi bi-octagon', 'ÇS 657 Birim Yönetimi Sayfası', parent_menu='Çizelge Sistemi 657'),
            MenuItem('Personel Yönetimi', 'mercis657:personel_yonetim', 'bi bi-octagon', 'ÇS 657 Personel Yönetimi Sayfası', parent_menu='Çizelge Sistemi 657'),
            MenuItem('Tanımlamalar', 'mercis657:tanimlamalar', 'bi bi-octagon', 'ÇS 657 Mesai Tanımlama', parent_menu='Çizelge Sistemi 657'),
            # Çizelge 696 ve Alt Menüleri
            MenuItem('Çizelge Sistemi 696', '#', 'bi bi-calendar-week', 'ÇS 696 Çizelge Sayfası', is_parent=True),
            MenuItem('696 Personeller', 'mercis657:personeller', 'bi bi-octagon', '	ÇS 696 Personel Yönetimi', parent_menu='Çizelge Sistemi 696'), #696 sistemi oluşturulunca değiştirilecek
            # Hizmet Sunum Alanı ve Alt Menüleri
            MenuItem('Hizmet Sunum Alanı', '#', 'bi bi-house', 'Hizmet Sunum Alanı Bildirim', is_parent=True),
            MenuItem('Bildirim İşlemleri', 'hizmet_sunum_app:bildirim', 'bi bi-octagon', 'Hizmet Sunum Alanı Bildirim', parent_menu='Hizmet Sunum Alanı'),
            MenuItem('Kesinleştirme İşlemleri', 'hizmet_sunum_app:raporlama', 'bi bi-octagon', 'HSA Kesinleştirme İşlemleri Ekranı',parent_menu='Hizmet Sunum Alanı'),
            MenuItem('Birim Bilgileri', 'hizmet_sunum_app:birim_yonetim', 'bi bi-octagon', 'HSA Birim Bilgileri', parent_menu='Hizmet Sunum Alanı'),
            # Hekim Çizelge Sistemi ve Alt Menüleri
            MenuItem('Hekim Çizelge Sistemi', '#', 'bi bi-h-square', 'HÇ Hizmet Raporu', is_parent=True),
            MenuItem('Çizelge', 'hekim_cizelge:cizelge', 'bi bi-octagon', 'HÇ Çizelge Sayfası', parent_menu='Hekim Çizelge Sistemi'),
            MenuItem('Birim Verileri', 'hekim_cizelge:birim_dashboard', 'bi bi-octagon', 'HÇ Birim Verileri', parent_menu='Hekim Çizelge Sistemi'),
            MenuItem('Çizelge Onay', 'hekim_cizelge:onay_bekleyen_mesailer', 'bi bi-octagon', 'HÇ Çizelge Onay', parent_menu='Hekim Çizelge Sistemi'),
            MenuItem('Bildirim İşlemleri', 'hekim_cizelge:bildirimler', 'bi bi-octagon', 'HÇ Bildirim İşlemleri', parent_menu='Hekim Çizelge Sistemi'),
            MenuItem('Hizmet Raporu', 'hekim_cizelge:hizmet_raporu', 'bi bi-octagon', 'HÇ Hizmet Raporu', parent_menu='Hekim Çizelge Sistemi'),
            MenuItem('Personeller', 'hekim_cizelge:personeller', 'bi bi-octagon', 'HÇ Personel Yönetimi', parent_menu='Hekim Çizelge Sistemi'),
            MenuItem('Kullanıcı Tanımları', 'kullanici_tanimlari', 'bi bi-octagon', 'HÇ Tanımlama Yapma Yetkisi', parent_menu='Hekim Çizelge Sistemi'),
            MenuItem('Hizmet Tanımları', 'hekim_cizelge:hizmet_tanimlari', 'bi bi-octagon', 'HÇ Tanımlama Yapma Yetkisi', parent_menu='Hekim Çizelge Sistemi'),
            MenuItem('Birim Tanımları', 'hekim_cizelge:birim_tanimlari', 'bi bi-octagon', 'HÇ Tanımlama Yapma Yetkisi', parent_menu='Hekim Çizelge Sistemi'),
            MenuItem('Resmi Tatil Tanımları', 'hekim_cizelge:resmi_tatiller', 'bi bi-octagon', 'HÇ Tanımlama Yapma Yetkisi', parent_menu='Hekim Çizelge Sistemi'),
            
        ]
        
        return [item for item in items if item.permission is None or self.user_has_permission(item.permission)]

    def user_has_permission(self, permission_name):
        user_roles = self.user.roles.all()
        permissions = Permission.objects.filter(
            rolepermission__Role__in=user_roles,  # RolePermission tablosu üzerinden ilişki
            PermissionName=permission_name        # İstenilen izin adı
        )
        has_permission = permissions.exists()
        return has_permission