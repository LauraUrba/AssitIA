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
import re
import logging

logger = logging.getLogger(__name__)


# ============ VIEWS PARA TELAS HTML ============

def login_view(request):
    """Página de login do site"""
    # Removido o check de autenticação para permitir logout

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not email or not password:
            messages.error(request, 'Por favor, preencha todos os campos.')
            return render(request, 'auth/login.html')

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Bem-vindo(a), {user.nome}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Email ou senha incorretos.')
            return render(request, 'auth/login.html')

    return render(request, 'auth/login.html')


def cadastro_view(request):
    """Página de cadastro do site"""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        email = request.POST.get('email', '').strip()
        perfil = request.POST.get('perfil', '').strip()
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        if not all([nome, email, perfil, password, confirm_password]):
            messages.error(request, 'Todos os campos são obrigatórios.')
            return render(request, 'auth/cadastro.html')

        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_regex, email):
            messages.error(request, 'Email em formato inválido.')
            return render(request, 'auth/cadastro.html')

        if len(password) < 8:
            messages.error(request, 'A senha deve ter no mínimo 8 caracteres.')
            return render(request, 'auth/cadastro.html')

        if password != confirm_password:
            messages.error(request, 'As senhas não coincidem.')
            return render(request, 'auth/cadastro.html')

        if Usuario.objects.filter(email=email).exists():
            messages.error(request, 'Este email já está cadastrado.')
            return render(request, 'auth/cadastro.html')

        try:
            usuario = Usuario.objects.create_user(
                email=email,
                nome=nome,
                perfil=perfil,
                password=password
            )
            messages.success(request, 'Conta criada com sucesso! Faça login.')
            return redirect('login')
        except Exception as e:
            logger.error(f"Erro ao criar usuário: {str(e)}")
            messages.error(request, 'Erro ao criar conta. Tente novamente.')
            return render(request, 'auth/cadastro.html')

    return render(request, 'auth/cadastro.html')


def logout_view(request):
    """Logout do usuário"""
    logout(request)
    messages.info(request, 'Você saiu da sua conta.')
    return redirect('login')


# user/views.py - Adicionar tratamento de erro

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


# ============ VIEWS PARA API (SEM DECORATORS) ============

# user/views.py - Adicionar GET nas views da API

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


def verificar_otp_view(request):
    """Página de verificação OTP"""
    if 'user_email' not in request.session:
        messages.error(request, 'Sessão expirada. Faça login novamente.')
        return redirect('login')

    # Mostrar código debug no terminal (desenvolvimento)
    if 'otp_code_debug' in request.session:
        print(f"\n CÓDIGO DEBUG: {request.session['otp_code_debug']}")

    if request.method == 'POST':
        otp = request.POST.get('otp', '').strip()
        email = request.session.get('user_email')

        if not otp or len(otp) != 6:
            messages.error(request, 'Código inválido. Digite os 6 dígitos.')
            return render(request, 'auth/verificar_otp.html')

        try:
            user = Usuario.objects.get(email=email)

            # Verificar se é código debug (desenvolvimento)
            debug_code = request.session.get('otp_code_debug')
            if debug_code and otp == debug_code:
                login(request, user)
                messages.success(request, f'Bem-vindo(a), {user.nome}!')
                request.session.pop('user_email', None)
                request.session.pop('otp_secret_key', None)
                request.session.pop('otp_valid_date', None)
                request.session.pop('otp_code_debug', None)
                return redirect('dashboard')

            # Verificar OTP normal
            otp_secret_key = request.session.get('otp_secret_key')
            otp_valid_until = request.session.get('otp_valid_date')

            if not otp_secret_key or not otp_valid_until:
                messages.error(request, 'Sessão inválida. Faça login novamente.')
                return redirect('login')

            import pyotp
            from datetime import datetime

            valid_until = datetime.fromisoformat(otp_valid_until)
            if datetime.now() > valid_until:
                messages.error(request, 'Código expirado. Solicite um novo login.')
                return redirect('login')

            totp = pyotp.TOTP(otp_secret_key, interval=300)
            if totp.verify(otp):
                login(request, user)
                messages.success(request, f'Bem-vindo(a), {user.nome}!')
                request.session.pop('user_email', None)
                request.session.pop('otp_secret_key', None)
                request.session.pop('otp_valid_date', None)
                request.session.pop('otp_code_debug', None)
                return redirect('dashboard')
            else:
                messages.error(request, 'Código inválido. Tente novamente.')

        except Usuario.DoesNotExist:
            messages.error(request, 'Usuário não encontrado.')
            return redirect('login')

    return render(request, 'auth/verificar_otp.html')

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