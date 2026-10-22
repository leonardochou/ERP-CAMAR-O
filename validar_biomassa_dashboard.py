import re
import subprocess
import tempfile
from pathlib import Path

html = Path(r"G:\Meu Drive\ANTIGRAVITY DRIVE\CAMARÃO\ERP CAMARÃO\dashboard_interativo_prototipo.html").read_text(encoding="utf-8")

checks = [
    ("SheetJS no head", "xlsx.full.min.js" in html),
    ("Botão Sincronizar Drive", "sincronizarPlanilhaDriveBiomassa" in html),
    ("Botão Importar .xlsx", "importarArquivoXlsxBiomassa" in html),
    ("Botão Lançamento Manual", "abrirModalLancamentoBiomassa" in html),
    ("Pills de Viveiros", "pills-container-viveiros-biomassa" in html),
    ("Container Biomassa Geral", "container-biomassa-geral" in html),
    ("Container Viveiro Detalhe", "container-biomassa-viveiro-detalhe" in html),
    ("Tabela Completa do Tanque", "tbody-tabela-diaria-viveiro" in html),
    ("Modal Relatório Importação", "modal-relatorio-importacao-planilha" in html),
    ("Modal Lançamento Manual", "modal-lancamento-biomassa-viveiro" in html),
    ("Função selecionarViveiroBiomassa", "selecionarViveiroBiomassa" in html),
    ("Função renderizarDashboardViveiroBiomassa", "renderizarDashboardViveiroBiomassa" in html),
    ("Função exibirRelatorioImportacao", "exibirRelatorioImportacao" in html),
    ("Objeto DADOS_PLANILHA_VIVEIROS", "DADOS_PLANILHA_VIVEIROS" in html),
]

all_passed = True
for label, result in checks:
    print(f"[{'PASS' if result else 'FAIL'}] {label}")
    if not result:
        all_passed = False

# Validar sintaxe JS com Node.js
scripts = re.findall(r'<script(?:\s+[^>]*)?>([\s\S]*?)</script>', html, re.IGNORECASE)
for i, script_code in enumerate(scripts, 1):
    if not script_code.strip():
        continue
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as tf:
        tf.write(script_code)
        temp_js_path = tf.name

    res = subprocess.run(["node", "--check", temp_js_path], capture_output=True, text=True)
    if res.returncode == 0:
        print(f"[PASS] Bloco JS #{i} sintaxe válida!")
    else:
        print(f"[FAIL] Bloco JS #{i} erro de sintaxe:\n{res.stderr}")
        all_passed = False

if all_passed:
    print("\n>>> TUDO 100% VALIDADO: ESTRUTURA, CONTROLES E JAVASCRIPT! <<<")
else:
    print("\n>>> FALHA NA VALIDACAO! <<<")
