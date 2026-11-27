"""Gera os currículos em PDF (português e inglês) do site.

Uso, na pasta do repositório:

    python -m pip install reportlab      (só na primeira vez)
    python cv/gerar_curriculos.py

Saída: Curriculo_Diogo_Araujo_Nunes.pdf e Resume_Diogo_Araujo_Nunes.pdf na raiz
do repositório, que são os arquivos do botão "Baixar currículo" do site.

O layout reproduz o dos PDFs anteriores: A4, Inter (pasta cv/fontes, licença
OFL), faixa azul no topo, seções com título espaçado e um fio embaixo, datas
alinhadas à direita. Para mudar um texto, edite os dicionários PT e EN, no fim
deste arquivo. O script avisa se o currículo passar de uma página.
"""
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.lib.fonts import addMapping
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (HRFlowable, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)

PASTA = Path(__file__).resolve().parent
RAIZ = PASTA.parent

# Fontes: Inter 4.0 (rsms/inter), só com os caracteres latinos. <b> = SemiBold.
for peso in ('Regular', 'Medium', 'SemiBold', 'Bold'):
    pdfmetrics.registerFont(TTFont(f'Inter-{peso}', str(PASTA / 'fontes' / f'Inter-{peso}.ttf')))
addMapping('Inter-Regular', 0, 0, 'Inter-Regular')
addMapping('Inter-Regular', 1, 0, 'Inter-SemiBold')
addMapping('Inter-Regular', 0, 1, 'Inter-Regular')
addMapping('Inter-Regular', 1, 1, 'Inter-SemiBold')

# Cores
AZUL = HexColor('#1E40AF')         # faixa do topo, cargo, títulos das seções, marcadores
TINTA = HexColor('#111827')        # nome e títulos dos itens
TEXTO = HexColor('#374151')        # texto corrido e links
CINZA = HexColor('#6B7280')        # datas, instituições, contato
CINZA_CLARO = '#9CA3AF'            # separador "|" do contato
FIO = HexColor('#D1D5DB')          # fio embaixo do título das seções

LARGURA = A4[0] - 2 * 17 * mm - 12  # área útil: margens de 17 mm + 6 pt de respiro do quadro em cada lado

# Espaçamentos (em pontos). Os valores do layout anterior estão no comentário:
# com eles, o script gera os PDFs antigos idênticos. Alguns ficaram um pouco
# menores para os 8 prêmios caberem em uma página.
MEDIDAS = {
    'antes_da_secao': 8,       # antes: 11
    'fim_do_item': 4,          # antes: 6
    'fio_antes': 3,
    'fio_depois': 6,
    'premios_entre': 2,        # antes: 2.5
    'habilidades_entre': 2,
    'margem_inferior': 9 * mm,  # antes: 12 mm
}

E = ParagraphStyle
ESTILOS = {
    'nome': E('nome', fontName='Inter-Bold', fontSize=23, leading=27, textColor=TINTA),
    'cargo': E('cargo', fontName='Inter-Medium', fontSize=10.5, leading=14, textColor=AZUL),
    'contato': E('contato', fontName='Inter-Regular', fontSize=8.6, leading=12, textColor=CINZA),
    'secao': E('secao', fontName='Inter-SemiBold', fontSize=9, leading=11, textColor=AZUL),
    'corpo': E('corpo', fontName='Inter-Regular', fontSize=9.3, leading=13.6, textColor=TEXTO, alignment=TA_LEFT),
    'titulo': E('titulo', fontName='Inter-SemiBold', fontSize=9.8, leading=13, textColor=TINTA),
    'data': E('data', fontName='Inter-Regular', fontSize=8.6, leading=13, textColor=CINZA, alignment=TA_RIGHT),
    'sub': E('sub', fontName='Inter-Regular', fontSize=8.8, leading=12, textColor=CINZA),
    'item': E('item', fontName='Inter-Regular', fontSize=9.3, leading=13.6, textColor=TEXTO,
              leftIndent=11, bulletIndent=1, bulletFontName='Inter-Bold', bulletFontSize=8, bulletColor=AZUL),
    'rotulo': E('rotulo', fontName='Inter-SemiBold', fontSize=9, leading=13, textColor=TINTA),
}


def link(texto, url):
    """Texto clicável, na cor do texto corrido (mais escuro que o cinza ao redor)."""
    return f'<a href="{url}"><font color="#374151">{texto}</font></a>'


def juntar(partes, separador):
    """Junta itens de uma linha com um separador e dois espaços de cada lado."""
    return separador.join(link(t, u) if u else t for t, u in partes)


SEP_CONTATO = f'&nbsp; <font color="{CINZA_CLARO}">|</font>&nbsp; '
SEP_PONTO = '&nbsp; ·&nbsp; '


def titulo_secao(nome, m):
    # "Resumo" vira "R E S U M O"; entre palavras ficam três espaços.
    # O nome é texto simples: o "&" só é escapado depois de espaçar as letras.
    espacado = '&nbsp;&nbsp; '.join(' '.join(escape(letra) for letra in palavra)
                                    for palavra in nome.upper().split())
    return [Spacer(1, m['antes_da_secao']),
            Paragraph(espacado, ESTILOS['secao']),
            HRFlowable(width='100%', thickness=0.6, lineCap='round', color=FIO,
                       spaceBefore=m['fio_antes'], spaceAfter=m['fio_depois'])]


def tabela(linhas, larguras, entre):
    t = Table(linhas, colWidths=larguras)
    t.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), entre),
    ]))
    return t


def item(dados, m):
    """Um item de Experiência, Projetos ou Formação: título e data, linha de
    detalhes em cinza e, se houver, os tópicos com marcador."""
    blocos = [tabela([[Paragraph(dados['titulo'], ESTILOS['titulo']), Paragraph(dados['data'], ESTILOS['data'])]],
                     [LARGURA - 42 * mm, 42 * mm], 0),
              Paragraph(juntar(dados['sub'], SEP_PONTO), ESTILOS['sub'])]
    if dados.get('topicos'):
        blocos.append(Spacer(1, 2))
        blocos += [Paragraph(t, ESTILOS['item'], bulletText='•') for t in dados['topicos']]
    blocos.append(Spacer(1, m['fim_do_item']))
    return blocos


def premios(linhas, m):
    """Uma linha por prêmio, com a data à direita. Um grupo (vários prêmios no
    mesmo evento) ganha embaixo uma linha de detalhes em cinza, na largura toda,
    como as linhas de detalhes dos itens de Experiência e Projetos."""
    dados, extras = [], []
    for texto, data, detalhe in linhas:
        dados.append([Paragraph(texto, ESTILOS['corpo']), Paragraph(data, ESTILOS['data'])])
        if detalhe:
            r = len(dados) - 1
            extras += [('BOTTOMPADDING', (0, r), (-1, r), 0), ('SPAN', (0, r + 1), (1, r + 1))]
            dados.append([Paragraph(detalhe, ESTILOS['sub']), ''])
    t = tabela(dados, [LARGURA - 24 * mm, 24 * mm], m['premios_entre'])
    t.setStyle(TableStyle(extras))
    return [t]


def habilidades(linhas, m):
    return [tabela([[Paragraph(r, ESTILOS['rotulo']), Paragraph(v, ESTILOS['corpo'])] for r, v in linhas],
                   [30 * mm, LARGURA - 30 * mm], m['habilidades_entre'])]


def faixa_azul(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(AZUL)
    canvas.rect(0, A4[1] - 5, A4[0], 5, stroke=0, fill=1)
    canvas.restoreState()


def montar(c, m=MEDIDAS):
    h = [Paragraph(c['nome'], ESTILOS['nome']),
         Spacer(1, 1),
         Paragraph(SEP_PONTO.join(c['cargo']), ESTILOS['cargo']),
         Spacer(1, 5),
         Paragraph(juntar(c['contato'], SEP_CONTATO), ESTILOS['contato'])]
    h += titulo_secao(c['secoes']['resumo'], m) + [Paragraph(c['resumo'], ESTILOS['corpo'])]
    h += titulo_secao(c['secoes']['experiencia'], m)
    for dados in c['experiencia']:
        h += item(dados, m)
    h += titulo_secao(c['secoes']['projetos'], m)
    for dados in c['projetos']:
        h += item(dados, m)
    h += titulo_secao(c['secoes']['premios'], m) + premios(c['premios'], m)
    h += titulo_secao(c['secoes']['formacao'], m)
    for dados in c['formacao']:
        h += item(dados, m)
    h += titulo_secao(c['secoes']['habilidades'], m) + habilidades(c['habilidades'], m)
    return h


def gerar(c, destino, m=MEDIDAS):
    """Gera o PDF e devolve o número de páginas."""
    doc = SimpleDocTemplate(str(destino), pagesize=A4,
                            leftMargin=17 * mm, rightMargin=17 * mm,
                            topMargin=14 * mm, bottomMargin=m['margem_inferior'],
                            title=c['titulo_pdf'], author='Diogo Araujo Nunes',
                            subject=c['assunto_pdf'], creator='cv/gerar_curriculos.py')
    doc.build(montar(c, m), onFirstPage=faixa_azul, onLaterPages=faixa_azul)
    return doc.page


# ---------------------------------------------------------------------------
# Conteúdo. Marcação aceita pelo ReportLab: <b>negrito</b>, &nbsp; etc.
# Os links (contato e projetos) são pares (texto, endereço).
# ---------------------------------------------------------------------------
LATTES = 'https://lattes.cnpq.br/1566913403093846'
CONTATO_LINKS = [
    ('diogonunes2711@gmail.com', 'mailto:diogonunes2711@gmail.com'),
    ('linkedin.com/in/diogoaraujonunes', 'https://linkedin.com/in/diogoaraujonunes'),
    ('diogonuness.github.io', 'https://diogonuness.github.io'),
    ('github.com/diogonuness', 'https://github.com/diogonuness'),
    ('Lattes', LATTES),
]

PT = {
    'arquivo': 'Curriculo_Diogo_Araujo_Nunes.pdf',
    'titulo_pdf': 'Currículo – Diogo Araujo Nunes',
    'assunto_pdf': 'Currículo',
    'nome': 'Diogo Araujo Nunes',
    'cargo': ['Estágio em Desenvolvimento Web', 'PHP, Laravel e JavaScript', 'Disponível a partir de jan/2027'],
    'contato': [('Araguaína – TO', None), ('(63) 99284-6300', None)] + CONTATO_LINKS,
    'secoes': {'resumo': 'Resumo', 'experiencia': 'Experiência', 'projetos': 'Projetos',
               'premios': 'Prêmios', 'formacao': 'Formação', 'habilidades': 'Habilidades e idiomas'},
    'resumo': ('Estudante do Técnico em Informática Integrado ao Ensino Médio no IFTO (conclusão em dezembro '
               'de 2026) e bolsista de Iniciação Científica Júnior do CNPq. Participo do desenvolvimento do '
               '<b>LembreMED</b>, sistema web feito com Laravel e Filament que já está no ar e recebeu sete '
               'prêmios. Busco estágio em desenvolvimento web a partir de janeiro de 2027, presencial, híbrido '
               'ou remoto.'),
    'experiencia': [{
        'titulo': 'Bolsista de Iniciação Científica Júnior (CNPq)',
        'data': 'dez/2025 – atual',
        'sub': [('Instituto Federal do Tocantins (IFTO), Campus Araguaína', None),
                ('Orientador: Prof. Iury Gomes de Oliveira', None)],
        'topicos': [
            'Participo do desenvolvimento do LembreMED, plataforma web (Laravel + Filament) para programar '
            'doses, registrar as tomadas e acompanhar o histórico de medicação de idosos.',
            'Trabalho com perfis de acesso para idoso, cuidador e administrador e com o painel que mostra a '
            'situação de cada dose (pendente, atrasada, tomada ou perdida).',
            'Apresentei o projeto em pôster na 17ª JICE do IFTO (Araguatins, nov/2026), onde ficou em 1º lugar.',
        ],
    }],
    'projetos': [{
        'titulo': 'LembreMED',
        'data': '2025 – atual',
        'sub': [('lembremed.labsis.dev.br', 'https://lembremed.labsis.dev.br'), ('Laravel, Filament, PHP', None)],
        'topicos': [
            'Sistema em produção que ajuda idosos e cuidadores a tomar os medicamentos na hora certa, com '
            'interface simples para o idoso e acompanhamento das doses pelo cuidador.',
        ],
    }, {
        'titulo': 'Norma Clara',
        'data': 'nov/2026',
        'sub': [('Demonstração', 'https://diogonuness.github.io/norma-clara'),
                ('Código', 'https://github.com/diogonuness/norma-clara'),
                ('JavaScript, HTML, CSS', None)],
        'topicos': [
            'Assistente que responde dúvidas sobre as normativas do IFTO citando o artigo e o documento oficial, '
            'por texto ou voz (Web Speech API). O protótipo usa busca por palavras-chave; a proposta prevê '
            'evoluir para IA com RAG.',
        ],
    }],
    # (texto, data, detalhe em cinza ou None). Mais recente primeiro.
    'premios': [
        ('<b>4 prêmios</b> no Viva Ciência 2026, IFTO (LembreMED, em dupla com João Gabryel)', 'nov/2026',
         '<b>1º lugar</b> em Ciências Biomédicas e da Saúde&nbsp; ·&nbsp; <b>1º lugar</b> no Prêmio Ciência que '
         'Transforma, do Rotary Club de Araguaína (Prevenção e Tratamento de Doenças)&nbsp; ·&nbsp; '
         'Prêmio Ciência Empreendedora, do Sebrae, com capacitação em empreendedorismo e direito a apresentar '
         'um pitch para empresários e investidores&nbsp; ·&nbsp; Prêmio UNITPAC Afya'),
        ('<b>1º lugar</b> em Ciências da Saúde – 17ª JICE do IFTO (LembreMED)', 'nov/2026', None),
        ('<b>3º lugar</b> – V Ideathon Maker da 17ª JICE do IFTO (Norma Clara)', 'nov/2026', None),
        ('<b>1º lugar</b> em Ciências Biomédicas e da Saúde – Viva Ciência 2025, IFTO (LembreMED)', 'nov/2025', None),
        ('<b>3º lugar</b> – Ideathon da Campus Party Goiás (LembreMED, em equipe)', 'nov/2025', None),
    ],
    'formacao': [{
        'titulo': 'Técnico em Informática Integrado ao Ensino Médio',
        'data': '2024 – dez/2026',
        'sub': [('Instituto Federal do Tocantins (IFTO), Campus Araguaína', None)],
    }, {
        'titulo': 'Curso de Inglês – conceito final Above Expectations',
        'data': '2022 – 2025',
        'sub': [('Fisk, Araguaína', None)],
    }],
    'habilidades': [
        ('Back-end', 'PHP, Laravel, Filament'),
        ('Front-end', 'JavaScript, HTML, CSS'),
        ('Ferramentas', 'Git, GitHub, Figma (protótipos de interface)'),
        ('Idiomas', 'Português (nativo)&nbsp; ·&nbsp; Inglês intermediário – B1 no Michigan English Test (2025)'),
    ],
}

EN = {
    'arquivo': 'Resume_Diogo_Araujo_Nunes.pdf',
    'titulo_pdf': 'Résumé – Diogo Araujo Nunes',
    'assunto_pdf': 'Résumé',
    'nome': 'Diogo Araujo Nunes',
    'cargo': ['Web Development Intern', 'PHP, Laravel &amp; JavaScript', 'Available from January 2027'],
    'contato': [('Araguaína, Brazil', None), ('+55 63 99284-6300', None)] + CONTATO_LINKS,
    'secoes': {'resumo': 'Summary', 'experiencia': 'Experience', 'projetos': 'Projects',
               'premios': 'Awards', 'formacao': 'Education', 'habilidades': 'Skills & Languages'},
    'resumo': ('IT Technician student at the Federal Institute of Tocantins (IFTO), Brazil, graduating in '
               'December 2026, and Junior Research Fellow funded by CNPq, Brazil\'s national research council. '
               'I contribute to <b>LembreMED</b>, a live web system built with Laravel and Filament that has won '
               'seven awards. Looking for a web development internship starting January 2027 (on-site, hybrid '
               'or remote).'),
    'experiencia': [{
        'titulo': 'Junior Research Fellow (CNPq)',
        'data': 'Dec 2025 – Present',
        'sub': [('Federal Institute of Tocantins (IFTO), Araguaína Campus', None),
                ('Advisor: Prof. Iury Gomes de Oliveira', None)],
        'topicos': [
            'Contribute to LembreMED, a web platform (Laravel + Filament) for scheduling doses, logging when '
            'they are taken and tracking the medication history of elderly patients.',
            'Work on role-based access for elderly users, caregivers and administrators, and on the dashboard '
            'that shows each dose\'s status (pending, late, taken or missed).',
            'Presented the project as a poster at IFTO\'s 17th JICE research conference (Nov 2026), winning '
            '1st place.',
        ],
    }],
    'projetos': [{
        'titulo': 'LembreMED',
        'data': '2025 – Present',
        'sub': [('lembremed.labsis.dev.br', 'https://lembremed.labsis.dev.br'), ('Laravel, Filament, PHP', None)],
        'topicos': [
            'Live system that helps elderly people and their caregivers take medication on time, with a simple '
            'interface for the elderly user and dose tracking for the caregiver.',
        ],
    }, {
        'titulo': 'Norma Clara',
        'data': 'Nov 2026',
        'sub': [('Live demo', 'https://diogonuness.github.io/norma-clara'),
                ('Code', 'https://github.com/diogonuness/norma-clara'),
                ('JavaScript, HTML, CSS', None)],
        'topicos': [
            'Assistant that answers questions about IFTO regulations, citing the exact article and the official '
            'document, by text or voice (Web Speech API). The prototype uses keyword search; the plan is to '
            'evolve it into AI with RAG.',
        ],
    }],
    'premios': [
        ('<b>4 awards</b> at Viva Ciência 2026, IFTO (LembreMED, with João Gabryel)', 'Nov 2026',
         '<b>1st place</b>, Biomedical and Health Sciences&nbsp; ·&nbsp; <b>1st place</b>, Rotary Club of '
         'Araguaína “Ciência que Transforma” Award, Disease Prevention and Treatment category&nbsp; ·&nbsp; '
         'Sebrae “Ciência Empreendedora” Award: entrepreneurship training and a pitch to business leaders and '
         'investors&nbsp; ·&nbsp; UNITPAC Afya Award'),
        ('<b>1st place</b>, Health Sciences – IFTO 17th JICE research conference (LembreMED)', 'Nov 2026', None),
        ('<b>3rd place</b> – 5th Ideathon Maker, IFTO 17th JICE (Norma Clara)', 'Nov 2026', None),
        ('<b>1st place</b>, Biomedical and Health Sciences – Viva Ciência 2025 science fair, IFTO (LembreMED)',
         'Nov 2025', None),
        ('<b>3rd place</b> – Campus Party Goiás Ideathon (LembreMED, team)', 'Nov 2025', None),
    ],
    'formacao': [{
        'titulo': 'IT Technician Program integrated with High School',
        'data': '2024 – Dec 2026',
        'sub': [('Federal Institute of Tocantins (IFTO), Araguaína Campus, Brazil', None)],
    }, {
        'titulo': 'English Course – final grade: Above Expectations',
        'data': '2022 – 2025',
        'sub': [('Fisk Language School, Araguaína', None)],
    }],
    'habilidades': [
        ('Back-end', 'PHP, Laravel, Filament'),
        ('Front-end', 'JavaScript, HTML, CSS'),
        ('Tools', 'Git, GitHub, Figma (UI prototyping)'),
        ('Languages', 'Portuguese (native)&nbsp; ·&nbsp; English, intermediate – B1 on the Michigan English Test (2025)'),
    ],
}


if __name__ == '__main__':
    for conteudo in (PT, EN):
        destino = RAIZ / conteudo['arquivo']
        paginas = gerar(conteudo, destino)
        aviso = '' if paginas == 1 else '  <-- ATENÇÃO: passou de uma página!'
        print(f'{destino.name}: {paginas} página(s){aviso}')
