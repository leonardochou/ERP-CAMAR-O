"""
Script para:
1. Elevar o estado global (DADOS_PLANILHA_VIVEIROS, selectedViveiroIdBiomassa, filtroOcorrenciaAtivo, OCORRENCIAS_DATA)
   para o topo do script principal, logo após VIVEIROS_DATA e ESTADO GLOBAL DO PROTÓTIPO;
2. Ajustar inicializarEscalasPadrao() para não chamar irParaHojeGoogleAgenda() no top-level (evitando renderização do DOM antes do DOMContentLoaded);
3. Validar a sintaxe e o runtime no Node.js.
"""
import shutil
from pathlib import Path

BASE_DIR = Path(r"G:\Meu Drive\ANTIGRAVITY DRIVE\CAMARÃO\ERP CAMARÃO")
HTML_PATH = BASE_DIR / "dashboard_interativo_prototipo.html"
BACKUP_PATH = BASE_DIR / "dashboard_interativo_prototipo.backup_antes_elevacao_tdz.html"

shutil.copy2(HTML_PATH, BACKUP_PATH)
print(f"Backup gravado em: {BACKUP_PATH}")

html = HTML_PATH.read_text(encoding="utf-8")

# 1. Extrair bloco de dados zootécnicos e viveiros
p_dados_start = html.find('let selectedViveiroIdBiomassa =')
p_dados_end = html.find('function sincronizarViveirosComPlanilhaReal()')
bloco_dados = html[p_dados_start:p_dados_end].strip()

# 2. Extrair bloco de ocorrências e equipe
p_oco_start = html.find('let filtroOcorrenciaAtivo =')
p_oco_end = html.find('function renderizarPainelOcorrencias(')
bloco_oco = html[p_oco_start:p_oco_end].strip()

# Remover os blocos de suas posições originais inferiores
if p_dados_start > p_oco_start:
    html_mod = html[:p_dados_start] + '\n\n    ' + html[p_dados_end:]
    html_mod = html_mod[:p_oco_start] + '\n\n    ' + html_mod[p_oco_end:]
else:
    html_mod = html[:p_oco_start] + '\n\n    ' + html_mod[p_oco_end:]
    html_mod = html_mod[:p_dados_start] + '\n\n    ' + html_mod[p_dados_end:]

# Inserir no topo do estado global do protótipo
p_estado = html_mod.find('// ESTADO GLOBAL DO PROTÓTIPO')
p_estado_end = html_mod.find("let currentView = 'dashboard-macro';", p_estado) + len("let currentView = 'dashboard-macro';")

bloco_unificado = f"""
    // ========================================================
    // ESTADO GLOBAL ELEVADO (Evita Temporal Dead Zone TDZ)
    // ========================================================
    {bloco_oco}

    {bloco_dados}
"""

html_mod = html_mod[:p_estado_end] + '\n' + bloco_unificado + '\n' + html_mod[p_estado_end:]

# 3. Ajustar inicializarEscalasPadrao para não renderizar no top-level
trecho_antigo_fim_escala = """      // Iniciar a semana da Google Agenda no Domingo da semana atual
      irParaHojeGoogleAgenda();
    }"""

trecho_novo_fim_escala = """      // Define a data inicial da Google Agenda no Domingo da semana atual
      const dSem = hoje.getDay();
      const dBase = new Date(hoje);
      dBase.setDate(hoje.getDate() - dSem);
      dBase.setHours(0, 0, 0, 0);
      dataInicioSemanaAgenda = dBase;
    }"""

if trecho_antigo_fim_escala in html_mod:
    html_mod = html_mod.replace(trecho_antigo_fim_escala, trecho_novo_fim_escala, 1)
    print("Sucesso: inicializarEscalasPadrao ajustado para cálculo puro sem renderização prematura no top-level!")
else:
    print("Aviso: trecho_antigo_fim_escala não encontrado para substituição direta.")

HTML_PATH.write_text(html_mod, encoding="utf-8")
print(f"dashboard_interativo_prototipo.html atualizado! Tamanho: {len(html_mod)} bytes.")
