import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AssistIA.settings')
django.setup()

from telas.models import TecnologiaAssistiva

# Lista de tecnologias fixas do catálogo
TECNOLOGIAS = [
    {
        'nome': 'Prancha de Comunicação com Figuras',
        'categoria': 'comunicacao',
        'descricao': 'Recurso visual para auxiliar na comunicação não-verbal, permitindo que o aluno aponte para figuras que representam suas necessidades e desejos.',
        'exemplos_uso': 'Pode ser usada em sala de aula, durante refeições, em atividades lúdicas e para expressar emoções.',
        'materiais': 'Revistas velhas, tesoura, cola, papelão, velcro, plastificadora (opcional)',
        'como_fazer': '1. Recorte figuras de revistas. 2. Organize por categorias (comida, emoções, atividades). 3. Cole em papelão. 4. Plastifique para maior durabilidade. 5. Fixe velcro para facilitar a troca de figuras.',
        'como_usar': 'O aluno aponta para a figura do que deseja comunicar. O professor pode perguntar "O que você quer?" e auxiliar na escolha.',
        'para_que_serve': 'Facilita a comunicação não-verbal, expressão de necessidades, desejos e emoções. Aumenta a autonomia do aluno.',
        'ativo': True
    },
    {
        'nome': 'Garrafa da Calma',
        'categoria': 'regulacao_sensorial',
        'descricao': 'Recurso sensorial que ajuda na regulação emocional, proporcionando um momento de calma e foco através da observação do glitter caindo.',
        'exemplos_uso': 'Utilizado em momentos de crise, ansiedade, ou para iniciar atividades que requerem concentração.',
        'materiais': 'Garrafa PET, água, glitter, corante alimentício, cola quente, purpurina, miçangas',
        'como_fazer': '1. Encha a garrafa com água. 2. Adicione glitter e corante. 3. Adicione purpurina e miçangas. 4. Feche com cola quente para vedar. 5. Agite antes de usar.',
        'como_usar': 'Agite a garrafa e peça para o aluno observar o glitter caindo lentamente. Use em momentos de agitação ou ansiedade.',
        'para_que_serve': 'Ajuda na regulação emocional, autoconhecimento, foco e atenção. Proporciona um momento de calma.',
        'ativo': True
    },
    {
        'nome': 'Kit Sensorial com Caixas',
        'categoria': 'regulacao_sensorial',
        'descricao': 'Caixas com diferentes texturas para exploração tátil e estimulação sensorial, desenvolvendo a percepção e integração sensorial.',
        'exemplos_uso': 'Utilizado para explorar diferentes texturas, desenvolver a percepção tátil e promover a integração sensorial.',
        'materiais': 'Caixa de sapato, tecidos variados (veludo, lã, algodão, cetim), botões, fitas, papelão, feltro, grãos (arroz, feijão)',
        'como_fazer': '1. Forre a caixa com tecidos. 2. Cole botões, fitas e outros materiais. 3. Crie compartimentos com diferentes texturas. 4. Identifique cada compartimento.',
        'como_usar': 'Deixe o aluno explorar as texturas livremente. Peça para identificar as diferenças entre os materiais.',
        'para_que_serve': 'Estimula o tato, a percepção sensorial, a integração sensorial e a curiosidade.',
        'ativo': True
    },
    {
        'nome': 'Teclado Adaptado com Papelão',
        'categoria': 'motor',
        'descricao': 'Teclado adaptado com teclas grandes para auxiliar na coordenação motora fina e no aprendizado da digitação.',
        'exemplos_uso': 'Utilizado para atividades de escrita, digitação, jogos educativos e comunicação.',
        'materiais': 'Papelão, teclas desenhadas, fita adesiva, tesoura, cola, impressão do teclado',
        'como_fazer': '1. Desenhe um teclado em papelão. 2. Recorte as teclas individualmente. 3. Fixe com fita adesiva em uma base. 4. Identifique cada tecla com letras/cores.',
        'como_usar': 'O aluno usa para digitar ou apontar letras. Pode ser usado em atividades de alfabetização.',
        'para_que_serve': 'Auxilia na coordenação motora fina, no aprendizado do teclado e na comunicação.',
        'ativo': True
    },
    {
        'nome': 'Rotina Visual com Caixas',
        'categoria': 'estruturacao',
        'descricao': 'Caixas organizadoras para rotina visual, ajudando o aluno a entender a sequência de atividades do dia.',
        'exemplos_uso': 'Utilizado no início do dia para apresentar a rotina, e durante o dia para marcar atividades concluídas.',
        'materiais': 'Caixas de fósforo, papel, canetinhas, cola, velcro, palitos de picolé',
        'como_fazer': '1. Desenhe as atividades em papel. 2. Recorte e cole nas caixas. 3. Organize em sequência. 4. Fixe velcro para facilitar a troca.',
        'como_usar': 'Mostre a sequência do dia. O aluno pode mover as caixas conforme as atividades são concluídas.',
        'para_que_serve': 'Dá previsibilidade, reduz a ansiedade e ajuda na organização do tempo.',
        'ativo': True
    },
    {
        'nome': 'Cartões de Comunicação',
        'categoria': 'comunicacao',
        'descricao': 'Cartões com símbolos e figuras para comunicação alternativa, permitindo que o aluno se comunique de forma simples e eficaz.',
        'exemplos_uso': 'Usado para comunicação diária, pedidos, expressão de sentimentos e necessidades.',
        'materiais': 'Papel cartão, canetinhas, tesoura, plastificador, argola',
        'como_fazer': '1. Desenhe os símbolos. 2. Recorte e cole no papel cartão. 3. Plastifique. 4. Fure e coloque uma argola.',
        'como_usar': 'O aluno mostra o cartão para se comunicar. Pode usar para pedir água, ir ao banheiro, entre outros.',
        'para_que_serve': 'Facilita a comunicação alternativa, aumentando a autonomia e a expressão.',
        'ativo': True
    },
    {
        'nome': 'Fone de Ouvido Caseiro',
        'categoria': 'regulacao_sensorial',
        'descricao': 'Fone adaptado para reduzir a sobrecarga auditiva em ambientes barulhentos, proporcionando conforto e bem-estar.',
        'exemplos_uso': 'Usado em momentos de muito barulho, para concentração ou durante crises sensoriais.',
        'materiais': 'Fone velho, espuma acústica, tecido macio, cola quente',
        'como_fazer': '1. Remova as almofadas originais. 2. Encha com espuma acústica. 3. Recubra com tecido macio. 4. Fixe com cola quente.',
        'como_usar': 'Use em momentos de sobrecarga auditiva ou para auxiliar na concentração.',
        'para_que_serve': 'Reduz a sobrecarga auditiva, promove bem-estar e auxilia na concentração.',
        'ativo': True
    },
    {
        'nome': 'História Social Ilustrada',
        'categoria': 'interacao_social',
        'descricao': 'Histórias ilustradas para ensinar habilidades sociais e comportamentos adequados em diferentes situações.',
        'exemplos_uso': 'Preparar para situações sociais, como ir ao médico, fazer um amigo, ou ir ao supermercado.',
        'materiais': 'Papel, canetinhas, grampeador, impressões de imagens',
        'como_fazer': '1. Crie uma história simples. 2. Ilustre cada passo. 3. Grampeie para formar um livrinho.',
        'como_usar': 'Leia a história antes da situação acontecer. Releia quantas vezes for necessário.',
        'para_que_serve': 'Ensina habilidades sociais, reduz ansiedade e prepara para situações novas.',
        'ativo': True
    },
    {
        'nome': 'Agenda Visual de Tarefas',
        'categoria': 'estruturacao',
        'descricao': 'Agenda visual para organizar tarefas e compromissos do dia a dia, ajudando na autonomia e planejamento.',
        'exemplos_uso': 'Organizar tarefas escolares, atividades diárias e compromissos.',
        'materiais': 'Papel, canetinhas, velcro, quadro magnético ou cartolina',
        'como_fazer': '1. Desenhe as tarefas em cartões. 2. Recorte. 3. Cole velcro. 4. Organize no quadro.',
        'como_usar': 'O aluno organiza as tarefas do dia na agenda. Conforme realiza, pode remover ou marcar.',
        'para_que_serve': 'Ajuda na organização, planejamento diário e desenvolvimento da autonomia.',
        'ativo': True
    },
]

def popular_catalogo():
    print("=" * 50)
    print("📚 POPULANDO CATÁLOGO DE TECNOLOGIAS")
    print("=" * 50)
    
    # Verificar se já existem tecnologias
    existentes = TecnologiaAssistiva.objects.count()
    if existentes > 0:
        print(f"⚠️ Já existem {existentes} tecnologias no banco.")
        resposta = input("Deseja recriar tudo? (s/N): ")
        if resposta.lower() != 's':
            print("❌ Operação cancelada!")
            return
    
    # Limpar tudo
    TecnologiaAssistiva.objects.all().delete()
    print("🗑️ Tecnologias antigas removidas!")
    
    # Criar novas
    criadas = 0
    for tech in TECNOLOGIAS:
        try:
            TecnologiaAssistiva.objects.create(**tech)
            criadas += 1
            print(f"✅ Criada: {tech['nome']}")
        except Exception as e:
            print(f"❌ Erro ao criar {tech['nome']}: {e}")
    
    print("\n" + "=" * 50)
    print(f"✅ {criadas} tecnologias criadas com sucesso!")
    print(f"📊 Total no catálogo: {TecnologiaAssistiva.objects.count()}")
    print("=" * 50)

if __name__ == "__main__":
    popular_catalogo()
