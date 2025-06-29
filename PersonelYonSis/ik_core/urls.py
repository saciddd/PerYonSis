from django.urls import path
from . import views
from ik_core.api import views as api_views

app_name = 'ik_core'

urlpatterns = [
    path('personeller/', views.personel_list, name='personel_list'),
    path('personel/ekle/', views.personel_ekle, name='personel_ekle'),
    path('personel/<int:pk>/', views.personel_detay, name='personel_detay'),
    path('personel/<int:pk>/duzenle/', views.personel_duzenle, name='personel_duzenle'),
    path('personel/<int:pk>/ilisik-kesme/', views.ilisik_kesme_formu, name='ilisik_kesme_formu'),
    path('personel/<int:personel_id>/gecici-gorev-ekle/', views.gecici_gorev_ekle, name='gecici_gorev_ekle'),
    path('personel/<int:personel_id>/gecici-gorev-sil/<int:gorev_id>/', views.gecici_gorev_sil, name='gecici_gorev_sil'),
    path('kurum-tanimlari/', views.kurum_tanimlari, name='kurum_tanimlari'),
    path('unvan-brans-tanimlari/', views.unvan_branstanimlari, name='unvan_branstanimlari'),
    path('tanimlamalar/', views.tanimlamalar, name='tanimlamalar'),
    path('personel_kontrol/', views.personel_kontrol, name='personel_kontrol'),
    path('get_brans_by_unvan/', views.get_brans_by_unvan, name='get_brans_by_unvan'),
    # API endpoints
    path('api/personel_aktar/', api_views.filemaker_personel_aktar, name='filemaker_personel_aktar'),

]
