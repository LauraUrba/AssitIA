# telas/security_automation.py
import subprocess
import os
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
from .models import LogSeguranca
from .security_logger import log_seguranca


class SecurityAutomation:
    """Automação de respostas a ameaças"""

    @staticmethod
    def bloquear_ip(ip, duracao_minutos=30):
        """Bloquear IP automaticamente"""
        cache_key = f'blocked_ip_{ip}'
        cache.set(cache_key, True, duracao_minutos * 60)

        # Tentar bloquear no firewall (se disponível)
        try:
            subprocess.run([
                'sudo', 'ufw', 'deny', 'from', ip, 'to', 'any'
            ], timeout=5)
        except:
            pass

        log_seguranca.log_evento(
            tipo='ataque',
            usuario=None,
            ip=ip,
            nivel='critical',
            detalhe=f'IP bloqueado automaticamente por {duracao_minutos} minutos'
        )

        return True

    @staticmethod
    def desbloquear_ip(ip):
        """Desbloquear IP"""
        cache_key = f'blocked_ip_{ip}'
        cache.delete(cache_key)

        try:
            subprocess.run([
                'sudo', 'ufw', 'delete', 'deny', 'from', ip, 'to', 'any'
            ], timeout=5)
        except:
            pass

        return True

    @staticmethod
    def verificar_ip_bloqueado(ip):
        """Verificar se IP está bloqueado"""
        cache_key = f'blocked_ip_{ip}'
        return cache.get(cache_key, False)

    @staticmethod
    def analisar_logs_suspeitos():
        """Analisar logs em busca de padrões suspeitos"""
        # Última hora
        hora_atras = timezone.now() - timedelta(hours=1)

        # Buscar tentativas de login falhas
        falhas = LogSeguranca.objects.filter(
            tipo='falha_login',
            criado_em__gte=hora_atras
        ).values('ip').annotate(count=models.Count('id'))

        # IPs com mais de 5 falhas em 1 hora
        for item in falhas:
            if item['count'] >= 5:
                SecurityAutomation.bloquear_ip(item['ip'], duracao_minutos=60)
                log_seguranca.log_ataque(
                    ip=item['ip'],
                    user_agent=None,
                    tipo_ataque='Automação - Múltiplas falhas',
                    detalhe=f'{item["count"]} falhas de login em 1 hora - IP bloqueado'
                )

        # Buscar ataques detectados
        ataques = LogSeguranca.objects.filter(
            tipo='ataque',
            criado_em__gte=hora_atras
        ).values('ip').distinct()

        for item in ataques:
            if item['ip']:
                SecurityAutomation.bloquear_ip(item['ip'], duracao_minutos=120)

    @staticmethod
    def gerar_relatorio_seguranca():
        """Gerar relatório de segurança"""
        hoje = timezone.now().date()
        inicio_dia = timezone.make_aware(timezone.datetime.combine(hoje, timezone.datetime.min.time()))

        dados = {
            'total_logs': LogSeguranca.objects.filter(criado_em__gte=inicio_dia).count(),
            'falhas_login': LogSeguranca.objects.filter(tipo='falha_login', criado_em__gte=inicio_dia).count(),
            'ataques': LogSeguranca.objects.filter(tipo='ataque', criado_em__gte=inicio_dia).count(),
            'honeypots': LogSeguranca.objects.filter(tipo='honeypot', criado_em__gte=inicio_dia).count(),
            'ips_bloqueados': cache.get('blocked_ips_list', []),
        }

        return dados


security_automation = SecurityAutomation()