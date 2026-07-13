# telas/middleware.py
import json
import re
from django.utils import timezone
from django.core.cache import cache
from .security_logger import log_seguranca


class SecurityMonitoringMiddleware:
    """Middleware para monitoramento de segurança"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Coletar informações
        ip = self.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        # Detectar ataques de força bruta
        self.detect_brute_force(request, ip)

        # Detectar SQL Injection
        if self.detect_sql_injection(request):
            log_seguranca.log_ataque(
                ip=ip,
                user_agent=user_agent,
                tipo_ataque='SQL Injection',
                detalhe=f'URL: {request.path} - Dados: {request.GET.dict()}'
            )

        # Detectar XSS
        if self.detect_xss(request):
            log_seguranca.log_ataque(
                ip=ip,
                user_agent=user_agent,
                tipo_ataque='XSS',
                detalhe=f'URL: {request.path} - Dados: {request.GET.dict()}'
            )

        response = self.get_response(request)

        # Log de acessos suspeitos - CORRIGIDO
        if response.status_code in [403, 404, 500]:
            # Determinar o tipo de evento
            if response.status_code == 403:
                tipo_evento = 'acesso_negado'
                nivel = 'warning'
            elif response.status_code == 404:
                tipo_evento = 'pagina_nao_encontrada'
                nivel = 'info'
            else:  # 500
                tipo_evento = 'erro_servidor'
                nivel = 'error'

            # Log com os parâmetros corretos
            log_seguranca.log_evento(
                usuario=request.user if request.user.is_authenticated else None,
                acao=f'Status {response.status_code} - {request.path}',
                ip=ip,
                user_agent=user_agent,
                nivel=nivel,
                tipo=tipo_evento,
                detalhe=f'Status {response.status_code} - {request.path}'
            )

        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')

    def detect_brute_force(self, request, ip):
        """Detectar ataques de força bruta"""
        if request.path.startswith('/auth/login/') and request.method == 'POST':
            cache_key = f'bruteforce_{ip}'
            tentativas = cache.get(cache_key, 0) + 1
            cache.set(cache_key, tentativas, 300)  # 5 minutos

            if tentativas >= 10:
                log_seguranca.log_ataque(
                    ip=ip,
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    tipo_ataque='Brute Force',
                    detalhe=f'{tentativas} tentativas de login em 5 minutos'
                )

    def detect_sql_injection(self, request):
        """Detectar tentativas de SQL Injection"""
        sql_patterns = [
            r'\bSELECT\b.*\bFROM\b',
            r'\bINSERT\b.*\bINTO\b',
            r'\bDELETE\b.*\bFROM\b',
            r'\bDROP\b.*\bTABLE\b',
            r'\bUNION\b.*\bSELECT\b',
            r'\bOR\b.*\b=\b.*\b=\b',
            r"'\s+OR\s+'1'='1",
        ]
        data = str(request.GET.dict()) + str(request.POST.dict())
        for pattern in sql_patterns:
            if re.search(pattern, data, re.IGNORECASE):
                return True
        return False

    def detect_xss(self, request):
        """Detectar tentativas de XSS"""
        xss_patterns = [
            r'<script.*?>.*?</script>',
            r'javascript:',
            r'onerror=',
            r'onload=',
            r'onclick=',
            r'onmouseover=',
        ]
        data = str(request.GET.dict()) + str(request.POST.dict())
        for pattern in xss_patterns:
            if re.search(pattern, data, re.IGNORECASE):
                return True
        return False