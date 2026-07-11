import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings


class Estudante(models.Model):
    NIVEL_SUPORTE_CHOICES = [
        (1, 'Nível 1 - Suporte Leve'),
        (2, 'Nível 2 - Suporte Moderado'),
        (3, 'Nível 3 - Suporte Intensivo'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    professor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.RESTRICT, related_name='estudantes')
    nome = models.CharField(max_length=150)
    data_nascimento = models.DateField(null=True, blank=True)
    nivel_suporte = models.IntegerField(choices=NIVEL_SUPORTE_CHOICES)
    turma = models.CharField(max_length=50, blank=True, null=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'estudante'
        verbose_name = 'Estudante'
        verbose_name_plural = 'Estudantes'
        ordering = ['nome']

    def __str__(self):
        return f"{self.nome} - {self.get_nivel_suporte_display()}"


class PerfilTEA(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    estudante = models.OneToOneField(Estudante, on_delete=models.CASCADE, related_name='perfil_tea')
    comunicacao = models.CharField(max_length=100, blank=True, null=True)
    perfil_sensorial = models.CharField(max_length=100, blank=True, null=True)
    habilidade_motora = models.CharField(max_length=100, blank=True, null=True)
    perfil_cognitivo = models.CharField(max_length=100, blank=True, null=True)
    desafios = models.TextField(blank=True, null=True)
    observacoes = models.TextField(blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'perfil_tea'
        verbose_name = 'Perfil TEA'
        verbose_name_plural = 'Perfis TEA'

    def __str__(self):
        return f"Perfil TEA - {self.estudante.nome}"


# telas/models.py - Adicionar novos campos

class TecnologiaAssistiva(models.Model):
    CATEGORIA_CHOICES = [
        ('comunicacao', 'Comunicação'),
        ('regulacao_sensorial', 'Regulação Sensorial'),
        ('motor', 'Motor'),
        ('cognitivo', 'Cognitivo'),
        ('interacao_social', 'Interação Social'),
        ('estruturacao', 'Estruturação'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=200)
    categoria = models.CharField(max_length=50, choices=CATEGORIA_CHOICES)
    descricao = models.TextField(blank=True, null=True)
    exemplos_uso = models.TextField(blank=True, null=True)
    avaliacao_media = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    total_avaliacoes = models.IntegerField(default=0)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    # NOVOS CAMPOS PARA O CATÁLOGO
    materiais = models.TextField(blank=True, null=True, help_text="Materiais necessários para criar/adaptar")
    como_fazer = models.TextField(blank=True, null=True, help_text="Passo a passo de como criar/fazer")
    como_usar = models.TextField(blank=True, null=True, help_text="Como utilizar a tecnologia")
    para_que_serve = models.TextField(blank=True, null=True, help_text="Para que serve esta tecnologia")

    class Meta:
        db_table = 'tecnologia_assistiva'
        verbose_name = 'Tecnologia Assistiva'
        verbose_name_plural = 'Tecnologias Assistivas'
        ordering = ['nome']

    def __str__(self):
        return f"{self.nome} ({self.get_categoria_display()})"



class Recomendacao(models.Model):
    STATUS_CHOICES = [
        ('gerada', 'Gerada'),
        ('visualizada', 'Visualizada'),
        ('arquivada', 'Arquivada'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    estudante = models.ForeignKey(Estudante, on_delete=models.CASCADE, related_name='recomendacoes')
    professor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recomendacoes')
    parametros_entrada = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='gerada')
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'recomendacao'
        verbose_name = 'Recomendação'
        verbose_name_plural = 'Recomendações'
        ordering = ['-criado_em']

    def __str__(self):
        return f"Recomendação para {self.estudante.nome} - {self.get_status_display()}"


class RecomendacaoTA(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recomendacao = models.ForeignKey(Recomendacao, on_delete=models.CASCADE, related_name='recomendacoes_ta')
    ta = models.ForeignKey(TecnologiaAssistiva, on_delete=models.CASCADE, related_name='recomendacoes')
    justificativa = models.TextField(blank=True, null=True)
    posicao_ranking = models.IntegerField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'recomendacao_ta'
        verbose_name = 'Recomendação TA'
        verbose_name_plural = 'Recomendações TA'
        ordering = ['posicao_ranking']

    def __str__(self):
        return f"{self.ta.nome} - Ranking {self.posicao_ranking}"


class Feedback(models.Model):
    AVALIACAO_CHOICES = [
        ('aceita', 'Aceita'),
        ('a_testar', 'A Testar'),
        ('rejeitada', 'Rejeitada'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recomendacao_ta = models.ForeignKey(RecomendacaoTA, on_delete=models.CASCADE, related_name='feedbacks')
    professor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='feedbacks')
    avaliacao = models.CharField(max_length=20, choices=AVALIACAO_CHOICES)
    comentario = models.TextField(blank=True, null=True)
    registrado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'feedback'
        verbose_name = 'Feedback'
        verbose_name_plural = 'Feedbacks'

    def __str__(self):
        return f"Feedback {self.get_avaliacao_display()} - {self.professor.nome}"


class PEI(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    estudante = models.ForeignKey(Estudante, on_delete=models.CASCADE, related_name='peis')
    professor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='peis')
    objetivos = models.TextField(blank=True, null=True)
    estrategias = models.TextField(blank=True, null=True)
    recursos = models.TextField(blank=True, null=True)
    versao = models.IntegerField(default=1)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pei'
        verbose_name = 'PEI'
        verbose_name_plural = 'PEIs'
        ordering = ['-criado_em']

    def __str__(self):
        return f"PEI - {self.estudante.nome} (v{self.versao})"