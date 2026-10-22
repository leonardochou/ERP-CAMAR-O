import re
import subprocess
import tempfile
from pathlib import Path

html = Path(r"G:\Meu Drive\ANTIGRAVITY DRIVE\CAMARÃO\ERP CAMARÃO\dashboard_interativo_prototipo.html").read_text(encoding="utf-8")

checks = [
    ("Quadro Agenda max-h-[360px]", "max-h-[360px]" in html),
    ("Slot Horários h-[36px]", "h-[36px]" in html),
    ("Painel Ocorrências", "painel-ocorrencias-equipe" in html),
    ("Tabela Ocorrências", "tbody-ocorrencias" in html),
    ("Filtro Ocorrência Extras", "filtro-ocorr-EXTRA" in html),
    ("Filtro Ocorrência Faltas", "filtro-ocorr-FALTA" in html),
    ("Filtro Ocorrência Reclamações", "filtro-ocorr-RECLAMACAO" in html),
    ("Modal Nova Ocorrência", "modal-nova-ocorrencia" in html),
    ("Função renderizarPainelOcorrencias", "renderizarPainelOcorrencias" in html),
    ("Função salvarNovaOcorrencia", "salvarNovaOcorrencia" in html),
    ("Função enviarOcorrenciaWhatsApp", "enviarOcorrenciaWhatsApp" in html),
    ("Array OCORRENCIAS_DATA", "OCORRENCIAS_DATA" in html),
]

all_passed = True
for label, result in checks:
    print(f"[{'PASS' if result else 'FAIL'}] {label}")
    if not result:
        all_passed = False

# Validar ordem: Tabela Salários -> Google Agenda -> Painel Ocorrências
pos_salarios = html.find("Cadastro de Colaboradores")
pos_agenda = html.find("container-google-agenda")
pos_ocorrencias = html.find("painel-ocorrencias-equipe")

print(f"Posições: Salários={pos_salarios}, Agenda={pos_agenda}, Ocorrências={pos_ocorrencias}")
if 0 < pos_salarios < pos_agenda < pos_ocorrencias:
    print("[PASS] Ordem correta dos componentes: Salários no Topo -> Google Agenda Compacta -> Painel de Ocorrências Embaixo!")
else:
    print("[FAIL] Ordem incorreta!")
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
    print("\n>>> TUDO 100% VALIDADO: ESTRUTURA, DIMENSOES E JAVASCRIPT! <<<")
else:
    print("\n>>> FALHA NA VALIDACAO! <<<")
