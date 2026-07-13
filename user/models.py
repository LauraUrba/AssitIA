import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UsuarioManager(BaseUserManager):
    def create_user(self, email, nome, perfil, password=None, **extra_fields):
        if not email:
            raise ValueError('O email é obrigatório')
        email = self.normalize_email(email)
        user = self.model(email=email, nome=nome, perfil=perfil, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nome, password=None, **extra_fields):
        extra_fields.setdefault('perfil', 'administrador')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, nome, password=password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    PERFIL_CHOICES = [
        ('professor', 'Professor'),
        ('coordenador', 'Coordenador'),
        ('especialista', 'Especialista'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=150)
    email = models.EmailField(max_length=150, unique=True)
    perfil = models.CharField(max_length=20, choices=PERFIL_CHOICES)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    ultimo_login = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome', 'perfil']

    class Meta:
        db_table = 'usuario'
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return f"{self.nome} ({self.email})"

    def verificar_senha_no_historico(self, nova_senha, limite=5):
        """
        Verifica se a nova senha já foi usada anteriormente
        Args:
            nova_senha: A nova senha a ser verificada
            limite: Número máximo de senhas a verificar (padrão: 5)
        Returns:
            bool: True se a senha já foi usada, False caso contrário
        """
        historico = self.password_history.all()[:limite]

        for registro in historico:
            # Verificar se a senha corresponde ao hash armazenado
            from django.contrib.auth.hashers import check_password
            if check_password(nova_senha, registro.password_hash):
                return True
        return False

    def salvar_historico_senha(self, senha):
        """Salvar a senha no histórico"""
        from django.contrib.auth.hashers import make_password

        # Limitar histórico a 10 senhas
        if self.password_history.count() >= 10:
            # Remover a senha mais antiga
            mais_antiga = self.password_history.last()
            if mais_antiga:
                mais_antiga.delete()

        # Salvar nova senha
        PasswordHistory.objects.create(
            user=self,
            password_hash=make_password(senha)
        )


class PasswordHistory(models.Model):
    """Histórico de senhas do usuário"""
    user = models.ForeignKey('Usuario', on_delete=models.CASCADE, related_name='password_history')
    password_hash = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'password_history'
        verbose_name = 'Histórico de Senha'
        verbose_name_plural = 'Históricos de Senhas'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"