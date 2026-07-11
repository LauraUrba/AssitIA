# telas/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout
from django.http import HttpResponse, JsonResponse
from .models import Estudante, TecnologiaAssistiva, Recomendacao, PEI, PerfilTEA, RecomendacaoTA, Feedback
from user.models import Usuario
import json
import requests



# ============ DASHBOARD ============

@login_required
def dashboard(request):
    """Dashboard principal do professor"""
    context = {
        'usuario': request.user,
        'total_estudantes': Estudante.objects.filter(professor=request.user).count(),
        'total_recomendacoes': Recomendacao.objects.filter(professor=request.user).count(),
        'total_pei': PEI.objects.filter(professor=request.user).count(),
        'estudantes_ativos': Estudante.objects.filter(professor=request.user, ativo=True).count(),
    }
    return render(request, 'telas/dashboard.html', context)


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

# telas/views.py

@login_required
def catalogo_tecnologias(request):
    """Catálogo de tecnologias assistivas - APENAS as do banco de dados"""
    # Buscar APENAS tecnologias do banco de dados
    tecnologias = TecnologiaAssistiva.objects.filter(ativo=True)

    # Adicionar campos padrão para tecnologias que não têm os novos campos
    for tech in tecnologias:
        if not tech.descricao:
            tech.descricao = "Tecnologia assistiva para auxílio no desenvolvimento educacional."
        if not tech.exemplos_uso:
            tech.exemplos_uso = "Pode ser utilizada em sala de aula e em atividades terapêuticas."
        if not tech.materiais:
            tech.materiais = "Materiais recicláveis e de fácil acesso"
        if not tech.como_fazer:
            tech.como_fazer = "Siga as instruções do fabricante ou adapte conforme a necessidade do aluno."
        if not tech.como_usar:
            tech.como_usar = "Utilize sob supervisão de um profissional especializado."
        if not tech.para_que_serve:
            tech.para_que_serve = "Auxilia no desenvolvimento, aprendizagem e inclusão do aluno."

    context = {
        'tecnologias': tecnologias,
        'total': tecnologias.count(),
    }
    return render(request, 'tecnologias/catalogo.html', context)

# ============ RECOMENDAÇÕES ============

@login_required
def lista_recomendacoes(request):
    """Lista de recomendações"""
    recomendacoes = Recomendacao.objects.filter(professor=request.user)
    context = {
        'recomendacoes': recomendacoes,
        'total': recomendacoes.count(),
    }
    return render(request, 'recomendacoes/listas.html', context)



@login_required
def gerar_recomendacao(request, estudante_id):
    """Gerar recomendação de TA para um estudante usando a API"""
    estudante = get_object_or_404(Estudante, id=estudante_id, professor=request.user)
    perfil = PerfilTEA.objects.filter(estudante=estudante).first()

    if request.method == 'POST':
        try:
            # Coletar dados do formulário
            area_principal = request.POST.get('area_principal', 'comunicacao')
            prioridade = request.POST.get('prioridade', 'media')

            # Construir a descrição do professor baseada nos dados do aluno
            descricao = f"""Aluno: {estudante.nome}
Nível de suporte: {estudante.get_nivel_suporte_display()}
Turma: {estudante.turma or 'Não informada'}
"""

            if perfil:
                descricao += f"""
Perfil TEA:
- Comunicação: {perfil.comunicacao or 'Não informado'}
- Perfil Sensorial: {perfil.perfil_sensorial or 'Não informado'}
- Habilidade Motora: {perfil.habilidade_motora or 'Não informado'}
- Perfil Cognitivo: {perfil.perfil_cognitivo or 'Não informado'}
- Desafios: {perfil.desafios or 'Não informados'}
- Observações: {perfil.observacoes or 'Não informadas'}
"""

            # Dados para enviar para a API
            payload = {
                "descricao_professor": descricao,
                "idade_aluno": calcular_idade(estudante.data_nascimento) if estudante.data_nascimento else None,
                "nivel_suporte": str(estudante.nivel_suporte),
                "interesses_especificos": request.POST.get('interesses', ''),
                "sensibilidades_sensoriais": request.POST.get('sensibilidades', ''),
                "incluir_estruturas": True,
                "recursos_disponiveis": request.POST.get('recursos', ''),
                "buscar_online": True,
                "comunicacao": perfil.comunicacao if perfil else None,
                "motor": perfil.habilidade_motora if perfil else None,
                "atencao": request.POST.get('atencao', ''),
                "comportamentos": request.POST.get('comportamentos', '')
            }

            # Chamar a API
            api_url = 'https://api-assitia.onrender.com/analisar-aluno-tea/'

            try:
                response = requests.post(
                    api_url,
                    json=payload,
                    headers={'Content-Type': 'application/json'},
                    timeout=30
                )

                if response.status_code == 200:
                    resultado_api = response.json()

                    # Salvar recomendação no banco
                    recomendacao = Recomendacao.objects.create(
                        estudante=estudante,
                        professor=request.user,
                        parametros_entrada=json.dumps(payload),
                        status='gerada'
                    )

                    # Salvar tecnologias recomendadas (do catálogo)
                    # Extrair recursos da análise
                    analise = resultado_api.get('analise', '')
                    recursos_recomendados = extrair_recursos_da_analise(analise)

                    for idx, recurso in enumerate(recursos_recomendados[:5], 1):
                        # Buscar ou criar tecnologia assistiva
                        ta, created = TecnologiaAssistiva.objects.get_or_create(
                            nome=recurso.get('nome', f'Recurso {idx}'),
                            defaults={
                                'categoria': recurso.get('categoria', 'comunicacao'),
                                'descricao': recurso.get('descricao', ''),
                                'exemplos_uso': recurso.get('como_usar', ''),
                            }
                        )

                        RecomendacaoTA.objects.create(
                            recomendacao=recomendacao,
                            ta=ta,
                            justificativa=recurso.get('justificativa', ''),
                            posicao_ranking=idx
                        )

                    messages.success(request, f'Recomendação gerada com sucesso para {estudante.nome}!')
                    return redirect('detalhe_recomendacao', id=recomendacao.id)
                else:
                    messages.error(request, f'Erro na API: {response.status_code}')

            except requests.exceptions.Timeout:
                messages.error(request, 'A API demorou muito para responder. Tente novamente.')
            except requests.exceptions.ConnectionError:
                messages.error(request, 'Não foi possível conectar à API. Verifique sua internet.')
            except Exception as e:
                messages.error(request, f'Erro ao chamar a API: {str(e)}')

        except Exception as e:
            messages.error(request, f'Erro ao gerar recomendação: {str(e)}')

    context = {
        'estudante': estudante,
        'perfil_tea': perfil,
        'tecnologias': TecnologiaAssistiva.objects.filter(ativo=True),
    }
    return render(request, 'recomendacoes/gerar.html', context)


def calcular_idade(data_nascimento):
    """Calcular idade em anos"""
    from datetime import date
    hoje = date.today()
    return hoje.year - data_nascimento.year - ((hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day))


# telas/views.py - Substituir a função extrair_recursos_da_analise

def extrair_recursos_da_analise(analise):
    """
    Extrair tecnologias válidas da análise da IA.
    Retorna apenas tecnologias com nome, descrição e detalhes completos.
    """
    recursos = []

    # Lista de tecnologias conhecidas (para identificar no texto)
    tecnologias_conhecidas = {
        'Prancha de Comunicação': {
            'categoria': 'comunicacao',
            'descricao': 'Recurso visual para auxiliar na comunicação não-verbal, permitindo que o aluno aponte para figuras que representam suas necessidades.',
            'materiais': 'Revistas velhas, tesoura, cola, papelão, velcro, plastificadora',
            'como_fazer': 'Recorte figuras de revistas, organize por categorias, cole em papelão e plastifique.',
            'como_usar': 'O aluno aponta para a figura do que deseja comunicar.',
            'para_que_serve': 'Facilita a comunicação não-verbal e expressão de necessidades.'
        },
        'Garrafa da Calma': {
            'categoria': 'regulacao_sensorial',
            'descricao': 'Recurso sensorial que ajuda na regulação emocional, proporcionando calma e foco através da observação do glitter.',
            'materiais': 'Garrafa PET, água, glitter, corante, cola quente, purpurina',
            'como_fazer': 'Encha a garrafa com água, adicione glitter e corante, feche com cola quente.',
            'como_usar': 'Agite a garrafa e observe o glitter caindo lentamente.',
            'para_que_serve': 'Ajuda na regulação emocional e autoconhecimento.'
        },
        'Kit Sensorial': {
            'categoria': 'regulacao_sensorial',
            'descricao': 'Caixas com diferentes texturas para exploração tátil e estimulação sensorial.',
            'materiais': 'Caixa de sapato, tecidos variados, botões, fitas, grãos',
            'como_fazer': 'Forre a caixa com tecidos, cole botões e fitas, crie compartimentos.',
            'como_usar': 'Deixe o aluno explorar as texturas livremente.',
            'para_que_serve': 'Estimula o tato e a percepção sensorial.'
        },
        'Teclado Adaptado': {
            'categoria': 'motor',
            'descricao': 'Teclado adaptado com teclas grandes para auxiliar na coordenação motora fina.',
            'materiais': 'Papelão, teclas desenhadas, fita adesiva, tesoura',
            'como_fazer': 'Desenhe um teclado em papelão, recorte as teclas, fixe com fita.',
            'como_usar': 'O aluno usa para digitar ou apontar letras.',
            'para_que_serve': 'Auxilia na coordenação motora fina e aprendizado.'
        },
        'Rotina Visual': {
            'categoria': 'estruturacao',
            'descricao': 'Caixas organizadoras para rotina visual, ajudando o aluno a entender a sequência de atividades.',
            'materiais': 'Caixas de fósforo, papel, canetinhas, velcro',
            'como_fazer': 'Desenhe as atividades, recorte e cole nas caixas, organize em sequência.',
            'como_usar': 'Mostre a sequência do dia. O aluno pode mover as caixas conforme conclui.',
            'para_que_serve': 'Dá previsibilidade e reduz a ansiedade.'
        },
        'Cartões de Comunicação': {
            'categoria': 'comunicacao',
            'descricao': 'Cartões com símbolos e figuras para comunicação alternativa, permitindo comunicação simples e eficaz.',
            'materiais': 'Papel cartão, canetinhas, tesoura, plastificador, argola',
            'como_fazer': 'Desenhe os símbolos, recorte e cole no papel cartão, plastifique.',
            'como_usar': 'O aluno mostra o cartão para se comunicar.',
            'para_que_serve': 'Facilita a comunicação alternativa e autonomia.'
        },
        'Fone de Ouvido Caseiro': {
            'categoria': 'regulacao_sensorial',
            'descricao': 'Fone adaptado para reduzir a sobrecarga auditiva em ambientes barulhentos.',
            'materiais': 'Fone velho, espuma acústica, tecido macio, cola quente',
            'como_fazer': 'Remova as almofadas, encha com espuma, recubra com tecido.',
            'como_usar': 'Use em momentos de sobrecarga auditiva.',
            'para_que_serve': 'Reduz a sobrecarga auditiva e promove bem-estar.'
        },
        'História Social Ilustrada': {
            'categoria': 'interacao_social',
            'descricao': 'Histórias ilustradas para ensinar habilidades sociais e comportamentos adequados.',
            'materiais': 'Papel, canetinhas, grampeador, impressões',
            'como_fazer': 'Crie uma história simples, ilustre cada passo, grampeie.',
            'como_usar': 'Leia a história antes da situação acontecer.',
            'para_que_serve': 'Ensina habilidades sociais e reduz ansiedade.'
        },
        'Agenda Visual': {
            'categoria': 'estruturacao',
            'descricao': 'Agenda visual para organizar tarefas e compromissos do dia a dia.',
            'materiais': 'Papel, canetinhas, velcro, quadro magnético',
            'como_fazer': 'Desenhe as tarefas em cartões, recorte, cole velcro.',
            'como_usar': 'O aluno organiza as tarefas do dia na agenda.',
            'para_que_serve': 'Ajuda na organização e planejamento diário.'
        }
    }

    # Procurar por tecnologias conhecidas no texto
    for tech_nome, tech_dados in tecnologias_conhecidas.items():
        if tech_nome.lower() in analise.lower():
            # Verificar se já não foi adicionada
            if not any(r['nome'] == tech_nome for r in recursos):
                recursos.append({
                    'nome': tech_nome,
                    'categoria': tech_dados['categoria'],
                    'descricao': tech_dados['descricao'],
                    'materiais': tech_dados['materiais'],
                    'como_fazer': tech_dados['como_fazer'],
                    'como_usar': tech_dados['como_usar'],
                    'para_que_serve': tech_dados['para_que_serve'],
                    'justificativa': f'Recomendado pela IA para {tech_dados["categoria"]}',
                    'fonte': 'IA'
                })

    # Buscar recursos online (se houver resultados da busca)
    # Procurar por links ou menções a recursos online
    import re
    padrao_online = r'(?:https?://|www\.)[^\s]+'
    links = re.findall(padrao_online, analise)

    # Se encontrou links, adicionar como recursos online
    for i, link in enumerate(links[:3], 1):
        # Tentar extrair título do link
        titulo = f"Recurso Online #{i}"
        for linha in analise.split('\n'):
            if link in linha:
                titulo = linha.replace(link, '').strip()[:50] or f"Recurso Online #{i}"
                break

        recursos.append({
            'nome': f"🌐 {titulo}",
            'categoria': 'online',
            'descricao': f'Recurso encontrado na internet: {link}',
            'materiais': 'Verificar no site',
            'como_fazer': 'Acessar o link para mais informações',
            'como_usar': 'Explorar o recurso conforme instruções do site',
            'para_que_serve': 'Tecnologia assistiva encontrada na internet',
            'justificativa': 'Recurso encontrado na busca online',
            'fonte': 'Internet',
            'link': link
        })

    # Se não encontrou nenhuma tecnologia conhecida, usar as do catálogo
    if not recursos or len([r for r in recursos if r.get('fonte') == 'IA']) == 0:
        from telas.models import TecnologiaAssistiva
        catalogo = TecnologiaAssistiva.objects.filter(ativo=True)[:5]
        for ta in catalogo:
            if not any(r['nome'] == ta.nome for r in recursos):
                recursos.append({
                    'nome': ta.nome,
                    'categoria': ta.categoria,
                    'descricao': ta.descricao,
                    'materiais': ta.materiais,
                    'como_fazer': ta.como_fazer,
                    'como_usar': ta.como_usar,
                    'para_que_serve': ta.para_que_serve,
                    'justificativa': f'Recomendado pela IA para {ta.get_categoria_display()}',
                    'fonte': 'Catálogo'
                })

    return recursos

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


# telas/views.py - Adicionar a view se não existir

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
    """Gerar PDF do PEI"""
    pei = get_object_or_404(PEI, id=id, professor=request.user)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="PEI_{pei.estudante.nome}_v{pei.versao}.pdf"'

    content = f"""
    ========================================
    PLANO EDUCACIONAL INDIVIDUALIZADO - PEI
    ========================================

    Aluno: {pei.estudante.nome}
    Nível de Suporte: {pei.estudante.get_nivel_suporte_display()}
    Turma: {pei.estudante.turma or 'Não informada'}
    Versão: {pei.versao}
    Data: {pei.criado_em.strftime('%d/%m/%Y %H:%M')}

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
    Professor Responsável: {pei.professor.nome}
    ========================================
    """

    response.write(content)
    return response


# ============ PERFIL ============

@login_required
def perfil_usuario(request):
    """Perfil do usuário"""
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

        # Alterar senha
        if nova_senha:
            if not senha_atual:
                messages.error(request, 'Digite sua senha atual para alterar a senha.')
                return redirect('perfil_usuario')

            if not user.check_password(senha_atual):
                messages.error(request, 'Senha atual incorreta.')
                return redirect('perfil_usuario')

            if len(nova_senha) < 8:
                messages.error(request, 'A nova senha deve ter no mínimo 8 caracteres.')
                return redirect('perfil_usuario')

            if nova_senha != confirmar_senha:
                messages.error(request, 'As senhas não coincidem.')
                return redirect('perfil_usuario')

            user.set_password(nova_senha)
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
    }
    return render(request, 'perfil/perfil.html', context)