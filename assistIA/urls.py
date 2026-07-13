from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    # Redirecionar raiz para o dashboard ou login
    path('', lambda request: redirect('/telas/')),
    path('admin/', admin.site.urls),
    path('auth/', include('user.urls')),
    path('telas/', include('telas.urls')),
]