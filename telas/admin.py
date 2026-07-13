# telas/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import LogSeguranca, Estudante, TecnologiaAssistiva, Recomendacao, PEI, PerfilTEA
from .models import TermosUso, AceiteTermos
from .models import AvaliacaoTecnologia

@admin.register(LogSeguranca)
class LogSegurancaAdmin(admin.ModelAdmin):
    """Configuração do admin para logs de segurança"""

    # Campos que aparecem na lista
    list_display = [
        'criado_em',
        'tipo_formatado',
        'usuario',
        'ip',
        'nivel_colorido',
        'detalhes_resumidos'
    ]

    # Filtros laterais
    list_filter = [
        'tipo',
        'nivel',
        'criado_em',
    ]

    # Campos de busca
    search_fields = [
        'usuario__nome',
        'usuario__email',
        'ip',
        'detalhes'
    ]

    # Campos somente leitura
    readonly_fields = ['criado_em']

    # Ordenação
    ordering = ['-criado_em']

    # Paginação
    list_per_page = 50

    # Campos para exibição detalhada
    fieldsets = (
        ('Informações do Evento', {
            'fields': ('tipo', 'nivel', 'detalhes', 'dados_extra')
        }),
        ('Usuário e Localização', {
            'fields': ('usuario', 'ip', 'user_agent')
        }),
        ('Data', {
            'fields': ('criado_em',)
        }),
    )

    # Métodos customizados para exibição
    def tipo_formatado(self, obj):
        """Exibir tipo com ícone"""
        icones = {
            'login': '✅',
            'logout': '🚪',
            'falha_login': '❌',
            '2fa': '🔐',
            'cadastro': '📝',
            'alteracao_senha': '🔑',
            'recuperacao_senha': '📧',
            'acesso_negado': '⛔',
            'ataque': '⚠️',
            'honeypot': '🍯',
            'admin': '🛠️',
            'exclusao': '🗑️',
            'edicao': '✏️',
            'criacao': '➕',
        }
        icone = icones.get(obj.tipo, '📌')
        return f"{icone} {obj.get_tipo_display()}"

    tipo_formatado.short_description = 'Tipo'

    def nivel_colorido(self, obj):
        """Exibir nível com cores"""
        cores = {
            'info': '#0d6efd',  # azul
            'warning': '#ffc107',  # amarelo
            'error': '#dc3545',  # vermelho
            'critical': '#dc3545',  # vermelho escuro
        }
        cor = cores.get(obj.nivel, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">●</span> {}',
            cor,
            obj.get_nivel_display()
        )

    nivel_colorido.short_description = 'Nível'

    def detalhes_resumidos(self, obj):
        """Resumir detalhes longos"""
        if obj.detalhes:
            if len(obj.detalhes) > 50:
                return obj.detalhes[:50] + '...'
            return obj.detalhes
        return '-'

    detalhes_resumidos.short_description = 'Detalhes'

    # Ações personalizadas
    actions = ['exportar_selecionados']

    def exportar_selecionados(self, request, queryset):
        """Exportar logs selecionados para CSV"""
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="logs_seguranca.csv"'

        writer = csv.writer(response)
        writer.writerow(['Data', 'Tipo', 'Usuário', 'IP', 'Nível', 'Detalhes'])

        for obj in queryset:
            writer.writerow([
                obj.criado_em.strftime('%d/%m/%Y %H:%M:%S'),
                obj.get_tipo_display(),
                str(obj.usuario) if obj.usuario else 'Sistema',
                obj.ip or 'N/A',
                obj.get_nivel_display(),
                obj.detalhes or ''
            ])

        return response

    exportar_selecionados.short_description = '📥 Exportar logs selecionados (CSV)'

    # Estatísticas no topo
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}

        # Estatísticas
        hoje = timezone.now().date()
        extra_context['total_logs'] = LogSeguranca.objects.count()
        extra_context['logs_hoje'] = LogSeguranca.objects.filter(
            criado_em__date=hoje
        ).count()
        extra_context['ataques'] = LogSeguranca.objects.filter(tipo='ataque').count()
        extra_context['honeypots'] = LogSeguranca.objects.filter(tipo='honeypot').count()

        return super().changelist_view(request, extra_context=extra_context)


# Registrar outros modelos existentes
@admin.register(Estudante)
class EstudanteAdmin(admin.ModelAdmin):
    list_display = ['nome', 'professor', 'nivel_suporte', 'turma', 'ativo']
    list_filter = ['nivel_suporte', 'ativo', 'turma']
    search_fields = ['nome', 'turma']
    list_editable = ['ativo']


@admin.register(TecnologiaAssistiva)
class TecnologiaAssistivaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'categoria', 'ativo', 'avaliacao_media']
    list_filter = ['categoria', 'ativo']
    search_fields = ['nome', 'descricao']
    list_editable = ['ativo']

@admin.register(AvaliacaoTecnologia)
class AvaliacaoTecnologiaAdmin(admin.ModelAdmin):
    list_display = ['tecnologia', 'professor', 'nota', 'criado_em']
    list_filter = ['nota', 'criado_em']
    search_fields = ['tecnologia__nome', 'professor__nome', 'comentario']
    readonly_fields = ['criado_em', 'atualizado_em']

@admin.register(Recomendacao)
class RecomendacaoAdmin(admin.ModelAdmin):
    list_display = ['estudante', 'professor', 'status', 'criado_em']
    list_filter = ['status', 'criado_em']
    search_fields = ['estudante__nome', 'professor__nome']


@admin.register(PEI)
class PEIAdmin(admin.ModelAdmin):
    list_display = ['estudante', 'professor', 'versao', 'criado_em']
    list_filter = ['versao', 'criado_em']
    search_fields = ['estudante__nome', 'professor__nome']


@admin.register(PerfilTEA)
class PerfilTEAAdmin(admin.ModelAdmin):
    list_display = ['estudante', 'comunicacao', 'perfil_sensorial']
    search_fields = ['estudante__nome']

@admin.register(TermosUso)
class TermosUsoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'versao', 'tipo', 'ativo', 'data_criacao']
    list_filter = ['tipo', 'ativo']
    search_fields = ['titulo', 'conteudo']
    list_editable = ['ativo']

@admin.register(AceiteTermos)
class AceiteTermosAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'termo', 'data_aceite', 'ip']
    list_filter = ['data_aceite', 'termo__tipo']
    search_fields = ['usuario__email', 'ip']
    readonly_fields = ['data_aceite']