# telas/security_logger.py
import logging
from django.utils import timezone
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)


class SecurityLogger:
    """Logger de segurança para auditoria"""

    def log_evento(self, usuario=None, acao=None, ip=None, user_agent=None,
                   nivel='info', tipo=None, detalhe=None, **kwargs):
        """
        Registra um evento de segurança no sistema.

        Args:
            usuario: Usuário que realizou a ação
            acao: Descrição da ação
            ip: IP do usuário
            user_agent: User Agent do navegador
            nivel: info, warning, error, critical
            tipo: Tipo do evento (acesso_negado, erro_servidor, etc)
            detalhe: Detalhes adicionais
        """
        log_data = {
            'timestamp': timezone.now().isoformat(),
            'usuario': usuario.username if usuario and usuario.is_authenticated else 'Anonymous',
            'usuario_id': usuario.id if usuario and usuario.is_authenticated else None,
            'acao': acao,
            'ip': ip,
            'user_agent': user_agent,
            'nivel': nivel,
            'tipo': tipo,
            'detalhe': detalhe,
        }

        # Log no console ou arquivo
        log_message = f"[{log_data['timestamp']}] {log_data['nivel'].upper()}: {log_data['acao']} - Usuário: {log_data['usuario']} - IP: {log_data['ip']}"
        if detalhe:
            log_message += f" - Detalhe: {detalhe}"

        # Log usando o nível apropriado
        if nivel == 'error':
            logger.error(log_message)
        elif nivel == 'warning':
            logger.warning(log_message)
        elif nivel == 'critical':
            logger.critical(log_message)
        else:
            logger.info(log_message)

        # Aqui você pode salvar no banco de dados também
        # from .models import LogSeguranca
        # LogSeguranca.objects.create(**log_data)

        return log_data

    def log_ataque(self, ip=None, user_agent=None, tipo_ataque=None, detalhe=None):
        """Registra um ataque detectado"""
        return self.log_evento(
            usuario=None,
            acao=f"Ataque detectado: {tipo_ataque}",
            ip=ip,
            user_agent=user_agent,
            nivel='critical',
            tipo=tipo_ataque,
            detalhe=detalhe
        )


# Instância global para uso
log_seguranca = SecurityLogger()