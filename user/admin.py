from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ['email', 'nome', 'perfil', 'ativo', 'is_staff']
    list_filter = ['perfil', 'ativo', 'is_staff']
    search_fields = ['email', 'nome']
    ordering = ['email']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informações Pessoais', {'fields': ('nome', 'perfil')}),
        ('Permissões', {'fields': ('ativo', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas', {'fields': ('ultimo_login', 'criado_em')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nome', 'perfil', 'password1', 'password2'),
        }),
    )