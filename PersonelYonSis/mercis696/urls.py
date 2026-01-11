from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'mercis696'

urlpatterns = [
    path('', views.login_view, name='login_view'),
    path('login/', views.login_view, name='login_view'),
    path('schedule/', views.schedule_view, name='schedule_view'),
    path('update_schedule/', views.update_schedule, name='update_schedule'),
    path('schedule/edit/', views.schedule_edit, name='schedule_edit'),
    path('schedule/save/', views.cizelge_kaydet, name='cizelge_kaydet'),
    path('refresh-session/', views.refresh_session_view, name='refresh_session'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)