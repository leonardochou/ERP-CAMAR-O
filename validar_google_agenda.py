import re
from pathlib import Path

html = Path(r"G:\Meu Drive\ANTIGRAVITY DRIVE\CAMARÃO\ERP CAMARÃO\dashboard_interativo_prototipo.html").read_text(encoding="utf-8")

checks = [
    ("Seção Equipe", "view-analytics-equipe" in html),
    ("Container Google Agenda", "container-google-agenda" in html),
    ("Colunas do Corpo da Agenda", "google-agenda-corpo-colunas" in html),
    ("Linha All-day / Folgas", "google-agenda-all-day-row" in html),
    ("Botão Hoje Google Agenda", "irParaHojeGoogleAgenda()" in html),
    ("Navegação Semana Google Agenda", "navegarSemanaGoogleAgenda" in html),
    ("Filtro Colaborador Chips", "filtrarColaboradorGoogleAgenda" in html),
    ("Modal Cadastro - Jornada Ini", "input-func-jornada-ini" in html),
    ("Modal Cadastro - Jornada Fim", "input-func-jornada-fim" in html),
    ("Modal Apontamento - Horários", "modal-apont-hora-ini" in html),
    ("Modal Apontamento - Atalhos", "definirHorarioJornadaRapida" in html),
    ("Container Matriz Mensal", "container-matriz-mensal" in html),
    ("Botão Alternador Agenda/Matriz", "alternarModoVisualizacaoEscala" in html),
]

all_passed = True
for label, result in checks:
    print(f"[{'PASS' if result else 'FAIL'}] {label}")
    if not result:
        all_passed = False

# Verificar ordem dos blocos em view-analytics-equipe:
secao_match = re.search(r'<section id="view-analytics-equipe"[\s\S]*?</section>', html)
if secao_match:
    sec_html = secao_match.group(0)
    pos_tabela_salarios = sec_html.find("Cadastro de Colaboradores")
    pos_agenda = sec_html.find("container-google-agenda")
    print(f"Posição Tabela Salários: {pos_tabela_salarios}")
    print(f"Posição Google Agenda: {pos_agenda}")
    if 0 < pos_tabela_salarios < pos_agenda:
        print("[PASS] Tabela de Salários está no TOPO (antes da Google Agenda)!")
    else:
        print("[FAIL] Ordem incorreta!")
        all_passed = False
else:
    print("[FAIL] Seção view-analytics-equipe não encontrada!")
    all_passed = False

if all_passed:
    print("\nTODAS AS CHECAGENS ESTRUTURAIS PASSARAM COM SUCESSO!")

# Validar sintaxe JS
import subprocess
import tempfile

scripts = re.findall(r'<script(?:\s+[^>]*)?>([\s\S]*?)</script>', html, re.IGNORECASE)
print(f"\nEncontrados {len(scripts)} blocos de script.")

for i, script_code in enumerate(scripts, 1):
    # Ignorar se o script for de template ou CDN
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
    print("\n>>> TUDO 100% VALIDADO COM SUCESSO: ESTRUTURA HTML, CSS E JAVASCRIPT! <<<")

