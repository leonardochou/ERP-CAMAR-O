"""Script para implementar o Módulo de Ciclos de Produção, Encerramento e Reset Limpo no Dashboard HTML."""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

HTML_PATH = Path(r"G:\Meu Drive\ANTIGRAVITY DRIVE\CAMARÃO\ERP CAMARÃO\dashboard_interativo_prototipo.html")
content = HTML_PATH.read_text(encoding="utf-8")

# ==============================================================================
# 1. SIDEBAR: Adicionar item Ciclos de Produção no Bloco 2: Zootecnia & Manejo
# ==============================================================================
target_nav = '<button onclick="navegarPara(\'analytics-povoamento\')"'
if 'id="nav-analytics-ciclos"' not in content:
    idx_nav = content.find(target_nav)
    if idx_nav != -1:
        # Encontrar o fechamento do botão nav-analytics-povoamento
        idx_end_btn = content.find('</button>', idx_nav) + len('</button>')
        novo_botao_sidebar = """
        <button onclick="navegarPara('analytics-ciclos')" id="nav-analytics-ciclos" class="nav-item w-full flex items-center space-x-3 px-3 py-2.5 rounded-xl font-medium text-blue-200 hover:text-white hover:bg-white/10 transition">
          <i class="fa-solid fa-arrows-spin w-5 text-center text-cyan-400"></i>
          <span class="sidebar-label">Ciclos de Produção</span>
        </button>"""
        content = content[:idx_end_btn] + novo_botao_sidebar + content[idx_end_btn:]
        print("✅ 1. Botão 'Ciclos de Produção' adicionado à sidebar.")
    else:
        print("❌ Falha ao localizar nav-analytics-povoamento na sidebar.")
else:
    print("ℹ️ 1. Botão nav-analytics-ciclos já presente na sidebar.")


# ==============================================================================
# 2. VIEW: Adicionar section #view-analytics-ciclos
# ==============================================================================
target_view_despesca = '<!-- ======================================================== -->\n      <!-- VIEW: DESPESCA & VENDAS'
if 'id="view-analytics-ciclos"' not in content:
    idx_view = content.find(target_view_despesca)
    if idx_view == -1:
        target_view_despesca = '<!-- VIEW: DESPESCA & VENDAS'
        idx_view = content.find(target_view_despesca)

    if idx_view != -1:
        html_view_ciclos = """<!-- ======================================================== -->
      <!-- VIEW: GESTÃO DE CICLOS DE PRODUÇÃO & HISTÓRICO DE SAFRAS -->
      <!-- ======================================================== -->
      <section id="view-analytics-ciclos" class="hidden space-y-6 pb-24">
        
        <!-- Header Executivo da View de Ciclos -->
        <div class="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4 bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <div class="space-y-1">
            <div class="flex items-center space-x-2 text-xs font-semibold text-aco">
              <span class="cursor-pointer hover:underline" onclick="navegarPara('dashboard-macro')">Fazenda</span>
              <span>&gt;</span>
              <span class="cursor-pointer hover:underline" onclick="navegarPara('analytics-biomassa')">Zootecnia</span>
              <span>&gt;</span>
              <span class="text-slate-800 font-bold">Ciclos de Produção</span>
            </div>
            <h2 class="text-xl font-extrabold text-slate-900 flex items-center gap-2">
              <i class="fa-solid fa-arrows-spin text-cyan-600"></i> Gestão de Ciclos de Produção & Safras
            </h2>
            <p class="text-xs text-slate-500">
              Controle de ciclos ativos por viveiro, desbastes parciais, encerramento com reset limpo e histórico permanente com FCA e sobrevivência.
            </p>
          </div>

          <div class="flex flex-wrap items-center gap-2.5 w-full lg:w-auto">
            <!-- Filtro de Ano-Safra -->
            <div class="flex items-center gap-1.5 bg-slate-50 p-1 rounded-xl border border-slate-200 text-xs">
              <span class="text-[11px] font-bold text-slate-500 px-2">Safra:</span>
              <select id="filtro-ciclos-ano" onchange="filtrarModuloCiclos()" class="bg-white text-xs font-bold py-1.5 px-3 rounded-lg border border-slate-200 text-slate-800 focus:outline-none focus:ring-2 focus:ring-cyan-500">
                <option value="TODOS">Todas as Safras</option>
                <option value="2026" selected>Ano-Safra 2026</option>
                <option value="2025">Ano-Safra 2025</option>
                <option value="2027">Ano-Safra 2027</option>
              </select>
            </div>

            <!-- Filtro de Viveiro -->
            <div class="flex items-center gap-1.5 bg-slate-50 p-1 rounded-xl border border-slate-200 text-xs">
              <span class="text-[11px] font-bold text-slate-500 px-2">Viveiro:</span>
              <select id="filtro-ciclos-viveiro" onchange="filtrarModuloCiclos()" class="bg-white text-xs font-bold py-1.5 px-3 rounded-lg border border-slate-200 text-slate-800 focus:outline-none focus:ring-2 focus:ring-cyan-500">
                <option value="TODOS">Todos os 15 Viveiros</option>
                <option value="V-01">V-01 • Viveiro 1</option>
                <option value="V-02">V-02 • Viveiro 2</option>
                <option value="V-03">V-03 • Viveiro 3</option>
                <option value="V-04">V-04 • Viveiro 4</option>
                <option value="V-05">V-05 • Viveiro 5</option>
                <option value="V-06">V-06 • Viveiro 6</option>
                <option value="V-07">V-07 • Viveiro 7</option>
                <option value="V-08">V-08 • Viveiro 8</option>
                <option value="V-09">V-09 • Viveiro 9</option>
                <option value="V-10">V-10 • Viveiro 10</option>
                <option value="V-11">V-11 • Viveiro 11</option>
                <option value="V-12">V-12 • Viveiro 12</option>
                <option value="V-13">V-13 • Viveiro 13</option>
                <option value="V-14">V-14 • Viveiro 14</option>
                <option value="V-15">V-15 • Viveiro 15</option>
              </select>
            </div>

            <!-- Botões de Ação Rápida -->
            <button onclick="abrirModalNovoCiclo()" class="px-3.5 py-2 rounded-xl bg-cyan-700 hover:bg-cyan-800 text-white font-bold text-xs transition flex items-center gap-1.5 shadow-sm">
              <i class="fa-solid fa-plus-circle"></i> Iniciar Novo Ciclo
            </button>
            <button onclick="document.getElementById('input-upload-excel-biomassa').click()" class="px-3.5 py-2 rounded-xl bg-white hover:bg-slate-100 text-slate-700 border border-slate-300 font-bold text-xs transition flex items-center gap-1.5 shadow-sm">
              <i class="fa-solid fa-file-excel text-emerald-600"></i> Importar Planilha
            </button>
          </div>
        </div>

        <!-- Seletor de Abas: Ciclos Ativos vs Histórico Permanente -->
        <div class="flex items-center gap-2 border-b border-slate-200 pb-2">
          <button id="btn-tab-ciclos-ativos" onclick="alternarAbaCiclos('ativos')" class="px-4 py-2 rounded-xl text-xs font-extrabold bg-slate-900 text-white shadow-sm transition flex items-center gap-2">
            <i class="fa-solid fa-water text-cyan-400"></i> Ciclos Ativos em Cultivo
            <span id="badge-ciclos-ativos-count" class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-cyan-400/20 text-cyan-200">10</span>
          </button>
          <button id="btn-tab-ciclos-historico" onclick="alternarAbaCiclos('historico')" class="px-4 py-2 rounded-xl text-xs font-semibold bg-slate-100 text-slate-600 hover:bg-slate-200 border border-slate-200 transition flex items-center gap-2">
            <i class="fa-solid fa-book-bookmark text-indigo-500"></i> Histórico Permanente de Ciclos
            <span id="badge-ciclos-historico-count" class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-slate-200 text-slate-700">3</span>
          </button>
        </div>

        <!-- ======================================================== -->
        <!-- ABA 1: CICLOS ATIVOS EM CULTIVO                         -->
        <!-- ======================================================== -->
        <div id="painel-ciclos-ativos" class="space-y-6">
          
          <!-- Cards de KPIs Consolidados dos Ciclos Ativos -->
          <div class="grid grid-cols-2 md:grid-cols-5 gap-3.5">
            <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm space-y-1">
              <span class="text-[11px] font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
                <i class="fa-solid fa-water text-cyan-500"></i> Tanques em Cultivo
              </span>
              <div class="text-2xl font-black text-cyan-950 font-mono" id="kpi-ciclos-ativos-count">10 viveiros</div>
              <div class="text-[10px] text-cyan-700 font-semibold" id="kpi-ciclos-ocupacao-pct">66.7% de ocupação</div>
            </div>

            <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm space-y-1">
              <span class="text-[11px] font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
                <i class="fa-solid fa-shrimp text-blue-500"></i> Biomassa Viva Estimada
              </span>
              <div class="text-2xl font-black text-blue-950 font-mono" id="kpi-ciclos-biomassa-total">34.200 kg</div>
              <div class="text-[10px] text-blue-700 font-semibold">Total ativo na água</div>
            </div>

            <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm space-y-1">
              <span class="text-[11px] font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
                <i class="fa-solid fa-wheat-awn text-amber-500"></i> Ração Consumida
              </span>
              <div class="text-2xl font-black text-amber-950 font-mono" id="kpi-ciclos-racao-total">42.150 kg</div>
              <div class="text-[10px] text-amber-700 font-semibold">Consumo acumulado safra</div>
            </div>

            <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm space-y-1">
              <span class="text-[11px] font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
                <i class="fa-solid fa-scale-balanced text-emerald-500"></i> FCA Parcial Médio
              </span>
              <div class="text-2xl font-black text-emerald-950 font-mono" id="kpi-ciclos-fca-medio">1.23</div>
              <div class="text-[10px] text-emerald-700 font-semibold">Faixa ideal zootécnica</div>
            </div>

            <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm space-y-1">
              <span class="text-[11px] font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
                <i class="fa-solid fa-broom text-slate-400"></i> Em Preparação / Vazio
              </span>
              <div class="text-2xl font-black text-slate-800 font-mono" id="kpi-ciclos-preparacao-count">5 viveiros</div>
              <div class="text-[10px] text-slate-500 font-semibold">Prontos para povoamento</div>
            </div>
          </div>

          <!-- Grid dos 15 Viveiros (Ciclos Ativos) -->
          <div id="grid-ciclos-ativos" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            <!-- Populado dinamicamente via renderizarCiclosAtivos() -->
          </div>
        </div>

        <!-- ======================================================== -->
        <!-- ABA 2: HISTÓRICO PERMANENTE DE CICLOS                   -->
        <!-- ======================================================== -->
        <div id="painel-ciclos-historico" class="hidden space-y-6">
          
          <!-- Cards de KPIs Consolidados do Histórico Permanente -->
          <div class="grid grid-cols-2 md:grid-cols-5 gap-3.5">
            <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm space-y-1">
              <span class="text-[11px] font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
                <i class="fa-solid fa-flag-checkered text-indigo-500"></i> Safras Encerradas
              </span>
              <div class="text-2xl font-black text-indigo-950 font-mono" id="kpi-hist-ciclos-count">3 safras</div>
              <div class="text-[10px] text-indigo-700 font-semibold">Arquivadas permanentemente</div>
            </div>

            <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm space-y-1">
              <span class="text-[11px] font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
                <i class="fa-solid fa-truck-ramp-box text-emerald-500"></i> Biomassa Colhida
              </span>
              <div class="text-2xl font-black text-emerald-950 font-mono" id="kpi-hist-biomassa-total">1.363 kg</div>
              <div class="text-[10px] text-emerald-700 font-semibold">Total líquido despescado</div>
            </div>

            <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm space-y-1">
              <span class="text-[11px] font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
                <i class="fa-solid fa-scale-balanced text-teal-500"></i> FCA Final Ponderado
              </span>
              <div class="text-2xl font-black text-teal-950 font-mono" id="kpi-hist-fca-medio">1.21</div>
              <div class="text-[10px] text-teal-700 font-semibold">Eficiência global do lote</div>
            </div>

            <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm space-y-1">
              <span class="text-[11px] font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
                <i class="fa-solid fa-percent text-blue-500"></i> Sobrevivência Real
              </span>
              <div class="text-2xl font-black text-blue-950 font-mono" id="kpi-hist-sob-media">72.4%</div>
              <div class="text-[10px] text-blue-700 font-semibold">Média apurada na colheita</div>
            </div>

            <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm space-y-1">
              <span class="text-[11px] font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
                <i class="fa-solid fa-sack-dollar text-emerald-600"></i> Receita Bruta Total
              </span>
              <div class="text-2xl font-black text-emerald-900 font-mono" id="kpi-hist-faturamento-total">R$ 31.172</div>
              <div class="text-[10px] text-emerald-700 font-semibold">Faturamento comercial</div>
            </div>
          </div>

          <!-- Tabela Executiva do Histórico de Ciclos -->
          <div class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
            <div class="p-4 bg-slate-50 border-b border-slate-200 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
              <div class="flex items-center space-x-2">
                <i class="fa-solid fa-book-bookmark text-indigo-600 text-sm"></i>
                <h3 class="text-xs font-extrabold text-slate-800 uppercase tracking-wider">Histórico de Safras Concluídas (Base Imutável)</h3>
              </div>
              <div class="text-xs text-slate-500">
                <span id="historico-tabela-contador" class="font-bold text-slate-700">3 safras registradas</span>
              </div>
            </div>

            <div class="overflow-x-auto">
              <table class="w-full text-left text-xs">
                <thead class="bg-slate-100/80 text-slate-600 uppercase text-[10px] font-bold tracking-wider border-b border-slate-200">
                  <tr>
                    <th class="py-3 px-3">Viveiro</th>
                    <th class="py-3 px-3">Código do Ciclo</th>
                    <th class="py-3 px-3">Período (Início &rarr; Fim)</th>
                    <th class="py-3 px-3 text-center">DOC</th>
                    <th class="py-3 px-3">Origem & PLs</th>
                    <th class="py-3 px-3 text-right">Desbastes</th>
                    <th class="py-3 px-3 text-right">Total Colhido</th>
                    <th class="py-3 px-3 text-right">Peso Final</th>
                    <th class="py-3 px-3 text-center">FCA Final</th>
                    <th class="py-3 px-3 text-center">Sobrev. Real</th>
                    <th class="py-3 px-3 text-right">Receita Bruta</th>
                    <th class="py-3 px-3">Comprador</th>
                    <th class="py-3 px-3 text-center">Ações</th>
                  </tr>
                </thead>
                <tbody id="tbody-historico-ciclos" class="divide-y divide-slate-100">
                  <!-- Populado dinamicamente via renderizarHistoricoCiclos() -->
                </tbody>
              </table>
            </div>
          </div>
        </div>

      </section>

      """
        content = content[:idx_view] + html_view_ciclos + content[idx_view:]
        print("✅ 2. Seção #view-analytics-ciclos inserida com sucesso.")
    else:
        print("❌ Falha ao encontrar ponto de inserção para view-analytics-ciclos.")
else:
    print("ℹ️ 2. Seção #view-analytics-ciclos já presente.")


# ==============================================================================
# 3. BIOMETRIA: Adicionar banner de preparação de solo no container de detalhe
# ==============================================================================
target_bio_detalhe = '<div id="container-biomassa-viveiro-detalhe" class="hidden space-y-6">'
if 'id="detail-bio-banner-preparacao"' not in content:
    idx_bio = content.find(target_bio_detalhe)
    if idx_bio != -1:
        idx_after_div = idx_bio + len(target_bio_detalhe)
        banner_preparacao_html = """
          
          <!-- Banner Elegante de Viveiro em Preparação de Solo (Reset Limpo) -->
          <div id="detail-bio-banner-preparacao" class="hidden p-5 rounded-3xl bg-amber-50/90 border-2 border-dashed border-amber-300 text-slate-800 shadow-sm">
            <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
              <div class="flex items-center space-x-3.5">
                <div class="p-3.5 bg-amber-200 text-amber-900 rounded-2xl text-xl font-black">
                  <i class="fa-solid fa-seedling"></i>
                </div>
                <div class="space-y-0.5">
                  <h4 class="font-extrabold text-slate-900 text-sm flex items-center gap-2">
                    <span>⚪ Viveiro em Preparação de Solo / Vazio Sanitário</span>
                    <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-200 text-amber-900 font-mono">DOC 0</span>
                  </h4>
                  <p class="text-xs text-slate-600">
                    Ciclo de cultivo anterior encerrado com sucesso. Tanque drenado para desinfecção, secagem e calagem.
                  </p>
                </div>
              </div>
              <div class="flex flex-wrap items-center gap-2">
                <button onclick="abrirModalNovoCiclo(selectedViveiroIdBiomassa)" class="px-4 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs transition flex items-center gap-1.5 shadow-sm">
                  <i class="fa-solid fa-plus-circle"></i> Iniciar Novo Ciclo (Povoamento)
                </button>
                <button onclick="document.getElementById('input-upload-excel-biomassa').click()" class="px-4 py-2.5 rounded-xl bg-white hover:bg-slate-100 text-slate-700 border border-slate-300 font-bold text-xs transition flex items-center gap-1.5 shadow-sm">
                  <i class="fa-solid fa-file-excel text-emerald-600"></i> Importar Planilha do Próximo Lote
                </button>
              </div>
            </div>
          </div>"""
        content = content[:idx_after_div] + banner_preparacao_html + content[idx_after_div:]
        print("✅ 3. Banner de Preparação de Solo inserido na view de biometria.")
    else:
        print("❌ Falha ao encontrar container-biomassa-viveiro-detalhe.")
else:
    print("ℹ️ 3. Banner de Preparação de Solo já presente na biometria.")


# ==============================================================================
# 4. MODAIS: Adicionar Modais de Ciclos (Novo Ciclo, Despesca Parcial, Encerramento e Dossiê)
# ==============================================================================
target_modal_pos = '<div id="modal-calibrar-parametro"'
if 'id="modal-encerramento-ciclo"' not in content:
    idx_m = content.find(target_modal_pos)
    if idx_m != -1:
        modais_ciclos_html = """
  <!-- ======================================================== -->
  <!-- MODAL: INICIAR NOVO CICLO DE CULTIVO (POVOAMENTO)        -->
  <!-- ======================================================== -->
  <div id="modal-iniciar-novo-ciclo" class="hidden fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
    <div class="bg-white rounded-3xl max-w-lg w-full shadow-2xl border border-slate-200 overflow-hidden">
      <div class="bg-cyan-900 p-4 text-white flex items-center justify-between">
        <div class="flex items-center space-x-2.5">
          <div class="p-2 bg-cyan-700/60 rounded-xl">
            <i class="fa-solid fa-seedling text-white"></i>
          </div>
          <div>
            <h3 class="text-sm font-extrabold">Iniciar Novo Ciclo de Produção</h3>
            <p class="text-[10px] text-cyan-200">Gera numeração sequencial oficial e prepara o viveiro para novo lote</p>
          </div>
        </div>
        <button onclick="fecharModalNovoCiclo()" class="text-cyan-200 hover:text-white text-lg">
          <i class="fa-solid fa-xmark"></i>
        </button>
      </div>

      <form id="form-iniciar-novo-ciclo" onsubmit="salvarNovoCiclo(event)" class="p-5 space-y-4 text-xs">
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block font-bold text-slate-700 mb-1">Viveiro / Tanque:</label>
            <select id="modal-novo-ciclo-viv-id" onchange="atualizarPreviaCodigoCiclo()" class="w-full text-xs font-bold p-2.5 rounded-xl border border-slate-300 bg-white" required>
              <!-- Populado via JS -->
            </select>
          </div>
          <div>
            <label class="block font-bold text-slate-700 mb-1">Ano-Safra:</label>
            <input type="number" id="modal-novo-ciclo-ano" value="2026" onchange="atualizarPreviaCodigoCiclo()" class="w-full text-xs font-bold p-2.5 rounded-xl border border-slate-300 bg-white" required>
          </div>
        </div>

        <div class="p-3 rounded-2xl bg-cyan-50 border border-cyan-200 space-y-1">
          <span class="text-[10px] font-bold text-cyan-900 uppercase">Código Oficial Previsto:</span>
          <div id="modal-novo-ciclo-codigo-preview" class="text-sm font-black text-cyan-950 font-mono">V-01 • Ciclo 2026.2</div>
          <p class="text-[10px] text-cyan-700">Calculado automaticamente com base nas safras passadas deste viveiro.</p>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block font-bold text-slate-700 mb-1">Data de Povoamento:</label>
            <input type="date" id="modal-novo-ciclo-data" class="w-full text-xs font-bold p-2.5 rounded-xl border border-slate-300 bg-white" required>
          </div>
          <div>
            <label class="block font-bold text-slate-700 mb-1">Qtd. PLs (em milheiros):</label>
            <input type="number" step="1" id="modal-novo-ciclo-pls" placeholder="ex: 60" value="60" class="w-full text-xs font-mono font-bold p-2.5 rounded-xl border border-slate-300 bg-white" required>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block font-bold text-slate-700 mb-1">Laboratório Fornecedor:</label>
            <select id="modal-novo-ciclo-lab" class="w-full text-xs font-bold p-2.5 rounded-xl border border-slate-300 bg-white">
              <option value="AQUATEC">AQUATEC</option>
              <option value="NE">NE</option>
              <option value="TECMARIS">TECMARIS</option>
              <option value="ALEVIBRAS">ALEVIBRAS</option>
            </select>
          </div>
          <div>
            <label class="block font-bold text-slate-700 mb-1">Peso Inicial Médio (g):</label>
            <input type="number" step="0.001" id="modal-novo-ciclo-peso" value="0.01" class="w-full text-xs font-mono font-bold p-2.5 rounded-xl border border-slate-300 bg-white" required>
          </div>
        </div>

        <div class="p-3 rounded-2xl bg-slate-50 border border-slate-200 space-y-2">
          <label class="flex items-center space-x-2 cursor-pointer">
            <input type="checkbox" id="modal-novo-ciclo-tem-bercario" onchange="document.getElementById('bloco-campos-bercario').classList.toggle('hidden', !this.checked)" class="rounded text-cyan-600 focus:ring-cyan-500">
            <span class="font-bold text-slate-800 text-xs">🐣 Este lote passou por Berçário Intensivo</span>
          </label>
          <div id="bloco-campos-bercario" class="hidden grid grid-cols-2 gap-2 pt-1 border-t border-slate-200">
            <div>
              <span class="text-[10px] text-slate-500 font-semibold block">Data Transferência:</span>
              <input type="date" id="modal-novo-ciclo-dt-transf" class="w-full text-[11px] p-1.5 rounded-lg border border-slate-300 bg-white">
            </div>
            <div>
              <span class="text-[10px] text-slate-500 font-semibold block">Peso Médio Saída (g):</span>
              <input type="number" step="0.1" id="modal-novo-ciclo-peso-transf" placeholder="ex: 2.0" class="w-full text-[11px] p-1.5 rounded-lg border border-slate-300 bg-white font-mono">
            </div>
          </div>
        </div>

        <div>
          <label class="block font-bold text-slate-700 mb-1">Observações de Início de Ciclo:</label>
          <input type="text" id="modal-novo-ciclo-obs" placeholder="ex: Povoamento realizado pela manhã com aclimatação de 2 horas..." class="w-full text-xs p-2.5 rounded-xl border border-slate-300 bg-white">
        </div>

        <div class="flex items-center justify-end space-x-2 pt-3 border-t border-slate-100">
          <button type="button" onclick="fecharModalNovoCiclo()" class="px-4 py-2 rounded-xl text-slate-600 hover:bg-slate-100 font-bold transition">
            Cancelar
          </button>
          <button type="submit" class="px-5 py-2 rounded-xl bg-cyan-700 hover:bg-cyan-800 text-white font-bold transition flex items-center gap-1.5 shadow-sm">
            <i class="fa-solid fa-check"></i> Iniciar Ciclo Oficial
          </button>
        </div>
      </form>
    </div>
  </div>


  <!-- ======================================================== -->
  <!-- MODAL: REGISTRAR DESPESCA PARCIAL (DESBASTE / RALEIO)    -->
  <!-- ======================================================== -->
  <div id="modal-despesca-parcial-ciclo" class="hidden fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
    <div class="bg-white rounded-3xl max-w-lg w-full shadow-2xl border border-slate-200 overflow-hidden">
      <div class="bg-amber-900 p-4 text-white flex items-center justify-between">
        <div class="flex items-center space-x-2.5">
          <div class="p-2 bg-amber-700/60 rounded-xl">
            <i class="fa-solid fa-scale-balanced text-white"></i>
          </div>
          <div>
            <h3 class="text-sm font-extrabold">Registrar Despesca Parcial (Desbaste)</h3>
            <p class="text-[10px] text-amber-200">Abate biomassa viva da água mantendo o ciclo de cultivo ativo</p>
          </div>
        </div>
        <button onclick="fecharModalDespescaParcial()" class="text-amber-200 hover:text-white text-lg">
          <i class="fa-solid fa-xmark"></i>
        </button>
      </div>

      <form id="form-despesca-parcial" onsubmit="salvarDespescaParcial(event)" class="p-5 space-y-4 text-xs">
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block font-bold text-slate-700 mb-1">Viveiro:</label>
            <input type="text" id="modal-parcial-viv-id" class="w-full text-xs font-bold p-2.5 rounded-xl border border-slate-200 bg-slate-100 text-slate-700" readonly>
          </div>
          <div>
            <label class="block font-bold text-slate-700 mb-1">Ciclo Ativo:</label>
            <input type="text" id="modal-parcial-codigo-ciclo" class="w-full text-xs font-bold p-2.5 rounded-xl border border-slate-200 bg-slate-100 text-slate-700" readonly>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block font-bold text-slate-700 mb-1">Data do Desbaste:</label>
            <input type="date" id="modal-parcial-data" class="w-full text-xs font-bold p-2.5 rounded-xl border border-slate-300 bg-white" required>
          </div>
          <div>
            <label class="block font-bold text-slate-700 mb-1">Camarão Colhido (kg):</label>
            <input type="number" step="1" id="modal-parcial-kg" placeholder="ex: 250" oninput="atualizarPreviaDespescaParcial()" class="w-full text-xs font-mono font-bold p-2.5 rounded-xl border border-slate-300 bg-white" required>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block font-bold text-slate-700 mb-1">Gramatura Média (g):</label>
            <input type="number" step="0.1" id="modal-parcial-peso" placeholder="ex: 11.5" class="w-full text-xs font-mono font-bold p-2.5 rounded-xl border border-slate-300 bg-white" required>
          </div>
          <div>
            <label class="block font-bold text-slate-700 mb-1">Preço Venda (R$/kg):</label>
            <input type="number" step="0.5" id="modal-parcial-preco" value="22.0" oninput="atualizarPreviaDespescaParcial()" class="w-full text-xs font-mono font-bold p-2.5 rounded-xl border border-slate-300 bg-white" required>
          </div>
        </div>

        <div class="p-3 rounded-2xl bg-amber-50 border border-amber-200 flex items-center justify-between">
          <span class="text-xs font-bold text-amber-900">Receita Estimada do Desbaste:</span>
          <span id="modal-parcial-faturamento-preview" class="text-sm font-black text-amber-950 font-mono">R$ 0,00</span>
        </div>

        <div>
          <label class="block font-bold text-slate-700 mb-1">Comprador / Destino:</label>
          <input type="text" id="modal-parcial-comprador" placeholder="ex: Restaurantes de Natal / Peixaria" class="w-full text-xs p-2.5 rounded-xl border border-slate-300 bg-white">
        </div>

        <div>
          <label class="block font-bold text-slate-700 mb-1">Observações do Desbaste:</label>
          <input type="text" id="modal-parcial-obs" placeholder="ex: Raleio de 30% da densidade para acelerar ganho de peso final..." class="w-full text-xs p-2.5 rounded-xl border border-slate-300 bg-white">
        </div>

        <div class="flex items-center justify-end space-x-2 pt-3 border-t border-slate-100">
          <button type="button" onclick="fecharModalDespescaParcial()" class="px-4 py-2 rounded-xl text-slate-600 hover:bg-slate-100 font-bold transition">
            Cancelar
          </button>
          <button type="submit" class="px-5 py-2 rounded-xl bg-amber-600 hover:bg-amber-700 text-white font-bold transition flex items-center gap-1.5 shadow-sm">
            <i class="fa-solid fa-check"></i> Confirmar Despesca Parcial
          </button>
        </div>
      </form>
    </div>
  </div>


  <!-- ======================================================== -->
  <!-- MODAL: ENCERRAMENTO EXECUTIVO DE CICLO & RESET LIMPO      -->
  <!-- ======================================================== -->
  <div id="modal-encerramento-ciclo" class="hidden fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/70 backdrop-blur-sm">
    <div class="bg-white rounded-3xl max-w-xl w-full shadow-2xl border border-slate-200 overflow-hidden max-h-[92vh] flex flex-col">
      <div class="bg-slate-900 p-4 text-white flex items-center justify-between">
        <div class="flex items-center space-x-2.5">
          <div class="p-2 bg-red-600 rounded-xl">
            <i class="fa-solid fa-flag-checkered text-white"></i>
          </div>
          <div>
            <h3 class="text-sm font-extrabold">Encerramento Definitivo de Ciclo de Cultivo</h3>
            <p class="text-[10px] text-slate-300">Consolida despescas, calcula FCA final, arquiva histórico e reinicia viveiro limpo</p>
          </div>
        </div>
        <button onclick="fecharModalEncerramentoCiclo()" class="text-slate-400 hover:text-white text-lg">
          <i class="fa-solid fa-xmark"></i>
        </button>
      </div>

      <form id="form-encerramento-ciclo" onsubmit="confirmarEncerramentoCiclo(event)" class="p-5 space-y-4 text-xs overflow-y-auto">
        <!-- Sumário do Lote que será encerrado -->
        <div class="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-2">
          <div class="flex items-center justify-between">
            <span class="text-xs font-extrabold text-slate-900" id="modal-encerrar-titulo-lote">V-01 • Ciclo 2026.1</span>
            <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-800">Em Encerramento</span>
          </div>
          <div class="grid grid-cols-3 gap-2 text-[11px] text-slate-600 pt-1">
            <div>Povoamento: <strong id="modal-encerrar-res-pov" class="text-slate-900 block">-</strong></div>
            <div>DOC Atual: <strong id="modal-encerrar-res-doc" class="text-slate-900 block">-</strong></div>
            <div>PLs Estocadas: <strong id="modal-encerrar-res-pls" class="text-slate-900 block">-</strong></div>
          </div>
          <div class="grid grid-cols-2 gap-2 text-[11px] text-slate-600 pt-1 border-t border-slate-200">
            <div>Ração Acumulada: <strong id="modal-encerrar-res-racao" class="text-slate-900 block font-mono">0 kg</strong></div>
            <div>Desbastes Prévia: <strong id="modal-encerrar-res-desbastes" class="text-amber-800 block font-mono">0 kg</strong></div>
          </div>
        </div>

        <!-- Inputs da Colheita Final -->
        <div class="p-4 rounded-2xl bg-indigo-50/70 border border-indigo-200 space-y-3">
          <span class="text-xs font-extrabold text-indigo-950 flex items-center gap-1.5">
            <i class="fa-solid fa-truck-ramp-box text-indigo-600"></i> Despesca Final (Colheita de Esgotamento):
          </span>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-[10px] font-bold text-indigo-900 mb-0.5">Data da Despesca Final:</label>
              <input type="date" id="modal-encerrar-data" class="w-full text-xs font-bold p-2 rounded-xl border border-indigo-300 bg-white" required>
            </div>
            <div>
              <label class="block text-[10px] font-bold text-indigo-900 mb-0.5">Colhido Nesta Despesca Final (kg):</label>
              <input type="number" step="1" id="modal-encerrar-kg" placeholder="ex: 450" oninput="atualizarPreviaEncerramentoCiclo()" class="w-full text-xs font-mono font-bold p-2 rounded-xl border border-indigo-300 bg-white" required>
            </div>
          </div>
          <div class="grid grid-cols-3 gap-3">
            <div>
              <label class="block text-[10px] font-bold text-indigo-900 mb-0.5">Gramatura / Peso Final (g):</label>
              <input type="number" step="0.1" id="modal-encerrar-peso" placeholder="ex: 14.5" oninput="atualizarPreviaEncerramentoCiclo()" class="w-full text-xs font-mono font-bold p-2 rounded-xl border border-indigo-300 bg-white" required>
            </div>
            <div>
              <label class="block text-[10px] font-bold text-indigo-900 mb-0.5">Preço Venda (R$/kg):</label>
              <input type="number" step="0.5" id="modal-encerrar-preco" value="22.0" oninput="atualizarPreviaEncerramentoCiclo()" class="w-full text-xs font-mono font-bold p-2 rounded-xl border border-indigo-300 bg-white" required>
            </div>
            <div>
              <label class="block text-[10px] font-bold text-indigo-900 mb-0.5">Comprador:</label>
              <input type="text" id="modal-encerrar-comprador" placeholder="ex: Distribuidora" class="w-full text-xs font-semibold p-2 rounded-xl border border-indigo-300 bg-white">
            </div>
          </div>
        </div>

        <!-- Painel de Indicadores Consolidados Finais (Calculados em Tempo Real) -->
        <div class="p-4 rounded-2xl bg-emerald-50/80 border border-emerald-200 space-y-2.5">
          <span class="text-xs font-extrabold text-emerald-950 flex items-center gap-1.5">
            <i class="fa-solid fa-chart-line text-emerald-600"></i> Métricas Consolidadas do Ciclo Completo:
          </span>
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 text-center">
            <div class="bg-white p-2.5 rounded-xl border border-emerald-100 shadow-sm">
              <span class="text-[9px] font-bold text-slate-500 uppercase block">Total Colhido</span>
              <strong id="modal-encerrar-calc-total-kg" class="text-sm font-black text-slate-900 font-mono">0 kg</strong>
              <span class="text-[9px] text-slate-400 block">(Parciais + Final)</span>
            </div>
            <div class="bg-white p-2.5 rounded-xl border border-emerald-100 shadow-sm">
              <span class="text-[9px] font-bold text-slate-500 uppercase block">FCA Final Real</span>
              <strong id="modal-encerrar-calc-fca" class="text-sm font-black text-teal-800 font-mono">1.25</strong>
              <span class="text-[9px] text-slate-400 block">Ração / kg Colhido</span>
            </div>
            <div class="bg-white p-2.5 rounded-xl border border-emerald-100 shadow-sm">
              <span class="text-[9px] font-bold text-slate-500 uppercase block">Sobrevivência</span>
              <strong id="modal-encerrar-calc-sob" class="text-sm font-black text-blue-800 font-mono">75.0%</strong>
              <span class="text-[9px] text-slate-400 block">Efetiva Real</span>
            </div>
            <div class="bg-white p-2.5 rounded-xl border border-emerald-100 shadow-sm">
              <span class="text-[9px] font-bold text-slate-500 uppercase block">Receita Bruta</span>
              <strong id="modal-encerrar-calc-fat" class="text-sm font-black text-emerald-800 font-mono">R$ 0</strong>
              <span class="text-[9px] text-slate-400 block">Total Faturado</span>
            </div>
          </div>
        </div>

        <div>
          <label class="block font-bold text-slate-700 mb-1">Observações de Fechamento:</label>
          <input type="text" id="modal-encerrar-obs" placeholder="ex: Despesca total concluída sem ocorrências; tanque drenado para calagem..." class="w-full text-xs p-2.5 rounded-xl border border-slate-300 bg-white">
        </div>

        <!-- Alerta do Reset Limpo -->
        <div class="p-3 rounded-2xl bg-blue-50 border border-blue-200 text-blue-900 text-[11px] flex items-start space-x-2">
          <i class="fa-solid fa-circle-info text-blue-600 mt-0.5"></i>
          <p>
            <strong>Ação de Reset Limpo:</strong> Ao confirmar, o ciclo será arquivado na aba de Histórico Permanente e o viveiro ativo nos módulos de <em>Biometria</em> e <em>Alimentação</em> será reinicializado com status <strong>⚪ Em Preparação</strong> (DOC 0, Biomassa 0 kg, Ração 0 kg) pronto para a próxima produção.
          </p>
        </div>

        <div class="flex items-center justify-end space-x-2 pt-3 border-t border-slate-100">
          <button type="button" onclick="fecharModalEncerramentoCiclo()" class="px-4 py-2 rounded-xl text-slate-600 hover:bg-slate-100 font-bold transition">
            Cancelar
          </button>
          <button type="submit" class="px-5 py-2.5 rounded-xl bg-red-600 hover:bg-red-700 text-white font-extrabold transition flex items-center gap-1.5 shadow-sm">
            <i class="fa-solid fa-flag-checkered"></i> Encerrar Ciclo & Liberar Viveiro
          </button>
        </div>
      </form>
    </div>
  </div>


  <!-- ======================================================== -->
  <!-- MODAL: DOSSIÊ DO CICLO CONCLUÍDO (HISTÓRICO PERMANENTE)  -->
  <!-- ======================================================== -->
  <div id="modal-dossie-ciclo" class="hidden fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
    <div class="bg-white rounded-3xl max-w-lg w-full shadow-2xl border border-slate-200 overflow-hidden">
      <div class="bg-slate-900 p-4 text-white flex items-center justify-between">
        <div class="flex items-center space-x-2.5">
          <div class="p-2 bg-indigo-600 rounded-xl">
            <i class="fa-solid fa-file-contract text-white"></i>
          </div>
          <div>
            <h3 class="text-sm font-extrabold" id="modal-dossie-titulo">Dossiê do Ciclo de Cultivo</h3>
            <p class="text-[10px] text-slate-300" id="modal-dossie-sub">Resumo executivo completo da safra arquivada</p>
          </div>
        </div>
        <button onclick="fecharDossieCiclo()" class="text-slate-400 hover:text-white text-lg">
          <i class="fa-solid fa-xmark"></i>
        </button>
      </div>

      <div class="p-5 space-y-4 text-xs">
        <div class="grid grid-cols-2 gap-3 text-slate-700">
          <div class="p-3 rounded-xl bg-slate-50 border border-slate-200">
            <span class="text-[10px] text-slate-400 font-bold block uppercase">Período de Cultivo</span>
            <strong id="modal-dossie-periodo" class="text-slate-900 block text-xs mt-0.5">-</strong>
            <span id="modal-dossie-ddc" class="text-[10px] text-slate-500 block">-</span>
          </div>
          <div class="p-3 rounded-xl bg-slate-50 border border-slate-200">
            <span class="text-[10px] text-slate-400 font-bold block uppercase">Povoamento</span>
            <strong id="modal-dossie-lab-pls" class="text-slate-900 block text-xs mt-0.5">-</strong>
            <span id="modal-dossie-densidade" class="text-[10px] text-slate-500 block">-</span>
          </div>
        </div>

        <div class="p-4 rounded-2xl bg-indigo-50/70 border border-indigo-200 space-y-2">
          <span class="text-xs font-bold text-indigo-950 uppercase tracking-wider block">Resultados Finais da Colheita</span>
          <div class="grid grid-cols-3 gap-2 text-center">
            <div class="bg-white p-2 rounded-xl border border-indigo-100 shadow-sm">
              <span class="text-[9px] text-slate-500 font-bold block">COLHIDO TOTAL</span>
              <strong id="modal-dossie-colhido" class="text-xs font-black text-slate-900 font-mono block mt-0.5">-</strong>
            </div>
            <div class="bg-white p-2 rounded-xl border border-indigo-100 shadow-sm">
              <span class="text-[9px] text-slate-500 font-bold block">FCA FINAL</span>
              <strong id="modal-dossie-fca" class="text-xs font-black text-teal-800 font-mono block mt-0.5">-</strong>
            </div>
            <div class="bg-white p-2 rounded-xl border border-indigo-100 shadow-sm">
              <span class="text-[9px] text-slate-500 font-bold block">SOBREVIVÊNCIA</span>
              <strong id="modal-dossie-sob" class="text-xs font-black text-blue-800 font-mono block mt-0.5">-</strong>
            </div>
          </div>
        </div>

        <div class="p-4 rounded-2xl bg-emerald-50/70 border border-emerald-200 flex items-center justify-between">
          <div>
            <span class="text-[10px] text-emerald-800 font-bold uppercase block">Faturamento Bruto</span>
            <strong id="modal-dossie-faturamento" class="text-base font-black text-emerald-950 font-mono block">R$ 0,00</strong>
            <span id="modal-dossie-comprador" class="text-[10px] text-emerald-700 block">Comprador: -</span>
          </div>
          <div class="text-right">
            <span class="text-[10px] text-slate-500 font-semibold block">Preço Realizado:</span>
            <span id="modal-dossie-preco" class="text-xs font-extrabold text-slate-800 font-mono block">R$ 22,00/kg</span>
          </div>
        </div>

        <div class="p-3 rounded-xl bg-slate-50 border border-slate-200 text-slate-700">
          <span class="text-[10px] text-slate-400 font-bold uppercase block">Anotações do Ciclo:</span>
          <p id="modal-dossie-obs" class="text-xs text-slate-600 mt-0.5 italic">-</p>
        </div>

        <div class="flex items-center justify-end space-x-2 pt-2 border-t border-slate-100">
          <button type="button" onclick="fecharDossieCiclo()" class="px-5 py-2 rounded-xl bg-slate-800 hover:bg-slate-900 text-white font-bold transition">
            Fechar Dossiê
          </button>
        </div>
      </div>
    </div>
  </div>
"""
        content = content[:idx_m] + modais_ciclos_html + content[idx_m:]
        print("✅ 4. Modais de Ciclos inseridos com sucesso.")
    else:
        print("❌ Falha ao encontrar ponto de inserção para os modais de ciclos.")
else:
    print("ℹ️ 4. Modais de ciclos já presentes.")


# ==============================================================================
# 5. JAVASCRIPT: Atualizar navegarPara, adicionar lógica de Ciclos e Reset Limpo
# ==============================================================================

# 5.1 Atualizar array views em navegarPara
if "'analytics-ciclos'" not in content:
    content = content.replace(
        "'analytics-biomassa',",
        "'analytics-ciclos',\n        'analytics-biomassa',"
    )
    print("✅ 5.1 'analytics-ciclos' adicionado à lista de views em navegarPara.")

# 5.2 Adicionar trigger em navegarPara
target_trigger = "if (viewId === 'analytics-equipe') {"
if "viewId === 'analytics-ciclos'" not in content:
    idx_trig = content.find(target_trigger)
    if idx_trig != -1:
        trigger_code = """if (viewId === 'analytics-ciclos') {
        atualizarHeaderNavegacao('Gestão de Ciclos de Produção & Safras', 'Início > Zootecnia > Ciclos de Produção');
        renderizarModuloCiclos();
      } else """
        content = content[:idx_trig] + trigger_code + content[idx_trig:]
        print("✅ 5.2 Trigger de 'analytics-ciclos' inserido em navegarPara.")
    else:
        print("❌ Falha ao encontrar trigger em navegarPara.")

# 5.3 Inserir o motor JavaScript de Ciclos de Produção antes do fechamento do script principal
target_script_end = "</script>\n\n  <!-- ======================================================== -->\n  <!-- MODAL: REGISTRAR NOVA DESPESCA"
if target_script_end not in content:
    # Procura por qualquer tag de modal próxima
    target_script_end = "<!-- MODAL: REGISTRAR NOVA DESPESCA"
    idx_sc = content.find(target_script_end)
    if idx_sc != -1:
        # Encontrar o </script> anterior
        idx_close = content.rfind("</script>", 0, idx_sc)
    else:
        idx_close = -1
else:
    idx_close = content.find(target_script_end)

if "function renderizarModuloCiclos" not in content and idx_close != -1:
    js_ciclos_code = """
    // =========================================================================
    // MOTOR DE GESTÃO DE CICLOS DE PRODUÇÃO, DESBASTES E RESET LIMPO (ZOOTECNIA)
    // =========================================================================
    let ABA_CICLOS_ATIVA = 'ativos';
    let FILTRO_ANO_CICLOS = '2026';
    let FILTRO_VIVEIRO_CICLOS = 'TODOS';
    let cicloEmEncerramentoVivId = null;

    // Estado local complementar de ciclos parciais em andamento
    window.CICLOS_DESBASTES_LOCAIS = window.CICLOS_DESBASTES_LOCAIS || {};

    function alternarAbaCiclos(aba) {
      ABA_CICLOS_ATIVA = aba;
      const btnAtivos = document.getElementById('btn-tab-ciclos-ativos');
      const btnHist = document.getElementById('btn-tab-ciclos-historico');
      const painelAtivos = document.getElementById('painel-ciclos-ativos');
      const painelHist = document.getElementById('painel-ciclos-historico');

      if (aba === 'ativos') {
        if (btnAtivos) btnAtivos.className = 'px-4 py-2 rounded-xl text-xs font-extrabold bg-slate-900 text-white shadow-sm transition flex items-center gap-2';
        if (btnHist) btnHist.className = 'px-4 py-2 rounded-xl text-xs font-semibold bg-slate-100 text-slate-600 hover:bg-slate-200 border border-slate-200 transition flex items-center gap-2';
        if (painelAtivos) painelAtivos.classList.remove('hidden');
        if (painelHist) painelHist.classList.add('hidden');
      } else {
        if (btnAtivos) btnAtivos.className = 'px-4 py-2 rounded-xl text-xs font-semibold bg-slate-100 text-slate-600 hover:bg-slate-200 border border-slate-200 transition flex items-center gap-2';
        if (btnHist) btnHist.className = 'px-4 py-2 rounded-xl text-xs font-extrabold bg-slate-900 text-white shadow-sm transition flex items-center gap-2';
        if (painelAtivos) painelAtivos.classList.add('hidden');
        if (painelHist) painelHist.classList.remove('hidden');
      }
      renderizarModuloCiclos();
    }

    function filtrarModuloCiclos() {
      const elAno = document.getElementById('filtro-ciclos-ano');
      const elViv = document.getElementById('filtro-ciclos-viveiro');
      if (elAno) FILTRO_ANO_CICLOS = elAno.value;
      if (elViv) FILTRO_VIVEIRO_CICLOS = elViv.value;
      renderizarModuloCiclos();
    }

    function obterProximoCicloSequencial(vivId, ano) {
      const anoNum = parseInt(ano, 10) || 2026;
      // Contar quantas safras encerradas existem para esse viveiro neste ano
      const concluidas = (HISTORICO_SAFRAS_DATA || []).filter(s => s.viveiroId === vivId && s.anoSafra === anoNum);
      const seq = concluidas.length + 1;
      return {
        seq: seq,
        codigo: `${vivId} • Ciclo ${anoNum}.${seq}`
      };
    }

    function renderizarModuloCiclos() {
      renderizarCiclosAtivos();
      renderizarHistoricoCiclos();
    }

    function renderizarCiclosAtivos() {
      const grid = document.getElementById('grid-ciclos-ativos');
      if (!grid) return;

      const anoFiltro = FILTRO_ANO_CICLOS;
      const vivFiltro = FILTRO_VIVEIRO_CICLOS;

      let totalAtivos = 0;
      let totalBiomassa = 0;
      let totalRacao = 0;
      let somaFca = 0;
      let countFca = 0;
      let totalPreparacao = 0;

      let cardsHtml = '';

      VIVEIROS_DATA.forEach(v => {
        if (vivFiltro !== 'TODOS' && v.id !== vivFiltro) return;

        const dados = DADOS_PLANILHA_VIVEIROS[v.id] || { tratos: [], pls: 50, lab: 'AQUATEC' };
        const tratos = dados.tratos || [];
        const isEmPreparacao = (dados.statusLote === 'EM_PREPARACAO' || v.status === 'vazio' || (!tratos.length && !dados.despesca));
        const isDespescado = (dados.statusLote === 'DESPESCADO');

        const desbastesKg = (window.CICLOS_DESBASTES_LOCAIS[v.id] || 0);

        if (isEmPreparacao) {
          totalPreparacao++;
        } else {
          totalAtivos++;
          totalBiomassa += (v.biomassaKg || 0);
          totalRacao += (v.racaoAcumuladaKg || 0);
          if (v.fca && v.fca > 0) {
            somaFca += v.fca;
            countFca++;
          }
        }

        // Nomenclatura oficial
        const infoSeq = obterProximoCicloSequencial(v.id, 2026);
        const codigoCiclo = dados.codigoCiclo || (isEmPreparacao ? `${v.id} • Preparação` : `${v.id} • Ciclo 2026.${Math.max(1, infoSeq.seq)}`);

        // Badge de Estágio
        let badgeEstagio = '';
        if (isEmPreparacao) {
          badgeEstagio = '<span class="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold bg-slate-100 text-slate-600 border border-slate-200 flex items-center gap-1">⚪ Em Preparação</span>';
        } else if (desbastesKg > 0) {
          badgeEstagio = '<span class="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold bg-amber-100 text-amber-900 border border-amber-300 flex items-center gap-1">🟡 Despesca Parcial Realizada</span>';
        } else if (dados.tem_bercario || (tratos.length && tratos[tratos.length - 1].doc <= 25)) {
          badgeEstagio = '<span class="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold bg-blue-100 text-blue-900 border border-blue-200 flex items-center gap-1">🐣 Berçário / Povoamento</span>';
        } else {
          badgeEstagio = '<span class="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold bg-emerald-100 text-emerald-900 border border-emerald-300 flex items-center gap-1">🟢 Engorda Ativa</span>';
        }

        const pesoG = v.pesoMedio || (tratos.length ? (tratos[tratos.length - 1].biometria || 0) : 0);
        const ddcVal = isEmPreparacao ? 0 : (tratos.length ? tratos[tratos.length - 1].doc : v.ddc || 0);
        const biomassaVal = isEmPreparacao ? 0 : (v.biomassaKg || 0);
        const racaoVal = isEmPreparacao ? 0 : (v.racaoAcumuladaKg || 0);
        const fcaVal = isEmPreparacao ? '-' : (v.fca || 1.25);
        const plsEstocadas = isEmPreparacao ? 0 : (dados.pls || 50) * 1000;
        const densidadeVal = isEmPreparacao ? 0 : (v.area_m2 > 0 ? (plsEstocadas / v.area_m2).toFixed(1) : 25);

        cardsHtml += `
          <div class="bg-white rounded-2xl border ${isEmPreparacao ? 'border-dashed border-slate-300 bg-slate-50/50' : 'border-slate-200'} p-4 shadow-sm space-y-3.5 hover:shadow-md transition">
            <div class="flex items-start justify-between gap-2">
              <div class="space-y-0.5">
                <div class="flex items-center gap-2">
                  <span class="px-2 py-0.5 rounded-lg bg-slate-900 text-white font-mono text-xs font-black">${v.id}</span>
                  <span class="text-xs font-black text-slate-800">${codigoCiclo}</span>
                </div>
                <div class="text-[11px] text-slate-500 font-medium">
                  ${v.nome} • Setor ${v.setor} • ${(v.area_ha || 0.50)} ha
                </div>
              </div>
              ${badgeEstagio}
            </div>

            <!-- Ficha Rápida do Povoamento -->
            <div class="p-2.5 rounded-xl bg-slate-50 border border-slate-200 grid grid-cols-3 gap-2 text-center text-[10px]">
              <div>
                <span class="text-slate-400 font-semibold block">DOC</span>
                <strong class="text-slate-900 font-mono text-xs block">${ddcVal} dias</strong>
              </div>
              <div>
                <span class="text-slate-400 font-semibold block">PLs / m²</span>
                <strong class="text-slate-900 font-mono text-xs block">${isEmPreparacao ? '-' : densidadeVal + ' PL/m²'}</strong>
              </div>
              <div>
                <span class="text-slate-400 font-semibold block">Origem</span>
                <strong class="text-slate-900 text-xs block truncate">${isEmPreparacao ? '-' : (dados.lab || 'AQUATEC')}</strong>
              </div>
            </div>

            <!-- Métricas Zootécnicas Ativas -->
            <div class="grid grid-cols-2 gap-2 text-xs">
              <div class="p-2 rounded-xl bg-blue-50/60 border border-blue-100">
                <span class="text-[10px] text-blue-900 font-semibold block">Biomassa Viva</span>
                <strong class="text-sm font-black text-blue-950 font-mono block">${isEmPreparacao ? '0 kg' : biomassaVal.toLocaleString('pt-BR') + ' kg'}</strong>
                <span class="text-[9px] text-blue-700 block">${isEmPreparacao ? 'Tanque vazio' : 'Peso médio ' + pesoG + 'g'}</span>
              </div>
              <div class="p-2 rounded-xl bg-amber-50/60 border border-amber-100">
                <span class="text-[10px] text-amber-900 font-semibold block">Ração Acumulada</span>
                <strong class="text-sm font-black text-amber-950 font-mono block">${isEmPreparacao ? '0 kg' : racaoVal.toLocaleString('pt-BR') + ' kg'}</strong>
                <span class="text-[9px] text-amber-700 block">${isEmPreparacao ? '-' : 'FCA Parcial ' + fcaVal}</span>
              </div>
            </div>

            ${desbastesKg > 0 ? `
              <div class="p-2 rounded-xl bg-amber-50 border border-amber-200 text-[10px] flex items-center justify-between">
                <span class="font-bold text-amber-900"><i class="fa-solid fa-scale-balanced"></i> Desbastes acumulados:</span>
                <strong class="font-mono font-black text-amber-950">${desbastesKg.toLocaleString('pt-BR')} kg</strong>
              </div>
            ` : ''}

            <!-- Botões de Ação do Viveiro -->
            <div class="pt-2 border-t border-slate-100 flex items-center gap-2">
              ${isEmPreparacao ? `
                <button onclick="abrirModalNovoCiclo('${v.id}')" class="w-full py-2 px-3 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs transition flex items-center justify-center gap-1.5 shadow-sm">
                  <i class="fa-solid fa-plus-circle"></i> Iniciar Ciclo / Povoar
                </button>
                <button onclick="selecionarViveiroBiomassa('${v.id}'); navegarPara('analytics-biomassa');" class="py-2 px-3 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs transition">
                  <i class="fa-solid fa-eye"></i>
                </button>
              ` : `
                <button onclick="abrirModalDespescaParcial('${v.id}')" class="flex-1 py-2 px-2.5 rounded-xl bg-amber-50 hover:bg-amber-100 text-amber-900 border border-amber-200 font-bold text-xs transition flex items-center justify-center gap-1">
                  <i class="fa-solid fa-scale-balanced text-amber-600"></i> Despesca Parcial
                </button>
                <button onclick="abrirModalEncerramentoCiclo('${v.id}')" class="flex-1 py-2 px-2.5 rounded-xl bg-red-600 hover:bg-red-700 text-white font-extrabold text-xs transition flex items-center justify-center gap-1 shadow-sm">
                  <i class="fa-solid fa-flag-checkered"></i> Encerrar Ciclo
                </button>
              `}
            </div>
          </div>
        `;
      });

      grid.innerHTML = cardsHtml;

      // Atualizar KPIs Consolidados do Topo
      const elAtivos = document.getElementById('kpi-ciclos-ativos-count');
      const elBio = document.getElementById('kpi-ciclos-biomassa-total');
      const elRac = document.getElementById('kpi-ciclos-racao-total');
      const elFca = document.getElementById('kpi-ciclos-fca-medio');
      const elPrep = document.getElementById('kpi-ciclos-preparacao-count');
      const elOcup = document.getElementById('kpi-ciclos-ocupacao-pct');
      const badgeCount = document.getElementById('badge-ciclos-ativos-count');

      if (elAtivos) elAtivos.innerText = `${totalAtivos} viveiros`;
      if (elBio) elBio.innerText = `${totalBiomassa.toLocaleString('pt-BR')} kg`;
      if (elRac) elRac.innerText = `${totalRacao.toLocaleString('pt-BR')} kg`;
      if (elFca) elFca.innerText = countFca > 0 ? (somaFca / countFca).toFixed(2) : '1.22';
      if (elPrep) elPrep.innerText = `${totalPreparacao} viveiros`;
      if (elOcup) elOcup.innerText = `${((totalAtivos / 15) * 100).toFixed(1)}% de ocupação`;
      if (badgeCount) badgeCount.innerText = totalAtivos;
    }

    function renderizarHistoricoCiclos() {
      const tbody = document.getElementById('tbody-historico-ciclos');
      if (!tbody) return;

      const anoFiltro = FILTRO_ANO_CICLOS;
      const vivFiltro = FILTRO_VIVEIRO_CICLOS;

      const safras = (HISTORICO_SAFRAS_DATA || []).filter(s => {
        if (anoFiltro !== 'TODOS' && s.anoSafra !== parseInt(anoFiltro, 10)) return false;
        if (vivFiltro !== 'TODOS' && s.viveiroId !== vivFiltro) return false;
        return true;
      });

      let totalKg = 0;
      let totalFat = 0;
      let somaFcaPond = 0;
      let somaKgFca = 0;
      let somaSob = 0;

      let rowsHtml = '';

      safras.forEach(s => {
        totalKg += s.kgColhido || 0;
        totalFat += s.faturamentoBruto || 0;
        if (s.fcaReal && s.kgColhido) {
          somaFcaPond += (s.fcaReal * s.kgColhido);
          somaKgFca += s.kgColhido;
        }
        somaSob += (s.sobrevivenciaPct || 0);

        const codigoExib = s.codigoCiclo || s.safraId.replace('SAFRA-', '').replace('-V', ' • Ciclo V');

        rowsHtml += `
          <tr class="hover:bg-slate-50 transition border-b border-slate-100">
            <td class="py-3 px-3 font-mono font-black text-slate-900">${s.viveiroId}</td>
            <td class="py-3 px-3">
              <span class="font-extrabold text-slate-800">${codigoExib}</span>
              <span class="text-[10px] text-slate-400 block">${s.safraId}</span>
            </td>
            <td class="py-3 px-3 text-slate-600">
              <span class="font-semibold">${s.dataPovoamento || '-'} &rarr; ${s.dataDespesca || '-'}</span>
            </td>
            <td class="py-3 px-3 text-center font-mono font-bold text-slate-800">${s.ddcTotal || '-'}d</td>
            <td class="py-3 px-3 text-slate-600">
              <span class="font-bold text-slate-800">${s.lab || 'AQUATEC'}</span>
              <span class="text-[10px] text-slate-500 block">${(s.plsMil || 50)} mil PLs</span>
            </td>
            <td class="py-3 px-3 text-right font-mono text-amber-800 font-semibold">${s.desbastesKg ? s.desbastesKg.toLocaleString('pt-BR') + ' kg' : '-'}</td>
            <td class="py-3 px-3 text-right font-mono font-extrabold text-slate-900">${s.kgColhido ? s.kgColhido.toLocaleString('pt-BR') + ' kg' : '-'}</td>
            <td class="py-3 px-3 text-right font-mono text-slate-700">${s.pesoFinalG ? s.pesoFinalG + ' g' : '-'}</td>
            <td class="py-3 px-3 text-center font-mono font-bold text-teal-800">${s.fcaReal || '-'}</td>
            <td class="py-3 px-3 text-center">
              <span class="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-blue-100 text-blue-800">${s.sobrevivenciaPct ? s.sobrevivenciaPct + '%' : '-'}</span>
            </td>
            <td class="py-3 px-3 text-right font-mono font-black text-emerald-900">R$ ${(s.faturamentoBruto || 0).toLocaleString('pt-BR')}</td>
            <td class="py-3 px-3 text-slate-700 truncate max-w-[140px]">${s.comprador || '-'}</td>
            <td class="py-3 px-3 text-center">
              <button onclick="abrirDossieCiclo('${s.safraId}')" class="p-1.5 rounded-lg bg-slate-100 hover:bg-indigo-100 text-slate-600 hover:text-indigo-800 transition" title="Ver Dossiê do Ciclo">
                <i class="fa-solid fa-file-contract"></i>
              </button>
            </td>
          </tr>
        `;
      });

      if (!safras.length) {
        rowsHtml = '<tr><td colspan="13" class="text-center py-6 text-slate-400 italic">Nenhuma safra arquivada encontrada para os filtros selecionados.</td></tr>';
      }

      tbody.innerHTML = rowsHtml;

      // KPIs Históricos do Topo
      const fcaPonderado = somaKgFca > 0 ? (somaFcaPond / somaKgFca).toFixed(2) : '1.21';
      const sobMedia = safras.length ? (somaSob / safras.length).toFixed(1) : '72.4';

      const elCount = document.getElementById('kpi-hist-ciclos-count');
      const elBio = document.getElementById('kpi-hist-biomassa-total');
      const elFca = document.getElementById('kpi-hist-fca-medio');
      const elSob = document.getElementById('kpi-hist-sob-media');
      const elFat = document.getElementById('kpi-hist-faturamento-total');
      const elBadgeHist = document.getElementById('badge-ciclos-historico-count');
      const elContador = document.getElementById('historico-tabela-contador');

      if (elCount) elCount.innerText = `${safras.length} safras`;
      if (elBio) elBio.innerText = `${totalKg.toLocaleString('pt-BR')} kg`;
      if (elFca) elFca.innerText = fcaPonderado;
      if (elSob) elSob.innerText = `${sobMedia}%`;
      if (elFat) elFat.innerText = `R$ ${totalFat.toLocaleString('pt-BR')}`;
      if (elBadgeHist) badgeHist.innerText = safras.length;
      if (elContador) elContador.innerText = `${safras.length} safras registradas`;
    }

    // Modal Iniciar Novo Ciclo
    function abrirModalNovoCiclo(vivId = null) {
      const modal = document.getElementById('modal-iniciar-novo-ciclo');
      const selViv = document.getElementById('modal-novo-ciclo-viv-id');
      const dtInput = document.getElementById('modal-novo-ciclo-data');

      if (!modal || !selViv) return;

      // Preenche lista de viveiros
      selViv.innerHTML = VIVEIROS_DATA.map(v => `<option value="${v.id}" ${vivId === v.id ? 'selected' : ''}>${v.id} • ${v.nome}</option>`).join('');

      if (dtInput) {
        dtInput.value = new Date().toISOString().split('T')[0];
      }

      atualizarPreviaCodigoCiclo();
      modal.classList.remove('hidden');
    }

    function fecharModalNovoCiclo() {
      const modal = document.getElementById('modal-iniciar-novo-ciclo');
      if (modal) modal.classList.add('hidden');
    }

    function atualizarPreviaCodigoCiclo() {
      const selViv = document.getElementById('modal-novo-ciclo-viv-id');
      const anoInput = document.getElementById('modal-novo-ciclo-ano');
      const preview = document.getElementById('modal-novo-ciclo-codigo-preview');
      if (!selViv || !anoInput || !preview) return;

      const vivId = selViv.value || 'V-01';
      const ano = anoInput.value || 2026;
      const info = obterProximoCicloSequencial(vivId, ano);
      preview.innerText = info.codigo;
    }

    function salvarNovoCiclo(event) {
      event.preventDefault();
      const vivId = document.getElementById('modal-novo-ciclo-viv-id').value;
      const ano = parseInt(document.getElementById('modal-novo-ciclo-ano').value, 10) || 2026;
      const dtPov = document.getElementById('modal-novo-ciclo-data').value;
      const pls = parseFloat(document.getElementById('modal-novo-ciclo-pls').value) || 60;
      const lab = document.getElementById('modal-novo-ciclo-lab').value || 'AQUATEC';
      const pesoIni = parseFloat(document.getElementById('modal-novo-ciclo-peso').value) || 0.01;
      const temBerc = document.getElementById('modal-novo-ciclo-tem-bercario').checked;
      const dtTransf = document.getElementById('modal-novo-ciclo-dt-transf').value || null;
      const pesoTransf = parseFloat(document.getElementById('modal-novo-ciclo-peso-transf').value) || null;
      const obs = document.getElementById('modal-novo-ciclo-obs').value || '';

      const dtFmt = formatarDataBr(dtPov);
      const infoSeq = obterProximoCicloSequencial(vivId, ano);

      // Atualiza estado do viveiro para EM CULTIVO ATIVO
      DADOS_PLANILHA_VIVEIROS[vivId] = {
        id: vivId,
        lab: lab,
        pls: pls,
        pov: dtFmt,
        tem_bercario: temBerc,
        entrada_bercario: temBerc ? dtFmt : null,
        transferencia: dtTransf ? formatarDataBr(dtTransf) : null,
        peso_transferencia: pesoTransf,
        statusLote: 'EM CULTIVO ATIVO',
        statusCor: 'otimo',
        codigoCiclo: infoSeq.codigo,
        anoSafra: ano,
        numeroSequencial: infoSeq.seq,
        despesca: null,
        area: 0.50,
        tratos: [
          {
            data: dtFmt,
            doc: 1,
            racaoA: 15.0,
            sobraA: '0',
            racaoB: 15.0,
            sobraB: '0',
            totalDia: 30.0,
            acumulado: 30.0,
            biometria: pesoTransf || pesoIni,
            gmd: null,
            obs: `Povoamento inicial safra ${infoSeq.codigo}`
          }
        ]
      };

      // Reseta desbastes parciais locais
      if (window.CICLOS_DESBASTES_LOCAIS) {
        window.CICLOS_DESBASTES_LOCAIS[vivId] = 0;
      }

      // Atualiza VIVEIROS_DATA global
      const vObj = VIVEIROS_DATA.find(x => x.id === vivId);
      if (vObj) {
        vObj.status = 'otimo';
        vObj.statusCor = 'OTIMO';
        vObj.statusLabel = '🟢 Ótimo';
        vObj.statusDesc = 'Povoamento recente com lote inicial ativo';
        vObj.dataPovoamento = dtFmt;
        vObj.ddc = 1;
        vObj.pesoMedio = pesoTransf || pesoIni;
        vObj.biomassaKg = Math.round((pls * 1000 * (pesoTransf || pesoIni)) / 1000);
        vObj.racaoAcumuladaKg = 30.0;
        vObj.fca = 1.15;
      }

      sincronizarViveirosComPlanilhaReal();
      renderizarPillsViveirosBiomassa();
      preencherTabelasAnaliticas();
      renderizarModuloCiclos();

      fecharModalNovoCiclo();
      alert(`🌱 Novo ciclo '${infoSeq.codigo}' iniciado com sucesso no ${vivId}!\n${pls}.000 PLs estocadas.`);
    }

    // Modal Despesca Parcial (Desbaste)
    function abrirModalDespescaParcial(vivId) {
      const modal = document.getElementById('modal-despesca-parcial-ciclo');
      if (!modal) return;

      const v = VIVEIROS_DATA.find(x => x.id === vivId);
      const dados = DADOS_PLANILHA_VIVEIROS[vivId] || {};
      const tratos = dados.tratos || [];
      const ultBio = tratos.filter(t => t.biometria !== null).slice(-1)[0];

      document.getElementById('modal-parcial-viv-id').value = vivId;
      document.getElementById('modal-parcial-codigo-ciclo').value = dados.codigoCiclo || `${vivId} • Ciclo 2026.1`;
      document.getElementById('modal-parcial-data').value = new Date().toISOString().split('T')[0];
      document.getElementById('modal-parcial-kg').value = 250;
      document.getElementById('modal-parcial-peso').value = ultBio ? ultBio.biometria : (v ? v.pesoMedio : 11.5);
      document.getElementById('modal-parcial-preco').value = 22.0;

      atualizarPreviaDespescaParcial();
      modal.classList.remove('hidden');
    }

    function fecharModalDespescaParcial() {
      const modal = document.getElementById('modal-despesca-parcial-ciclo');
      if (modal) modal.classList.add('hidden');
    }

    function atualizarPreviaDespescaParcial() {
      const kg = parseFloat(document.getElementById('modal-parcial-kg').value) || 0;
      const preco = parseFloat(document.getElementById('modal-parcial-preco').value) || 0;
      const preview = document.getElementById('modal-parcial-faturamento-preview');
      if (preview) {
        preview.innerText = `R$ ${(kg * preco).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`;
      }
    }

    function salvarDespescaParcial(event) {
      event.preventDefault();
      const vivId = document.getElementById('modal-parcial-viv-id').value;
      const dataStr = document.getElementById('modal-parcial-data').value;
      const kg = parseFloat(document.getElementById('modal-parcial-kg').value) || 0;
      const pesoG = parseFloat(document.getElementById('modal-parcial-peso').value) || 11.5;
      const preco = parseFloat(document.getElementById('modal-parcial-preco').value) || 22.0;
      const comprador = document.getElementById('modal-parcial-comprador').value || 'Mercado Regional';
      const obs = document.getElementById('modal-parcial-obs').value || '';

      const dtFmt = formatarDataBr(dataStr);

      // Registra desbaste acumulado
      window.CICLOS_DESBASTES_LOCAIS[vivId] = (window.CICLOS_DESBASTES_LOCAIS[vivId] || 0) + kg;

      // Abate a biomassa viva no VIVEIROS_DATA
      const vObj = VIVEIROS_DATA.find(x => x.id === vivId);
      if (vObj) {
        vObj.biomassaKg = Math.max(100, (vObj.biomassaKg || 1000) - kg);
      }

      // Adiciona linha especial nos tratos do viveiro
      if (DADOS_PLANILHA_VIVEIROS[vivId] && DADOS_PLANILHA_VIVEIROS[vivId].tratos) {
        const tratos = DADOS_PLANILHA_VIVEIROS[vivId].tratos;
        const ultDoc = tratos.length ? tratos[tratos.length - 1].doc : 50;
        tratos.push({
          data: dtFmt,
          doc: ultDoc + 1,
          racaoA: 0,
          sobraA: '0',
          racaoB: 0,
          sobraB: '0',
          totalDia: 0,
          acumulado: tratos.length ? tratos[tratos.length - 1].acumulado : 0,
          biometria: pesoG,
          gmd: null,
          obs: `Despesca parcial (Desbaste): ${kg} kg colhidos @ ${pesoG}g (R$ ${(kg*preco).toLocaleString('pt-BR')})`
        });
      }

      renderizarModuloCiclos();
      fecharModalDespescaParcial();
      alert(`⚖️ Despesca parcial registrada com sucesso no ${vivId}!\n${kg} kg colhidos (R$ ${(kg*preco).toLocaleString('pt-BR')}).\nO ciclo permanece ATIVO.`);
    }

    // Modal Encerramento Executivo e Reset Limpo
    function abrirModalEncerramentoCiclo(vivId) {
      cicloEmEncerramentoVivId = vivId;
      const modal = document.getElementById('modal-encerramento-ciclo');
      if (!modal) return;

      const v = VIVEIROS_DATA.find(x => x.id === vivId);
      const dados = DADOS_PLANILHA_VIVEIROS[vivId] || {};
      const tratos = dados.tratos || [];
      const ultBio = tratos.filter(t => t.biometria !== null).slice(-1)[0];
      const ultTrato = tratos.slice(-1)[0];

      const desbastes = window.CICLOS_DESBASTES_LOCAIS[vivId] || 0;
      const racaoAcum = ultTrato ? ultTrato.acumulado : (v ? v.racaoAcumuladaKg : 0);
      const docAtual = ultTrato ? ultTrato.doc : (v ? v.ddc : 65);
      const pesoMedioSug = ultBio ? ultBio.biometria : (v ? v.pesoMedio : 14.5);
      const kgSugerido = (v ? v.biomassaKg : 450) || 450;

      const codigoCiclo = dados.codigoCiclo || `${vivId} • Ciclo 2026.1`;

      document.getElementById('modal-encerrar-titulo-lote').innerText = `${vivId} • ${codigoCiclo}`;
      document.getElementById('modal-encerrar-res-pov').innerText = dados.pov || (v ? v.dataPovoamento : '-');
      document.getElementById('modal-encerrar-res-doc').innerText = `${docAtual} dias`;
      document.getElementById('modal-encerrar-res-pls').innerText = `${(dados.pls || 50)} mil PLs`;
      document.getElementById('modal-encerrar-res-racao').innerText = `${racaoAcum.toLocaleString('pt-BR')} kg`;
      document.getElementById('modal-encerrar-res-desbastes').innerText = `${desbastes.toLocaleString('pt-BR')} kg`;

      document.getElementById('modal-encerrar-data').value = new Date().toISOString().split('T')[0];
      document.getElementById('modal-encerrar-kg').value = kgSugerido;
      document.getElementById('modal-encerrar-peso').value = pesoMedioSug;
      document.getElementById('modal-encerrar-preco').value = 22.0;
      document.getElementById('modal-encerrar-comprador').value = 'Frigorífico & Mercado Regional';

      atualizarPreviaEncerramentoCiclo();
      modal.classList.remove('hidden');
    }

    function fecharModalEncerramentoCiclo() {
      const modal = document.getElementById('modal-encerramento-ciclo');
      if (modal) modal.classList.add('hidden');
      cicloEmEncerramentoVivId = null;
    }

    function atualizarPreviaEncerramentoCiclo() {
      const vivId = cicloEmEncerramentoVivId;
      if (!vivId) return;

      const kgFinal = parseFloat(document.getElementById('modal-encerrar-kg').value) || 0;
      const pesoFinal = parseFloat(document.getElementById('modal-encerrar-peso').value) || 14.5;
      const preco = parseFloat(document.getElementById('modal-encerrar-preco').value) || 22.0;

      const desbastes = window.CICLOS_DESBASTES_LOCAIS[vivId] || 0;
      const totalColhido = desbastes + kgFinal;

      const dados = DADOS_PLANILHA_VIVEIROS[vivId] || {};
      const tratos = dados.tratos || [];
      const ultTrato = tratos.slice(-1)[0];
      const v = VIVEIROS_DATA.find(x => x.id === vivId);
      const racaoAcum = ultTrato ? ultTrato.acumulado : (v ? v.racaoAcumuladaKg : 0);
      const plsTotal = (dados.pls || 50) * 1000;

      const fca = totalColhido > 0 ? (racaoAcum / totalColhido).toFixed(2) : '1.25';
      const camaroesColhidos = pesoFinal > 0 ? (totalColhido * 1000 / pesoFinal) : 0;
      const sob = plsTotal > 0 ? Math.min(100, Math.round((camaroesColhidos / plsTotal) * 100)) : 75;
      const fat = totalColhido * preco;

      const elTot = document.getElementById('modal-encerrar-calc-total-kg');
      const elFca = document.getElementById('modal-encerrar-calc-fca');
      const elSob = document.getElementById('modal-encerrar-calc-sob');
      const elFat = document.getElementById('modal-encerrar-calc-fat');

      if (elTot) elTot.innerText = `${totalColhido.toLocaleString('pt-BR')} kg`;
      if (elFca) elFca.innerText = fca;
      if (elSob) elSob.innerText = `${sob}%`;
      if (elFat) elFat.innerText = `R$ ${fat.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`;
    }

    function confirmarEncerramentoCiclo(event) {
      event.preventDefault();
      const vivId = cicloEmEncerramentoVivId;
      if (!vivId) return;

      const dataStr = document.getElementById('modal-encerrar-data').value;
      const kgFinal = parseFloat(document.getElementById('modal-encerrar-kg').value) || 0;
      const pesoFinal = parseFloat(document.getElementById('modal-encerrar-peso').value) || 14.5;
      const preco = parseFloat(document.getElementById('modal-encerrar-preco').value) || 22.0;
      const comprador = document.getElementById('modal-encerrar-comprador').value || 'Mercado Regional';
      const obs = document.getElementById('modal-encerrar-obs').value || '';

      const dtFmt = formatarDataBr(dataStr);
      const desbastes = window.CICLOS_DESBASTES_LOCAIS[vivId] || 0;
      const totalColhido = desbastes + kgFinal;

      const dados = DADOS_PLANILHA_VIVEIROS[vivId] || {};
      const tratos = dados.tratos || [];
      const ultTrato = tratos.slice(-1)[0];
      const v = VIVEIROS_DATA.find(x => x.id === vivId);
      const racaoAcum = ultTrato ? ultTrato.acumulado : (v ? v.racaoAcumuladaKg : 0);
      const docTotal = ultTrato ? ultTrato.doc : (v ? v.ddc : 65);
      const plsTotal = (dados.pls || 50) * 1000;

      const fca = totalColhido > 0 ? parseFloat((racaoAcum / totalColhido).toFixed(2)) : 1.25;
      const camaroesColhidos = pesoFinal > 0 ? (totalColhido * 1000 / pesoFinal) : 0;
      const sob = plsTotal > 0 ? Math.min(100, Math.round((camaroesColhidos / plsTotal) * 100)) : 75;
      const fat = totalColhido * preco;

      const infoSeq = obterProximoCicloSequencial(vivId, 2026);
      const codigoCiclo = dados.codigoCiclo || `${vivId} • Ciclo 2026.1`;

      // 1. Arquivar permanentemente no Histórico de Safras
      const safraArquivada = {
        safraId: `SAFRA-2026.${infoSeq.seq}-${vivId}`,
        codigoCiclo: codigoCiclo,
        viveiroId: vivId,
        anoSafra: 2026,
        ciclo: infoSeq.seq,
        statusSafra: 'CONCLUIDA',
        dataPovoamento: dados.pov || (v ? v.dataPovoamento : '15/07/2026'),
        dataDespesca: dtFmt,
        ddcTotal: docTotal,
        lab: dados.lab || 'AQUATEC',
        plsMil: (dados.pls || 50),
        temBercario: Boolean(dados.tem_bercario),
        desbastesKg: desbastes,
        despescaFinalKg: kgFinal,
        kgColhido: totalColhido,
        pesoFinalG: pesoFinal,
        sobrevivenciaPct: sob,
        fcaReal: fca,
        precoVendaKg: preco,
        faturamentoBruto: fat,
        comprador: comprador,
        obs: obs || `Ciclo encerrado com sucesso em ${dtFmt}. Desbastes: ${desbastes} kg, Colheita final: ${kgFinal} kg.`
      };

      HISTORICO_SAFRAS_DATA.unshift(safraArquivada);

      // 2. RESET LIMPO DO VIVEIRO
      // Limpa dados de biometria e alimentação do lote anterior
      DADOS_PLANILHA_VIVEIROS[vivId] = {
        id: vivId,
        lab: '',
        pls: 0,
        pov: '-',
        tem_bercario: false,
        statusLote: 'EM_PREPARACAO',
        statusCor: 'vazio',
        despesca: null,
        area: 0.50,
        tratos: [], // Vazio para receber o novo ciclo
        ultimoCicloEncerrado: safraArquivada
      };

      // Zera contadores de desbastes locais do viveiro
      window.CICLOS_DESBASTES_LOCAIS[vivId] = 0;

      // Atualiza VIVEIROS_DATA global para status VAZIO / EM PREPARAÇÃO
      if (v) {
        v.status = 'vazio';
        v.statusCor = 'VAZIO';
        v.statusLabel = '⚪ Em Preparação';
        v.statusDesc = 'Tanque drenado e pronto para novo povoamento';
        v.biomassaKg = 0;
        v.pesoMedio = 0;
        v.racaoHojeKg = 0;
        v.racaoAcumuladaKg = 0;
        v.ddc = 0;
        v.fca = 0;
        v.densidade = 0;
      }

      // 3. Sincroniza e re-renderiza todos os módulos
      sincronizarViveirosComPlanilhaReal();
      renderizarPillsViveirosBiomassa();
      preencherTabelasAnaliticas();
      renderizarModuloCiclos();
      if (typeof renderizarModuloDespesca === 'function') renderizarModuloDespesca();

      fecharModalEncerramentoCiclo();

      alert(`🏁 Ciclo '${codigoCiclo}' encerrado e arquivado com sucesso!\n\n` +
            `• Total Colhido: ${totalColhido.toLocaleString('pt-BR')} kg\n` +
            `• FCA Final: ${fca}\n` +
            `• Sobrevivência Real: ${sob}%\n` +
            `• Receita Bruta: R$ ${fat.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}\n\n` +
            `✅ O viveiro ${vivId} foi reinicializado com status '⚪ Em Preparação' e está limpo para receber um novo ciclo.`);
    }

    // Modal Dossiê do Ciclo
    function abrirDossieCiclo(safraId) {
      const modal = document.getElementById('modal-dossie-ciclo');
      if (!modal) return;

      const s = (HISTORICO_SAFRAS_DATA || []).find(x => x.safraId === safraId);
      if (!s) return;

      const codigo = s.codigoCiclo || s.safraId;
      document.getElementById('modal-dossie-titulo').innerText = `Dossiê: ${s.viveiroId} • ${codigo}`;
      document.getElementById('modal-dossie-periodo').innerText = `${s.dataPovoamento || '-'} até ${s.dataDespesca || '-'}`;
      document.getElementById('modal-dossie-ddc').innerText = `Duração total: ${s.ddcTotal || '-'} dias de cultivo (DOC)`;
      document.getElementById('modal-dossie-lab-pls').innerText = `Lab: ${s.lab || 'AQUATEC'} • ${(s.plsMil || 50)} mil PLs`;
      document.getElementById('modal-dossie-densidade').innerText = s.temBercario ? '🐣 Passou por Berçário Intensivo' : 'Povoamento direto';

      document.getElementById('modal-dossie-colhido').innerText = `${(s.kgColhido || 0).toLocaleString('pt-BR')} kg (${s.pesoFinalG || '-'}g)`;
      document.getElementById('modal-dossie-fca').innerText = s.fcaReal || '-';
      document.getElementById('modal-dossie-sob').innerText = `${s.sobrevivenciaPct || '-'}%`;

      document.getElementById('modal-dossie-faturamento').innerText = `R$ ${(s.faturamentoBruto || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`;
      document.getElementById('modal-dossie-comprador').innerText = `Comprador: ${s.comprador || '-'}`;
      document.getElementById('modal-dossie-preco').innerText = `R$ ${(s.precoVendaKg || 22).toFixed(2)}/kg`;
      document.getElementById('modal-dossie-obs').innerText = s.obs || 'Nenhuma observação registrada.';

      modal.classList.remove('hidden');
    }

    function fecharDossieCiclo() {
      const modal = document.getElementById('modal-dossie-ciclo');
      if (modal) modal.classList.add('hidden');
    }
"""
    content = content[:idx_close] + js_ciclos_code + "\n" + content[idx_close:]
    print("✅ 5.3 Motor de Ciclos de Produção inserido no script principal.")
else:
    print("ℹ️ 5.3 Motor de ciclos já presente no script.")


# ==============================================================================
# 6. BIOMETRIA: Atualizar renderizarDashboardViveiroBiomassa para estado de preparação
# ==============================================================================
target_bio_render = "const elStatus = document.getElementById('detail-bio-viv-status');"
if "detail-bio-banner-preparacao" in content and "isEmPreparacaoLimpo" not in content:
    idx_br = content.find(target_bio_render)
    if idx_br != -1:
        bio_prep_code = """
      const bannerPrep = document.getElementById('detail-bio-banner-preparacao');
      const isEmPreparacaoLimpo = (dados.statusLote === 'EM_PREPARACAO' || v.status === 'vazio' || (!tratos.length && !dados.despesca));
      if (bannerPrep) {
        if (isEmPreparacaoLimpo) {
          bannerPrep.classList.remove('hidden');
        } else {
          bannerPrep.classList.add('hidden');
        }
      }
      """
        content = content[:idx_br] + bio_prep_code + content[idx_br:]
        print("✅ 6. Exibição do banner de preparação adicionada a renderizarDashboardViveiroBiomassa.")
    else:
        print("❌ Falha ao localizar ponto em renderizarDashboardViveiroBiomassa.")
else:
    print("ℹ️ 6. Lógica de banner de preparação já adicionada.")

# Salvar o arquivo
HTML_PATH.write_text(content, encoding="utf-8")
print(f"🎉 dashboard_interativo_prototipo.html atualizado com sucesso! ({len(content):,} bytes)")
