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
        totp = pyotp.TOTP(secret_key, interval=300)  # 5 minutos
        otp_code = totp.now()

        # Salvar na sessão
        request.session['otp_secret_key'] = secret_key
        request.session['otp_valid_date'] = (datetime.now() + timedelta(minutes=5)).isoformat()
        request.session['user_email'] = user.email

        # Tentar enviar email
        try:
            subject = '🔐 Código de Verificação - AssistIA'
            message = f"""
Olá, {user.nome}!

Seu código de verificação é: {otp_code}

Este código é válido por 5 minutos.

Se você não solicitou este código, ignore este email.

Atenciosamente,
Equipe AssistIA
"""
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False
            )
            logger.info(f"OTP enviado para {user.email}")
        except Exception as e:
            # Se falhar o email, mostrar o código no terminal (desenvolvimento)
            logger.warning(f"Erro ao enviar email: {e}")
            print(f"\n{'=' * 50}")
            print(f"CÓDIGO PARA {user.email}")
            print(f"Código: {otp_code}")
            print(f"⏱Válido por: 5 minutos")
            print(f"{'=' * 50}\n")

            # Salvar código na sessão para teste
            request.session['otp_code_debug'] = otp_code

        return True

    except Exception as e:
        logger.error(f"Erro ao gerar OTP: {str(e)}")
        return False