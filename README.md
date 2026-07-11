# 📚 AssistIA - Documentação Completa do Projeto

## Sistema de Recomendação de Tecnologias Assistivas para TEA

---

## 📋 Índice

1. [Sobre o Projeto](#sobre-o-projeto)
2. [Tecnologias Utilizadas](#tecnologias-utilizadas)
3. [Estrutura do Projeto](#estrutura-do-projeto)
4. [Configuração Inicial](#configuração-inicial)
5. [Banco de Dados PostgreSQL](#banco-de-dados-postgresql)
6. [Modelos do Sistema](#modelos-do-sistema)
7. [Autenticação e Segurança](#autenticação-e-segurança)
8. [Telas e Funcionalidades](#telas-e-funcionalidades)
9. [Integração com API de IA](#integração-com-api-de-ia)
10. [Comandos Úteis](#comandos-úteis)
11. [Erros e Soluções](#erros-e-soluções)
12. [Melhorias Implementadas](#melhorias-implementadas)
13. [Próximos Passos](#próximos-passos)
14. [Licença](#licença)

---

## Sobre o Projeto

O **AssistIA** é um sistema web desenvolvido para auxiliar profissionais da educação (professores, coordenadores e especialistas) a recomendar tecnologias assistivas para alunos com Transtorno do Espectro Autista (TEA). O sistema utiliza inteligência artificial para analisar o perfil do aluno e sugerir recursos personalizados.

### 🎯 Público-Alvo

- **Professores** - Gerenciam alunos, geram recomendações e PEIs
- **Coordenadores** - Supervisionam professores e acompanham resultados
- **Especialistas** - Validam recomendações e ajustam o sistema

### 📌 Status Atual

- ✅ Telas para professores completamente funcionais
- ⏳ Telas para coordenadores (em desenvolvimento)
- ⏳ Telas para especialistas (planejadas)

---

## Tecnologias Utilizadas

### Backend
- **Python 3.12.3** - Linguagem principal
- **Django 6.0** - Framework web
- **Django REST Framework 3.17.1** - API
- **PostgreSQL 16** - Banco de dados
- **Argon2** - Criptografia de senhas (mais seguro)
- **JWT** - Autenticação via tokens
- **PyOTP 2.10.0** - Autenticação de dois fatores

### Frontend
- **Bootstrap 5** - Framework CSS responsivo
- **HTML5 / CSS3** - Estrutura e estilização
- **JavaScript / jQuery** - Interatividade
- **Font Awesome 6** - Ícones
- **SweetAlert2** - Alertas e modais

### IA e APIs
- **FastAPI** - API de recomendação (deploy no Render)
- **TinyLlama-1.1B** - Modelo de IA para recomendações
- **Requests 2.34.2** - Comunicação entre APIs

### Segurança (Implementada)
- **Argon2** - Hash de senhas
- **JWT** - Tokens de autenticação
- **2FA (OTP)** - Autenticação de dois fatores
- **Rate Limiting** - Proteção contra brute force
- **CSRF Protection** - Proteção contra ataques CSRF
- **Headers de Segurança** - XSS, Clickjacking, HSTS
- **Bloqueio por Tentativas** - Bloqueio após múltiplas falhas
- **Logs de Segurança** - Registro de tentativas de acesso

---

## Estrutura do Projeto

```
AssistIA_site/
├── assistIA/                          # Configurações do projeto
│   ├── __init__.py
│   ├── settings.py                    # Configurações principais
│   ├── urls.py                        # URLs principais
│   ├── asgi.py                        # ASGI config
│   └── wsgi.py                        # WSGI config
│
├── user/                              # App de autenticação
│   ├── migrations/
│   ├── templates/
│   │   └── auth/                      # Templates de autenticação
│   │       ├── base.html
│   │       ├── login.html
│   │       ├── cadastro.html
│   │       ├── esqueci_senha.html
│   │       ├── redefinir_senha.html
│   │       └── verificar_otp.html
│   ├── models.py                      # Modelo Usuario
│   ├── views.py                       # Views de autenticação
│   ├── urls.py                        # URLs de autenticação
│   ├── serializers.py                 # Serializers
│   ├── utils.py                       # Utilitários (OTP)
│   └── security_logger.py             # Logs de segurança
│
├── telas/                             # App principal
│   ├── migrations/
│   ├── templates/                     # Templates do sistema
│   │   ├── telas/
│   │   │   ├── base.html              # Base das telas internas
│   │   │   └── dashboard.html         # Dashboard do professor
│   │   ├── estudantes/                # Gestão de alunos
│   │   │   ├── lista.html
│   │   │   ├── form.html
│   │   │   └── detalhe.html
│   │   ├── pei/                       # Planos Educacionais
│   │   │   ├── lista.html
│   │   │   ├── gerar.html
│   │   │   ├── detalhe.html
│   │   │   └── form.html
│   │   ├── perfil/                    # Perfil do usuário
│   │   │   └── perfil.html
│   │   ├── recomendacoes/             # Recomendações
│   │   │   ├── lista.html
│   │   │   ├── gerar.html
│   │   │   └── detalhe.html
│   │   └── tecnologias/               # Catálogo de TAs
│   │       └── catalogo.html
│   ├── models.py                      # Modelos do sistema
│   ├── views.py                       # Views do sistema
│   └── urls.py                        # URLs do sistema
│
├── static/                            # Arquivos estáticos
│   └── css/
│       └── style.css                  # CSS global
│
├── staticfiles/                       # Coletados pelo Django
├── logs/                              # Logs do sistema
│   ├── django.log                     # Logs gerais
│   └── security.log                   # Logs de segurança
├── .env                               # Variáveis de ambiente
├── manage.py                          # Gerenciador do Django
└── requirements.txt                   # Dependências
```

---

## Configuração Inicial

### 1. Criar Ambiente Virtual

```bash
# Criar ambiente virtual
python -m venv .venv

# Ativar ambiente virtual
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows
```

### 2. Instalar Dependências

```bash
# Instalar Django e dependências principais
pip install django==6.0
pip install django-environ==0.14.0
pip install psycopg2-binary==2.9.12
pip install djangorestframework==3.17.1
pip install djangorestframework-simplejwt==5.5.1
pip install django-cors-headers==4.9.0
pip install python-dotenv==1.2.2
pip install pyotp==2.10.0
pip install requests==2.34.2
pip install argon2-cffi==25.1.0
pip install django-filter==25.2
pip install drf-yasg==1.21.15
pip install django-allauth==65.18.0
pip install dj-rest-auth==7.2.0

# Salvar dependências
pip freeze > requirements.txt
```

### 3. Criar Projeto e Apps

```bash
# Criar projeto
django-admin startproject assistIA .
cd assistIA

# Criar apps
python manage.py startapp user
python manage.py startapp telas
```

### 4. Configurar `.env`

```bash
cat > .env << 'EOF'
# Django Settings
DJANGO_SECRET_KEY='django-insecure-2-rz8s9oCgs81jf9kGJuveTcIw0vFYIsbwn2UBtt6D1egFcnzS5DQP8wyU7k4b4d_tA'
DEBUG=True

# Hosts
ALLOWED_HOSTS=localhost,127.0.0.1,.onrender.com

# Database - PostgreSQL
DB_NAME=assitia_db
DB_USER=postgres
DB_PASSWORD=Cherry0601@
DB_HOST=localhost
DB_PORT=5432

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000,http://localhost:8002

# Email (desenvolvimento)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EOF
```

---

## Banco de Dados PostgreSQL

### 1. Instalar PostgreSQL

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# Verificar status
sudo systemctl status postgresql
```

### 2. Criar Banco e Usuário

```bash
# Acessar PostgreSQL
sudo -u postgres psql

# Dentro do psql:
CREATE DATABASE assitia_db;
GRANT ALL PRIVILEGES ON DATABASE assitia_db TO postgres;
\c assitia_db;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
\q
```

### 3. Configurar Django para PostgreSQL

```python
# assistIA/settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'assitia_db'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'password'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
}
```

### 4. Migrar Banco

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## Modelos do Sistema

### Usuario (`user/models.py`)

```python
class Usuario(AbstractBaseUser, PermissionsMixin):
    PERFIL_CHOICES = [
        ('professor', 'Professor'),
        ('coordenador', 'Coordenador'),
        ('especialista', 'Especialista'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=150)
    email = models.EmailField(max_length=150, unique=True)
    perfil = models.CharField(max_length=20, choices=PERFIL_CHOICES)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    # ... campos de segurança e autenticação
```

### TecnologiaAssistiva (`telas/models.py`)

```python
class TecnologiaAssistiva(models.Model):
    CATEGORIA_CHOICES = [
        ('comunicacao', 'Comunicação'),
        ('regulacao_sensorial', 'Regulação Sensorial'),
        ('motor', 'Motor'),
        ('cognitivo', 'Cognitivo'),
        ('interacao_social', 'Interação Social'),
        ('estruturacao', 'Estruturação'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=200)
    categoria = models.CharField(max_length=50, choices=CATEGORIA_CHOICES)
    descricao = models.TextField(blank=True, null=True)
    materiais = models.TextField(blank=True, null=True)
    como_fazer = models.TextField(blank=True, null=True)
    como_usar = models.TextField(blank=True, null=True)
    para_que_serve = models.TextField(blank=True, null=True)
    # ... outros campos
```

### Estudante (`telas/models.py`)

```python
class Estudante(models.Model):
    NIVEL_SUPORTE_CHOICES = [
        (1, 'Nível 1 - Suporte Leve'),
        (2, 'Nível 2 - Suporte Moderado'),
        (3, 'Nível 3 - Suporte Intensivo'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    professor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.RESTRICT)
    nome = models.CharField(max_length=150)
    nivel_suporte = models.IntegerField(choices=NIVEL_SUPORTE_CHOICES)
    turma = models.CharField(max_length=50, blank=True, null=True)
    ativo = models.BooleanField(default=True)
    # ... outros campos
```

---

## Autenticação e Segurança

### 1. Argon2 - Criptografia de Senhas

```python
# settings.py
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]
```

### 2. 2FA com OTP

```python
# user/utils.py
def send_otp(request, user):
    secret_key = pyotp.random_base32()
    totp = pyotp.TOTP(secret_key, interval=300)
    otp_code = totp.now()
    
    # Salvar na sessão
    request.session['otp_secret_key'] = secret_key
    request.session['otp_valid_date'] = (datetime.now() + timedelta(minutes=5)).isoformat()
    
    # Enviar por email (console em desenvolvimento)
    print(f"🔐 Código OTP: {otp_code}")
    return True
```

### 3. JWT Configuration

```python
# settings.py
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}
```

### 4. Headers de Segurança

```python
# settings.py
SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
```

### 5. Rate Limiting e Bloqueio

```python
# user/views.py
def login_view(request):
    # Verificar tentativas de login
    if 'tentativas_login' not in request.session:
        request.session['tentativas_login'] = 0
    
    if request.session['tentativas_login'] >= 5:
        messages.error(request, 'Muitas tentativas. Tente novamente em 5 minutos.')
        return render(request, 'auth/login.html')
    
    # Login bem-sucedido
    if usuario is not None:
        request.session['tentativas_login'] = 0
        # ...
    else:
        request.session['tentativas_login'] += 1
```

---

## Telas e Funcionalidades

### Telas de Autenticação (`user/auth/`)

| Tela | URL | Descrição |
|------|-----|-----------|
| Login | `/auth/login/` | Tela de login com 2FA |
| Cadastro | `/auth/cadastro/` | Cadastro de novos usuários |
| Esqueci Senha | `/auth/esqueci-senha/` | Recuperação de senha |
| Redefinir Senha | `/auth/redefinir-senha/<uid>/<token>/` | Redefinição de senha |
| Verificar OTP | `/auth/verificar-otp/` | Verificação de 2FA |

### Telas do Sistema (`telas/templates/`)

| Tela | URL | Descrição |
|------|-----|-----------|
| Dashboard | `/telas/` | Visão geral do professor |
| Lista de Alunos | `/telas/estudantes/` | Gerenciamento de alunos |
| Cadastro de Aluno | `/telas/estudantes/novo/` | Criar novo aluno |
| Detalhe do Aluno | `/telas/estudantes/<id>/` | Perfil completo do aluno |
| Catálogo de TAs | `/telas/tecnologias/catalogo/` | Catálogo de tecnologias |
| Lista de Recomendações | `/telas/recomendacoes/` | Recomendações geradas |
| Gerar Recomendação | `/telas/recomendacoes/gerar/<id>/` | Recomendação com IA |
| Detalhe Recomendação | `/telas/recomendacoes/<id>/` | Detalhes da recomendação |
| Lista de PEIs | `/telas/pei/` | Planos Educacionais |
| Gerar PEI | `/telas/pei/gerar/<id>/` | Criar PEI |
| Detalhe PEI | `/telas/pei/<id>/` | Visualizar PEI |
| Perfil do Usuário | `/telas/perfil/` | Editar perfil |

### Funcionalidades Principais

1. **CRUD de Alunos** - Criar, ler, editar e deletar alunos
2. **Perfil TEA** - Cadastro de perfil completo do aluno
3. **Catálogo de TAs** - Visualização de todas as tecnologias disponíveis
4. **Recomendações com IA** - Geração de recomendações personalizadas
5. **Feedback de Recomendações** - Aceitar, testar ou rejeitar recomendações
6. **PEIs** - Criação e edição de Planos Educacionais Individualizados
7. **PDF de PEIs** - Geração de PDF para impressão
8. **2FA** - Autenticação de dois fatores por OTP
9. **Perfil do Usuário** - Edição de dados e alteração de senha

---

## Integração com API de IA

### API FastAPI no Render

A API de recomendação está disponível em:
- **URL**: `https://api-assitia.onrender.com`
- **Documentação**: `https://api-assitia.onrender.com/docs`

### Endpoints

```http
POST /analisar-aluno-tea/
```

**Request Body:**
```json
{
    "descricao_professor": "Aluno com dificuldade de comunicação...",
    "idade_aluno": 8,
    "nivel_suporte": "2",
    "interesses_especificos": "Música, desenhos",
    "sensibilidades_sensoriais": "Sons altos, luzes fortes",
    "comunicacao": "Não Verbal",
    "motor": "Coordenação Fina"
}
```

### Integração no Django

```python
# telas/views.py
def gerar_recomendacao(request, estudante_id):
    payload = {
        "descricao_professor": descricao,
        "idade_aluno": idade,
        "nivel_suporte": str(estudante.nivel_suporte),
        # ... mais campos
    }
    
    response = requests.post(
        'https://api-assitia.onrender.com/analisar-aluno-tea/',
        json=payload,
        timeout=30
    )
    
    if response.status_code == 200:
        resultado = response.json()
        # Processar e salvar recomendações
```

---

## Comandos Úteis

### Gerenciamento do Projeto

```bash
# Rodar servidor de desenvolvimento
python manage.py runserver
python manage.py runserver 8002

# Criar migrações
python manage.py makemigrations
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Coletar arquivos estáticos
python manage.py collectstatic --noinput

# Verificar configurações
python manage.py check

# Shell interativo
python manage.py shell

# Mostrar URLs
python manage.py show_urls
```

### Gerenciamento do Banco de Dados

```bash
# Acessar PostgreSQL
sudo -u postgres psql
psql -U postgres -d assitia_db

# Comandos no psql
\l              # Listar bancos
\c assitia_db  # Conectar ao banco
\dt            # Listar tabelas
\q             # Sair

# Backup e Restore
pg_dump -U postgres assitia_db > backup.sql
psql -U postgres assitia_db < backup.sql
```

### Ambiente Virtual

```bash
# Criar
python -m venv .venv

# Ativar
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Desativar
deactivate

# Dependências
pip freeze > requirements.txt
pip install -r requirements.txt
```

### Ferramentas de Desenvolvimento

```bash
# Limpar cache Python
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete

# Matar processos na porta 8000
sudo fuser -k 8000/tcp
sudo fuser -k 8001/tcp

# Verificar processos
ps aux | grep python
lsof -i :8000
```

---

## Erros e Soluções

### 1. Erro: IA Enviando Recomendações para o Catálogo
A IA estava criando tecnologias assistivas diretamente no catálogo do sistema. Isso acontecia porque, ao gerar recomendações, o código salvava as tecnologias 
recomendadas pela IA como objetos TecnologiaAssistiva no banco de dados, fazendo com que aparecessem no catálogo junto com as tecnologias fixas.

#### O Que Estava Acontecendo:
- O professor clicava em "Gerar Recomendação com IA"
- A IA analisava o perfil do aluno e retornava sugestões
- O sistema criava novas tecnologias no banco de dados com os dados da IA
- Essas tecnologias apareciam no catálogo como se fossem tecnologias fixas
- O catálogo ficava cheio de tecnologias genéricas como "Baseado no relato:", "Idade:", "Como fazer:", etc.

#### Por Que Isso Era um Problema:
- ❌ Catálogo poluído com tecnologias geradas pela IA

- ❌ Tecnologias sem informações completas (materiais, como fazer, etc.)

- ❌ Nomes genéricos que não ajudavam os professores

- ❌ Dificuldade em distinguir tecnologias fixas das recomendadas

#### Resumo da Correção
| Problema | Antes | Depois |
|----------|-------|--------|
| **Criação de Tecnologias** | IA criava tecnologias diretamente no catálogo | IA apenas recomenda tecnologias existentes |
| **Catálogo** | Catálogo poluído com nomes genéricos ("Baseado no relato:", "Idade:", etc.) | Catálogo limpo com apenas tecnologias fixas |
| **Informações das Tecnologias** | Tecnologias sem informações completas (materiais, como fazer, etc.) | Tecnologias com dados completos e estruturados |
| **Diferenciação** | Dificuldade de distinguir tecnologias fixas das recomendadas | Campo `criada_por_ia` para diferenciar claramente |
| **Filtragem** | Catálogo mostrava todas as tecnologias (fixas + IA) | Catálogo filtra apenas tecnologias fixas (`criada_por_ia=False`) |

### 2. Erro: `ModuleNotFoundError: No module named 'environ'`

**Solução:**
```bash
pip install django-environ python-dotenv
```

### 3. Erro: `password authentication failed for user "postgres"`

**Solução:**
```bash
# Verificar senha no .env
# Ou redefinir a senha
sudo -u postgres psql
ALTER USER postgres WITH PASSWORD 'nova_senha';
\q
```

### 4. Erro: `TemplateDoesNotExist: telas/estudantes/form.html`

**Solução:**
```bash
# Verificar estrutura
ls -la telas/templates/estudantes/

# Criar pasta se não existir
mkdir -p telas/templates/estudantes
```

### 5. Erro: `Network is unreachable` (email)

**Solução:**
```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

### 6. Erro: `salvar_perfil_tea() got an unexpected keyword argument 'id'`

**Solução:**
```python
# telas/urls.py
path('estudantes/<uuid:estudante_id>/salvar-perfil/', views.salvar_perfil_tea, name='salvar_perfil_tea'),

# telas/views.py
def salvar_perfil_tea(request, estudante_id):
    estudante = get_object_or_404(Estudante, id=estudante_id, professor=request.user)
```

### 7. Erro: `RestrictedError` ao excluir tecnologias

**Solução:**
```python
# Primeiro excluir referências
RecomendacaoTA.objects.all().delete()
Recomendacao.objects.all().delete()
TecnologiaAssistiva.objects.all().delete()
```

### 8. Erro: `Tag start is not closed` no template

**Solução:**
```html
<!-- Errado -->
{% if request.POST.perfil == 'professor' %}

<!-- Correto -->
{% if request.POST.perfil == "professor" %}
```

### 9. Erro: Porta 8000 em uso

**Solução:**
```bash
# Verificar quem está usando
sudo lsof -i :8000

# Matar processo
sudo kill -9 PID

# Ou usar outra porta
python manage.py runserver 8002
```

### 10. Erro: `FieldError: Cannot resolve keyword 'criada_por_ia'` erro 1 esta mais explicado (é o mesmo erro)

**Solução:**
```python
# Adicionar campo no modelo
criada_por_ia = models.BooleanField(default=False)

# Criar migração
python manage.py makemigrations
python manage.py migrate
```

### 11. Erro: `ModuleNotFoundError: No module named 'AssistIA'`

**Solução:**
```bash
# Corrigir referências no manage.py e settings.py
# Mudar de 'AssistIA.settings' para 'assistIA.settings'
sed -i "s/AssistIA.settings/assistIA.settings/g" manage.py
sed -i "s/AssistIA.urls/assistIA.urls/g" assistIA/settings.py
```

### 12. Erro: CSS não carregando (404)

**Solução:**
```bash
# Criar pasta e arquivo CSS
mkdir -p static/css
cat > static/css/style.css << 'EOF'
/* CSS content */
EOF

# Coletar estáticos
python manage.py collectstatic --noinput
```

### 13. Erro: 404 ao excluir recomendação

**Solução:**
```bash
# Verificar se a URL está correta no template
# Mudar de /app/ para /telas/
fetch(`/telas/recomendacoes/${id}/excluir/`, {
    method: 'POST',
    headers: {
        'X-CSRFToken': '{{ csrf_token }}',
    },
})
```

---

## Melhorias Implementadas

### 🚀 Melhorias Realizadas

1. **Arquitetura**
   - ✅ Estrutura de pastas reorganizada
   - ✅ Apps separados por responsabilidade (user, telas)
   - ✅ URLs organizadas e semânticas

2. **Segurança**
   - ✅ Argon2 para criptografia de senhas
   - ✅ 2FA com OTP
   - ✅ JWT para autenticação
   - ✅ Headers de segurança
   - ✅ Rate limiting
   - ✅ CSRF protection
   - ✅ Bloqueio por tentativas de login

3. **Interface**
   - ✅ Design responsivo com Bootstrap 5
   - ✅ CSS global centralizado
   - ✅ Ícones Font Awesome
   - ✅ Alertas e modais com SweetAlert2
   - ✅ Estrela para indicar IA

4. **Funcionalidades**
   - ✅ CRUD completo de alunos
   - ✅ Perfil TEA com modal
   - ✅ Catálogo de tecnologias com filtros
   - ✅ Recomendações com IA
   - ✅ Feedback de recomendações
   - ✅ PEIs com versionamento
   - ✅ Geração de PDF
   - ✅ Lista de recomendações com filtros e busca

5. **Banco de Dados**
   - ✅ PostgreSQL com UUID
   - ✅ Relacionamentos entre tabelas
   - ✅ Índices para performance

6. **Desenvolvimento**
   - ✅ Ambiente virtual
   - ✅ Dependências versionadas
   - ✅ Variáveis de ambiente
   - ✅ Logs de sistema

### 🔧 Correções de Bugs

1. ✅ Corrigido erro de referência `AssistIA` → `assistIA`
2. ✅ Corrigido erro de `criada_por_ia` no modelo
3. ✅ Corrigido erro de `salvar_perfil_tea()`
4. ✅ Corrigido erro de CSS não carregando
5. ✅ Corrigido erro de exclusão de recomendações
6. ✅ Corrigido erro de RESTRICT vs CASCADE no models
7. ✅ Corrigido erro de template `Tag start is not closed`
8. ✅ Corrigido erro de email `Network is unreachable`
9. ✅ Corrigido erro de portas em uso

---

## Próximos Passos

### 🔐 Segurança Avançada (Próximas Implementações)

1. **Hardening de Senhas**
   - ✅ Histórico de senhas (evitar reutilização)
   - ✅ Notificação de senhas fracas
   - ✅ Verificação contra vazamentos (Have I Been Pwned API)

2. **Honeypot**
   - ✅ Campos ocultos em formulários para detectar bots
   - ✅ Tempo de preenchimento para detectar automação
   - ✅ Bloqueio automático de IPs suspeitos
   - ✅ Logs de tentativas de honeypot

3. **Logs de Monitoramento**
   - ✅ Logs estruturados em JSON
   - ✅ Monitoramento de tentativas de login (sucesso/falha)
   - ✅ Alertas de múltiplas falhas
   - ✅ Dashboard de segurança
   - ✅ Integração com ferramentas de SIEM

4. **Automação de Segurança**
   - ✅ Backup automatizado do banco de dados
   - ✅ Rotação automática de chaves
   - ✅ Atualização automática de dependências
   - ✅ Scan automático de vulnerabilidades
   - ✅ Testes de penetração automatizados


### 📊 Telas para Coordenadores

1. **Dashboard do Coordenador**
   - Visão geral de todos os professores
   - Estatísticas de recomendações
   - Gráficos de desempenho

2. **Acompanhamento de Professores**
   - Lista de professores
   - Atividades recentes
   - Métricas de uso

### 🧠 Telas para Especialistas

1. **Validação de Recomendações**
   - Revisão de recomendações geradas pela IA
   - Ajuste de parâmetros
   - Feedback do sistema

2. **Configurações do Sistema**
   - Ajuste do modelo de IA
   - Configuração de parâmetros
   - Gerenciamento de usuários

### 🚀 Funcionalidades Adicionais (possívelmente serão colocadas)

1. **Notificações**
   - Email de novas recomendações
   - Alertas de segurança
   - Lembretes de PEIs

2. **Exportação**
   - Relatórios em PDF
   - Exportação de dados em CSV
   - Impressão de recomendações

3. **Performance**
   - Cache de consultas
   - Paginação otimizada
   - Lazy loading

---

## Licença

Este projeto está sob a licença MIT.

---

**Última atualização:** 24 de Junho de 2026

**Desenvolvedora:** Laura

**Links:**
- **API de IA**: https://api-assitia.onrender.com
- **Documentação**: https://api-assitia.onrender.com/docs

---

** Obrigada por utilizar o AssistIA!**