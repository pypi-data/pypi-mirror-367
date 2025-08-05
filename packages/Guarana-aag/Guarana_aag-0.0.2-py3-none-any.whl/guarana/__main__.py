import argparse

from . import comandos
from .config import *

descricao = f"{NOME}: estrutura de front-end para Flask. Versão: {VERSAO}"


def main():
    parser = argparse.ArgumentParser(description=descricao)
    subparsers = parser.add_subparsers(dest='comando')

    flask_help = 'Instala a estrutura básica de flask'
    instalar = subparsers.add_parser(
        'instalar',
        help=f'Instala o'
        f' {COR_AMARELO}{NOME}{COR_FIM} na pasta {COR_VERDE}{PASTA_STATIC}/{COR_FIM}, '
        f'criando as subpastas {COR_VERDE}/{PASTA_CSS}/{COR_FIM} '
        f'e {COR_VERDE}/{PASTA_CSS}/{COR_FIM}, junto de seus conteúdo\t'
        f'{COR_AMARELO}--flask{COR_FIM}: {flask_help}'
    )
    instalar.add_argument(
        '--flask', action='store_true',
        help=flask_help
    )

    atualizar = subparsers.add_parser(
        'atualizar',
        help='TODO:'
    )

    resetar = subparsers.add_parser(
        'resetar',
        help='TODO:'
    )

    minificar = subparsers.add_parser(
        'min',
        help=f'TODO:'
    )

    args = parser.parse_args()
    match args.comando:
        case 'instalar': comandos.instalar_guarana(args.flask)
        case 'atualizar': print('TODO:')
        case 'resetar': print('TODO:')
        case 'min': comandos.criar_estilo_css_min()
        case _: parser.print_help()

if __name__ == "__main__":
    main()
    