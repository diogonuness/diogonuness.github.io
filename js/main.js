/* ==========================================================================
   Portfólio de Diogo Araujo Nunes: JavaScript
   Sem bibliotecas e sem build. Cada bloco cuida de uma coisa só:

   1. Preferências salvas (localStorage com segurança)
   2. Idioma (PT/EN)
   3. Tema claro/escuro
   4. Topo: fundo ao rolar e link da seção atual
   5. Menu em tela cheia (celular)
   6. Régua da trajetória
   ========================================================================== */

const raiz = document.documentElement;


/* 1. Preferências salvas ----------------------------------------------------
   O localStorage pode falhar (navegação privada, cookies bloqueados).
   Por isso toda leitura e escrita fica dentro de try/catch: se falhar,
   o site continua funcionando, só não lembra a escolha. */
function lerPreferencia(chave) {
  try {
    return localStorage.getItem(chave);
  } catch (erro) {
    return null;
  }
}

function salvarPreferencia(chave, valor) {
  try {
    localStorage.setItem(chave, valor);
  } catch (erro) {
    /* sem problema: a escolha vale só até fechar a aba */
  }
}


/* 2. Idioma -----------------------------------------------------------------
   O português fica escrito direto no HTML: é o idioma padrão e é o que o
   Google lê. Aqui ficam só os textos em inglês.

   Como funciona: cada elemento traduzível tem um atributo no HTML.
   - data-i18n="chave"            troca o texto do elemento
   - data-i18n-html="chave"       troca o HTML (só para textos nossos, com <b> etc.)
   - data-i18n-attr="atributo:chave"  troca um atributo, como o aria-label

   Ao carregar, o JS guarda o português que está no HTML em "textosPt".
   Para corrigir um texto em português, edite o HTML; em inglês, edite aqui. */
const textosEn = {
  'meta.titulo': 'Diogo Araujo Nunes · Web developer',
  'meta.descricao': 'Web developer and IT student at IFTO, Brazil. LembreMED, a system I helped build, is live and has won three awards. Available for internships from January 2027.',

  'a11y.pular': 'Skip to content',
  'a11y.marca': 'Diogo Araujo Nunes, back to top',
  'a11y.navPrincipal': 'Main',
  'a11y.navCelular': 'Menu',
  'a11y.idioma': 'Language',
  'a11y.tema': 'Dark theme',
  'a11y.github': 'GitHub (opens in a new tab)',
  'a11y.linkedin': 'LinkedIn (opens in a new tab)',

  'nav.projetos': 'Projects',
  'nav.sobre': 'About',
  'nav.contato': 'Contact',
  'nav.menu': 'Menu',
  'nav.fechar': 'Close',

  'hero.status': 'Available for internships · Jan 2027',
  'hero.local': 'Araguaína, Brazil · Remote',
  'hero.cargo': 'Web developer · IT student at IFTO',
  'hero.valor': 'I build web systems for real problems. LembreMED, which helps older adults remember their medication, is live and has already won three awards.',
  'hero.verProjetos': 'See projects',
  'hero.baixarCv': 'Download résumé',

  'data.nov25': 'Nov 2025',
  'data.nov26': 'Nov 2026',
  'data.jan27': 'Jan 2027',

  'regua.rotulo': 'Timeline, from 2024 to January 2027',
  'regua.inicio': 'Started the IT program at IFTO',
  'regua.viva': '<b>1st</b> Viva Ciência',
  'regua.campus': '<b>3rd</b> Campus Party Goiás',
  'regua.jice': '<b>1st</b> JICE · Health Sciences',
  'regua.ideathon': '<b>3rd</b> V Ideathon Maker',
  'regua.fim': 'Available for internships',

  'a11y.novaAba': '(opens in a new tab)',
  'a11y.tecnologias': 'Technologies',
  'a11y.ferramentas': 'Tools',

  'projetos.titulo': 'Projects',
  'projetos.nota': '2 live systems · 1 interface prototype',

  'lembremed.rotulo': 'Main project · live',
  'lembremed.resumo': 'A web system that helps older adults and their caregivers organize medication and remember every dose.',
  'lembremed.verNoAr': 'See it live',
  'caso.problema': 'Problem',
  'caso.solucao': 'Solution',
  'caso.papel': 'My role',
  'caso.resultado': 'Results',
  'lembremed.problema': 'People who take several medications a day need to remember every dose on time, and their caregivers need to know it was taken.',
  'lembremed.solucao': 'The caregiver registers medications and schedules and follows each dose. The older adult uses a simple, accessible screen. There are three access levels: older adult, caregiver and administrator.',
  'lembremed.papel': 'I build the system with João Gabryel, advised by Prof. Iury Gomes de Oliveira (IFTO / LabSIS). I hold a CNPq junior research scholarship on the project.',
  'premio.primeiro': '1st place',
  'premio.terceiro': '3rd place',
  'lembremed.premio1': 'Health Sciences, 17th JICE (IFTO)',
  'lembremed.premio2': 'Biological and Health Sciences, Viva Ciência',
  'lembremed.premio3': 'Campus Party Goiás Ideathon',

  'norma.rotulo': 'Prototype · live demo',
  'norma.resumo': 'An assistant that answers questions about IFTO’s regulations, by text or voice, citing the exact article and the official PDF.',
  'norma.detalhe': 'Search currently uses keywords and synonyms; the next step is AI with RAG. Built by team Fonte Certa, advised by Prof. Iury.',
  'norma.premio': 'V Ideathon Maker, 17th JICE (IFTO)',
  'norma.demo': 'Live demo',
  'norma.codigo': 'Code on GitHub',

  'sonora.rotulo': 'Interface design · Figma',
  'sonora.resumo': 'A mobile prototype of a music streaming app, designed in Figma for the User Interface course at IFTO.',
  'sonora.tag': 'Mobile prototype',
  'sonora.figma': 'View in Figma',
};

const textosPt = {};
let idiomaAtual = 'pt';
const metaDescricao = document.querySelector('meta[name="description"]');

// Lê "aria-label:a11y.tema; title:outra.chave" e devolve [["aria-label", "a11y.tema"], ...]
function lerAtributos(elemento) {
  return elemento.dataset.i18nAttr
    .split(';')
    .map((par) => par.split(':').map((parte) => parte.trim()))
    .filter(([atributo, chave]) => atributo && chave);
}

function guardarPortugues() {
  document.querySelectorAll('[data-i18n]').forEach((el) => {
    textosPt[el.dataset.i18n] ??= el.textContent.trim();
  });
  document.querySelectorAll('[data-i18n-html]').forEach((el) => {
    textosPt[el.dataset.i18nHtml] ??= el.innerHTML.trim();
  });
  document.querySelectorAll('[data-i18n-attr]').forEach((el) => {
    lerAtributos(el).forEach(([atributo, chave]) => {
      textosPt[chave] ??= el.getAttribute(atributo);
    });
  });
  textosPt['meta.titulo'] = document.title;
  textosPt['meta.descricao'] = metaDescricao.getAttribute('content');
  textosPt['nav.menu'] = 'Menu';
  textosPt['nav.fechar'] = 'Fechar';
}

// Devolve o texto da chave no idioma atual (se faltar em inglês, usa o português)
function texto(chave) {
  const textos = idiomaAtual === 'en' ? textosEn : textosPt;
  return textos[chave] ?? textosPt[chave] ?? '';
}

function aplicarIdioma(idioma) {
  idiomaAtual = idioma === 'en' ? 'en' : 'pt';
  raiz.lang = idiomaAtual === 'en' ? 'en' : 'pt-BR';

  document.querySelectorAll('[data-i18n]').forEach((el) => {
    el.textContent = texto(el.dataset.i18n);
  });
  document.querySelectorAll('[data-i18n-html]').forEach((el) => {
    el.innerHTML = texto(el.dataset.i18nHtml);
  });
  document.querySelectorAll('[data-i18n-attr]').forEach((el) => {
    lerAtributos(el).forEach(([atributo, chave]) => el.setAttribute(atributo, texto(chave)));
  });

  document.title = texto('meta.titulo');
  metaDescricao.setAttribute('content', texto('meta.descricao'));

  document.querySelectorAll('[data-idioma]').forEach((botao) => {
    botao.setAttribute('aria-pressed', String(botao.dataset.idioma === idiomaAtual));
  });

  atualizarRotuloMenu();
}

guardarPortugues();

document.querySelectorAll('[data-idioma]').forEach((botao) => {
  botao.addEventListener('click', () => {
    aplicarIdioma(botao.dataset.idioma);
    salvarPreferencia('idioma', idiomaAtual);
  });
});


/* 3. Tema claro/escuro ------------------------------------------------------
   Sem escolha salva, o site segue o sistema (prefers-color-scheme).
   Ao clicar, a escolha vira data-theme="light" ou "dark" no <html>
   e fica salva. O script no <head> reaplica antes de a página aparecer. */
const botaoTema = document.querySelector('[data-tema]');
const sistemaEscuro = window.matchMedia('(prefers-color-scheme: dark)');

function temaAtual() {
  return raiz.dataset.theme || (sistemaEscuro.matches ? 'dark' : 'light');
}

// A barra do navegador no celular acompanha a cor de fundo do tema
function atualizarCorDoNavegador() {
  const cor = getComputedStyle(raiz).getPropertyValue('--fundo').trim();
  document.querySelectorAll('meta[name="theme-color"]').forEach((meta) => meta.setAttribute('content', cor));
}

function atualizarBotaoTema() {
  botaoTema.setAttribute('aria-pressed', String(temaAtual() === 'dark'));
  atualizarCorDoNavegador();
}

botaoTema.addEventListener('click', () => {
  const novoTema = temaAtual() === 'dark' ? 'light' : 'dark';
  // Desliga as transições por um instante: a troca de cores fica instantânea e uniforme
  raiz.classList.add('sem-transicao');
  raiz.dataset.theme = novoTema;
  salvarPreferencia('tema', novoTema);
  atualizarBotaoTema();
  requestAnimationFrame(() => requestAnimationFrame(() => raiz.classList.remove('sem-transicao')));
});

sistemaEscuro.addEventListener('change', atualizarBotaoTema);
atualizarBotaoTema();


/* 4. Topo -------------------------------------------------------------------
   a) Ganha fundo translúcido quando a página sai do topo.
   b) Marca no menu a seção que está na tela (aria-current). */
const topo = document.querySelector('[data-topo]');

function atualizarTopo() {
  topo.classList.toggle('rolou', window.scrollY > 8);
}

window.addEventListener('scroll', atualizarTopo, { passive: true });
atualizarTopo();

const linksDoMenu = document.querySelectorAll('.menu a[href^="#"]');
const observadorDeSecoes = new IntersectionObserver(
  (entradas) => {
    entradas.forEach((entrada) => {
      if (!entrada.isIntersecting) return;
      const id = '#' + entrada.target.id;
      linksDoMenu.forEach((link) => {
        if (link.getAttribute('href') === id) link.setAttribute('aria-current', 'true');
        else link.removeAttribute('aria-current');
      });
    });
  },
  // Só conta a seção que cruza uma faixa fina no meio da tela
  { rootMargin: '-45% 0px -50% 0px' }
);
document.querySelectorAll('main > section[id]').forEach((secao) => observadorDeSecoes.observe(secao));


/* 5. Menu em tela cheia (celular) ------------------------------------------- */
const botaoMenu = document.querySelector('[data-menu-btn]');
const rotuloMenu = document.querySelector('[data-menu-rotulo]');
const gaveta = document.querySelector('[data-gaveta]');
const menuMobile = window.matchMedia('(max-width: 759px)');

function menuEstaAberto() {
  return botaoMenu.getAttribute('aria-expanded') === 'true';
}

function atualizarRotuloMenu() {
  rotuloMenu.textContent = menuEstaAberto() ? texto('nav.fechar') : texto('nav.menu');
}

// "inert" desativa cliques e foco no resto da página enquanto o menu está aberto
function deixarFundoInerte(inerte) {
  document.querySelectorAll('main, footer').forEach((el) => {
    el.inert = inerte;
  });
}

function abrirMenu() {
  gaveta.hidden = false;
  gaveta.getBoundingClientRect(); // força o navegador a desenhar o estado inicial antes da transição
  gaveta.classList.add('aberta');
  raiz.classList.add('menu-aberto');
  botaoMenu.setAttribute('aria-expanded', 'true');
  atualizarRotuloMenu();
  deixarFundoInerte(true);
  gaveta.querySelector('a').focus();
}

function fecharMenu({ devolverFoco = true } = {}) {
  if (!menuEstaAberto()) return;
  gaveta.classList.remove('aberta');
  raiz.classList.remove('menu-aberto');
  botaoMenu.setAttribute('aria-expanded', 'false');
  atualizarRotuloMenu();
  deixarFundoInerte(false);
  // Espera o fade de saída (180ms) para esconder de vez
  window.setTimeout(() => {
    if (!menuEstaAberto()) gaveta.hidden = true;
  }, 180);
  if (devolverFoco) botaoMenu.focus();
}

botaoMenu.addEventListener('click', () => (menuEstaAberto() ? fecharMenu() : abrirMenu()));

// Clicar num link fecha o menu e deixa a página rolar até a seção
gaveta.querySelectorAll('a').forEach((link) => {
  link.addEventListener('click', () => fecharMenu({ devolverFoco: false }));
});

document.addEventListener('keydown', (evento) => {
  if (evento.key === 'Escape') fecharMenu();
});

// Se a tela crescer (girou o celular, por exemplo), o menu fecha sozinho
menuMobile.addEventListener('change', (evento) => {
  if (!evento.matches) fecharMenu({ devolverFoco: false });
});


/* 6. Régua da trajetória ----------------------------------------------------
   Calcula quantos meses se passaram desde jan/2024 (mês 0) até hoje.
   A régua usa esse número (--hoje) para separar a linha sólida (passado)
   da tracejada (o que falta até jan/2027, mês 36). */
const regua = document.querySelector('[data-regua]');

if (regua) {
  const agora = new Date();
  const meses = (agora.getFullYear() - 2024) * 12 + agora.getMonth();
  regua.style.setProperty('--hoje', String(Math.min(36, Math.max(0, meses))));
}


/* Por último: aplica o idioma salvo (se a pessoa já escolheu inglês antes) */
if (lerPreferencia('idioma') === 'en') aplicarIdioma('en');
