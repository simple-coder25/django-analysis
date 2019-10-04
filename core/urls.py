from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from core import auth

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),
    path('formatting/', include('formatting.urls')),
    path('graphs/', include('graphs.urls')),
    url(r'^accounts/', include('allauth.urls')),
    path('accounts/login/', auth.LoginView.as_view(), name='login'),
    path('accounts/signup/', auth.SignUpView.as_view(), name='signup'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
