from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from .models import Usuario
from django.utils import timezone
from django.http import JsonResponse
from telas.models import TermosUso

from .security_logger import (
    log_tentativa_login,
    log_tentativa_2fa,
    log_tentativa_cadastro,
    log_recuperacao_senha,
    log_ataque_suspeito,
    log_honeypot
)

import re
import logging
import hashlib
from django.core.cache import cache
from django.http import HttpResponseServerError
import time
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse


logger = logging.getLogger(__name__)

# ============= HONEYPOT ===============

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse


@csrf_exempt
def honeypot_log(request):
    """Registrar tentativas de honeypot"""
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            ip = request.META.get('REMOTE_ADDR')

            log_honeypot(ip, data.get('campo', 'desconhecido'), f"Valor: {data.get('valor', 'vazio')}")

            return JsonResponse({'status': 'ok'})
        except:
            pass
    return JsonResponse({'status': 'error'}, status=400)

# ============ VIEWS PARA TELAS HTML ============

def login_view(request):
    """Página de login do site com Honeypot e proteção contra brute force"""

    # ============ HONEYPOT: VERIFICAR IP BLOQUEADO ============
    ip = request.META.get('REMOTE_ADDR')
    cache_key_falhas = f'login_falhas_{ip}'
    cache_key_bloqueado = f'login_bloqueado_{ip}'

    # Verificar se o IP está bloqueado (honeypot ativado)
    if cache.get(cache_key_bloqueado):
        # 🔥 PÁGINA FALSA DE ERRO 500 - HONEYPOT!
        logger.warning(f"🚨 HONEYPOT ATIVADO! IP {ip} bloqueado após múltiplas tentativas")
        log_ataque_suspeito(ip, "Honeypot - Erro 500", "IP bloqueado após 3 tentativas")
        return HttpResponseServerError("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Erro 500 - AssistIA</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    background: #1a1a1a; 
                    color: #fff; 
                    display: flex; 
                    justify-content: center; 
                    align-items: center; 
                    height: 100vh; 
                    margin: 0;
                    flex-direction: column;
                }
                .error-container {
                    text-align: center;
                    padding: 40px;
                }
                .error-code {
                    font-size: 72px;
                    font-weight: bold;
                    color: #EF4444;
                    text-shadow: 0 0 20px rgba(239, 68, 68, 0.3);
                }
                .error-title {
                    font-size: 24px;
                    margin: 20px 0;
                    color: #F3F4F6;
                }
                .error-message {
                    color: #9CA3AF;
                    max-width: 500px;
                    line-height: 1.6;
                }
                .error-details {
                    margin-top: 30px;
                    padding: 20px;
                    background: rgba(255,255,255,0.05);
                    border-radius: 8px;
                    font-size: 13px;
                    color: #6B7280;
                    border: 1px solid rgba(255,255,255,0.1);
                }
                .error-details code {
                    color: #FCD34D;
                    background: rgba(0,0,0,0.3);
                    padding: 2px 8px;
                    border-radius: 4px;
                }
                .error-icon {
                    font-size: 48px;
                    margin-bottom: 20px;
                }
                .blink {
                    animation: blink 1s step-end infinite;
                }
                @keyframes blink {
                    50% { opacity: 0; }
                }
            </style>
        </head>
        <body>
            <div class="error-container">
                <div class="error-icon">⚠️</div>
                <div class="error-code">500</div>
                <div class="error-title">Erro Interno do Servidor</div>
                <div class="error-message">
                    Ocorreu um erro inesperado ao processar sua solicitação.
                    A equipe de suporte foi notificada e está trabalhando na resolução.
                </div>
                <div class="error-details">
                    <p><strong>ID do Erro:</strong> <code>#HONEYPOT_{{ ip.replace('.', '_') }}</code></p>
                    <p><strong>Status:</strong> <span style="color: #EF4444;">● Crítico</span></p>
                    <p><strong>Timestamp:</strong> <span id="timestamp"></span></p>
                    <p style="margin-top: 10px; font-size: 12px; color: #4B5563;">
                        Este erro foi registrado automaticamente. <span class="blink">●</span>
                    </p>
                </div>
            </div>
            <script>
                document.getElementById('timestamp').textContent = new Date().toLocaleString('pt-BR');
            </script>
        </body>
        </html>
        """, status=500)

    # ============ VERIFICAR TENTATIVAS DE LOGIN ============
    tentativas = cache.get(cache_key_falhas, 0)

    # Se já tem 3 tentativas, ativar honeypot
    if tentativas >= 3:
        # Bloquear IP por 15 minutos
        cache.set(cache_key_bloqueado, True, 900)  # 15 minutos
        # Manter contagem para monitoramento
        cache.set(cache_key_falhas, 0, 900)

        logger.warning(f"🚨 HONEYPOT ATIVADO! IP {ip} - {tentativas} tentativas falhas")
        log_ataque_suspeito(ip, "Honeypot - Erro 500", f"{tentativas} tentativas falhas")

        # 🔥 PÁGINA FALSA DE ERRO 500
        return HttpResponseServerError("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Erro 500 - AssistIA</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    background: #1a1a1a; 
                    color: #fff; 
                    display: flex; 
                    justify-content: center; 
                    align-items: center; 
                    height: 100vh; 
                    margin: 0;
                    flex-direction: column;
                }
                .error-container {
                    text-align: center;
                    padding: 40px;
                }
                .error-code {
                    font-size: 72px;
                    font-weight: bold;
                    color: #EF4444;
                    text-shadow: 0 0 20px rgba(239, 68, 68, 0.3);
                }
                .error-title {
                    font-size: 24px;
                    margin: 20px 0;
                    color: #F3F4F6;
                }
                .error-message {
                    color: #9CA3AF;
                    max-width: 500px;
                    line-height: 1.6;
                }
                .error-details {
                    margin-top: 30px;
                    padding: 20px;
                    background: rgba(255,255,255,0.05);
                    border-radius: 8px;
                    font-size: 13px;
                    color: #6B7280;
                    border: 1px solid rgba(255,255,255,0.1);
                }
                .error-details code {
                    color: #FCD34D;
                    background: rgba(0,0,0,0.3);
                    padding: 2px 8px;
                    border-radius: 4px;
                }
                .blink {
                    animation: blink 1s step-end infinite;
                }
                @keyframes blink {
                    50% { opacity: 0; }
                }
            </style>
        </head>
        <body>
            <div class="error-container">
                <div class="error-icon">⚠️</div>
                <div class="error-code">500</div>
                <div class="error-title">Erro Interno do Servidor</div>
                <div class="error-message">
                    Ocorreu um erro inesperado ao processar sua solicitação.
                    A equipe de suporte foi notificada e está trabalhando na resolução.
                </div>
                <div class="error-details">
                    <p><strong>ID do Erro:</strong> <code>Erro ao acessar a página{{ ip.replace('.', '_') }}</code></p>
                    <p><strong>Status:</strong> <span style="color: #EF4444;">● Crítico</span></p>
                    <p><strong>Timestamp:</strong> <span id="timestamp2"></span></p>
                    <p style="margin-top: 10px; font-size: 12px; color: #4B5563;">
                        Este erro foi registrado automaticamente. <span class="blink">●</span>
                    </p>
                </div>
            </div>
            <script>
                document.getElementById('timestamp2').textContent = new Date().toLocaleString('pt-BR');
            </script>
        </body>
        </html>
        """, status=500)

    # ============ PROCESSAMENTO NORMAL DO LOGIN ============
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # ============ VERIFICAR HONEYPOT ============
        # Campo honeypot - se foi preenchido, é um bot
        honeypot = request.POST.get('honeypot', '')
        if honeypot:
            log_honeypot(ip, 'honeypot', f"Valor preenchido: {honeypot}")
            # Retorna erro 500 falso
            return HttpResponseServerError("""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Erro 500 - AssistIA</title>
                <style>
                    body { 
                        font-family: Arial, sans-serif; 
                        background: #1a1a1a; 
                        color: #fff; 
                        display: flex; 
                        justify-content: center; 
                        align-items: center; 
                        height: 100vh; 
                        margin: 0;
                        flex-direction: column;
                    }
                    .error-container {
                        text-align: center;
                        padding: 40px;
                    }
                    .error-code {
                        font-size: 72px;
                        font-weight: bold;
                        color: #EF4444;
                        text-shadow: 0 0 20px rgba(239, 68, 68, 0.3);
                    }
                    .error-title {
                        font-size: 24px;
                        margin: 20px 0;
                        color: #F3F4F6;
                    }
                    .error-message {
                        color: #9CA3AF;
                        max-width: 500px;
                        line-height: 1.6;
                    }
                    .error-details {
                        margin-top: 30px;
                        padding: 20px;
                        background: rgba(255,255,255,0.05);
                        border-radius: 8px;
                        font-size: 13px;
                        color: #6B7280;
                        border: 1px solid rgba(255,255,255,0.1);
                    }
                    .error-details code {
                        color: #FCD34D;
                        background: rgba(0,0,0,0.3);
                        padding: 2px 8px;
                        border-radius: 4px;
                    }
                    .blink {
                        animation: blink 1s step-end infinite;
                    }
                    @keyframes blink {
                        50% { opacity: 0; }
                    }
                </style>
            </head>
            <body>
                <div class="error-container">
                    <div class="error-icon">⚠️</div>
                    <div class="error-code">500</div>
                    <div class="error-title">Erro Interno do Servidor</div>
                    <div class="error-message">
                        Ocorreu um erro inesperado ao processar sua solicitação.
                        A equipe de suporte foi notificada e está trabalhando na resolução.
                    </div>
                    <div class="error-details">
                        <p><strong>ID do Erro:</strong> <code>#BOT_DETECTED</code></p>
                        <p><strong>Status:</strong> <span style="color: #EF4444;">● Crítico</span></p>
                        <p><strong>Timestamp:</strong> <span id="timestamp3"></span></p>
                        <p style="margin-top: 10px; font-size: 12px; color: #4B5563;">
                            Este erro foi registrado automaticamente. <span class="blink">●</span>
                        </p>
                    </div>
                </div>
                <script>
                    document.getElementById('timestamp3').textContent = new Date().toLocaleString('pt-BR');
                </script>
            </body>
            </html>
            """, status=500)

        # ============ VERIFICAR TEMPO DE PREENCHIMENTO ============
        honeypot_time = request.POST.get('honeypot_time', '')
        if honeypot_time:
            try:
                time_diff = (int(time.time() * 1000) - int(honeypot_time)) / 1000
                if time_diff < 3:  # Menos de 3 segundos = bot
                    log_honeypot(ip, 'tempo_preenchimento', f"Tempo: {time_diff:.2f} segundos")
                    return HttpResponseServerError("""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <title>Erro 500 - AssistIA</title>
                        <style>
                            body { 
                                font-family: Arial, sans-serif; 
                                background: #1a1a1a; 
                                color: #fff; 
                                display: flex; 
                                justify-content: center; 
                                align-items: center; 
                                height: 100vh; 
                                margin: 0;
                                flex-direction: column;
                            }
                            .error-container {
                                text-align: center;
                                padding: 40px;
                            }
                            .error-code {
                                font-size: 72px;
                                font-weight: bold;
                                color: #EF4444;
                                text-shadow: 0 0 20px rgba(239, 68, 68, 0.3);
                            }
                            .error-title {
                                font-size: 24px;
                                margin: 20px 0;
                                color: #F3F4F6;
                            }
                            .error-message {
                                color: #9CA3AF;
                                max-width: 500px;
                                line-height: 1.6;
                            }
                            .error-details {
                                margin-top: 30px;
                                padding: 20px;
                                background: rgba(255,255,255,0.05);
                                border-radius: 8px;
                                font-size: 13px;
                                color: #6B7280;
                                border: 1px solid rgba(255,255,255,0.1);
                            }
                            .error-details code {
                                color: #FCD34D;
                                background: rgba(0,0,0,0.3);
                                padding: 2px 8px;
                                border-radius: 4px;
                            }
                            .blink {
                                animation: blink 1s step-end infinite;
                            }
                            @keyframes blink {
                                50% { opacity: 0; }
                            }
                        </style>
                    </head>
                    <body>
                        <div class="error-container">
                            <div class="error-icon">⚠️</div>
                            <div class="error-code">500</div>
                            <div class="error-title">Erro Interno do Servidor</div>
                            <div class="error-message">
                                Ocorreu um erro inesperado ao processar sua solicitação.
                            </div>
                            <div class="error-details">
                                <p><strong>ID do Erro:</strong> <code>#RAPID_FILL</code></p>
                                <p><strong>Status:</strong> <span style="color: #EF4444;">● Crítico</span></p>
                                <p><strong>Timestamp:</strong> <span id="timestamp4"></span></p>
                            </div>
                        </div>
                        <script>
                            document.getElementById('timestamp4').textContent = new Date().toLocaleString('pt-BR');
                        </script>
                    </body>
                    </html>
                    """, status=500)
            except:
                pass

        if not email or not password:
            messages.error(request, 'Por favor, preencha todos os campos.')
            return render(request, 'auth/login.html')

        user = authenticate(request, username=email, password=password)

        if user is not None:
            if user.ativo:
                # 🔥 REATIVAR 2FA - DESCOMENTADO E FUNCIONANDO
                try:
                    from .utils import send_otp
                    if send_otp(request, user):
                        # Salvar email na sessão para verificação
                        request.session['user_email'] = user.email
                        request.session['_auth_user_id'] = str(user.id)

                        # Resetar tentativas
                        cache.delete(cache_key_falhas)
                        cache.delete(cache_key_bloqueado)

                        log_tentativa_login(email, user.nome, True, ip, "Login bem-sucedido - Aguardando 2FA")
                        messages.info(request, f'🔐 Código de verificação enviado para {user.email}')

                        # Redirecionar para verificação OTP
                        return redirect('verificar_otp')
                    else:
                        messages.error(request, 'Erro ao enviar código de verificação. Tente novamente.')
                        return render(request, 'auth/login.html')
                except Exception as e:
                    logger.error(f"Erro no 2FA: {str(e)}")
                    messages.error(request, 'Erro no sistema de verificação. Tente novamente.')
                    return render(request, 'auth/login.html')
            else:
                messages.error(request, 'Usuário inativo. Contate o administrador.')
                return render(request, 'auth/login.html')
        else:
            # ============ LOGIN FALHOU ============
            tentativas = cache.get(cache_key_falhas, 0) + 1
            cache.set(cache_key_falhas, tentativas, 900)

            log_tentativa_login(email, email, False, ip, f"Senha incorreta - tentativa {tentativas}/3")

            tentativas_restantes = 3 - tentativas
            if tentativas_restantes > 0:
                messages.error(request,
                               f'Email ou senha incorretos. Você tem mais {tentativas_restantes} tentativa(s) antes do bloqueio.')
            else:
                messages.error(request, 'Email ou senha incorretos. Sua próxima tentativa será registrada.')

            return render(request, 'auth/login.html')

    return render(request, 'auth/login.html')

# user/views.py - Função cadastro_view completa com termos

def cadastro_view(request):
    """Página de cadastro do site com Hardening de Senhas, Histórico e Termos de Uso"""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        email = request.POST.get('email', '').strip()
        perfil = request.POST.get('perfil', '').strip()
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        # ============ VALIDAÇÃO DE CAMPOS OBRIGATÓRIOS ============
        if not all([nome, email, perfil, password, confirm_password]):
            messages.error(request, 'Todos os campos são obrigatórios.')
            return render(request, 'auth/cadastro.html')

        # ============ VALIDAÇÃO DE EMAIL ============
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_regex, email):
            messages.error(request, 'Email em formato inválido.')
            return render(request, 'auth/cadastro.html')

        # ============ VALIDAÇÃO DE SENHA (HARDENING) ============
        erros_senha = validar_senha_segura(password, nome, email)
        if erros_senha:
            for erro in erros_senha:
                messages.error(request, erro)
            return render(request, 'auth/cadastro.html')

        # ============ VERIFICAR SE A SENHA FOI VAZADA ============
        if verificar_senha_vazada(password):
            messages.error(request,
                           'Esta senha foi encontrada em vazamentos de dados. Por favor, escolha uma senha mais segura.')
            return render(request, 'auth/cadastro.html')

        # ============ VERIFICAR SE AS SENHAS COINCIDEM ============
        if password != confirm_password:
            messages.error(request, 'As senhas não coincidem.')
            return render(request, 'auth/cadastro.html')

        # ============ VERIFICAR SE USUÁRIO JÁ EXISTE ============
        if Usuario.objects.filter(email=email).exists():
            messages.error(request, 'Este email já está cadastrado.')
            return render(request, 'auth/cadastro.html')

        # ============ VERIFICAR TERMOS DE USO ============
        termos_aceitos = request.POST.get('termos_uso')
        politica_aceita = request.POST.get('politica_privacidade')

        if not termos_aceitos or not politica_aceita:
            messages.error(request, 'Você deve aceitar os Termos de Uso e a Política de Privacidade.')
            return render(request, 'auth/cadastro.html')

        # ============ CRIAR USUÁRIO ============
        try:
            usuario = Usuario.objects.create_user(
                email=email,
                nome=nome,
                perfil=perfil,
                password=password
            )

            # ============ SALVAR ACEITE DOS TERMOS ============
            try:
                from telas.models import TermosUso, AceiteTermos

                ip = request.META.get('REMOTE_ADDR')
                user_agent = request.META.get('HTTP_USER_AGENT', '')

                # Termos de Uso
                termo_uso = TermosUso.objects.filter(tipo='termos_uso', ativo=True).first()
                if termo_uso:
                    AceiteTermos.objects.create(
                        usuario=usuario,
                        termo=termo_uso,
                        ip=ip,
                        user_agent=user_agent
                    )
                    logger.info(f"Termos de Uso aceitos por {usuario.email}")

                # Política de Privacidade
                politica = TermosUso.objects.filter(tipo='politica_privacidade', ativo=True).first()
                if politica:
                    AceiteTermos.objects.create(
                        usuario=usuario,
                        termo=politica,
                        ip=ip,
                        user_agent=user_agent
                    )
                    logger.info(f"Política de Privacidade aceita por {usuario.email}")

                # Consentimento para Menores (se marcado)
                consentimento_menor = request.POST.get('consentimento_menor')
                if consentimento_menor:
                    consentimento = TermosUso.objects.filter(tipo='consentimento_menor', ativo=True).first()
                    if consentimento:
                        AceiteTermos.objects.create(
                            usuario=usuario,
                            termo=consentimento,
                            ip=ip,
                            user_agent=user_agent
                        )
                        logger.info(f"Consentimento para Menores aceito por {usuario.email}")

            except Exception as e:
                logger.error(f"Erro ao salvar aceite dos termos: {str(e)}")
                # Não impede o cadastro se falhar o salvamento dos termos

            # ============ SALVAR SENHA NO HISTÓRICO ============
            usuario.salvar_historico_senha(password)

            messages.success(request, 'Conta criada com sucesso! Faça login.')
            return redirect('login')

        except Exception as e:
            logger.error(f"Erro ao criar usuário: {str(e)}")
            messages.error(request, 'Erro ao criar conta. Tente novamente.')
            return render(request, 'auth/cadastro.html')

    return render(request, 'auth/cadastro.html')

def termos_view(request, tipo):
    """Retorna os termos solicitados em JSON"""
    try:
        termo = TermosUso.objects.filter(tipo=tipo, ativo=True).first()
        if termo:
            return JsonResponse({
                'titulo': termo.titulo,
                'versao': termo.versao,
                'conteudo': termo.conteudo
            })
        return JsonResponse({'conteudo': 'Conteúdo não disponível.'}, status=404)
    except Exception as e:
        return JsonResponse({'conteudo': 'Erro ao carregar os termos.'}, status=500)



def verificar_senha_vazada(password):
    """Verificar se a senha foi vazada usando Have I Been Pwned API"""
    try:
        import requests
        import hashlib
        sha1 = hashlib.sha1(password.encode()).hexdigest().upper()
        prefix, suffix = sha1[:5], sha1[5:]

        response = requests.get(f'https://api.pwnedpasswords.com/range/{prefix}', timeout=5)
        if response.status_code == 200:
            for line in response.text.splitlines():
                if line.startswith(suffix):
                    return True
        return False
    except:
        # Se falhar a verificação, permitir (não bloquear)
        return False

def logout_view(request):
    """Logout do usuário"""
    logout(request)
    messages.info(request, 'Você saiu da sua conta.')
    return redirect('login')


# tratamento de erro

def esqueci_senha_view(request):
    """Página de recuperação de senha"""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()

        if not email:
            messages.error(request, 'Por favor, informe seu email.')
            return render(request, 'auth/esqueci_senha.html')

        try:
            user = Usuario.objects.get(email=email)

            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            reset_link = request.build_absolute_uri(
                f'/auth/redefinir-senha/{uid}/{token}/'
            )

            try:
                send_mail(
                    'Redefinição de senha - AssistIA',
                    f"""Olá, {user.nome}!

Você solicitou a redefinição de senha.

Clique no link abaixo para redefinir sua senha:
{reset_link}

Este link expira em 24 horas.

Se você não solicitou esta redefinição, ignore este email.

Atenciosamente,
Equipe AssistIA
""",
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False
                )
                messages.success(request, 'Email enviado com sucesso! Verifique sua caixa de entrada.')
            except Exception as e:
                # Se falhar o envio, mostrar mensagem amigável
                messages.warning(request, 'Não foi possível enviar o email. Tente novamente mais tarde.')
                logger.error(f"Erro ao enviar email: {str(e)}")

        except Usuario.DoesNotExist:
            messages.info(request, 'Se o email estiver cadastrado, você receberá as instruções.')

    return render(request, 'auth/esqueci_senha.html')


def redefinir_senha_view(request, uidb64, token):
    """Página para redefinir senha"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Usuario.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
        messages.error(request, 'Link inválido ou expirado.')
        return redirect('login')

    if not default_token_generator.check_token(user, token):
        messages.error(request, 'Link inválido ou expirado.')
        return redirect('login')

    if request.method == 'POST':
        nova_senha = request.POST.get('nova_senha', '').strip()
        confirmar_senha = request.POST.get('confirmar_senha', '').strip()

        if not nova_senha or not confirmar_senha:
            messages.error(request, 'Preencha todos os campos.')
            return render(request, 'auth/redefinir_senha.html', {'validlink': True})

        if nova_senha != confirmar_senha:
            messages.error(request, 'As senhas não coincidem.')
            return render(request, 'auth/redefinir_senha.html', {'validlink': True})

        if len(nova_senha) < 8:
            messages.error(request, 'A senha deve ter no mínimo 8 caracteres.')
            return render(request, 'auth/redefinir_senha.html', {'validlink': True})

        user.set_password(nova_senha)
        user.save()

        messages.success(request, 'Senha redefinida com sucesso! Faça login.')
        return redirect('login')

    return render(request, 'auth/redefinir_senha.html', {'validlink': True})


# ============ HARDENING DE SENHAS ============

def validar_senha_segura(password, nome, email):
    """Validar senha com requisitos de segurança avançados"""
    erros = []

    # 1. Mínimo 12 caracteres (aumentado de 8 para 12)
    if len(password) < 12:
        erros.append('A senha deve ter no mínimo 12 caracteres')

    # 2. Pelo menos uma letra maiúscula
    if not re.search(r'[A-Z]', password):
        erros.append('A senha deve conter pelo menos uma letra maiúscula (A-Z)')

    # 3. Pelo menos uma letra minúscula
    if not re.search(r'[a-z]', password):
        erros.append('A senha deve conter pelo menos uma letra minúscula (a-z)')

    # 4. Pelo menos um número
    if not re.search(r'[0-9]', password):
        erros.append('A senha deve conter pelo menos um número (0-9)')

    # 5. Pelo menos um caractere especial
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        erros.append('A senha deve conter pelo menos um caractere especial (!@#$%^&*(),.?":{}|<>)')

    # 6. Não pode conter nome ou email
    if nome and password.lower().find(nome.lower()) != -1:
        erros.append('A senha não pode conter seu nome')

    if email and password.lower().find(email.split('@')[0].lower()) != -1:
        erros.append('A senha não pode conter seu email')

    # 7. Não pode conter sequências comuns
    sequencias_comuns = ['123456', 'abcdef', 'qwerty', 'senha', 'password', 'admin']
    for seq in sequencias_comuns:
        if seq in password.lower():
            erros.append(f'A senha não pode conter sequências comuns como "{seq}"')
            break

    # 8. Não pode ter caracteres repetidos em sequência (ex: aaaa, 1111)
    if re.search(r'(.)\1{3,}', password):
        erros.append('A senha não pode ter 4 ou mais caracteres repetidos em sequência')

    return erros



# ============ VIEWS PARA API (SEM DECORATORS) ============

def register_user(request):
    """Registrar novo usuário via API"""
    if request.method == 'GET':
        # Para teste, mostrar uma mensagem simples
        return JsonResponse({
            'mensagem': 'Esta é uma API de registro. Use POST para criar um usuário.',
            'exemplo': {
                'email': 'usuario@email.com',
                'nome': 'Seu Nome',
                'perfil': 'professor',
                'password': 'senha123'
            }
        })

    if request.method != 'POST':
        return JsonResponse({'erro': 'Método não permitido. Use POST.'}, status=405)

    import json
    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({'erro': 'Dados inválidos'}, status=400)

    email = data.get('email', '').strip()
    nome = data.get('nome', '').strip()
    perfil = data.get('perfil', '').strip()
    password = data.get('password', '').strip()

    if not all([email, nome, perfil, password]):
        return JsonResponse({'erro': 'Todos os campos são obrigatórios.'}, status=400)

    if Usuario.objects.filter(email=email).exists():
        return JsonResponse({'erro': 'Este email já está cadastrado.'}, status=400)

    try:
        usuario = Usuario.objects.create_user(
            email=email,
            nome=nome,
            perfil=perfil,
            password=password
        )
        return JsonResponse({
            'sucesso': 'Usuário cadastrado com sucesso!',
            'usuario': {
                'id': str(usuario.id),
                'nome': usuario.nome,
                'email': usuario.email,
                'perfil': usuario.perfil
            }
        }, status=201)
    except Exception as e:
        return JsonResponse({'erro': f'Erro ao criar usuário: {str(e)}'}, status=500)


def login_user(request):
    """Login via API"""
    if request.method == 'GET':
        # Para teste, mostrar uma mensagem simples
        return JsonResponse({
            'mensagem': 'Esta é uma API de login. Use POST para fazer login.',
            'exemplo': {
                'email': 'usuario@email.com',
                'password': 'senha123'
            }
        })

    if request.method != 'POST':
        return JsonResponse({'erro': 'Método não permitido. Use POST.'}, status=405)

    import json
    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({'erro': 'Dados inválidos'}, status=400)

    email = data.get('email', '').strip()
    password = data.get('password', '').strip()

    if not email or not password:
        return JsonResponse({'erro': 'Email e senha são obrigatórios.'}, status=400)

    try:
        user = Usuario.objects.get(email=email)
        if not user.check_password(password):
            return JsonResponse({'erro': 'Credenciais inválidas.'}, status=401)

        login(request, user)

        return JsonResponse({
            'sucesso': 'Login realizado com sucesso!',
            'usuario': {
                'id': str(user.id),
                'nome': user.nome,
                'email': user.email,
                'perfil': user.perfil
            }
        })
    except Usuario.DoesNotExist:
        return JsonResponse({'erro': 'Credenciais inválidas.'}, status=401)


# user/views.py - Adicione esta função

def verificar_otp_view(request):
    """Página de verificação OTP com segurança e integração com login"""

    # ============ VERIFICAR SESSÃO ============
    email = request.session.get('user_email')
    user_id = request.session.get('_auth_user_id')

    if not email or not user_id:
        messages.error(request, 'Sessão expirada. Faça login novamente.')
        return redirect('login')

    ip = request.META.get('REMOTE_ADDR')

    # Buscar usuário
    try:
        user = Usuario.objects.get(id=user_id, email=email)
    except Usuario.DoesNotExist:
        messages.error(request, 'Usuário não encontrado.')
        return redirect('login')

    # ============ HONEYPOT PARA 2FA ============
    cache_key_2fa = f'2fa_tentativas_{ip}_{email}'
    tentativas_2fa = cache.get(cache_key_2fa, 0)

    if tentativas_2fa >= 5:
        messages.error(request, 'Muitas tentativas. Aguarde 5 minutos para tentar novamente.')
        return render(request, 'auth/verificar_otp.html', {'bloqueado': True, 'email': email})

    # Mostrar código debug no terminal
    if 'otp_code_debug' in request.session:
        print(f"\n{'=' * 50}")
        print(f"🔐 CÓDIGO OTP PARA {email}")
        print(f"📱 Código: {request.session['otp_code_debug']}")
        print(f"⏱️  Válido por: 5 minutos")
        print(f"{'=' * 50}\n")

    if request.method == 'POST':
        otp = request.POST.get('otp', '').strip()

        if not otp or len(otp) != 6:
            messages.error(request, 'Código inválido. Digite os 6 dígitos.')
            return render(request, 'auth/verificar_otp.html', {'email': email})

        # ============ VERIFICAR CÓDIGO ============
        debug_code = request.session.get('otp_code_debug')
        otp_secret_key = request.session.get('otp_secret_key')
        codigo_valido = False

        # Verificar debug_code
        if debug_code and otp == debug_code:
            codigo_valido = True
            logger.info(f"✅ OTP validado com código DEBUG para {email}")

        # Verificar OTP normal
        elif otp_secret_key:
            otp_valid_until = request.session.get('otp_valid_date')
            if otp_valid_until:
                from datetime import datetime
                valid_until = datetime.fromisoformat(otp_valid_until)
                if datetime.now() <= valid_until:
                    import pyotp
                    totp = pyotp.TOTP(otp_secret_key, interval=300)
                    if totp.verify(otp):
                        codigo_valido = True
                        logger.info(f"✅ OTP validado com sucesso para {email}")

        if codigo_valido:
            # ============ LIMPAR SESSÃO 2FA ============
            request.session.pop('user_email', None)
            request.session.pop('_auth_user_id', None)
            request.session.pop('otp_secret_key', None)
            request.session.pop('otp_valid_date', None)
            request.session.pop('otp_code_debug', None)
            cache.delete(cache_key_2fa)

            # ============ FAZER LOGIN ============
            from django.contrib.auth import login as auth_login

            # 🔑 Definir backend explicitamente
            user.backend = 'django.contrib.auth.backends.ModelBackend'

            # 🔑 Fazer login
            auth_login(request, user)

            # 🔑 FORÇAR SALVAMENTO DA SESSÃO
            request.session.modified = True
            request.session.save()

            # 🔑 Atualizar último login
            user.ultimo_login = timezone.now()
            user.save(update_fields=['ultimo_login'])

            # 🔑 LOGS PARA DEBUG
            print(f"✅ Usuário autenticado: {request.user.is_authenticated}")
            print(f"✅ Usuário ID: {request.user.id}")
            print(f"✅ Session ID: {request.session.session_key}")

            messages.success(request, f'Bem-vindo(a), {user.nome}!')

            # ============ REDIRECIONAR ============
            from django.http import HttpResponseRedirect
            from django.urls import reverse

            # 🔑 Forçar redirecionamento para o dashboard
            if request.user.is_authenticated:
                print(f"✅ Redirecionando para dashboard")
                return HttpResponseRedirect(reverse('dashboard'))
            else:
                # 🔑 Fallback: tentar autenticar novamente
                print(f"⚠️ Usuário NÃO autenticado após login! Tentando novamente...")
                return HttpResponseRedirect(reverse('login'))

        else:
            # ============ OTP INVÁLIDO ============
            tentativas_2fa = cache.get(cache_key_2fa, 0) + 1
            cache.set(cache_key_2fa, tentativas_2fa, 300)

            tentativas_restantes = 5 - tentativas_2fa
            logger.warning(f"❌ OTP inválido para {email} - tentativa {tentativas_2fa}/5")

            if tentativas_restantes > 0:
                messages.error(request, f'Código inválido. Você tem mais {tentativas_restantes} tentativa(s).')
            else:
                messages.error(request, 'Código inválido. Muitas tentativas. Aguarde 5 minutos.')

            return render(request, 'auth/verificar_otp.html', {'email': email})

    return render(request, 'auth/verificar_otp.html', {'email': email})



def logout_user(request):
    """Logout via API"""
    if request.method != 'POST':
        return JsonResponse({'erro': 'Método não permitido'}, status=405)
    logout(request)
    return JsonResponse({'sucesso': 'Logout realizado com sucesso.'})


def forgot_password(request):
    """Recuperação de senha via API"""
    if request.method != 'POST':
        return JsonResponse({'erro': 'Método não permitido'}, status=405)

    import json
    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({'erro': 'Dados inválidos'}, status=400)

    email = data.get('email', '').strip()

    if not email:
        return JsonResponse({'erro': 'Email é obrigatório.'}, status=400)

    try:
        user = Usuario.objects.get(email=email)
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        reset_link = f"http://localhost:8002/auth/redefinir-senha/{uid}/{token}/"

        send_mail(
            'Redefinição de senha - AssistIA',
            f"Olá, {user.nome}!\n\n"
            f"Clique no link abaixo para redefinir sua senha:\n{reset_link}\n\n"
            f"Este link expira em 24 horas.\n\n"
            f"Se você não solicitou esta redefinição, ignore este email.",
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False
        )

        return JsonResponse({'sucesso': 'Email enviado com sucesso!'})
    except Usuario.DoesNotExist:
        return JsonResponse({'mensagem': 'Se o email estiver cadastrado, você receberá as instruções.'})


def reset_password(request, uidb64, token):
    """Resetar senha via API"""
    if request.method != 'POST':
        return JsonResponse({'erro': 'Método não permitido'}, status=405)

    import json
    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({'erro': 'Dados inválidos'}, status=400)

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Usuario.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
        return JsonResponse({'erro': 'Link inválido ou expirado.'}, status=400)

    if not default_token_generator.check_token(user, token):
        return JsonResponse({'erro': 'Link inválido ou expirado.'}, status=400)

    nova_senha = data.get('nova_senha', '').strip()

    if len(nova_senha) < 8:
        return JsonResponse({'erro': 'A senha deve ter no mínimo 8 caracteres.'}, status=400)

    user.set_password(nova_senha)
    user.save()

    return JsonResponse({'sucesso': 'Senha redefinida com sucesso!'})


def user_profile(request):
    """Perfil do usuário via API"""
    if not request.user.is_authenticated:
        return JsonResponse({'erro': 'Não autenticado'}, status=401)

    if request.method == 'GET':
        user = request.user
        return JsonResponse({
            'id': str(user.id),
            'nome': user.nome,
            'email': user.email,
            'perfil': user.perfil
        })

    if request.method == 'PUT':
        import json
        try:
            data = json.loads(request.body)
        except:
            return JsonResponse({'erro': 'Dados inválidos'}, status=400)

        if 'nome' in data:
            request.user.nome = data['nome'].strip()
        if 'email' in data:
            request.user.email = data['email'].strip()
        request.user.save()
        return JsonResponse({'sucesso': 'Perfil atualizado!'})

    return JsonResponse({'erro': 'Método não permitido'}, status=405)


def health_check(request):
    """Verificar status da API"""
    return JsonResponse({
        'status': 'ok',
        'mensagem': 'API AssistIA está funcionando!'
    })