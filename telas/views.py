from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required
from .security_logger import log_seguranca
from .security_automation import security_automation
from .models import LogSeguranca
from django.db.models import Count
from django.http import JsonResponse
from django.db.models import Avg
from .models import AvaliacaoTecnologia
from .models import (
    Estudante,
    TecnologiaAssistiva,
    Recomendacao,
    PEI,
    PerfilTEA,
    RecomendacaoTA,
    Feedback
)
from user.models import Usuario
import json
import requests
import re
import logging

logger = logging.getLogger(__name__)

# ============ DASHBOARD ============

@login_required
def dashboard(request):
    """Dashboard principal do professor"""

    total_estudantes = Estudante.objects.filter(professor=request.user).count()
    estudantes_ativos = Estudante.objects.filter(professor=request.user, ativo=True).count()
    total_recomendacoes = Recomendacao.objects.filter(professor=request.user).count()
    total_pei = PEI.objects.filter(professor=request.user).count()

    # Calcular percentual de alunos ativos
    percentual_ativos = 0
    if total_estudantes > 0:
        percentual_ativos = round((estudantes_ativos / total_estudantes) * 100)

    # Buscar últimos alunos acessados
    ultimos_estudantes = Estudante.objects.filter(
        professor=request.user
    ).order_by('-atualizado_em')[:5]

    cores = [
        'primary', 'success', 'warning', 'danger', 'purple',
        'pink', 'teal', 'orange', 'indigo', 'cyan',
        'rose', 'amber', 'emerald', 'violet', 'fuchsia',
    ]

    for i, estudante in enumerate(ultimos_estudantes):
        estudante.cor = cores[i % len(cores)]

    context = {
        'usuario': request.user,
        'total_estudantes': total_estudantes,
        'estudantes_ativos': estudantes_ativos,
        'percentual_ativos': percentual_ativos,  # ⬅️ ADICIONE ESTA LINHA
        'total_recomendacoes': total_recomendacoes,
        'total_pei': total_pei,
        'ultimos_estudantes': ultimos_estudantes,
    }
    return render(request, 'telas/dashboard.html', context)


@login_required
@staff_member_required
def dashboard_seguranca(request):
    """Dashboard de segurança (apenas para administradores)"""

    # Estatísticas
    hoje = timezone.now().date()
    inicio_dia = timezone.make_aware(timezone.datetime.combine(hoje, timezone.datetime.min.time()))

    stats = {
        'total_logs': LogSeguranca.objects.filter(criado_em__gte=inicio_dia).count(),
        'falhas_login': LogSeguranca.objects.filter(tipo='falha_login', criado_em__gte=inicio_dia).count(),
        'ataques': LogSeguranca.objects.filter(tipo='ataque', criado_em__gte=inicio_dia).count(),
        'honeypots': LogSeguranca.objects.filter(tipo='honeypot', criado_em__gte=inicio_dia).count(),
    }

    # Últimos logs
    logs_recentes = LogSeguranca.objects.all()[:50]

    # IPs mais ativos (suspeitos)
    ips_suspeitos = LogSeguranca.objects.filter(
        criado_em__gte=inicio_dia
    ).exclude(
        ip__isnull=True
    ).values('ip').annotate(
        total=Count('id')
    ).order_by('-total')[:10]

    # Gráficos por tipo
    tipos = LogSeguranca.objects.filter(
        criado_em__gte=inicio_dia
    ).values('tipo').annotate(
        total=Count('id')
    ).order_by('tipo')

    # Verificar IPs bloqueados
    ip_bloqueado = security_automation.verificar_ip_bloqueado

    context = {
        'stats': stats,
        'logs_recentes': logs_recentes,
        'ips_suspeitos': ips_suspeitos,
        'tipos': tipos,
        'ip_bloqueado': ip_bloqueado,
    }

    return render(request, 'telas/seguranca/dashboard.html', context)

@login_required
@staff_member_required
def desbloquear_ip_view(request, ip):
    """Desbloquear um IP"""
    if request.method == 'POST':
        from .security_automation import security_automation
        security_automation.desbloquear_ip(ip)
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Método não permitido'}, status=405)



# ============ ESTUDANTES ============

@login_required
def lista_estudantes(request):
    """Lista de estudantes"""
    estudantes = Estudante.objects.filter(professor=request.user)
    context = {
        'estudantes': estudantes,
        'total': estudantes.count(),
    }
    return render(request, 'estudantes/listas.html', context)


@login_required
def novo_estudante(request):
    """Formulário para criar estudante"""
    if request.method == 'POST':
        nome = request.POST.get('nome')
        data_nascimento = request.POST.get('data_nascimento')
        nivel_suporte = request.POST.get('nivel_suporte')
        turma = request.POST.get('turma')

        if not nome or not nivel_suporte:
            messages.error(request, 'Nome e Nível de Suporte são obrigatórios.')
            return render(request, 'estudantes/form.html', {'edit': False})

        try:
            estudante = Estudante.objects.create(
                professor=request.user,
                nome=nome,
                data_nascimento=data_nascimento if data_nascimento else None,
                nivel_suporte=nivel_suporte,
                turma=turma
            )
            messages.success(request, f'Estudante {nome} criado com sucesso!')
            return redirect('detalhe_estudante', id=estudante.id)
        except Exception as e:
            messages.error(request, f'Erro ao criar estudante: {str(e)}')

    return render(request, 'estudantes/form.html', {'edit': False})


@login_required
def detalhe_estudante(request, id):
    """Detalhe do estudante"""
    estudante = get_object_or_404(Estudante, id=id, professor=request.user)
    context = {
        'estudante': estudante,
        'recomendacoes': Recomendacao.objects.filter(estudante=estudante),
        'peis': PEI.objects.filter(estudante=estudante),
        'perfil': PerfilTEA.objects.filter(estudante=estudante).first(),
    }
    return render(request, 'estudantes/detalhe.html', context)


@login_required
def editar_estudante(request, id):
    """Editar estudante"""
    estudante = get_object_or_404(Estudante, id=id, professor=request.user)

    if request.method == 'POST':
        estudante.nome = request.POST.get('nome', estudante.nome)
        estudante.data_nascimento = request.POST.get('data_nascimento') or None
        estudante.nivel_suporte = request.POST.get('nivel_suporte', estudante.nivel_suporte)
        estudante.turma = request.POST.get('turma', estudante.turma)
        estudante.ativo = request.POST.get('ativo') == 'on'
        estudante.save()

        messages.success(request, 'Estudante atualizado com sucesso!')
        return redirect('detalhe_estudante', id=estudante.id)

    context = {
        'estudante': estudante,
        'edit': True,
    }
    return render(request, 'estudantes/form.html', context)


@login_required
def salvar_perfil_tea(request, estudante_id):
    """Salvar perfil TEA"""
    estudante = get_object_or_404(Estudante, id=estudante_id, professor=request.user)

    if request.method == 'POST':
        perfil, created = PerfilTEA.objects.get_or_create(estudante=estudante)
        perfil.comunicacao = request.POST.get('comunicacao')
        perfil.perfil_sensorial = request.POST.get('perfil_sensorial')
        perfil.habilidade_motora = request.POST.get('habilidade_motora')
        perfil.perfil_cognitivo = request.POST.get('perfil_cognitivo')
        perfil.desafios = request.POST.get('desafios')
        perfil.observacoes = request.POST.get('observacoes')
        perfil.save()

        messages.success(request, 'Perfil TEA salvo com sucesso!')

    return redirect('detalhe_estudante', id=estudante_id)


# ============ TECNOLOGIAS ASSISTIVAS ============


@login_required
def catalogo_tecnologias(request):
    """Catálogo de tecnologias assistivas - APENAS as fixas"""
    from django.db.models import Avg, Count

    tecnologias = TecnologiaAssistiva.objects.filter(
        ativo=True,
        criada_por_ia=False
    )

    # ATUALIZAR OS CAMPOS DE AVALIAÇÃO PARA CADA TECNOLOGIA
    for tech in tecnologias:
        # Calcular média e total
        media = tech.avaliacoes.aggregate(Avg('nota'))['nota__avg']
        total = tech.avaliacoes.count()

        # Atualizar os campos do modelo (se houver alteração)
        if tech.avaliacao_media != (media or 0) or tech.total_avaliacoes != total:
            tech.avaliacao_media = media or 0
            tech.total_avaliacoes = total
            tech.save(update_fields=['avaliacao_media', 'total_avaliacoes'])

        # Dados para exibição
        tech.avaliacao_media_display = tech.avaliacao_media
        tech.total_avaliacoes_display = tech.total_avaliacoes

        # Verificar se o usuário já avaliou
        avaliacao_usuario = tech.avaliacoes.filter(professor=request.user).first()
        tech.avaliacao_usuario = avaliacao_usuario.nota if avaliacao_usuario else 0

        # Pré-carregar avaliações para o modal
        tech.avaliacoes_list = tech.avaliacoes.select_related('professor')[:10]

    context = {
        'tecnologias': tecnologias,
        'total': tecnologias.count(),
    }
    return render(request, 'tecnologias/catalogo.html', context)


@login_required
def avaliar_tecnologia(request):
    """Salvar avaliação de uma tecnologia"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método não permitido'}, status=405)

    import json
    try:
        data = json.loads(request.body)
        tecnologia_id = data.get('tecnologia_id')
        nota = data.get('nota')
        comentario = data.get('comentario', '')

        if not tecnologia_id or not nota:
            return JsonResponse({'success': False, 'message': 'Dados incompletos'})

        if nota < 1 or nota > 5:
            return JsonResponse({'success': False, 'message': 'Nota inválida'})

        tecnologia = get_object_or_404(TecnologiaAssistiva, id=tecnologia_id, ativo=True)

        # Verificar se o usuário já avaliou
        avaliacao, created = AvaliacaoTecnologia.objects.get_or_create(
            tecnologia=tecnologia,
            professor=request.user,
            defaults={
                'nota': nota,
                'comentario': comentario
            }
        )

        if not created:
            avaliacao.nota = nota
            avaliacao.comentario = comentario
            avaliacao.save()
            message = 'Sua avaliação foi atualizada com sucesso!'
        else:
            message = 'Avaliação enviada com sucesso! Obrigado pelo seu feedback.'

        # ATUALIZAR OS CAMPOS DA TECNOLOGIA
        from django.db.models import Avg, Count
        media = tecnologia.avaliacoes.aggregate(Avg('nota'))['nota__avg'] or 0
        total = tecnologia.avaliacoes.count()

        tecnologia.avaliacao_media = media
        tecnologia.total_avaliacoes = total
        tecnologia.save(update_fields=['avaliacao_media', 'total_avaliacoes'])

        return JsonResponse({
            'success': True,
            'message': message,
            'nova_media': round(media, 1),
            'total_avaliacoes': total,
            'nota_usuario': nota
        })

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Dados inválidos'}, status=400)
    except Exception as e:
        logger.error(f"Erro ao salvar avaliação: {str(e)}")
        return JsonResponse({'success': False, 'message': 'Erro ao salvar avaliação'}, status=500)


# ============ RECOMENDAÇÕES ============

@login_required
def gerar_recomendacao(request, estudante_id):
    """Gerar recomendação de TA para um estudante usando a API com dados dos checkboxes"""
    estudante = get_object_or_404(Estudante, id=estudante_id, professor=request.user)
    perfil = PerfilTEA.objects.filter(estudante=estudante).first()

    if request.method == 'POST':
        try:
            # ============ COLETAR DADOS DO FORMULÁRIO ============
            area_principal = request.POST.get('area_principal', 'comunicacao')
            prioridade = request.POST.get('prioridade', 'media')

            interesses = request.POST.get('interesses', '')
            interesses_observacao = request.POST.get('interesses_observacao', '')
            if interesses_observacao:
                interesses = f"{interesses}, {interesses_observacao}" if interesses else interesses_observacao

            sensibilidades = request.POST.get('sensibilidades', '')
            sensibilidades_observacao = request.POST.get('sensibilidades_observacao', '')
            if sensibilidades_observacao:
                sensibilidades = f"{sensibilidades}, {sensibilidades_observacao}" if sensibilidades else sensibilidades_observacao

            recursos = request.POST.get('recursos', '')
            recursos_observacao = request.POST.get('recursos_observacao', '')
            if recursos_observacao:
                recursos = f"{recursos}, {recursos_observacao}" if recursos else recursos_observacao

            areas_atencao = request.POST.getlist('areas')
            areas_texto = ', '.join(areas_atencao) if areas_atencao else 'Nao informadas'

            # ============ CONSTRUIR DESCRIÇÃO ============
            descricao = f"""Aluno: {estudante.nome}
Nível: {estudante.get_nivel_suporte_display()}
Turma: {estudante.turma or 'N/I'}
"""

            if perfil:
                descricao += f"""
Comunicação: {perfil.comunicacao or 'N/I'}
Sensorial: {perfil.perfil_sensorial or 'N/I'}
Motor: {perfil.habilidade_motora or 'N/I'}
Cognitivo: {perfil.perfil_cognitivo or 'N/I'}
Desafios: {perfil.desafios or 'N/I'}
"""

            # ============ PAYLOAD PARA A API ============
            payload = {
                "descricao_professor": descricao,
                "idade_aluno": calcular_idade(estudante.data_nascimento) if estudante.data_nascimento else None,
                "nivel_suporte": str(estudante.nivel_suporte),
                "interesses_especificos": interesses,
                "sensibilidades_sensoriais": sensibilidades,
                "incluir_estruturas": True,
                "recursos_disponiveis": recursos,
                "buscar_online": True,
                "comunicacao": perfil.comunicacao if perfil else None,
                "motor": perfil.habilidade_motora if perfil else None,
                "atencao": request.POST.get('atencao', ''),
                "comportamentos": request.POST.get('comportamentos', ''),
                "area_principal": area_principal,
                "prioridade": prioridade,
                "areas_atencao": areas_texto,
                "interesses": interesses,
                "sensibilidades": sensibilidades,
                "recursos": recursos,
                "interesses_observacao": interesses_observacao,
                "sensibilidades_observacao": sensibilidades_observacao,
                "recursos_observacao": recursos_observacao
            }

            # 🔥 SALVAR AS SELEÇÕES PARA USAR NO FALLBACK
            selecoes = {
                'areas_atencao': areas_atencao,
                'interesses': interesses,
                'sensibilidades': sensibilidades,
                'recursos': recursos,
                'area_principal': area_principal,
                'prioridade': prioridade
            }

            # ============ CHAMAR API  ============
            api_url = 'https://api-assitia.onrender.com/analisar-aluno-tea/'

            import time
            response = None
            max_tentativas = 3

            for tentativa in range(max_tentativas):
                try:
                    response = requests.post(
                        api_url,
                        json=payload,
                        headers={'Content-Type': 'application/json'},
                        timeout=180  # 🔥 90 segundos por tentativa
                    )
                    if response.status_code == 200:
                        break
                    elif response.status_code != 200:
                        break
                except requests.exceptions.Timeout:
                    if tentativa < max_tentativas - 1:
                        print(f"⏱️ Tentativa {tentativa + 1} falhou. Aguardando 5 segundos...")
                        time.sleep(5)
                        continue
                    else:
                        messages.warning(request, '⏱️ A IA está demorando. Usando recomendações rápidas do catálogo.')
                        return gerar_recomendacao_rapida(request, estudante, selecoes)
                except Exception as e:
                    messages.error(request, f'❌ Erro ao gerar recomendação: {str(e)}')
                    return gerar_recomendacao_rapida(request, estudante, selecoes)

            if response and response.status_code == 200:
                resultado_api = response.json()
                recomendacao = Recomendacao.objects.create(
                    estudante=estudante,
                    professor=request.user,
                    parametros_entrada=json.dumps(payload),
                    status='gerada'
                )

                analise = resultado_api.get('analise', '')
                recursos_recomendados = extrair_recursos_da_analise(analise, selecoes)


                # Salvar tecnologias recomendadas (ATÉ 11)
                # telas/views.py - Substituir o bloco de salvar recomendações

                for idx, recurso in enumerate(recursos_recomendados[:11], 1):
                    # 🔥 SE FOR LINK DA INTERNET
                    if recurso.get('link'):
                        # 🔥 NÃO CRIAR NO CATÁLOGO! Apenas associar à recomendação
                        # Buscar ou criar uma tecnologia "virtual" apenas para esta recomendação
                        ta, created = TecnologiaAssistiva.objects.get_or_create(
                            nome=f"🌐 {recurso.get('nome', f'Recurso Online {idx}')[:50]}",
                            defaults={
                                'categoria': 'online',
                                'descricao': recurso.get('descricao', 'Recurso encontrado na internet'),
                                'materiais': recurso.get('materiais', 'Acessar o link para ver os materiais'),
                                'como_fazer': recurso.get('como_fazer', 'Acesse o link para mais informações'),
                                'como_usar': recurso.get('como_usar',
                                                         'Explore o recurso conforme as instruções do site'),
                                'para_que_serve': recurso.get('para_que_serve',
                                                              'Tecnologia assistiva encontrada na internet'),
                                'exemplos_uso': recurso.get('link', ''),  # Guardar o link aqui
                                'criada_por_ia': True,  # 🔥 MARCAR COMO IA
                                'ativo': True
                            }
                        )
                    else:
                        # 🔥 SE FOR DO CATÁLOGO, BUSCAR OU CRIAR
                        ta, created = TecnologiaAssistiva.objects.get_or_create(
                            nome=recurso.get('nome', f'Recurso {idx}'),
                            defaults={
                                'categoria': recurso.get('categoria', 'comunicacao'),
                                'descricao': recurso.get('descricao', ''),
                                'materiais': recurso.get('materiais', ''),
                                'como_fazer': recurso.get('como_fazer', ''),
                                'como_usar': recurso.get('como_usar', ''),
                                'para_que_serve': recurso.get('para_que_serve', ''),
                                'criada_por_ia': True,  # 🔥 MARCAR COMO IA
                                'ativo': True
                            }
                        )

                    # Criar a associação na recomendação
                    RecomendacaoTA.objects.create(
                        recomendacao=recomendacao,
                        ta=ta,
                        justificativa=recurso.get('justificativa', 'Recomendado pela IA'),
                        posicao_ranking=idx
                    )

                messages.success(request, f'✅ Recomendação gerada com sucesso para {estudante.nome}!')
                return redirect('detalhe_recomendacao', id=recomendacao.id)
            else:
                messages.error(request, f'❌ Erro na API: {response.status_code if response else "Sem resposta"}')
                return gerar_recomendacao_rapida(request, estudante, selecoes)

        except requests.exceptions.Timeout:
            messages.warning(request, '⏱️ A IA está demorando. Usando recomendações rápidas do catálogo.')
            return gerar_recomendacao_rapida(request, estudante, selecoes)
        except Exception as e:
            messages.error(request, f'❌ Erro ao gerar recomendação: {str(e)}')
            logger.error(f"Erro ao gerar recomendação: {str(e)}")
            return gerar_recomendacao_rapida(request, estudante, selecoes)

    context = {
        'estudante': estudante,
        'perfil_tea': perfil,
        'tecnologias': TecnologiaAssistiva.objects.filter(ativo=True, criada_por_ia=False),
    }
    return render(request, 'recomendacoes/gerar.html', context)


def gerar_recomendacao_rapida(request, estudante, selecoes=None):
    """Gerar recomendação rápida usando catálogo priorizando áreas selecionadas"""
    try:
        recomendacao = Recomendacao.objects.create(
            estudante=estudante,
            professor=request.user,
            parametros_entrada='{"fallback": "rapido"}',
            status='gerada'
        )

        # PRIORIZAR ÁREAS SELECIONADAS
        if selecoes and selecoes.get('areas_atencao'):
            areas = selecoes['areas_atencao']
            mapa_categorias = {
                'comunicacao': 'comunicacao',
                'sensorial': 'regulacao_sensorial',
                'motor': 'motor',
                'cognitivo': 'cognitivo',
                'social': 'interacao_social',
                'estrutura': 'estruturacao'
            }

            categorias_para_buscar = []
            for area in areas:
                area = area.lower().strip()
                if area in mapa_categorias:
                    categorias_para_buscar.append(mapa_categorias[area])

            if categorias_para_buscar:
                tecs = TecnologiaAssistiva.objects.filter(
                    ativo=True,
                    criada_por_ia=False,
                    categoria__in=categorias_para_buscar
                )[:5]
            else:
                tecs = TecnologiaAssistiva.objects.filter(ativo=True, criada_por_ia=False)[:5]
        else:
            tecs = TecnologiaAssistiva.objects.filter(ativo=True, criada_por_ia=False)[:5]

        # SALVAR COM JUSTIFICATIVA CORRETA
        for idx, ta in enumerate(tecs[:5], 1):
            RecomendacaoTA.objects.create(
                recomendacao=recomendacao,
                ta=ta,
                justificativa=f'Recomendado pela IA para {ta.get_categoria_display()}',
                posicao_ranking=idx
            )

        messages.info(request, f'✅ Recomendação gerada para {estudante.nome}!')
        return redirect('detalhe_recomendacao', id=recomendacao.id)
    except Exception as e:
        messages.error(request, f'❌ Erro ao gerar recomendação: {str(e)}')
        return redirect('detalhe_estudante', id=estudante.id)

def calcular_idade(data_nascimento):
    """Calcular idade em anos"""
    from datetime import date
    hoje = date.today()
    return hoje.year - data_nascimento.year - ((hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day))


def extrair_recursos_da_analise(analise, selecoes=None):
    """
    Extrair recursos da análise da IA.
    Retorna: 3 do catálogo + 6 links únicos + 2 do catálogo (complemento) = 11
    """
    recursos = []
    from telas.models import TecnologiaAssistiva
    import re

    if not selecoes:
        selecoes = {}

    # ================================================
    # 1. RECURSOS DO CATÁLOGO (DA ANÁLISE DA API)
    # ================================================
    padrao_recurso = r'#### \d+\. \*\*(.+?)\*\*\s*\n\n\*\*📦 Materiais:\*\* (.+?)\n\n\*\*🔧 Como fazer:\*\* (.+?)\n\n\*\*👩‍🏫 Como usar:\*\* (.+?)\n\n\*\*🎯 Para que serve:\*\* (.+?)(?=\n\n---|\n\n###|\Z)'
    matches = re.findall(padrao_recurso, analise, re.DOTALL)

    for match in matches:
        nome = match[0].strip()
        materiais, como_fazer, como_usar, para_que_serve = [m.strip() for m in match[1:]]

        try:
            ta = TecnologiaAssistiva.objects.get(nome=nome, criada_por_ia=False)
            categoria = ta.categoria
        except TecnologiaAssistiva.DoesNotExist:
            categoria = 'comunicacao'

        recursos.append({
            'nome': nome,
            'categoria': categoria,
            'descricao': para_que_serve,
            'materiais': materiais,
            'como_fazer': como_fazer,
            'como_usar': como_usar,
            'para_que_serve': para_que_serve,
            'justificativa': f'Recomendado pela IA para {categoria}',
            'fonte': 'IA',
            'link': None
        })

        if len([r for r in recursos if r.get('fonte') == 'IA']) >= 3:
            break

    # ================================================
    # 2. RECURSOS DA INTERNET (CORRIGIDO)
    # ================================================
    padrao_online = re.compile(
        r'\*\*\d+\.\s*(.+?)\*\*\s*\n\n(.*?)\n\n🔗\s*Fonte:\s*(\S+)',
        re.DOTALL
    )
    matches_online = padrao_online.findall(analise)

    links_vistos = set()
    for titulo_bruto, snippet, link in matches_online:
        link = link.strip()

        # Pular links inválidos ou duplicados
        if not link or link in links_vistos:
            continue
        if 'assitia' in link or 'localhost' in link or '127.0.0.1' in link:
            continue

        links_vistos.add(link)
        titulo = titulo_bruto.strip()[:80]

        # Identificar fonte
        if "youtube" in link or "youtu.be" in link:
            fonte = "YouTube"
        elif "tiktok" in link:
            fonte = "TikTok"
        elif "pinterest" in link:
            fonte = "Pinterest"
        elif ".pdf" in link:
            fonte = "PDF"
        elif "slideshare" in link:
            fonte = "Slideshare"
        elif "edu" in link or "educ" in link:
            fonte = "Educacional"
        else:
            fonte = "Site"

        recursos.append({
            'nome': f"🌐 {titulo}",
            'categoria': 'online',
            'descricao': snippet.strip()[:300] or 'Recurso encontrado na internet pela IA',
            'materiais': 'Acessar o link para ver os materiais',
            'como_fazer': 'Acesse o link para mais informações',
            'como_usar': 'Explore o recurso conforme as instruções do site',
            'para_que_serve': 'Tecnologia assistiva encontrada na internet',
            'justificativa': f'Recurso recomendado pela IA - Fonte: {fonte}',
            'fonte': 'Internet',
            'link': link
        })

        if len([r for r in recursos if r.get('fonte') == 'Internet']) >= 6:
            break

    # ================================================
    # 3. COMPLETAR COM CATÁLOGO (ATÉ 11)
    # ================================================
    if len(recursos) < 11:
        areas_atencao = selecoes.get('areas_atencao', [])
        mapa_catalogo = {
            'comunicacao': ['AAC - Livro de Comunicação Personalizado', 'Cartões de Comunicação',
                            'Prancha de Comunicação'],
            'regulacao_sensorial': ['Garrafa da Calma', 'Kit Sensorial com Caixas', 'Fone de Ouvido Caseiro'],
            'motor': ['Teclado Adaptado com Papelão', 'Prancha de Atividades Motoras'],
            'cognitivo': ['Jogo da Memória Adaptado', 'Atividades de Raciocínio Lógico'],
            'interacao_social': ['Cartões de Habilidades Sociais', 'História Social Ilustrada'],
            'estruturacao': ['Rotina Visual com Caixas', 'Agenda Visual de Tarefas'],
        }

        tecs_adicionais = []
        for area in areas_atencao:
            area = area.lower().strip()
            if area in mapa_catalogo:
                for nome_tech in mapa_catalogo[area]:
                    if not any(r['nome'] == nome_tech for r in recursos):
                        try:
                            ta = TecnologiaAssistiva.objects.get(nome=nome_tech, criada_por_ia=False)
                            tecs_adicionais.append(ta)
                        except TecnologiaAssistiva.DoesNotExist:
                            pass

        for ta in tecs_adicionais[:11 - len(recursos)]:
            recursos.append({
                'nome': ta.nome,
                'categoria': ta.categoria,
                'descricao': ta.descricao,
                'materiais': ta.materiais,
                'como_fazer': ta.como_fazer,
                'como_usar': ta.como_usar,
                'para_que_serve': ta.para_que_serve,
                'justificativa': f'Recomendado pela IA para {ta.get_categoria_display()}',
                'fonte': 'Catálogo',
                'link': None
            })

    return recursos[:11]


@login_required
def detalhe_recomendacao(request, id):
    """Detalhe da recomendação"""
    recomendacao = get_object_or_404(Recomendacao, id=id, professor=request.user)

    if recomendacao.status == 'gerada':
        recomendacao.status = 'visualizada'
        recomendacao.save()

    context = {
        'recomendacao': recomendacao,
        'tecnologias_recomendadas': recomendacao.recomendacoes_ta.all(),
    }
    return render(request, 'recomendacoes/detalhe.html', context)


@login_required
def salvar_recomendacao(request):
    """Salvar recomendação gerada pela IA"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            estudante_id = data.get('estudante_id')
            recomendacoes = data.get('recomendacoes', [])
            parametros = data.get('parametros', {})

            estudante = get_object_or_404(Estudante, id=estudante_id, professor=request.user)

            recomendacao = Recomendacao.objects.create(
                estudante=estudante,
                professor=request.user,
                parametros_entrada=json.dumps(parametros),
                status='gerada'
            )

            for idx, rec in enumerate(recomendacoes, 1):
                try:
                    ta = TecnologiaAssistiva.objects.get(id=rec.get('id'))
                    RecomendacaoTA.objects.create(
                        recomendacao=recomendacao,
                        ta=ta,
                        justificativa=rec.get('justificativa', ''),
                        posicao_ranking=idx
                    )
                except TecnologiaAssistiva.DoesNotExist:
                    continue

            return JsonResponse({
                'success': True,
                'recomendacao_id': str(recomendacao.id)
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)

    return JsonResponse({'error': 'Método não permitido'}, status=405)


@login_required
def excluir_recomendacao(request, id):
    """Excluir uma recomendação específica"""
    if request.method == 'POST':
        try:
            recomendacao = get_object_or_404(Recomendacao, id=id, professor=request.user)

            # Verificar se o usuário tem permissão para excluir
            if recomendacao.professor != request.user:
                return JsonResponse({
                    'success': False,
                    'error': 'Você não tem permissão para excluir esta recomendação.'
                }, status=403)

            # Excluir a recomendação (cascade vai excluir as RecomendacaoTA também)
            nome_estudante = recomendacao.estudante.nome
            recomendacao.delete()

            return JsonResponse({
                'success': True,
                'message': f'Recomendação para {nome_estudante} excluída com sucesso!'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)

    return JsonResponse({'error': 'Método não permitido'}, status=405)


@login_required
def salvar_feedback(request):
    """Salvar feedback do professor sobre recomendação"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            recomendacao_ta_id = data.get('recomendacao_ta_id')
            avaliacao = data.get('avaliacao')
            comentario = data.get('comentario', '')

            recomendacao_ta = get_object_or_404(RecomendacaoTA, id=recomendacao_ta_id)

            feedback, created = Feedback.objects.get_or_create(
                recomendacao_ta=recomendacao_ta,
                professor=request.user,
                defaults={
                    'avaliacao': avaliacao,
                    'comentario': comentario
                }
            )

            if not created:
                feedback.avaliacao = avaliacao
                feedback.comentario = comentario
                feedback.save()

            # Atualizar avaliação média da tecnologia
            ta = recomendacao_ta.ta
            avaliacoes = Feedback.objects.filter(
                recomendacao_ta__ta=ta,
                avaliacao='aceita'
            ).count()
            total_avaliacoes = Feedback.objects.filter(
                recomendacao_ta__ta=ta
            ).count()

            if total_avaliacoes > 0:
                ta.avaliacao_media = (avaliacoes / total_avaliacoes) * 5
                ta.total_avaliacoes = total_avaliacoes
                ta.save()

            return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)

    return JsonResponse({'error': 'Método não permitido'}, status=405)


@login_required
def arquivar_recomendacao(request, id):
    """Arquivar uma recomendação"""
    if request.method == 'POST':
        try:
            recomendacao = get_object_or_404(Recomendacao, id=id, professor=request.user)
            recomendacao.status = 'arquivada'
            recomendacao.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)

    return JsonResponse({'error': 'Método não permitido'}, status=405)

@login_required
def lista_recomendacoes(request):
    """Lista de recomendações"""
    recomendacoes = Recomendacao.objects.filter(professor=request.user)
    context = {
        'recomendacoes': recomendacoes,
        'total': recomendacoes.count(),
    }
    return render(request, 'recomendacoes/listas.html', context)


# ============ POPULAR CATÁLOGO ============

@staff_member_required
def executar_populate(request):
    """View para executar o populate_catalogos.py no Render (sem shell)"""
    from django.core.management import call_command
    import io
    import sys

    try:
        # Capturar a saída do comando
        out = io.StringIO()
        sys.stdout = out

        # Executar o comando populate_catalogos
        call_command('populate_catalogos')

        # Restaurar stdout
        sys.stdout = sys.__stdout__

        resultado = out.getvalue()

        return HttpResponse(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Popular Catálogo</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 900px; margin: 50px auto; padding: 20px; background: #f3f4f6; }}
                .container {{ background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
                h1 {{ color: #4F46E5; margin-top: 0; }}
                h2 {{ color: #1F2937; font-size: 18px; margin: 20px 0 10px; }}
                pre {{ 
                    background: #1a1a1a; 
                    color: #10B981; 
                    padding: 20px; 
                    border-radius: 8px; 
                    overflow-x: auto; 
                    font-size: 13px;
                    max-height: 500px;
                    overflow-y: auto;
                    font-family: 'Courier New', monospace;
                    line-height: 1.6;
                }}
                .btn-group {{ margin-top: 20px; display: flex; gap: 10px; flex-wrap: wrap; }}
                .btn {{ 
                    display: inline-block; 
                    background: #4F46E5; 
                    color: white; 
                    padding: 12px 24px; 
                    text-decoration: none; 
                    border-radius: 8px; 
                    font-weight: 600;
                    transition: background 0.2s;
                }}
                .btn:hover {{ background: #4338CA; }}
                .btn-secondary {{ background: #6B7280; }}
                .btn-secondary:hover {{ background: #4B5563; }}
                .btn-success {{ background: #10B981; }}
                .btn-success:hover {{ background: #059669; }}
                .stats {{ 
                    background: #F3F4F6; 
                    padding: 15px 20px; 
                    border-radius: 8px; 
                    margin: 15px 0;
                    display: flex;
                    gap: 30px;
                    flex-wrap: wrap;
                }}
                .stats-item {{ display: flex; align-items: center; gap: 8px; }}
                .stats-number {{ font-size: 24px; font-weight: 700; color: #4F46E5; }}
                .stats-label {{ color: #6B7280; font-size: 14px; }}
                .success {{ color: #10B981; }}
                .error {{ color: #EF4444; }}
                hr {{ border: none; border-top: 2px solid #E5E7EB; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📚 Popular Catálogo de Tecnologias</h1>
                <hr>

                <div class="stats">
                    <div class="stats-item">
                        <span class="stats-number" id="totalCount">0</span>
                        <span class="stats-label">Tecnologias criadas</span>
                    </div>
                    <div class="stats-item">
                        <span class="stats-number" id="totalTecnologias">0</span>
                        <span class="stats-label">Total no catálogo</span>
                    </div>
                </div>

                <h2>📝 Resultado da execução:</h2>
                <pre id="output">{resultado}</pre>

                <div class="btn-group">
                    <a href="/telas/tecnologias/catalogo/" class="btn btn-success">🔗 Ver Catálogo</a>
                    <a href="/admin/" class="btn btn-secondary">⚙️ Admin</a>
                    <a href="/telas/executar-populate/" class="btn">🔄 Executar Novamente</a>
                </div>
            </div>

            <script>
                // Contar quantas tecnologias foram criadas
                const output = document.getElementById('output');
                const text = output.textContent;
                const criadas = (text.match(/✅ Criada:/g) || []).length;
                const total = (text.match(/📊 Total no catálogo: (\\d+)/) || [])[1] || '0';

                document.getElementById('totalCount').textContent = criadas;
                document.getElementById('totalTecnologias').textContent = total;

                // Adicionar cores ao output
                let html = output.innerHTML;
                html = html.replace(/✅ Criada:.*/g, match => `<span style="color: #10B981;">${match}</span>`);
                html = html.replace(/⚠️.*/g, match => `<span style="color: #F59E0B;">${match}</span>`);
                html = html.replace(/❌.*/g, match => `<span style="color: #EF4444;">${match}</span>`);
                output.innerHTML = html;
            </script>
        </body>
        </html>
        """)

    except Exception as e:
        import traceback
        return HttpResponse(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Erro</title>
            <style>
                body {{ font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px; background: #FEF2F2; }}
                .container {{ background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
                h1 {{ color: #DC2626; }}
                .error {{ color: #DC2626; background: #FEE2E2; padding: 15px; border-radius: 8px; overflow-x: auto; }}
                .traceback {{ background: #1a1a1a; color: #FCD34D; padding: 20px; border-radius: 8px; overflow-x: auto; font-size: 13px; }}
                .btn {{ display: inline-block; background: #6B7280; color: white; padding: 10px 20px; text-decoration: none; border-radius: 6px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>❌ Erro ao executar</h1>
                <div class="error">
                    <strong>Mensagem:</strong> {str(e)}
                </div>
                <div class="traceback">
                    {traceback.format_exc()}
                </div>
                <a href="/admin/" class="btn">⚙️ Voltar ao Admin</a>
            </div>
        </body>
        </html>
        """, status=500)


# ============ PEI ============

@login_required
def lista_pei(request):
    """Lista de PEIs"""
    peis = PEI.objects.filter(professor=request.user)
    context = {
        'peis': peis,
        'total': peis.count(),
    }
    return render(request, 'pei/listas.html', context)


@login_required
def gerar_pei(request, estudante_id):
    """Gerar PEI para um estudante"""
    estudante = get_object_or_404(Estudante, id=estudante_id, professor=request.user)

    if request.method == 'POST':
        objetivos = request.POST.get('objetivos')
        estrategias = request.POST.get('estrategias')
        recursos = request.POST.get('recursos')

        if not objetivos:
            messages.error(request, 'Objetivos são obrigatórios.')
            return render(request, 'pei/gerar.html', {'estudante': estudante})

        try:
            pei = PEI.objects.create(
                estudante=estudante,
                professor=request.user,
                objetivos=objetivos,
                estrategias=estrategias,
                recursos=recursos
            )
            messages.success(request, f'PEI gerado para {estudante.nome}!')
            return redirect('detalhe_pei', id=pei.id)
        except Exception as e:
            messages.error(request, f'Erro ao gerar PEI: {str(e)}')

    context = {
        'estudante': estudante,
    }
    return render(request, 'pei/gerar.html', context)


@login_required
def detalhe_pei(request, id):
    """Detalhe do PEI"""
    pei = get_object_or_404(PEI, id=id, professor=request.user)
    return render(request, 'pei/detalhe.html', {'pei': pei})


@login_required
def editar_pei(request, id):
    """Editar PEI"""
    pei = get_object_or_404(PEI, id=id, professor=request.user)

    if request.method == 'POST':
        pei.objetivos = request.POST.get('objetivos', pei.objetivos)
        pei.estrategias = request.POST.get('estrategias', pei.estrategias)
        pei.recursos = request.POST.get('recursos', pei.recursos)
        pei.versao += 1
        pei.save()

        messages.success(request, 'PEI atualizado com sucesso!')
        return redirect('detalhe_pei', id=pei.id)

    context = {
        'pei': pei,
        'edit': True,
    }
    return render(request, 'pei/form.html', context)


@login_required
def gerar_pdf_pei(request, id):
    """Gerar PDF do PEI com formatação melhorada"""
    pei = get_object_or_404(PEI, id=id, professor=request.user)

    # Criar resposta PDF
    response = HttpResponse(content_type='application/pdf')
    response[
        'Content-Disposition'] = f'attachment; filename="PEI_{pei.estudante.nome}_v{pei.versao}_{pei.criado_em.strftime("%Y%m%d")}.pdf'

    # Criar conteúdo do PDF
    content = f"""
    ========================================
    PLANO EDUCACIONAL INDIVIDUALIZADO - PEI
    ========================================

    DATA DE GERAÇÃO: {timezone.now().strftime('%d/%m/%Y %H:%M')}

    ----------------------------------------
    INFORMAÇÕES DO ALUNO
    ----------------------------------------
    Nome: {pei.estudante.nome}
    Nível de Suporte: {pei.estudante.get_nivel_suporte_display()}
    Turma: {pei.estudante.turma or 'Não informada'}
    Data de Nascimento: {pei.estudante.data_nascimento.strftime('%d/%m/%Y') if pei.estudante.data_nascimento else 'Não informada'}

    ----------------------------------------
    OBJETIVOS
    ----------------------------------------
    {pei.objetivos or 'Não informado'}

    ----------------------------------------
    ESTRATÉGIAS
    ----------------------------------------
    {pei.estrategias or 'Não informado'}

    ----------------------------------------
    RECURSOS
    ----------------------------------------
    {pei.recursos or 'Não informado'}

    ----------------------------------------
    INFORMAÇÕES DO PEI
    ----------------------------------------
    Versão: {pei.versao}
    Criado em: {pei.criado_em.strftime('%d/%m/%Y %H:%M')}
    Última atualização: {pei.atualizado_em.strftime('%d/%m/%Y %H:%M')}
    Professor Responsável: {pei.professor.nome}

    ========================================
    AssistIA - Sistema de Recomendação de Tecnologias Assistivas
    ========================================
    """

    response.write(content)
    return response


# ============ PERFIL ============


@login_required
def perfil_usuario(request):
    """Perfil do usuário com histórico de senhas"""
    if request.method == 'POST':
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        senha_atual = request.POST.get('senha_atual')
        nova_senha = request.POST.get('nova_senha')
        confirmar_senha = request.POST.get('confirmar_senha')

        user = request.user

        # Atualizar nome e email
        if nome:
            user.nome = nome
        if email and email != user.email:
            if Usuario.objects.filter(email=email).exclude(id=user.id).exists():
                messages.error(request, 'Este email já está em uso.')
                return redirect('perfil_usuario')
            user.email = email

        # ============ ALTERAR SENHA COM HISTÓRICO ============
        if nova_senha:
            # Validar senha atual
            if not senha_atual:
                messages.error(request, 'Digite sua senha atual para alterar a senha.')
                return redirect('perfil_usuario')

            if not user.check_password(senha_atual):
                messages.error(request, 'Senha atual incorreta.')
                return redirect('perfil_usuario')

            # Validar nova senha com hardening
            from user.views import validar_senha_segura, verificar_senha_vazada
            erros_senha = validar_senha_segura(nova_senha, user.nome, user.email)
            if erros_senha:
                for erro in erros_senha:
                    messages.error(request, erro)
                return redirect('perfil_usuario')

            # Verificar se a senha foi vazada
            if verificar_senha_vazada(nova_senha):
                messages.error(request,
                               'Esta senha foi encontrada em vazamentos de dados. Por favor, escolha uma senha mais segura.')
                return redirect('perfil_usuario')

            # Verificar se a senha já foi usada anteriormente
            if user.verificar_senha_no_historico(nova_senha):
                messages.error(request, 'Esta senha já foi usada anteriormente. Por favor, escolha uma nova senha.')
                return redirect('perfil_usuario')

            if len(nova_senha) < 8:
                messages.error(request, 'A nova senha deve ter no mínimo 8 caracteres.')
                return redirect('perfil_usuario')

            if nova_senha != confirmar_senha:
                messages.error(request, 'As senhas não coincidem.')
                return redirect('perfil_usuario')

            # Salvar nova senha
            user.set_password(nova_senha)

            # Salvar no histórico
            user.salvar_historico_senha(nova_senha)

            messages.success(request, 'Senha alterada com sucesso!')

        user.save()
        messages.success(request, 'Perfil atualizado com sucesso!')

        # Se a senha foi alterada, fazer logout para forçar novo login
        if nova_senha:
            logout(request)
            messages.info(request, 'Faça login novamente com sua nova senha.')
            return redirect('login')

        return redirect('perfil_usuario')

    context = {
        'usuario': request.user,
        'total_estudantes': Estudante.objects.filter(professor=request.user).count(),
        'total_recomendacoes': Recomendacao.objects.filter(professor=request.user).count(),
        'total_pei': PEI.objects.filter(professor=request.user).count(),
        'total_tecnologias': TecnologiaAssistiva.objects.filter(ativo=True).count(),
        'historico_senhas': request.user.password_history.all()[:5]  # Últimas 5 senhas
    }
    return render(request, 'perfil/perfil.html', context)