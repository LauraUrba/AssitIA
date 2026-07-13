import os
import django

# 🔥 CORRIGIR: O nome do módulo é 'assistIA.settings' (minúsculo)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'assistIA.settings')
django.setup()

from telas.models import TecnologiaAssistiva

# Lista de tecnologias fixas do catálogo
TECNOLOGIAS = [
    # ========== COMUNICAÇÃO (5) ==========
    {
        'nome': 'Prancha de Comunicação com Figuras',
        'categoria': 'comunicacao',
        'descricao': 'Recurso visual para auxiliar na comunicação não-verbal, permitindo que o aluno aponte para figuras que representam suas necessidades e desejos.',
        'exemplos_uso': 'Pode ser usada em sala de aula, durante refeições, em atividades lúdicas e para expressar emoções.',
        'materiais': 'Revistas velhas, tesoura, cola, papelão, velcro, plastificadora (opcional)',
        'como_fazer': '1. Recorte figuras de revistas. 2. Organize por categorias. 3. Cole em papelão. 4. Plastifique. 5. Fixe velcro.',
        'como_usar': 'O aluno aponta para a figura do que deseja comunicar.',
        'para_que_serve': 'Facilita a comunicação não-verbal e expressão de necessidades.',
        'criada_por_ia': False,
        'ativo': True
    },
    {
        'nome': 'Cartões de Comunicação',
        'categoria': 'comunicacao',
        'descricao': 'Cartões com símbolos e figuras para comunicação alternativa, permitindo que o aluno se comunique de forma simples e eficaz.',
        'exemplos_uso': 'Usado para comunicação diária, pedidos, expressão de sentimentos e necessidades.',
        'materiais': 'Papel cartão, canetinhas, tesoura, plastificador, argola',
        'como_fazer': '1. Desenhe os símbolos. 2. Recorte e cole no papel cartão. 3. Plastifique. 4. Fure e coloque uma argola.',
        'como_usar': 'O aluno mostra o cartão para se comunicar.',
        'para_que_serve': 'Facilita a comunicação alternativa e autonomia.',
        'criada_por_ia': False,
        'ativo': True
    },
    {
        'nome': 'AAC - Livro de Comunicação Personalizado',
        'categoria': 'comunicacao',
        'descricao': 'Livro de comunicação com símbolos e fotos personalizados do cotidiano do aluno.',
        'exemplos_uso': 'Usado em casa, na escola, e em diferentes situações do dia a dia.',
        'materiais': 'Álbum de fotos, figuras personalizadas, velcro, cartões, plastificador',
        'como_fazer': '1. Tire fotos de objetos/atividades. 2. Imprima e plastifique. 3. Organize em um álbum. 4. Use velcro.',
        'como_usar': 'O aluno folheia o livro e aponta para a figura desejada.',
        'para_que_serve': 'Aumenta a comunicação funcional e a participação social.',
        'criada_por_ia': False,
        'ativo': True
    },
    {
        'nome': 'Tabuleiro de Comunicação com Símbolos',
        'categoria': 'comunicacao',
        'descricao': 'Tabuleiro com símbolos e imagens organizados por categorias para facilitar a comunicação.',
        'exemplos_uso': 'Usado em sala de aula, durante refeições e em atividades terapêuticas.',
        'materiais': 'Tabuleiro de madeira ou papelão, figuras impressas, velcro, plastificador',
        'como_fazer': '1. Crie um tabuleiro com divisórias. 2. Imprima e plastifique as figuras. 3. Organize por categorias.',
        'como_usar': 'O aluno aponta para as figuras no tabuleiro para se comunicar.',
        'para_que_serve': 'Facilita a comunicação não-verbal e expressão de desejos.',
        'criada_por_ia': False,
        'ativo': True
    },
    {
        'nome': 'Prancha de Comunicação com Símbolos PECS',
        'categoria': 'comunicacao',
        'descricao': 'Sistema de comunicação por troca de figuras (PECS) que permite ao aluno se comunicar entregando figuras.',
        'exemplos_uso': 'Usado para comunicação diária, pedidos, expressão de sentimentos.',
        'materiais': 'Figuras impressas, cartões, velcro, pasta organizadora, plastificador',
        'como_fazer': '1. Selecione figuras. 2. Plastifique. 3. Organize em uma pasta com velcro.',
        'como_usar': 'O aluno entrega a figura para o professor ou aponta na prancha.',
        'para_que_serve': 'Desenvolve a comunicação funcional e reduz frustrações.',
        'criada_por_ia': False,
        'ativo': True
    },

    # ========== REGULAÇÃO SENSORIAL (4) ==========
    {
        'nome': 'Garrafa da Calma',
        'categoria': 'regulacao_sensorial',
        'descricao': 'Recurso sensorial que ajuda na regulação emocional, proporcionando calma e foco.',
        'exemplos_uso': 'Usado em momentos de crise, ansiedade ou para iniciar atividades.',
        'materiais': 'Garrafa PET, água, glitter, corante, cola quente, purpurina',
        'como_fazer': '1. Encha com água. 2. Adicione glitter e corante. 3. Feche com cola quente.',
        'como_usar': 'Agite e observe o glitter caindo lentamente.',
        'para_que_serve': 'Ajuda na regulação emocional e autoconhecimento.',
        'criada_por_ia': False,
        'ativo': True
    },
    {
        'nome': 'Kit Sensorial com Caixas',
        'categoria': 'regulacao_sensorial',
        'descricao': 'Caixas com diferentes texturas para exploração tátil e estimulação sensorial.',
        'exemplos_uso': 'Explorar diferentes texturas e desenvolver percepção tátil.',
        'materiais': 'Caixa de sapato, tecidos variados, botões, fitas, grãos',
        'como_fazer': '1. Forre a caixa com tecidos. 2. Cole botões e fitas. 3. Crie compartimentos.',
        'como_usar': 'Deixe o aluno explorar as texturas livremente.',
        'para_que_serve': 'Estimula o tato e a percepção sensorial.',
        'criada_por_ia': False,
        'ativo': True
    },
    {
        'nome': 'Fone de Ouvido Caseiro',
        'categoria': 'regulacao_sensorial',
        'descricao': 'Fone adaptado para reduzir a sobrecarga auditiva em ambientes barulhentos.',
        'exemplos_uso': 'Usado em momentos de muito barulho ou para concentração.',
        'materiais': 'Fone velho, espuma acústica, tecido macio, cola quente',
        'como_fazer': '1. Remova as almofadas. 2. Encha com espuma. 3. Recubra com tecido.',
        'como_usar': 'Use em momentos de sobrecarga auditiva.',
        'para_que_serve': 'Reduz a sobrecarga auditiva e promove bem-estar.',
        'criada_por_ia': False,
        'ativo': True
    },
    {
        'nome': 'Tapete Sensorial',
        'categoria': 'regulacao_sensorial',
        'descricao': 'Tapete com diferentes texturas para estimulação sensorial dos pés e mãos.',
        'exemplos_uso': 'Usado para regulação sensorial e integração tátil.',
        'materiais': 'Tapete EVA, tecidos variados, botões, feltro, cola quente',
        'como_fazer': '1. Corte o tapete em seções. 2. Cole diferentes texturas em cada seção. 3. Deixe secar.',
        'como_usar': 'O aluno caminha ou toca as diferentes texturas.',
        'para_que_serve': 'Estimula a integração sensorial e a regulação tátil.',
        'criada_por_ia': False,
        'ativo': True
    },

    # ========== MOTOR (4) ==========
    {
        'nome': 'Teclado Adaptado com Papelão',
        'categoria': 'motor',
        'descricao': 'Teclado adaptado com teclas grandes para auxiliar na coordenação motora fina.',
        'exemplos_uso': 'Atividades de escrita, digitação e jogos educativos.',
        'materiais': 'Papelão, teclas desenhadas, fita adesiva, tesoura, cola',
        'como_fazer': '1. Desenhe um teclado. 2. Recorte as teclas. 3. Fixe com fita.',
        'como_usar': 'O aluno usa para digitar ou apontar letras.',
        'para_que_serve': 'Auxilia na coordenação motora fina e aprendizado.',
        'criada_por_ia': False,
        'ativo': True
    },
    {
        'nome': 'Prancha de Atividades Motoras',
        'categoria': 'motor',
        'descricao': 'Prancha com atividades para desenvolver a coordenação motora fina e grossa.',
        'exemplos_uso': 'Usado em terapia ocupacional, educação física e em sala de aula.',
        'materiais': 'Papelão, clipes, botões, cordas, tesoura, cola',
        'como_fazer': '1. Crie uma prancha com diferentes atividades. 2. Inclua abrir clipes, amarrar cordas, encaixar botões.',
        'como_usar': 'O aluno realiza as atividades na prancha.',
        'para_que_serve': 'Desenvolve a coordenação motora fina e a destreza manual.',
        'criada_por_ia': False,
        'ativo': True
    },
    {
        'nome': 'Kit de Atividades com Massinha',
        'categoria': 'motor',
        'descricao': 'Kit com massinha de modelar e ferramentas para estimular a coordenação motora fina.',
        'exemplos_uso': 'Usado em atividades lúdicas, terapia ocupacional e em sala de aula.',
        'materiais': 'Massinha caseira (farinha, sal, água), rolinhos, cortadores, palitos',
        'como_fazer': '1. Prepare a massinha. 2. Separe ferramentas. 3. Armazene em potes.',
        'como_usar': 'O aluno modela formas, letras e números.',
        'para_que_serve': 'Desenvolve a coordenação motora fina e a criatividade.',
        'criada_por_ia': False,
        'ativo': True
    },
    {
        'nome': 'Painel de Encaixes',
        'categoria': 'motor',
        'descricao': 'Painel com diferentes encaixes para desenvolver a coordenação motora e o raciocínio lógico.',
        'exemplos_uso': 'Usado em atividades de coordenação motora e resolução de problemas.',
        'materiais': 'Papelão, formas geométricas, tesoura, cola, tinta',
        'como_fazer': '1. Desenhe formas no papelão. 2. Recorte os encaixes. 3. Pinte para identificar.',
        'como_usar': 'O aluno encaixa as formas no lugar correto.',
        'para_que_serve': 'Desenvolve a coordenação motora e o raciocínio lógico.',
        'criada_por_ia': False,
        'ativo': True
    },

    # ========== COGNITIVO (4) ==========
    {
        'nome': 'Jogo da Memória Adaptado',
        'categoria': 'cognitivo',
        'descricao': 'Jogo da memória com figuras grandes e coloridas para estimular a memória visual e a atenção.',
        'exemplos_uso': 'Usado em atividades de estimulação cognitiva e terapia ocupacional.',
        'materiais': 'Papelão, figuras impressas, tesoura, cola, plastificador',
        'como_fazer': '1. Imprima pares de figuras. 2. Plastifique. 3. Recorte em cartões.',
        'como_usar': 'Espalhe os cartões virados para baixo. Encontre os pares.',
        'para_que_serve': 'Estimula a memória visual, atenção e concentração.',
        'criada_por_ia': False,
        'ativo': True
    },
    {
        'nome': 'Atividades de Raciocínio Lógico',
        'categoria': 'cognitivo',
        'descricao': 'Conjunto de atividades impressas para estimular o raciocínio lógico e resolução de problemas.',
        'exemplos_uso': 'Usado em sala de aula e em atendimentos terapêuticos.',
        'materiais': 'Papel, canetinhas, lápis, figuras para recortar e colar',
        'como_fazer': '1. Crie sequências lógicas. 2. Imprima labirintos e desafios.',
        'como_usar': 'O aluno realiza as atividades com a mediação do professor.',
        'para_que_serve': 'Desenvolve o raciocínio lógico e o pensamento crítico.',
        'criada_por_ia': False,
        'ativo': True
    },
    {
        'nome': 'Painel de Rotina Diária',
        'categoria': 'cognitivo',
        'descricao': 'Painel visual com a rotina diária do aluno, ajudando na organização e planejamento.',
        'exemplos_uso': 'Usado no início do dia, durante transições e para organizar tarefas.',
        'materiais': 'Painel de cortiça, cartões, velcro, canetinhas, papel',
        'como_fazer': '1. Desenhe as atividades em cartões. 2. Plastifique. 3. Organize no painel.',
        'como_usar': 'O aluno organiza os cartões no painel conforme a sequência do dia.',
        'para_que_serve': 'Desenvolve a organização, planejamento e autonomia.',
        'criada_por_ia': False,
        'ativo': True
    },
    {
        'nome': 'Agenda Visual de Tarefas',
        'categoria': 'cognitivo',
        'descricao': 'Agenda visual para organizar tarefas e compromissos do dia a dia.',
        'exemplos_uso': 'Organizar tarefas escolares e atividades diárias.',
        'materiais': 'Papel, canetinhas, velcro, quadro magnético',
        'como_fazer': '1. Desenhe as tarefas em cartões. 2. Recorte. 3. Cole velcro.',
        'como_usar': 'O aluno organiza as tarefas do dia na agenda.',
        'para_que_serve': 'Ajuda na organização e planejamento diário.',
        'criada_por_ia': False,
        'ativo': True
    },

    # ========== INTERAÇÃO SOCIAL (4) ==========
    {
        'nome': 'História Social Ilustrada',
        'categoria': 'interacao_social',
        'descricao': 'Histórias ilustradas para ensinar habilidades sociais e comportamentos adequados.',
        'exemplos_uso': 'Preparar para situações sociais, como ir ao médico ou fazer um amigo.',
        'materiais': 'Papel, canetinhas, grampeador, impressões',
        'como_fazer': '1. Crie uma história simples. 2. Ilustre cada passo. 3. Grampeie.',
        'como_usar': 'Leia a história antes da situação acontecer.',
        'para_que_serve': 'Ensina habilidades sociais e reduz ansiedade.',
        'criada_por_ia': False,
        'ativo': True
    },
    {
        'nome': 'Cartões de Habilidades Sociais',
        'categoria': 'interacao_social',
        'descricao': 'Cartões com situações sociais e dicas de como agir em cada uma.',
        'exemplos_uso': 'Usado para ensinar como iniciar uma conversa, fazer amigos, lidar com conflitos.',
        'materiais': 'Papel cartão, canetinhas, figuras, plastificador',
        'como_fazer': '1. Desenhe situações sociais em cartões. 2. Escreva dicas de como agir. 3. Plastifique.',
        'como_usar': 'Leia a situação e discuta as possíveis respostas.',
        'para_que_serve': 'Ensina habilidades sociais, empatia e resolução de conflitos.',
        'criada_por_ia': False,
        'ativo': True
    },
    {
        'nome': 'Jogo de Role-Play Social',
        'categoria': 'interacao_social',
        'descricao': 'Jogo de faz de conta com situações sociais para praticar habilidades de interação.',
        'exemplos_uso': 'Usado em terapia e em sala de aula para praticar situações sociais.',
        'materiais': 'Fantoches, roupas, objetos para encenação, cartões com situações',
        'como_fazer': '1. Crie cartões com situações sociais. 2. Prepare materiais para encenação.',
        'como_usar': 'Os alunos encenam as situações sociais.',
        'para_que_serve': 'Desenvolve habilidades sociais, empatia e comunicação.',
        'criada_por_ia': False,
        'ativo': True
    },
    {
        'nome': 'Painel de Emoções',
        'categoria': 'interacao_social',
        'descricao': 'Painel com diferentes expressões faciais para ajudar o aluno a identificar e expressar emoções.',
        'exemplos_uso': 'Usado para ensinar reconhecimento de emoções e expressão de sentimentos.',
        'materiais': 'Papelão, figuras de expressões faciais, velcro, canetinhas',
        'como_fazer': '1. Desenhe diferentes expressões faciais. 2. Recorte. 3. Fixe no painel.',
        'como_usar': 'O aluno aponta para a expressão que corresponde ao que está sentindo.',
        'para_que_serve': 'Ensina o reconhecimento e expressão de emoções.',
        'criada_por_ia': False,
        'ativo': True
    },

    # ========== ESTRUTURAÇÃO (4) ==========
    {
        'nome': 'Rotina Visual com Caixas',
        'categoria': 'estruturacao',
        'descricao': 'Caixas organizadoras para rotina visual, ajudando o aluno a entender a sequência de atividades do dia.',
        'exemplos_uso': 'Utilizado no início do dia para apresentar a rotina, e durante o dia para marcar atividades concluídas.',
        'materiais': 'Caixas de fósforo, papel, canetinhas, cola, velcro, palitos de picolé',
        'como_fazer': '1. Desenhe as atividades em papel. 2. Recorte e cole nas caixas. 3. Organize em sequência. 4. Fixe velcro para facilitar a troca.',
        'como_usar': 'Mostre a sequência do dia. O aluno pode mover as caixas conforme as atividades são concluídas.',
        'para_que_serve': 'Dá previsibilidade, reduz a ansiedade e ajuda na organização do tempo.',
        'criada_por_ia': False,
        'ativo': True
    },
    {
        'nome': 'Agenda Visual de Tarefas (Estrutura)',
        'categoria': 'estruturacao',
        'descricao': 'Agenda visual para organizar tarefas e compromissos do dia a dia, ajudando na autonomia e planejamento.',
        'exemplos_uso': 'Organizar tarefas escolares, atividades diárias e compromissos.',
        'materiais': 'Papel, canetinhas, velcro, quadro magnético ou cartolina',
        'como_fazer': '1. Desenhe as tarefas em cartões. 2. Recorte. 3. Cole velcro. 4. Organize no quadro.',
        'como_usar': 'O aluno organiza as tarefas do dia na agenda. Conforme realiza, pode remover ou marcar.',
        'para_que_serve': 'Ajuda na organização, planejamento diário e desenvolvimento da autonomia.',
        'criada_por_ia': False,
        'ativo': True
    },
    {
        'nome': 'Painel de Rotina com Cards',
        'categoria': 'estruturacao',
        'descricao': 'Painel com cards magnéticos ou com velcro para organizar a rotina diária do aluno.',
        'exemplos_uso': 'Usado para visualizar a sequência de atividades do dia, transições entre tarefas.',
        'materiais': 'Painel magnético ou de cortiça, cards de atividades, ímãs ou velcro, canetinhas',
        'como_fazer': '1. Crie cards com as atividades do dia. 2. Plastifique para maior durabilidade. 3. Organize no painel em ordem cronológica.',
        'como_usar': 'O aluno visualiza a rotina do dia e vai removendo ou marcando as atividades concluídas.',
        'para_que_serve': 'Dá previsibilidade, reduz ansiedade e ajuda na transição entre atividades.',
        'criada_por_ia': False,
        'ativo': True
    },
    {
        'nome': 'Organizador de Tarefas por Cores',
        'categoria': 'estruturacao',
        'descricao': 'Sistema de organização de tarefas utilizando cores para categorizar diferentes tipos de atividades.',
        'exemplos_uso': 'Organizar tarefas escolares por disciplina, ou atividades por nível de dificuldade.',
        'materiais': 'Papel colorido, caixas ou pastas coloridas, etiquetas, fita adesiva',
        'como_fazer': '1. Separe cores para cada categoria de tarefa (ex: azul = matemática, verde = leitura). 2. Crie caixas ou pastas para cada cor. 3. Organize as tarefas nas respectivas pastas.',
        'como_usar': 'O aluno identifica a cor da tarefa e sabe onde encontrar ou guardar cada atividade.',
        'para_que_serve': 'Facilita a organização, categorização e autonomia do aluno na execução de tarefas.',
        'criada_por_ia': False,
        'ativo': True
    },
]

def popular_catalogo():
    print("=" * 50)
    print("📚 POPULANDO CATÁLOGO DE TECNOLOGIAS")
    print("=" * 50)
    
    existentes = TecnologiaAssistiva.objects.count()
    if existentes > 0:
        print(f"⚠️ Já existem {existentes} tecnologias no banco.")
        resposta = input("Deseja recriar tudo? (s/N): ")
        if resposta.lower() != 's':
            print("❌ Operação cancelada!")
            return
    
    TecnologiaAssistiva.objects.all().delete()
    print("🗑️ Tecnologias antigas removidas!")
    
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
