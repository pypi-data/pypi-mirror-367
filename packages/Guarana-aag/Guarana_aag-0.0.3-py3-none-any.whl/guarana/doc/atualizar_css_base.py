from pathlib import Path
from datetime import date
import re

CAMADAS = 'prism, doc_gua';

#region PASTAS E ARQUIVOS
pasta_atual = Path(__file__).parent
pasta_destino = pasta_atual/'static/css'
pasta_origem = pasta_atual.parent/'origem/css'
pasta_base = pasta_origem/'base'

arquivo_destino = pasta_destino/'guarana.css'
arquivos = list(pasta_base.glob('*'))
# endregion


# TEXTO A SER USADO
texto = f'/*{date.today().strftime("%d/%m/%Y")}*/\n'

# TEXTO DO ESTILO.CSS
regex_imports = r'(.|\n)*?/\* LAYERS \*/\n'
regex_layers = r'(\s*@layer\s+.*?)(\s*);'
estilo_original = pasta_origem/'estilo.css'
texto += re.sub(regex_imports, '', estilo_original.read_text(), 1)
texto = re.sub(regex_layers, r'\1' + f', {CAMADAS}' + r';', texto)


for arquivo in arquivos:
    texto += '\n'
    texto += arquivo.read_text()
    texto += '\n'

arquivo_destino.write_text(texto)

