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
            MenuItem('Yönetim Paneli', '#', 'bi bi-incognito', is_parent=True),
            MenuItem('Kullanıcı Tanımları', 'kullanici_tanimlari', 'bi bi-octagon', 'Yeni Kullanıcı Tanımlama', parent_menu='Yönetim Paneli'),
            MenuItem('Rol Tanımları', 'rol_tanimlari', 'bi bi-octagon', 'Yeni Rol Tanımlama', parent_menu='Yönetim Paneli'),
            MenuItem('Yetki Tanımları', 'yetki_tanimlari', 'bi bi-octagon', 'Yeni Yetki Tanımlama', parent_menu='Yönetim Paneli'),
            # İnsan Kaynakları Modülü ve Alt Menüleri
            MenuItem('İK Modülü', '#', 'bi bi-person-lines-fill', is_parent=True),
            MenuItem('Personel Tanımları', 'kullanici_tanimlari', 'bi bi-octagon', 'Yeni Kullanıcı Tanımlama', parent_menu='İnsan Kaynakları Modülü'),
            # İzin Modülü ve Alt Menüleri
            MenuItem('İzin Modülü', '#', 'bi bi-calendar-check', is_parent=True),
            MenuItem('İzin Tanımları', 'kullanici_tanimlari', 'bi bi-octagon', 'Yeni Kullanıcı Tanımlama', parent_menu='İzin Modülü'),
            # Mutemetlik Moddülü ve Alt Menüleri
            MenuItem('Mutemetlik Modülü', '#', 'bi bi-newspaper', is_parent=True),
            MenuItem('Personel Takibi', 'mutemet_app:personel_listesi', 'bi bi-octagon', parent_menu='Mutemetlik Modülü'),
            MenuItem('Sendika Takibi', 'mutemet_app:sendika_takibi', 'bi bi-octagon', parent_menu='Mutemetlik Modülü'),
            MenuItem('İcra Takibi', 'mutemet_app:icra_takibi', 'bi bi-octagon', parent_menu='Mutemetlik Modülü'),
            MenuItem('Hekim Bildirimleri', 'hekim_cizelge:mutemetlik_islemleri', 'bi bi-octagon', parent_menu='Mutemetlik Modülü'),
            # Çizelge 657 ve Alt Menüleri
            MenuItem('Çizelge Sistemi 657', '#', 'bi bi-calendar3', is_parent=True),
            MenuItem('657 Personeller', 'mercis657:personeller', 'bi bi-octagon', parent_menu='Çizelge Sistemi 657'),
            MenuItem('Çizelge', 'mercis657:cizelge', 'bi bi-octagon', parent_menu='Çizelge Sistemi 657'),
            MenuItem('Mesai Tanımları', 'mercis657:mesai_tanimlari', 'bi bi-octagon', parent_menu='Çizelge Sistemi 657'),
            # Çizelge 696 ve Alt Menüleri
            MenuItem('Çizelge Sistemi 696', '#', 'bi bi-calendar-week', is_parent=True),
            MenuItem('696 Personeller', 'mercis657:personeller', 'bi bi-octagon', parent_menu='Çizelge Sistemi 696'), #696 sistemi oluşturulunca değiştirilecek
            # Hekim Çizelge Sistemi ve Alt Menüleri
            MenuItem('Hekim Çizelge Sistemi', '#', 'bi bi-h-square', is_parent=True),
            MenuItem('Çizelge', 'hekim_cizelge:cizelge', 'bi bi-octagon', parent_menu='Hekim Çizelge Sistemi'),
            MenuItem('Birim Verileri', 'hekim_cizelge:birim_dashboard', 'bi bi-octagon', parent_menu='Hekim Çizelge Sistemi'),
            MenuItem('Çizelge Onay', 'hekim_cizelge:onay_bekleyen_mesailer', 'bi bi-octagon', parent_menu='Hekim Çizelge Sistemi'),
            MenuItem('Bildirim İşlemleri', 'hekim_cizelge:bildirimler', 'bi bi-octagon', parent_menu='Hekim Çizelge Sistemi'),
            MenuItem('Hizmet Raporu', 'hekim_cizelge:hizmet_raporu', 'bi bi-octagon', parent_menu='Hekim Çizelge Sistemi'),
            MenuItem('Personeller', 'hekim_cizelge:personeller', 'bi bi-octagon', parent_menu='Hekim Çizelge Sistemi'),
            MenuItem('Hizmet Tanımları', 'hekim_cizelge:hizmet_tanimlari', 'bi bi-octagon', parent_menu='Hekim Çizelge Sistemi'),
            MenuItem('Birim Tanımları', 'hekim_cizelge:birim_tanimlari', 'bi bi-octagon', parent_menu='Hekim Çizelge Sistemi'),
            MenuItem('Resmi Tatil Tanımları', 'hekim_cizelge:resmi_tatiller', 'bi bi-octagon', parent_menu='Hekim Çizelge Sistemi'),
            
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