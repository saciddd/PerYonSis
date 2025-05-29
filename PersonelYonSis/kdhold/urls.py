from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'kdhold'

urlpatterns = [
    path('m657/login/', views.m657_login_view, name='login_view'),
    path('m657/schedule/', views.m657_schedule_view, name='schedule_view'),
    path('m657/update_schedule/', views.m657_update_schedule, name='update_schedule'),
    path('m657/schedule/edit/', views.m657_schedule_edit, name='schedule_edit'),
    path('m657/schedule/save/', views.m657_cizelge_kaydet, name='cizelge_kaydet'),
    path('m657/refresh-session/', views.m657_refresh_session_view, name='refresh_session'),
    # path('mercisreports/', include('mercisreports.urls')),
    # path('mercis657/', include('mercis657.urls')),
    # path('mercis696/', include('mercis696.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)