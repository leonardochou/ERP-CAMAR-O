"""
Script para fechar corretamente o #view-pai-banner e garantir que o novo
Dashboard Principal fique 100% visível e estruturado fora do banner oculto.
"""
from pathlib import Path

p = Path(r"G:\Meu Drive\ANTIGRAVITY DRIVE\CAMARÃO\ERP CAMARÃO\dashboard_interativo_prototipo.html")
html = p.read_text(encoding="utf-8")

# Bloco completo do view-pai-banner
banner_pai_completo = """        <!-- Banner Pai / Campo (visível apenas no modo pai) -->
        <div id="view-pai-banner" class="hidden bg-gradient-to-r from-amber-500 to-amber-600 rounded-2xl p-5 text-white shadow-md">
          <div class="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            <div class="flex items-center gap-3">
              <div class="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center text-2xl font-bold">🌾</div>
              <div>
                <h2 class="text-xl font-bold">Modo Operacional de Campo — Visão Simplificada</h2>
                <p class="text-amber-100 text-sm">Botões grandes e diretos. Lance medições em 2 cliques ou por áudio no WhatsApp.</p>
              </div>
            </div>
            <div class="flex flex-wrap items-center gap-2">
              <button onclick="openWhatsAppModal()" class="bg-white text-emerald-800 font-bold px-4 py-2.5 rounded-xl shadow hover:bg-emerald-50 transition flex items-center gap-2">
                <i class="fa-brands fa-whatsapp text-emerald-600 text-lg"></i> Gravar Áudio de Campo
              </button>
              <button onclick="abrirModalPreenchimentoRapido('V-01')" class="bg-amber-900/60 hover:bg-amber-900/80 text-white font-bold px-4 py-2.5 rounded-xl shadow transition flex items-center gap-2">
                <i class="fa-solid fa-plus-circle"></i> Lançar Ração Agora
              </button>
            </div>
          </div>
        </div>"""

idx_macro_open = html.find('id="view-dashboard-macro"')
if idx_macro_open == -1: idx_macro_open = html.find('view-dashboard-macro')
idx_tag_macro_end = html.find('>', idx_macro_open) + 1

idx_regua = html.find('<!-- ======================================================== -->\n        <!-- 1. RÉGUA DE PRODUÇÃO NOS TRÊS HORIZONTES')

if idx_macro_open != -1 and idx_regua != -1:
    html = html[:idx_tag_macro_end] + "\n\n" + banner_pai_completo + "\n\n" + html[idx_regua:]
    p.write_text(html, encoding="utf-8")
    print("Sucesso: Banner pai restaurado e fechado corretamente antes da Régua de Produção!")
else:
    print(f"Indices: {idx_macro_open}, {idx_regua}")
