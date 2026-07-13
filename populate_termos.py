import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assistIA.settings')
django.setup()

from telas.models import TermosUso

def popular_termos():
    print("=" * 60)
    print("📜 POPULANDO TERMOS DE USO E POLÍTICAS")
    print("=" * 60)
    
    # Verificar se já existem
    existentes = TermosUso.objects.count()
    if existentes > 0:
        print(f"⚠️ Já existem {existentes} termos no banco.")
        resposta = input("Deseja recriar tudo? (s/N): ")
        if resposta.lower() != 's':
            print("❌ Operação cancelada!")
            return
    
    # Limpar existentes
    TermosUso.objects.all().delete()
    print("🗑️ Termos antigos removidos!")
    
    # ========== TERMOS DE USO ==========
    TermosUso.objects.create(
        versao='1.0',
        titulo='Termos de Uso - AssistIA',
        tipo='termos_uso',
        ativo=True,
        conteudo="""
TERMOS DE USO - AssistIA

1. ACEITAÇÃO DOS TERMOS

Ao criar uma conta no AssistIA, você declara que leu, compreendeu e aceita integralmente estes Termos de Uso. Se você não concordar com qualquer parte destes termos, não utilize o sistema.

2. DESCRIÇÃO DO SERVIÇO

O AssistIA é um sistema de recomendação de tecnologias assistivas para alunos com Transtorno do Espectro Autista (TEA), desenvolvido para auxiliar professores, coordenadores e especialistas da educação.

O sistema utiliza inteligência artificial para analisar o perfil do aluno e sugerir recursos personalizados, sempre com foco na inclusão e no desenvolvimento educacional.

3. CADASTRO E RESPONSABILIDADES DO USUÁRIO

3.1. O usuário é responsável por fornecer informações verdadeiras, precisas e atualizadas durante o cadastro.

3.2. O usuário é responsável por manter a confidencialidade de sua senha e dados de acesso.

3.3. O usuário deve notificar imediatamente o AssistIA sobre qualquer uso não autorizado de sua conta.

3.4. O usuário assume total responsabilidade por todas as atividades realizadas em sua conta.

4. PRIVACIDADE E PROTEÇÃO DE DADOS

4.1. O AssistIA coleta apenas os dados estritamente necessários para o funcionamento do sistema.

4.2. Todos os dados pessoais são tratados em conformidade com a Lei Geral de Proteção de Dados (LGPD - Lei nº 13.709/2018).

4.3. Os dados dos alunos são coletados exclusivamente para fins educacionais.

4.4. O usuário pode solicitar a qualquer momento a exclusão de seus dados.

5. USO PERMITIDO E PROIBIDO

5.1. O sistema deve ser utilizado exclusivamente para fins educacionais e de suporte a alunos com TEA.

5.2. É proibido utilizar o sistema para qualquer finalidade ilegal, discriminatória ou prejudicial.

5.3. É proibido compartilhar informações de outros usuários ou alunos sem autorização.

6. PROPRIEDADE INTELECTUAL

6.1. Todo o conteúdo, design e funcionalidades do AssistIA são protegidos por direitos autorais.

6.2. O usuário não tem permissão para copiar, modificar ou distribuir o sistema.

7. LIMITAÇÃO DE RESPONSABILIDADE

7.1. O AssistIA fornece recomendações baseadas em inteligência artificial, que devem ser avaliadas criticamente pelo profissional.

7.2. O AssistIA não se responsabiliza por decisões tomadas com base nas recomendações geradas.

8. ALTERAÇÕES NOS TERMOS

8.1. O AssistIA pode atualizar estes termos periodicamente.

8.2. Os usuários serão notificados sobre mudanças significativas.

9. CONTATO

Email: contato@assistia.com

Data da última atualização: 13 de Julho de 2026
"""
    )
    print("✅ Termos de Uso criados")

    # ========== POLÍTICA DE PRIVACIDADE ==========
    TermosUso.objects.create(
        versao='1.0',
        titulo='Política de Privacidade - AssistIA',
        tipo='politica_privacidade',
        ativo=True,
        conteudo="""
POLÍTICA DE PRIVACIDADE - AssistIA

1. INTRODUÇÃO

Esta Política de Privacidade descreve como o AssistIA coleta, utiliza, armazena e protege suas informações pessoais, em conformidade com a Lei Geral de Proteção de Dados (LGPD - Lei nº 13.709/2018).

2. QUAIS DADOS COLETAMOS

2.1. Dados do Professor, Coordenador ou Especialista:
- Nome completo
- Endereço de email
- Perfil profissional
- Endereço IP e dados de acesso
- Data de criação da conta
- Histórico de login

2.2. Dados dos Alunos:
- Nome completo
- Data de nascimento
- Nível de suporte (DSM-5)
- Turma e escola
- Perfil TEA
- Desafios e observações pedagógicas
- Histórico de recomendações e PEIs

2.3. Dados de Uso do Sistema:
- Recomendações geradas
- Feedbacks e avaliações
- Interações com o sistema

3. FINALIDADE DO TRATAMENTO DOS DADOS

3.1. Gerar recomendações personalizadas de tecnologias assistivas.

3.2. Auxiliar professores na elaboração de Planos Educacionais Individualizados (PEIs).

3.3. Aprimorar o sistema com base no feedback dos usuários.

3.4. Manter comunicação sobre atualizações e melhorias.

3.5. Cumprir obrigações legais.

4. BASE LEGAL PARA O TRATAMENTO

4.1. Consentimento do titular.

4.2. Legítimo interesse do controlador.

4.3. Cumprimento de obrigação legal.

4.4. Execução de contrato.

5. COMPARTILHAMENTO DE DADOS

5.1. O AssistIA NÃO compartilha dados pessoais com terceiros, exceto:
- Quando exigido por lei ou ordem judicial.
- Com o consentimento explícito do usuário.

5.2. Os dados dos alunos são acessíveis apenas aos profissionais autorizados.

6. DIREITOS DO TITULAR (LGPD)

6.1. Confirmar a existência de tratamento de dados.

6.2. Acessar seus dados pessoais.

6.3. Corrigir dados incompletos ou desatualizados.

6.4. Solicitar a eliminação de dados.

6.5. Solicitar a portabilidade dos dados.

6.6. Revogar o consentimento a qualquer momento.

Para exercer seus direitos, entre em contato: privacidade@assistia.com

7. SEGURANÇA DOS DADOS

7.1. Utilizamos criptografia (Argon2) para proteção de senhas.

7.2. Implementamos autenticação em dois fatores (2FA).

7.3. Dados armazenados em servidores seguros.

7.4. Realizamos backups regulares.

8. RETENÇÃO DE DADOS

8.1. Os dados são mantidos pelo tempo necessário para cumprir as finalidades descritas.

8.2. Após solicitação de exclusão, os dados serão eliminados em até 30 dias.

9. DADOS DE CRIANÇAS E ADOLESCENTES

9.1. O AssistIA coleta dados de menores exclusivamente para fins educacionais.

9.2. O cadastro de menores é realizado por professores ou responsáveis legais.

9.3. Os responsáveis têm acesso completo aos dados dos alunos.

10. CONTATO DO ENCARREGADO

Para dúvidas sobre privacidade:
Email: privacidade@assistia.com

Data da última atualização: 13 de Julho de 2026
"""
    )
    print("✅ Política de Privacidade criada")

    # ========== CONSENTIMENTO PARA MENORES ==========
    TermosUso.objects.create(
        versao='1.0',
        titulo='Consentimento para Cadastro de Menores',
        tipo='consentimento_menor',
        ativo=True,
        conteudo="""
CONSENTIMENTO PARA CADASTRO DE MENORES

1. DECLARAÇÃO DE RESPONSABILIDADE

Ao cadastrar um aluno menor de idade, declaro que:

1.1. Sou o responsável legal pelo aluno (pai, mãe ou tutor legal).

1.2. Autorizo o cadastro e o tratamento dos dados do aluno no AssistIA.

1.3. Estou ciente de que os dados serão utilizados exclusivamente para fins educacionais.

2. DIREITOS DO MENOR

2.1. O menor tem direito à privacidade e proteção de seus dados.

2.2. O menor tem direito de ser ouvido sobre decisões que o afetam.

2.3. Os dados do menor serão tratados com o mesmo nível de segurança.

3. DADOS COLETADOS DO MENOR

3.1. Informações básicas (nome, data de nascimento, turma).

3.2. Perfil TEA (comunicação, sensorial, motor, cognitivo).

3.3. Recomendações e PEIs gerados pelo sistema.

4. ACESSO E CONTROLE

4.1. O professor tem acesso limitado aos dados necessários.

4.2. O responsável pode solicitar a exclusão dos dados a qualquer momento.

4.3. O responsável pode acessar e corrigir os dados cadastrados.

5. USO DOS DADOS

5.1. Os dados serão usados apenas para gerar recomendações educacionais.

5.2. Os dados não serão compartilhados com terceiros sem consentimento explícito.

6. COMPROMISSO DO RESPONSÁVEL

Comprometo-me a:

6.1. Acompanhar o uso do sistema pelo menor.

6.2. Garantir que o sistema está sendo utilizado de forma adequada.

6.3. Informar o AssistIA sobre qualquer mudança na situação do menor.

7. CANCELAMENTO DO CONSENTIMENTO

O responsável pode revogar este consentimento a qualquer momento, solicitando a exclusão dos dados do menor.

Data da última atualização: 13 de Julho de 2026
"""
    )
    print("✅ Consentimento para Menores criado")

    print("\n" + "=" * 60)
    print(f"✅ {TermosUso.objects.count()} termos criados com sucesso!")
    print("=" * 60)

if __name__ == "__main__":
    popular_termos()
