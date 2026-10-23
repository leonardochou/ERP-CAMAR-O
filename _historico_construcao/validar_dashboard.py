import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

html_path = Path(r"G:\Meu Drive\ANTIGRAVITY DRIVE\CAMARÃO\ERP CAMARÃO\dashboard_interativo_prototipo.html")
content = html_path.read_text(encoding="utf-8")

print(f"File size: {len(content):,} bytes")

required_ids = [
    "view-viveiros-mapa",
    "btn-tab-satelite",
    "btn-tab-vetorial",
    "btn-tab-tabela",
    "kpi-topo-area-satelite",
    "kpi-topo-area-ajustada",
    "kpi-topo-volume",
    "container-modo-satelite",
    "container-modo-vetorial",
    "container-modo-tabela",
    "img-satelite-principal",
    "lista-cards-satelite",
    "coluna-setor-oeste",
    "coluna-setor-central",
    "coluna-setor-leste",
    "tbody-tabela-calibracao-metragens",
    "modal-calibracao-metragem",
    "modal-satelite-ampliado",
    "modal-calibrar-titulo",
    "input-calibrar-area-m2"
]

missing_ids = [i for i in required_ids if f'id="{i}"' not in content]
if missing_ids:
    print(f"❌ Missing IDs: {missing_ids}")
else:
    print("✅ All required HTML element IDs are present!")

required_funcs = [
    "renderizarModuloMapa2D",
    "alternarAbaMapa",
    "zoomSatelite",
    "resetZoomSatelite",
    "abrirModalSateliteAmpliado",
    "fecharModalSateliteAmpliado",
    "filtrarCardsSatelite",
    "filtrarMapaSetor",
    "renderizarCardsSatelite",
    "renderizarCardsVetoriais",
    "criarCardTanqueTopografico",
    "renderizarTabelaCalibracao",
    "atualizarTotaisTopograficos",
    "abrirModalCalibracao",
    "fecharModalCalibracao",
    "recalcularPreviaCalibracao",
    "restaurarMetragemSatelite",
    "salvarCalibracaoMetragem"
]

missing_funcs = [f for f in required_funcs if f"function {f}" not in content]
if missing_funcs:
    print(f"❌ Missing Functions: {missing_funcs}")
else:
    print("✅ All required JS functions are defined!")

# Check if image data URI is properly set
if "data:image/png;base64,iVBORw" in content:
    print("✅ Base64 Satellite Image embedded successfully!")
else:
    print("❌ Base64 Satellite Image missing or incomplete!")

# Check VIVEIROS_DATA count
matches = re.findall(r"id:\s*'(V-\d\d)'", content)
print(f"✅ VIVEIROS_DATA entries detected: {len(matches)} tanques")

# Check father numbering
pais = re.findall(r"nomePai:\s*'Viveiro\s+(\d+)'", content)
print(f"✅ Viveiros do Pai (1 a 10) detected: {len(set(pais))} viveiros: {sorted([int(x) for x in set(pais)])}")
