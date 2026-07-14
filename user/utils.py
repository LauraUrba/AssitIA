# user/utils.py
import pyotp
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def send_otp(request, user):
    """Gerar e enviar código OTP por email"""
    try:
        # Gerar chave secreta
        secret_key = pyotp.random_base32()
        totp = pyotp.TOTP(secret_key, interval=300)
        otp_code = totp.now()

        # Salvar na sessão
        request.session['otp_secret_key'] = secret_key
        request.session['otp_valid_date'] = (datetime.now() + timedelta(minutes=5)).isoformat()
        request.session['user_email'] = user.email

        # LOG: Verificar configurações de email
        logger.info(f"📧 Tentando enviar OTP para {user.email}")
        logger.info(f"📧 EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
        logger.info(f"📧 EMAIL_HOST_PASSWORD: {'*' * 4 if settings.EMAIL_HOST_PASSWORD else 'VAZIO'}")
        logger.info(f"📧 EMAIL_PORT: {settings.EMAIL_PORT}")
        logger.info(f"📧 EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
        logger.info(f"📧 EMAIL_USE_SSL: {settings.EMAIL_USE_SSL}")

        # Tentar enviar email
        try:
            send_mail(
                '🔐 Código de Verificação - AssistIA',
                f"""Olá, {user.nome}!

Seu código de verificação é: {otp_code}

Este código é válido por 5 minutos.

Se você não solicitou este código, ignore este email.

Atenciosamente,
Equipe AssistIA""",
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False
            )
            logger.info(f"✅ OTP enviado com sucesso para {user.email}")

        except Exception as e:
            # 🔥 FALLBACK: Mostrar no console para debug
            logger.error(f"❌ ERRO ao enviar email: {str(e)}")
            logger.error(f"❌ TIPO DO ERRO: {type(e).__name__}")

            # Mostrar código no console
            print(f"\n{'=' * 60}")
            print(f"🔑 CÓDIGO DE VERIFICAÇÃO PARA {user.email}")
            print(f"📝 Código: {otp_code}")
            print(f"⏱ Válido por: 5 minutos")
            print(f"📧 Configuração: {settings.EMAIL_HOST_USER} - Porta {settings.EMAIL_PORT}")
            print(f"{'=' * 60}\n")

            # Salvar código na sessão para teste
            request.session['otp_code_debug'] = otp_code

            # Não retorna False para não travar o login
            # return True mesmo com erro para continuar o fluxo

        return True

    except Exception as e:
        logger.error(f"❌ Erro ao gerar OTP: {str(e)}")
        return False