import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

html_path = Path(r"G:\Meu Drive\ANTIGRAVITY DRIVE\CAMARÃO\ERP CAMARÃO\dashboard_interativo_prototipo.html")
content = html_path.read_text(encoding="utf-8")

required_ids = [
    "view-analytics-equipe",
    "kpi-equipe-total",
    "kpi-vigia-nome",
    "kpi-custo-folha-total",
    "kpi-folgas-hoje",
    "btn-visao-semana",
    "btn-visao-mes",
    "thead-grade-escala",
    "tbody-grade-escala",
    "tbody-tabela-colaboradores",
    "modal-apontamento-dia",
    "modal-cadastro-funcionario",
    "modal-aplicar-template-escala",
    "modal-checkin-vigia",
    "modal-apont-turno",
    "modal-apont-eh-extra",
    "modal-apont-valor-diaria",
    "modal-apont-obs",
    "input-func-nome",
    "input-func-salario",
    "input-func-diaria"
]

missing_ids = [i for i in required_ids if f'id="{i}"' not in content]
if missing_ids:
    print(f"❌ Missing IDs: {missing_ids}")
else:
    print("✅ All required Team Module HTML IDs are present!")

required_funcs = [
    "renderizarModuloEquipe",
    "alternarVisualizacaoEscala",
    "renderizarGradeEscala",
    "renderizarTabelaColaboradores",
    "atualizarKpisEquipe",
    "abrirModalApontamentoDia",
    "fecharModalApontamentoDia",
    "toggleInputValorExtra",
    "salvarApontamentoDia",
    "abrirModalNovoColaborador",
    "abrirModalEditarColaborador",
    "fecharModalCadastroFuncionario",
    "salvarCadastroFuncionario",
    "abrirModalTemplateEscala",
    "fecharModalTemplateEscala",
    "aplicarTemplateEscala",
    "abrirModalCheckinVigia",
    "fecharModalCheckinVigia",
    "salvarCheckinVigia",
    "enviarEscalaWhatsApp"
]

missing_funcs = [f for f in required_funcs if f"function {f}" not in content]
if missing_funcs:
    print(f"❌ Missing Functions: {missing_funcs}")
else:
    print("✅ All required Team Module JS functions are defined!")
