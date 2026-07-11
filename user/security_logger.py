import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def log_tentativa_login(email, username, sucesso, ip, detalhe=""):
    """Registrar tentativa de login"""
    level = logging.INFO if sucesso else logging.WARNING
    logger.log(level, f"LOGIN - Email: {email}, Usuario: {username}, Sucesso: {sucesso}, IP: {ip}, Detalhe: {detalhe}")

def log_tentativa_2fa(username, sucesso, ip, detalhe=""):
    """Registrar tentativa de 2FA"""
    level = logging.INFO if sucesso else logging.WARNING
    logger.log(level, f"2FA - Usuario: {username}, Sucesso: {sucesso}, IP: {ip}, Detalhe: {detalhe}")

def log_tentativa_cadastro(email, username, sucesso, ip, detalhe=""):
    """Registrar tentativa de cadastro"""
    level = logging.INFO if sucesso else logging.WARNING
    logger.log(level, f"CADASTRO - Email: {email}, Usuario: {username}, Sucesso: {sucesso}, IP: {ip}, Detalhe: {detalhe}")

def log_recuperacao_senha(email, sucesso, ip, detalhe=""):
    """Registrar tentativa de recuperação de senha"""
    level = logging.INFO if sucesso else logging.WARNING
    logger.log(level, f"RECUPERACAO_SENHA - Email: {email}, Sucesso: {sucesso}, IP: {ip}, Detalhe: {detalhe}")

def log_ataque_suspeito(ip, tipo, detalhe=""):
    """Registrar possível ataque"""
    logger.warning(f"ATAQUE_SUSPEITO - IP: {ip}, Tipo: {tipo}, Detalhe: {detalhe}")

def log_honeypot(ip, campo, detalhe=""):
    """Registrar acesso ao honeypot"""
    logger.warning(f"HONEYPOT - IP: {ip}, Campo: {campo}, Detalhe: {detalhe}")
