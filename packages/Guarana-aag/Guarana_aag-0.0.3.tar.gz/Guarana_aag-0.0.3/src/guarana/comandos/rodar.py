from flask import Flask, render_template, abort
from pathlib import Path
import markdown
import json
import re

from ..config import *

def rodar_doc():
    app = Flask(__name__)
    app.config['DEBUG'] = True
    app.config['PORT'] = PORTA_LOCAL
    app.static_folder = '../doc/static'
    app.template_folder = '../doc/templates'

    print('Rodando o Front_End em segundo plano.')
    print(f'Endereço para acessar: {COR_VERMELHO}http://localhost:{PORTA_LOCAL}{COR_FIM}')

    # --------------------------------------------------------------------------
    # Coleta de Contexto
    # --------------------------------------------------------------------------
    # Os dados são coletados uma vez na inicialização para otimizar o desempenho.
    arquivo_atual = Path(__file__).resolve()
    # Navega para o diretório raiz do projeto
    raiz = arquivo_atual.parent.parent.parent.parent

    # Importa o changelog
    md = {}
    try:
        with open(raiz / 'changelog.md', 'r', encoding='utf-8') as f:
            md_lido = f.read()
            md['changelog'] = markdown.markdown(md_lido)
    except FileNotFoundError:
        md['changelog'] = '<p>Arquivo changelog.md não encontrado.</p>'

    # Importa os snippets
    snippets_path = raiz / '.vscode'
    snippets = {}
    for tipo in ['js', 'css', 'html']:
        arquivo = snippets_path / f'guarana-{tipo}.code-snippets'
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                snippets[tipo] = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            snippets[tipo] = {}

    # TODO: mapear os arquivos de views para criar o menu

    # Dicionário com todo o contexto a ser passado para o template
    template_context = {
        'app': NOME.replace('na', 'ná'),
        'versao': VERSAO,
        'pasta_utils': PASTA_UTILS,
        'pasta_views': PASTA_VIEWS,
        'md': md,
        'snippets': snippets,
        'views': None
    }

    # --------------------------------------------------------------------------
    #  GERANDO AS ROTAS
    # --------------------------------------------------------------------------
    @app.route('/')
    @app.route('/<string:view_id>')
    def show_page(view_id=None):
        """
        Renderiza a página principal.
        Esta função lida tanto com a raiz ('/') quanto com as views específicas ('/tabela').
        """
        # TODO:
        # Se um view_id for fornecido na URL, verifica se ele é válido
        # if view_id and view_id not in valid_view_ids:
        #     abort(404)

        # Renderiza sempre o mesmo 'index.html', passando o contexto.
        # O JavaScript no cliente cuidará de exibir o conteúdo correto.
        return render_template('index.html', **template_context)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html', error=e), 404

    app.run()
