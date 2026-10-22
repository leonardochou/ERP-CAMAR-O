"""
Script de implementação de:
1. Módulo Despesca & Vendas (#view-analytics-despesca);
2. Módulo Central de Parâmetros e Calibração (#view-analytics-parametros);
3. Sidebar atualizada com os novos botões e navegação;
4. Motor JavaScript com renderizarModuloDespesca, renderizarModuloParametros,
   HISTORICO_SAFRAS_DATA, PARAMETROS_SISTEMA_DATA, arquivamento sem conflito e modais;
5. Ajuste de padding para o botão flutuante do WhatsApp.
"""
import shutil
from pathlib import Path

BASE_DIR = Path(r"G:\Meu Drive\ANTIGRAVITY DRIVE\CAMARÃO\ERP CAMARÃO")
HTML_PATH = BASE_DIR / "dashboard_interativo_prototipo.html"
BACKUP_PATH = BASE_DIR / "dashboard_interativo_prototipo.backup_antes_despesca_parametros.html"

shutil.copy2(HTML_PATH, BACKUP_PATH)
print(f"Backup gravado em: {BACKUP_PATH}")

html = HTML_PATH.read_text(encoding="utf-8")

# ==============================================================================
# 1. ATUALIZAR SIDEBAR: Adicionar "Parâmetros & Calibração"
# ==============================================================================
sidebar_antiga = """        <button onclick="navegarPara('analytics-ged')" id="nav-analytics-ged" class="nav-item w-full flex items-center space-x-3 px-3 py-2.5 rounded-xl font-medium text-blue-200 hover:text-white hover:bg-white/10 transition">
          <i class="fa-solid fa-folder-open w-5 text-center text-amber-200"></i>
          <span class="sidebar-label">GED & Notas / IDEMA</span>
        </button>

      </nav>"""

sidebar_nova = """        <button onclick="navegarPara('analytics-ged')" id="nav-analytics-ged" class="nav-item w-full flex items-center space-x-3 px-3 py-2.5 rounded-xl font-medium text-blue-200 hover:text-white hover:bg-white/10 transition">
          <i class="fa-solid fa-folder-open w-5 text-center text-amber-200"></i>
          <span class="sidebar-label">GED & Notas / IDEMA</span>
        </button>

        <!-- Bloco 4: Configurações & Calibração -->
        <div class="sidebar-section-title px-3 pt-4 pb-1 text-[10px] font-bold uppercase tracking-wider text-blue-300/70">
          Configurações da Fazenda
        </div>
        <button onclick="navegarPara('analytics-parametros')" id="nav-analytics-parametros" class="nav-item w-full flex items-center space-x-3 px-3 py-2.5 rounded-xl font-medium text-blue-200 hover:text-white hover:bg-white/10 transition">
          <i class="fa-solid fa-sliders w-5 text-center text-teal-300"></i>
          <span class="sidebar-label">Parâmetros & Calibração</span>
        </button>

      </nav>"""

if sidebar_antiga in html:
    html = html.replace(sidebar_antiga, sidebar_nova, 1)
    print("Sucesso: Item 'Parâmetros & Calibração' adicionado à Sidebar!")
else:
    print("Aviso: sidebar_antiga não encontrada para substituição direta.")

# ==============================================================================
# 2. IMPLEMENTAR SEÇÃO DE DESPESCA & VENDAS E CENTRAL DE PARÂMETROS NO HTML
# ==============================================================================
secao_despesca_html = """
      <!-- ======================================================== -->
      <!-- VIEW: DESPESCA & VENDAS (SAFRAS, COLHEITA & RECEITA)    -->
      <!-- ======================================================== -->
      <section id="view-analytics-despesca" class="hidden space-y-6 pb-24">
        
        <!-- Header da Página de Despesca -->
        <div class="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4 bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <div class="space-y-1">
            <div class="flex items-center space-x-2 text-xs font-semibold text-aco">
              <span class="cursor-pointer hover:underline" onclick="navegarPara('dashboard-macro')">Fazenda</span>
              <span>&gt;</span>
              <span class="text-slate-800 font-bold">Despesca & Vendas</span>
            </div>
            <h2 class="text-xl font-extrabold text-slate-900 flex items-center gap-2">
              <i class="fa-solid fa-truck-ramp-box text-indigo-600"></i> Despesca, Safras & Comercialização
            </h2>
            <p class="text-xs text-slate-500">
              Controle de safras concluídas, biometrias de colheita, sobrevivência real, faturamento bruto e histórico de lotes sem perda de dados.
            </p>
          </div>

          <div class="flex flex-wrap items-center gap-2.5 w-full lg:w-auto">
            <!-- Seletor de Safra -->
            <div class="flex items-center gap-1.5 bg-slate-50 p-1 rounded-xl border border-slate-200 text-xs">
              <span class="text-[11px] font-bold text-slate-500 px-2">Safra:</span>
              <select id="filtro-despesca-safra" onchange="filtrarTabelaDespescas(this.value)" class="bg-white text-xs font-bold py-1.5 px-3 rounded-lg border border-slate-200 text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500">
                <option value="TODAS">Todas as Safras (Consolidado)</option>
                <option value="2026.1" selected>Safra 2026.1 (Ciclo Atual)</option>
              </select>
            </div>

            <!-- Botão Registrar Despesca -->
            <button onclick="abrirModalNovaDespesca()" class="px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs transition flex items-center gap-2 shadow-sm">
              <i class="fa-solid fa-plus-circle"></i> Registrar Despesca / Encerrar Lote
            </button>
          </div>
        </div>

        <!-- Cards de KPIs Consolidados da Despesca -->
        <div class="grid grid-cols-2 md:grid-cols-5 gap-3.5">
          <!-- KPI 1: Total Colhido -->
          <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm space-y-1">
            <span class="text-[11px] font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
              <i class="fa-solid fa-weight-scale text-indigo-500"></i> Total Colhido
            </span>
            <div class="text-2xl font-black text-indigo-950 font-mono" id="kpi-despesca-total-kg">1.363 kg</div>
            <div class="text-[10px] text-indigo-700 font-semibold" id="kpi-despesca-tanques-count">3 viveiros colhidos</div>
          </div>

          <!-- KPI 2: Faturamento Bruto -->
          <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm space-y-1">
            <span class="text-[11px] font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
              <i class="fa-solid fa-sack-dollar text-emerald-500"></i> Receita Bruta Est.
            </span>
            <div class="text-2xl font-black text-emerald-900 font-mono" id="kpi-despesca-receita-total">R$ 31.172</div>
            <div class="text-[10px] text-emerald-700 font-semibold">Média R$ 22,87/kg</div>
          </div>

          <!-- KPI 3: FCA Final Ponderado -->
          <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm space-y-1">
            <span class="text-[11px] font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
              <i class="fa-solid fa-scale-balanced text-teal-500"></i> FCA Ponderado
            </span>
            <div class="text-2xl font-black text-teal-900 font-mono" id="kpi-despesca-fca-ponderado">1.21</div>
            <div class="text-[10px] text-emerald-600 font-extrabold flex items-center gap-1">
              <i class="fa-solid fa-circle-check"></i> Alta Eficiência (&le; 1.25)
            </div>
          </div>

          <!-- KPI 4: Sobrevivência Ponderada -->
          <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm space-y-1">
            <span class="text-[11px] font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
              <i class="fa-solid fa-heart-pulse text-amber-500"></i> Sobrevivência Média
            </span>
            <div class="text-2xl font-black text-amber-950 font-mono" id="kpi-despesca-sobr-media">58.1%</div>
            <div class="text-[10px] text-amber-700 font-semibold">Ponderada por densidade</div>
          </div>

          <!-- KPI 5: Gramatura Média -->
          <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm space-y-1">
            <span class="text-[11px] font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
              <i class="fa-solid fa-shrimp text-violet-500"></i> Peso Médio Final
            </span>
            <div class="text-2xl font-black text-violet-950 font-mono" id="kpi-despesca-peso-medio">15.2 g</div>
            <div class="text-[10px] text-violet-700 font-semibold">Gama: 13.5g a 17.2g</div>
          </div>
        </div>

        <!-- Gráficos de Produtividade e Desempenho de Safra -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-5">
          <!-- Gráfico 1: Biomassa Colhida e Produtividade kg/ha -->
          <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
            <div class="flex items-center justify-between">
              <h3 class="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-2">
                <i class="fa-solid fa-chart-simple text-indigo-500"></i> Volume Colhido por Viveiro (kg)
              </h3>
              <span class="text-[10px] font-semibold text-slate-400">Safra 2026.1</span>
            </div>
            <div class="h-56 relative">
              <canvas id="chart-despesca-volume"></canvas>
            </div>
          </div>

          <!-- Gráfico 2: Comparativo Gramatura vs FCA Real -->
          <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
            <div class="flex items-center justify-between">
              <h3 class="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-2">
                <i class="fa-solid fa-chart-line text-emerald-500"></i> Gramatura Final (g) vs FCA Real
              </h3>
              <span class="text-[10px] font-semibold text-slate-400">Meta FCA: &le; 1.25</span>
            </div>
            <div class="h-56 relative">
              <canvas id="chart-despesca-fca"></canvas>
            </div>
          </div>
        </div>

        <!-- Tabela Executiva de Safras Concluídas / Despescas Reais -->
        <div class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
          <div class="p-4 bg-slate-50/70 border-b border-slate-200 flex flex-wrap items-center justify-between gap-2">
            <div>
              <h3 class="font-extrabold text-sm text-slate-900 flex items-center gap-2">
                <i class="fa-solid fa-award text-amber-500"></i> Registro Oficial de Safras Concluídas & Despescas
              </h3>
              <p class="text-[11px] text-slate-500">Histórico auditado com dados extraídos da planilha do campo e fechamento executivo da safra.</p>
            </div>
            <span class="px-2.5 py-1 rounded-lg bg-indigo-50 text-indigo-800 font-extrabold text-[11px] border border-indigo-200">
              <i class="fa-solid fa-database"></i> Histórico Permanente Protegido
            </span>
          </div>

          <div class="overflow-x-auto">
            <table class="w-full text-left text-xs">
              <thead class="bg-slate-100 text-slate-700 font-bold uppercase text-[10px] tracking-wider border-b border-slate-200">
                <tr>
                  <th class="p-3">Tanque</th>
                  <th class="p-3">Safra / Lote</th>
                  <th class="p-3">Data Despesca</th>
                  <th class="p-3">DDC Total</th>
                  <th class="p-3">Camarão Colhido</th>
                  <th class="p-3">Peso Final</th>
                  <th class="p-3">Sobrevivência</th>
                  <th class="p-3">FCA Final</th>
                  <th class="p-3">Preço/kg</th>
                  <th class="p-3">Receita Bruta</th>
                  <th class="p-3">Comprador / Destino</th>
                  <th class="p-3 text-center">Ações</th>
                </tr>
              </thead>
              <tbody id="tbody-despescas-lista" class="divide-y divide-slate-100 font-medium">
                <!-- Populado dinamicamente via JS -->
              </tbody>
            </table>
          </div>
        </div>

      </section>
"""

secao_parametros_html = """
      <!-- ======================================================== -->
      <!-- VIEW: CENTRAL DE PARÂMETROS & CALIBRAÇÃO ZOOTÉCNICA     -->
      <!-- ======================================================== -->
      <section id="view-analytics-parametros" class="hidden space-y-6 pb-24">
        
        <!-- Header da Central de Parâmetros -->
        <div class="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4 bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <div class="space-y-1">
            <div class="flex items-center space-x-2 text-xs font-semibold text-aco">
              <span class="cursor-pointer hover:underline" onclick="navegarPara('dashboard-macro')">Fazenda</span>
              <span>&gt;</span>
              <span class="text-slate-800 font-bold">Configurações & Calibração</span>
            </div>
            <h2 class="text-xl font-extrabold text-slate-900 flex items-center gap-2">
              <i class="fa-solid fa-sliders text-teal-600"></i> Central de Parâmetros & Calibração Zootécnica
            </h2>
            <p class="text-xs text-slate-500">
              Dicionário técnico da fazenda: significado prático de cada índice, faixas recomendadas pela literatura (ABCC/EMBRAPA) e parâmetros customizados ativos em uso.
            </p>
          </div>

          <div class="flex items-center gap-2.5">
            <button onclick="restaurarParametrosPadrao()" class="px-3.5 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs transition flex items-center gap-1.5 border border-slate-200">
              <i class="fa-solid fa-rotate-left"></i> Restaurar Padrões Recomendados
            </button>
          </div>
        </div>

        <!-- Barra de Filtros por Módulo -->
        <div class="flex items-center gap-2 overflow-x-auto pb-1 text-xs">
          <button onclick="filtrarCategoriaParametros('TODOS')" id="btn-param-filter-TODOS" class="param-filter-btn px-4 py-2 rounded-xl font-bold bg-slate-900 text-white shadow-xs transition whitespace-nowrap">
            📋 Todos os Parâmetros (14)
          </button>
          <button onclick="filtrarCategoriaParametros('BIOMASSA')" id="btn-param-filter-BIOMASSA" class="param-filter-btn px-4 py-2 rounded-xl font-semibold bg-white text-slate-700 hover:bg-slate-100 border border-slate-200 transition whitespace-nowrap">
            🦐 Biomassa & Ração
          </button>
          <button onclick="filtrarCategoriaParametros('AGUA')" id="btn-param-filter-AGUA" class="param-filter-btn px-4 py-2 rounded-xl font-semibold bg-white text-slate-700 hover:bg-slate-100 border border-slate-200 transition whitespace-nowrap">
            💧 Qualidade da Água
          </button>
          <button onclick="filtrarCategoriaParametros('TOPOGRAFIA')" id="btn-param-filter-TOPOGRAFIA" class="param-filter-btn px-4 py-2 rounded-xl font-semibold bg-white text-slate-700 hover:bg-slate-100 border border-slate-200 transition whitespace-nowrap">
            🏞️ Topografia & Áreas
          </button>
          <button onclick="filtrarCategoriaParametros('POVOAMENTO')" id="btn-param-filter-POVOAMENTO" class="param-filter-btn px-4 py-2 rounded-xl font-semibold bg-white text-slate-700 hover:bg-slate-100 border border-slate-200 transition whitespace-nowrap">
            🐣 Povoamento & Berçário
          </button>
          <button onclick="filtrarCategoriaParametros('DESPESCA')" id="btn-param-filter-DESPESCA" class="param-filter-btn px-4 py-2 rounded-xl font-semibold bg-white text-slate-700 hover:bg-slate-100 border border-slate-200 transition whitespace-nowrap">
            🏆 Despesca & Vendas
          </button>
        </div>

        <!-- Grade de Cartões Explicativos de Parâmetros -->
        <div id="grid-cards-parametros" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <!-- Populado via JS -->
        </div>

        <!-- Seção Especial: Calibração de Áreas dos 15 Viveiros (Satélite vs Pai) -->
        <div id="card-calibracao-areas-viveiros" class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden space-y-3 p-5">
          <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 border-b border-slate-100 pb-3">
            <div>
              <h3 class="font-extrabold text-sm text-slate-900 flex items-center gap-2">
                <i class="fa-solid fa-draw-polygon text-emerald-600"></i> Calibração das Áreas dos 15 Viveiros (Lâmina d'Água)
              </h3>
              <p class="text-[11px] text-slate-500">Defina se o ERP deve usar a medição geométrica por satélite GPS ou a área tradicional informada pelo produtor (Pai).</p>
            </div>
            <div class="flex items-center gap-2 text-xs">
              <button onclick="aplicarAreaEmLote('SATELITE')" class="px-3 py-1.5 rounded-lg bg-blue-50 text-blue-700 hover:bg-blue-100 font-bold border border-blue-200 transition">
                Usar Satélite em Todos
              </button>
              <button onclick="aplicarAreaEmLote('PAI')" class="px-3 py-1.5 rounded-lg bg-amber-50 text-amber-800 hover:bg-amber-100 font-bold border border-amber-200 transition">
                Usar Área do Pai em Todos
              </button>
            </div>
          </div>

          <div class="overflow-x-auto">
            <table class="w-full text-left text-xs">
              <thead class="bg-slate-100 text-slate-700 font-bold uppercase text-[10px] tracking-wider">
                <tr>
                  <th class="p-2.5">Tanque</th>
                  <th class="p-2.5">Área Satélite (m²)</th>
                  <th class="p-2.5">Área Satélite (ha)</th>
                  <th class="p-2.5">Área Tradicional Pai (ha)</th>
                  <th class="p-2.5">Área Efetiva no ERP (ha)</th>
                  <th class="p-2.5">Profundidade Média</th>
                  <th class="p-2.5">Volume (m³)</th>
                  <th class="p-2.5 text-center">Ação</th>
                </tr>
              </thead>
              <tbody id="tbody-calibracao-areas" class="divide-y divide-slate-100">
                <!-- Populado dinamicamente via JS -->
              </tbody>
            </table>
          </div>
        </div>

      </section>
"""

# Inserir antes de </main>
idx_main_close = html.find('</main>')
if idx_main_close != -1:
    html = html[:idx_main_close] + secao_despesca_html + "\n\n" + secao_parametros_html + "\n    " + html[idx_main_close:]
    print("Sucesso: Seções view-analytics-despesca e view-analytics-parametros inseridas dentro de <main>!")
else:
    print("Erro: </main> não encontrado!")

# ==============================================================================
# 3. MODAIS: MODAL DE NOVA DESPESCA E MODAL DE EDIÇÃO DE PARÂMETRO
# ==============================================================================
modais_html = """
  <!-- ======================================================== -->
  <!-- MODAL: REGISTRAR NOVA DESPESCA / ENCERRAMENTO DE SAFRA   -->
  <!-- ======================================================== -->
  <div id="modal-registro-despesca" class="hidden fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
    <div class="bg-white rounded-3xl max-w-lg w-full shadow-2xl border border-slate-200 overflow-hidden">
      <div class="bg-indigo-900 p-4 text-white flex items-center justify-between">
        <div class="flex items-center space-x-2.5">
          <div class="p-2 bg-indigo-700/60 rounded-xl">
            <i class="fa-solid fa-truck-ramp-box text-white"></i>
          </div>
          <div>
            <h3 class="text-sm font-extrabold">Registrar Despesca & Encerrar Lote</h3>
            <p class="text-[10px] text-indigo-200">Arquiva a safra no histórico permanente e calcula o resultado final</p>
          </div>
        </div>
        <button onclick="fecharModalNovaDespesca()" class="text-indigo-200 hover:text-white text-lg">
          <i class="fa-solid fa-xmark"></i>
        </button>
      </div>

      <form id="form-registro-despesca" onsubmit="salvarNovaDespesca(event)" class="p-5 space-y-4 text-xs">
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block font-bold text-slate-700 mb-1">Viveiro / Tanque:</label>
            <select id="modal-desp-viv-id" class="w-full text-xs font-bold p-2.5 rounded-xl border border-slate-300 bg-white" required>
              <!-- Populado via JS com viveiros em cultivo -->
            </select>
          </div>
          <div>
            <label class="block font-bold text-slate-700 mb-1">Data da Despesca:</label>
            <input type="date" id="modal-desp-data" class="w-full text-xs font-bold p-2.5 rounded-xl border border-slate-300 bg-white" required>
          </div>
        </div>

        <div class="p-3.5 rounded-2xl bg-indigo-50/70 border border-indigo-200 space-y-3">
          <span class="text-[11px] font-bold text-indigo-950 flex items-center gap-1.5">
            <i class="fa-solid fa-scale-balanced text-indigo-600"></i> Biometria Final da Colheita:
          </span>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-[10px] font-bold text-indigo-900 mb-0.5">Camarão Colhido Total (kg):</label>
              <input type="number" step="1" id="modal-desp-kg" placeholder="ex: 450" class="w-full text-xs font-mono font-bold p-2 rounded-xl border border-indigo-300 bg-white" required>
            </div>
            <div>
              <label class="block text-[10px] font-bold text-indigo-900 mb-0.5">Gramatura / Peso Final (g):</label>
              <input type="number" step="0.1" id="modal-desp-peso" placeholder="ex: 14.5" class="w-full text-xs font-mono font-bold p-2 rounded-xl border border-indigo-300 bg-white" required>
            </div>
          </div>
        </div>

        <div class="p-3.5 rounded-2xl bg-emerald-50/70 border border-emerald-200 space-y-3">
          <span class="text-[11px] font-bold text-emerald-950 flex items-center gap-1.5">
            <i class="fa-solid fa-sack-dollar text-emerald-600"></i> Comercialização & Venda:
          </span>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-[10px] font-bold text-emerald-900 mb-0.5">Preço Praticado (R$/kg):</label>
              <input type="number" step="0.5" id="modal-desp-preco" value="22.0" class="w-full text-xs font-mono font-bold p-2 rounded-xl border border-emerald-300 bg-white" required>
            </div>
            <div>
              <label class="block text-[10px] font-bold text-emerald-900 mb-0.5">Comprador / Destino:</label>
              <input type="text" id="modal-desp-comprador" placeholder="ex: Distribuidora Natal" class="w-full text-xs font-semibold p-2 rounded-xl border border-emerald-300 bg-white" required>
            </div>
          </div>
        </div>

        <div>
          <label class="block font-bold text-slate-700 mb-1">Observações da Despesca:</label>
          <input type="text" id="modal-desp-obs" placeholder="ex: Despesca noturna; lote com ótima casca e coloração..." class="w-full text-xs p-2.5 rounded-xl border border-slate-300 bg-white">
        </div>

        <div class="flex items-center justify-end space-x-2 pt-3 border-t border-slate-100">
          <button type="button" onclick="fecharModalNovaDespesca()" class="px-4 py-2 rounded-xl text-slate-600 hover:bg-slate-100 font-bold transition">
            Cancelar
          </button>
          <button type="submit" class="px-5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold transition flex items-center gap-1.5 shadow-sm">
            <i class="fa-solid fa-check-circle"></i> Concluir Despesca & Arquivar
          </button>
        </div>
      </form>
    </div>
  </div>

  <!-- ======================================================== -->
  <!-- MODAL: CALIBRAÇÃO / EDIÇÃO DE PARÂMETRO DA FAZENDA      -->
  <!-- ======================================================== -->
  <div id="modal-calibrar-parametro" class="hidden fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
    <div class="bg-white rounded-3xl max-w-md w-full shadow-2xl border border-slate-200 overflow-hidden">
      <div class="bg-teal-900 p-4 text-white flex items-center justify-between">
        <div class="flex items-center space-x-2.5">
          <div class="p-2 bg-teal-700/60 rounded-xl">
            <i class="fa-solid fa-sliders text-white"></i>
          </div>
          <div>
            <h3 class="text-sm font-extrabold" id="modal-param-titulo">Calibrar Parâmetro</h3>
            <p class="text-[10px] text-teal-200" id="modal-param-modulo">Módulo Zootécnico</p>
          </div>
        </div>
        <button onclick="fecharModalCalibrarParametro()" class="text-teal-200 hover:text-white text-lg">
          <i class="fa-solid fa-xmark"></i>
        </button>
      </div>

      <div class="p-5 space-y-4 text-xs">
        <div class="p-3 rounded-2xl bg-slate-50 border border-slate-200 space-y-1">
          <span class="text-[10px] font-bold text-slate-400 uppercase">Significado Técnico</span>
          <p class="text-xs text-slate-700 font-medium" id="modal-param-significado">-</p>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div class="p-3 rounded-xl bg-blue-50/70 border border-blue-200">
            <span class="text-[10px] font-bold text-blue-900 uppercase">Recomendado (ABCC)</span>
            <div class="text-sm font-extrabold text-blue-950 font-mono mt-0.5" id="modal-param-sugerido">-</div>
          </div>
          <div>
            <label class="block font-bold text-slate-800 mb-1">Parâmetro Ativo na Fazenda:</label>
            <input type="text" id="modal-param-input-ativo" class="w-full text-sm font-mono font-bold p-2.5 rounded-xl border border-teal-500 bg-teal-50/30 text-teal-950 focus:outline-none focus:ring-2 focus:ring-teal-500">
          </div>
        </div>

        <div class="text-[11px] text-slate-500 bg-amber-50 p-2.5 rounded-xl border border-amber-200">
          <i class="fa-solid fa-circle-info text-amber-600"></i> Ao alterar este parâmetro, todos os indicadores zootécnicos e alertas serão recalculados automaticamente.
        </div>

        <div class="flex items-center justify-end space-x-2 pt-2 border-t border-slate-100">
          <button type="button" onclick="fecharModalCalibrarParametro()" class="px-4 py-2 rounded-xl text-slate-600 hover:bg-slate-100 font-bold transition">
            Cancelar
          </button>
          <button type="button" onclick="salvarParametroEditado()" class="px-5 py-2 rounded-xl bg-teal-600 hover:bg-teal-700 text-white font-bold transition flex items-center gap-1.5 shadow-sm">
            <i class="fa-solid fa-save"></i> Salvar Calibração
          </button>
        </div>
      </div>
    </div>
  </div>
"""

# Inserir modais antes do fechamento de </body>
idx_body_close = html.rfind('</body>')
if idx_body_close != -1:
    html = html[:idx_body_close] + modais_html + "\n\n" + html[idx_body_close:]
    print("Sucesso: Modais de despesca e calibração de parâmetros inseridos antes de </body>!")
else:
    print("Erro: </body> não encontrado!")

# ==============================================================================
# 4. ATUALIZAR LISTA DE VIEWS EM navegarPara()
# ==============================================================================
view_lista_antiga = """        'analytics-povoamento',
        'analytics-despesca',
        'analytics-ged'
      ];"""

view_lista_nova = """        'analytics-povoamento',
        'analytics-despesca',
        'analytics-parametros',
        'analytics-ged'
      ];"""

if view_lista_antiga in html:
    html = html.replace(view_lista_antiga, view_lista_nova, 1)
    print("Sucesso: 'analytics-parametros' adicionado à lista de views!")

# Adicionar triggers de rota em navegarPara:
triggers_antigos = """      } else if (viewId === 'analytics-despesca') {
        atualizarHeaderNavegacao('Despesca & Vendas', 'Início > Zootecnia > Despesca');
      }"""

triggers_novos = """      } else if (viewId === 'analytics-despesca') {
        atualizarHeaderNavegacao('Despesca, Safras & Comercialização', 'Início > Zootecnia > Despesca');
        renderizarModuloDespesca();
      } else if (viewId === 'analytics-parametros') {
        atualizarHeaderNavegacao('Central de Parâmetros & Calibração', 'Início > Configurações > Parâmetros');
        renderizarModuloParametros();
      }"""

if triggers_antigos in html:
    html = html.replace(triggers_antigos, triggers_novos, 1)
    print("Sucesso: Triggers de rota para despesca e parâmetros adicionados em navegarPara!")
else:
    print("Aviso: triggers_antigos não encontrado para substituição direta. Procurando alternativa...")
    # Tenta achar onde analytics-despesca é tratada
    idx_trig = html.find("viewId === 'analytics-despesca'")
    if idx_trig != -1:
        idx_end_trig = html.find("}", idx_trig) + 1
        html = html[:idx_trig] + "viewId === 'analytics-despesca') {\n        atualizarHeaderNavegacao('Despesca, Safras & Comercialização', 'Início > Zootecnia > Despesca');\n        renderizarModuloDespesca();\n      } else if (viewId === 'analytics-parametros') {\n        atualizarHeaderNavegacao('Central de Parâmetros & Calibração', 'Início > Configurações > Parâmetros');\n        renderizarModuloParametros();" + html[idx_end_trig:]
        print("Sucesso alternativo: Triggers de rota injetados!")

# ==============================================================================
# 5. DADOS E MOTOR JAVASCRIPT DE DESPESCA, PARÂMETROS E HISTÓRICO DE SAFRAS
# ==============================================================================
bloco_dados_despesca_parametros_js = """
    // ========================================================
    // DADOS HISTÓRICOS DE SAFRAS & CENTRAL DE PARÂMETROS
    // ========================================================

    // 1. Histórico Permanente de Safras Concluídas (Imutável contra sobreposição)
    let HISTORICO_SAFRAS_DATA = [
      {
        safraId: 'SAFRA-2026.1-V05',
        viveiroId: 'V-05',
        anoSafra: 2026,
        ciclo: 1,
        statusSafra: 'CONCLUIDA',
        dataPovoamento: '01/09/2026',
        dataDespesca: '06/10/2026',
        ddcTotal: 36,
        lab: 'AQUATEC',
        plsMil: 41,
        temBercario: false,
        kgColhido: 593.0,
        pesoFinalG: 17.2,
        sobrevivenciaPct: 84.1,
        fcaReal: 1.15,
        precoVendaKg: 24.00,
        faturamentoBruto: 14232.00,
        comprador: 'Distribuidora Natal Camarão',
        obs: 'despesca 593 kg de 17,2 gr - Excelente crescimento e casca firme.'
      },
      {
        safraId: 'SAFRA-2026.1-V06',
        viveiroId: 'V-06',
        anoSafra: 2026,
        ciclo: 1,
        statusSafra: 'CONCLUIDA',
        dataPovoamento: '18/08/2026',
        dataDespesca: '08/10/2026',
        ddcTotal: 52,
        lab: 'NE',
        plsMil: 60,
        temBercario: false,
        kgColhido: 450.0,
        pesoFinalG: 14.0,
        sobrevivenciaPct: 53.6,
        fcaReal: 1.25,
        precoVendaKg: 22.00,
        faturamentoBruto: 9900.00,
        comprador: 'Restaurantes & Mercado Local',
        obs: 'despesca 450 kg de 14.0 gr - Lote uniforme com despesca total.'
      },
      {
        safraId: 'SAFRA-2026.1-V03',
        viveiroId: 'V-03',
        anoSafra: 2026,
        ciclo: 1,
        statusSafra: 'CONCLUIDA',
        dataPovoamento: '19/06/2026',
        dataDespesca: '07/10/2026',
        ddcTotal: 80,
        lab: 'NE',
        plsMil: 65,
        temBercario: false,
        kgColhido: 320.0,
        pesoFinalG: 13.5,
        sobrevivenciaPct: 36.5,
        fcaReal: 1.28,
        precoVendaKg: 22.00,
        faturamentoBruto: 7040.00,
        comprador: 'Frigorífico Litoral Potiguar',
        obs: 'despesca 320 kg 13,5 gr - Cultivo de inverno com sobrevivência moderada.'
      }
    ];

    // 2. Central de Parâmetros e Calibração da Fazenda
    let PARAMETROS_SISTEMA_DATA = [
      {
        id: 'fca_alvo',
        codigo: 'FCA',
        nome: 'Fator de Conversão Alimentar (FCA Meta)',
        categoria: 'BIOMASSA',
        moduloLabel: 'Biomassa & Ração',
        moduloClass: 'bg-blue-100 text-blue-800 border-blue-200',
        significado: 'Indica quantos quilos de ração foram consumidos para gerar 1 kg de camarão vivo. Quanto menor, mais eficiente e lucrativa é a safra.',
        sugerido: '1.15 a 1.30',
        ativo: '1.25',
        unidade: 'ratio (kg ração / kg camarão)',
        impacto: 'Classifica o lote como Ótima Conversão (<= 1.25), Atenção (1.26 - 1.35) ou Desvio Detectado (> 1.35).'
      },
      {
        id: 'gmd_meta',
        codigo: 'GMD',
        nome: 'Ganho Médio Diário de Peso (GMD)',
        categoria: 'BIOMASSA',
        moduloLabel: 'Biomassa & Ração',
        moduloClass: 'bg-blue-100 text-blue-800 border-blue-200',
        significado: 'Gramas de peso que o camarão ganha por dia de cultivo. Equivale a cerca de 1.10g a 1.40g por semana.',
        sugerido: '0.15 a 0.25 g/dia',
        ativo: '0.18 g/dia',
        unidade: 'g/dia',
        impacto: 'Projeta o crescimento das curvas teóricas e estima a data ótima para a despesca comercial.'
      },
      {
        id: 'sobra_bandeja_corte',
        codigo: 'CORTE_SOBRA',
        nome: 'Corte de Ração por Sobra em Bandeja',
        categoria: 'BIOMASSA',
        moduloLabel: 'Biomassa & Ração',
        moduloClass: 'bg-blue-100 text-blue-800 border-blue-200',
        significado: 'Percentual de redução na dosagem do trato subsequente quando o prato de alimentação volta com muita sobra (Nível 3).',
        sugerido: '15% a 25%',
        ativo: '20%',
        unidade: '% de redução',
        impacto: 'Previne a poluição do fundo do tanque, picos de amônia e desperdício de ração de alto custo.'
      },
      {
        id: 'o2_critico',
        codigo: 'O2_CRITICO',
        nome: 'Oxigênio Dissolvido Crítico (Madrugada)',
        categoria: 'AGUA',
        moduloLabel: 'Qualidade da Água',
        moduloClass: 'bg-cyan-100 text-cyan-800 border-cyan-200',
        significado: 'Teor mínimo tolerável de oxigênio na água durante a madrugada (02h às 05h). Abaixo desse valor o camarão entra em anóxia aguda.',
        sugerido: '>= 3.5 mg/L',
        ativo: '3.0 mg/L',
        unidade: 'mg/L',
        impacto: 'Dispara alarme vermelho no mapa, notificação para o vigia noturno e acionamento imediato de aeradores.'
      },
      {
        id: 'ph_faixa',
        codigo: 'PH_FAIXA',
        nome: 'Faixa Ótima de pH da Água',
        categoria: 'AGUA',
        moduloLabel: 'Qualidade da Água',
        moduloClass: 'bg-cyan-100 text-cyan-800 border-cyan-200',
        significado: 'Equilíbrio ácido-base da água do viveiro. O camarão Litopenaeus vannamei exige água ligeiramente alcalina para troca de casca e sanidade.',
        sugerido: '7.5 a 8.3',
        ativo: '7.6 a 8.2',
        unidade: 'escala pH',
        impacto: 'Indica necessidade de calagem ou renovação. Variação diária manhã vs tarde não deve exceder 0.5.'
      },
      {
        id: 'amonia_limite',
        codigo: 'NH3_MAX',
        nome: 'Amônia Tóxica Máxima (NH₃ Livre)',
        categoria: 'AGUA',
        moduloLabel: 'Qualidade da Água',
        moduloClass: 'bg-cyan-100 text-cyan-800 border-cyan-200',
        significado: 'Gás de amônia dissolvido não-ionizado, altamente tóxico que queima as brânquias do camarão e causa mortalidade.',
        sugerido: '< 0.05 mg/L',
        ativo: '< 0.05 mg/L',
        unidade: 'mg/L',
        impacto: 'Dispara recomendação de corte de ração em 50% e renovação de água na maré alta do Rio Ceará-Mirim.'
      },
      {
        id: 'salinidade_estuario',
        codigo: 'SALINIDADE',
        nome: 'Salinidade Média do Estuário',
        categoria: 'AGUA',
        moduloLabel: 'Qualidade da Água',
        moduloClass: 'bg-cyan-100 text-cyan-800 border-cyan-200',
        significado: 'Concentração de sais na água captada do estuário de Ceará-Mirim/RN.',
        sugerido: '10 a 25 ppt',
        ativo: '15 ppt',
        unidade: 'ppt (g/L)',
        impacto: 'Determina a osmorregulação, tempo de aclimatação das pós-larvas e cálculo de trocas de carapaça.'
      },
      {
        id: 'area_viveiro_padrao',
        codigo: 'AREA_VIV',
        nome: 'Critério de Área dos Viveiros no ERP',
        categoria: 'TOPOGRAFIA',
        moduloLabel: 'Topografia & Áreas',
        moduloClass: 'bg-emerald-100 text-emerald-800 border-emerald-200',
        significado: 'Define qual fonte de área de lâmina d\'água é usada para cálculo de densidade (PL/m²), produtividade (kg/ha) e dosagem por metro.',
        sugerido: 'Área Satélite GPS',
        ativo: 'Área Calibrada Pai (0.50 ha)',
        unidade: 'ha / m²',
        impacto: 'Pode ser alternado entre medição via satélite GPS ou a área histórica informada pelo produtor rural.'
      },
      {
        id: 'densidade_povoamento',
        codigo: 'DENSIDADE_PL',
        nome: 'Densidade de Povoamento Inicial',
        categoria: 'POVOAMENTO',
        moduloLabel: 'Povoamento & Berçário',
        moduloClass: 'bg-teal-100 text-teal-800 border-teal-200',
        significado: 'Número de pós-larvas estocadas por metro quadrado no início do cultivo ou após a transferência do berçário.',
        sugerido: '8 a 15 PL/m² (sem aeração pesada)',
        ativo: '12 PL/m²',
        unidade: 'PL/m²',
        impacto: 'Calcula a população inicial, necessidade de oxigênio de suporte e taxa de sobrevivência real final.'
      },
      {
        id: 'peso_transf_bercario',
        codigo: 'PESO_BERC',
        nome: 'Peso Alvo de Transferência do Berçário',
        categoria: 'POVOAMENTO',
        moduloLabel: 'Povoamento & Berçário',
        moduloClass: 'bg-teal-100 text-teal-800 border-teal-200',
        significado: 'Peso em gramas que os juvenis devem atingir no berçário antes da transferência para os viveiros de engorda.',
        sugerido: '1.5 a 3.0 g',
        ativo: '2.0 g',
        unidade: 'gramas (g)',
        impacto: 'Encurta o ciclo de engorda em 30 a 40 dias e aumenta drasticamente a sobrevivência na fase de engorda.'
      },
      {
        id: 'preco_venda_kg',
        codigo: 'PRECO_KG',
        nome: 'Preço Médio de Venda do Camarão',
        categoria: 'DESPESCA',
        moduloLabel: 'Despesca & Vendas',
        moduloClass: 'bg-indigo-100 text-indigo-800 border-indigo-200',
        significado: 'Cotação média em reais por quilo do camarão in natura colhido na despesca na região de Natal/RN.',
        sugerido: 'R$ 20,00 a R$ 26,00/kg',
        ativo: 'R$ 22,00/kg',
        unidade: 'R$/kg',
        impacto: 'Calcula o faturamento bruto de cada lote despescado e a margem de lucro operacional por viveiro.'
      },
      {
        id: 'gramatura_despesca_alvo',
        codigo: 'PESO_COLHEITA',
        nome: 'Gramatura Comercial Alvo de Despesca',
        categoria: 'DESPESCA',
        moduloLabel: 'Despesca & Vendas',
        moduloClass: 'bg-indigo-100 text-indigo-800 border-indigo-200',
        significado: 'Tamanho médio individual pretendido para encerramento da safra e atendimento dos compradores locais.',
        sugerido: '12.0g a 16.0g',
        ativo: '14.0g',
        unidade: 'gramas (g)',
        impacto: 'Sinaliza no dashboard quando o tanque atinge a janela ideal de despesca para corte de custos.'
      }
    ];

    let paramEditandoId = null;
    let chartDespescaVolInst = null;
    let chartDespescaFcaInst = null;

    // ========================================================
    // RENDERIZADOR DO MÓDULO DE DESPESCA & VENDAS
    // ========================================================
    function renderizarModuloDespesca() {
      // 1. Atualizar KPIs Consolidados
      let totKg = 0;
      let totReceita = 0;
      let somaFcaPond = 0;
      let somaSobrPond = 0;
      let somaPesoPond = 0;

      HISTORICO_SAFRAS_DATA.forEach(s => {
        totKg += s.kgColhido;
        totReceita += (s.faturamentoBruto || s.kgColhido * (s.precoVendaKg || 22.0));
        somaFcaPond += (s.fcaReal * s.kgColhido);
        somaSobrPond += (s.sobrevivenciaPct * s.kgColhido);
        somaPesoPond += (s.pesoFinalG * s.kgColhido);
      });

      const fcaPond = totKg > 0 ? (somaFcaPond / totKg).toFixed(2) : '1.21';
      const sobrPond = totKg > 0 ? (somaSobrPond / totKg).toFixed(1) : '58.1';
      const pesoPond = totKg > 0 ? (somaPesoPond / totKg).toFixed(1) : '15.2';

      const elKg = document.getElementById('kpi-despesca-total-kg');
      const elRec = document.getElementById('kpi-despesca-receita-total');
      const elFca = document.getElementById('kpi-despesca-fca-ponderado');
      const elSobr = document.getElementById('kpi-despesca-sobr-media');
      const elPeso = document.getElementById('kpi-despesca-peso-medio');
      const elCount = document.getElementById('kpi-despesca-tanques-count');

      if (elKg) elKg.innerText = `${totKg.toLocaleString('pt-BR')} kg`;
      if (elRec) elRec.innerText = `R$ ${Math.round(totReceita).toLocaleString('pt-BR')}`;
      if (elFca) elFca.innerText = fcaPond;
      if (elSobr) elSobr.innerText = `${sobrPond}%`;
      if (elPeso) elPeso.innerText = `${pesoPond} g`;
      if (elCount) elCount.innerText = `${HISTORICO_SAFRAS_DATA.length} safras encerradas`;

      // 2. Preencher Tabela de Safras Concluídas
      const tbody = document.getElementById('tbody-despescas-lista');
      if (tbody) {
        tbody.innerHTML = '';
        HISTORICO_SAFRAS_DATA.forEach(s => {
          const rec = s.faturamentoBruto || (s.kgColhido * (s.precoVendaKg || 22.0));
          const tr = document.createElement('tr');
          tr.className = 'hover:bg-slate-50 transition border-b border-slate-100 cursor-pointer';
          tr.onclick = () => {
            navegarPara('analytics-biomassa');
            selecionarViveiroBiomassa(s.viveiroId);
          };

          tr.innerHTML = `
            <td class="p-3 font-extrabold text-slate-900">
              <span class="text-indigo-900">${s.viveiroId}</span>
              <span class="ml-1.5 px-1.5 py-0.2 rounded text-[9px] font-bold bg-violet-100 text-violet-800 border border-violet-200">${s.lab}</span>
            </td>
            <td class="p-3 font-mono font-semibold text-slate-600">${s.safraId}</td>
            <td class="p-3 font-bold text-slate-800">${s.dataDespesca}</td>
            <td class="p-3 font-semibold text-slate-600">${s.ddcTotal} dias</td>
            <td class="p-3 font-mono font-black text-indigo-950 text-sm">${s.kgColhido.toLocaleString('pt-BR')} kg</td>
            <td class="p-3 font-mono font-bold text-amber-900">${s.pesoFinalG} g</td>
            <td class="p-3 font-bold ${s.sobrevivenciaPct >= 60 ? 'text-emerald-700' : 'text-amber-700'}">${s.sobrevivenciaPct}%</td>
            <td class="p-3">
              <span class="px-2 py-0.5 rounded font-mono font-extrabold text-[11px] ${s.fcaReal <= 1.25 ? 'bg-emerald-100 text-emerald-800 border border-emerald-200' : 'bg-amber-100 text-amber-800 border border-amber-200'}">
                ${s.fcaReal}
              </span>
            </td>
            <td class="p-3 font-mono text-slate-700">R$ ${(s.precoVendaKg || 22.0).toFixed(2)}</td>
            <td class="p-3 font-mono font-black text-emerald-900">R$ ${Math.round(rec).toLocaleString('pt-BR')}</td>
            <td class="p-3 text-slate-600 font-semibold">${s.comprador || 'Mercado Regional'}</td>
            <td class="p-3 text-center">
              <button onclick="event.stopPropagation(); navegarPara('analytics-biomassa'); selecionarViveiroBiomassa('${s.viveiroId}')" class="px-2.5 py-1 rounded-xl bg-indigo-50 hover:bg-indigo-100 text-indigo-800 font-bold text-[10px] border border-indigo-200 transition flex items-center gap-1 mx-auto">
                <i class="fa-solid fa-eye"></i> Ficha Safra
              </button>
            </td>
          `;
          tbody.appendChild(tr);
        });
      }

      // 3. Renderizar Gráficos de Despesca
      renderizarGraficosDespesca();
    }

    function renderizarGraficosDespescas() {
      renderizarGraficosDespesca();
    }

    function renderizarGraficosDespesca() {
      // Gráfico de Volume Colhido
      const ctxVol = document.getElementById('chart-despesca-volume');
      if (ctxVol && typeof Chart !== 'undefined') {
        if (chartDespescaVolInst) chartDespescaVolInst.destroy();
        const labels = HISTORICO_SAFRAS_DATA.map(s => `${s.viveiroId} (${s.pesoFinalG}g)`);
        const dadosKg = HISTORICO_SAFRAS_DATA.map(s => s.kgColhido);

        chartDespescaVolInst = new Chart(ctxVol, {
          type: 'bar',
          data: {
            labels: labels,
            datasets: [{
              label: 'Camarão Colhido (kg)',
              data: dadosKg,
              backgroundColor: ['#4F46E5', '#10B981', '#0EA5E9'],
              borderRadius: 8
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
              y: { beginAtZero: true, grid: { color: '#f1f5f9' } },
              x: { grid: { display: false } }
            }
          }
        });
      }

      // Gráfico Gramatura vs FCA
      const ctxFca = document.getElementById('chart-despesca-fca');
      if (ctxFca && typeof Chart !== 'undefined') {
        if (chartDespescaFcaInst) chartDespescaFcaInst.destroy();
        const labels = HISTORICO_SAFRAS_DATA.map(s => s.viveiroId);
        const fcas = HISTORICO_SAFRAS_DATA.map(s => s.fcaReal);
        const pesos = HISTORICO_SAFRAS_DATA.map(s => s.pesoFinalG);

        chartDespescaFcaInst = new Chart(ctxFca, {
          type: 'bar',
          data: {
            labels: labels,
            datasets: [
              {
                label: 'FCA Real',
                data: fcas,
                backgroundColor: '#14B8A6',
                borderRadius: 8,
                yAxisID: 'y'
              },
              {
                label: 'Gramatura Final (g)',
                data: pesos,
                type: 'line',
                borderColor: '#F59E0B',
                backgroundColor: '#F59E0B',
                borderWidth: 2,
                pointRadius: 4,
                yAxisID: 'y1'
              }
            ]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              y: { beginAtZero: false, min: 0.8, max: 1.8, grid: { color: '#f1f5f9' }, title: { display: true, text: 'FCA' } },
              y1: { beginAtZero: false, min: 10, max: 22, position: 'right', grid: { display: false }, title: { display: true, text: 'Gramatura (g)' } },
              x: { grid: { display: false } }
            }
          }
        });
      }
    }

    function abrirModalNovaDespesca() {
      const selectViv = document.getElementById('modal-desp-viv-id');
      if (selectViv) {
        selectViv.innerHTML = '';
        VIVEIROS_DATA.forEach(v => {
          const dados = DADOS_PLANILHA_VIVEIROS[v.id];
          const isAtivo = (dados && dados.statusLote !== 'DESPESCADO' && dados.tratos && dados.tratos.length > 0);
          const opt = document.createElement('option');
          opt.value = v.id;
          opt.innerText = `${v.nome} (${v.id}) - ${isAtivo ? '🟢 Em Cultivo' : '⚪ Outro'}`;
          selectViv.appendChild(opt);
        });
      }

      const inputData = document.getElementById('modal-desp-data');
      if (inputData) inputData.value = new Date().toISOString().split('T')[0];

      const modal = document.getElementById('modal-registro-despesca');
      if (modal) modal.classList.remove('hidden');
    }

    function fecharModalNovaDespesca() {
      const modal = document.getElementById('modal-registro-despesca');
      if (modal) modal.classList.add('hidden');
    }

    function salvarNovaDespesca(event) {
      event.preventDefault();
      const vivId = document.getElementById('modal-desp-viv-id').value;
      const dataStr = document.getElementById('modal-desp-data').value;
      const kg = parseFloat(document.getElementById('modal-desp-kg').value) || 0;
      const pesoG = parseFloat(document.getElementById('modal-desp-peso').value) || 0;
      const preco = parseFloat(document.getElementById('modal-desp-preco').value) || 22.0;
      const comprador = document.getElementById('modal-desp-comprador').value || 'Comprador Regional';
      const obs = document.getElementById('modal-desp-obs').value || '';

      const dataFormatada = formatarDataBr(dataStr);
      const dados = DADOS_PLANILHA_VIVEIROS[vivId] || {};
      const pls = dados.pls || 50;
      const sob = Math.round(((kg * 1000 / pesoG) / (pls * 1000)) * 100);

      const novaSafra = {
        safraId: `SAFRA-2026.1-${vivId}`,
        viveiroId: vivId,
        anoSafra: 2026,
        ciclo: 1,
        statusSafra: 'CONCLUIDA',
        dataPovoamento: dados.pov || '15/07/2026',
        dataDespesca: dataFormatada,
        ddcTotal: dados.tratos ? dados.tratos.length : 60,
        lab: dados.lab || 'AQUATEC',
        plsMil: pls,
        temBercario: Boolean(dados.tem_bercario),
        kgColhido: kg,
        pesoFinalG: pesoG,
        sobrevivenciaPct: sob,
        fcaReal: 1.25,
        precoVendaKg: preco,
        faturamentoBruto: kg * preco,
        comprador: comprador,
        obs: obs || `Despesca registrada no ERP em ${dataFormatada}`
      };

      // Atualiza estado do viveiro para DESPESCADO
      if (DADOS_PLANILHA_VIVEIROS[vivId]) {
        DADOS_PLANILHA_VIVEIROS[vivId].statusLote = 'DESPESCADO';
        DADOS_PLANILHA_VIVEIROS[vivId].despesca = {
          data: dataFormatada,
          doc: novaSafra.ddcTotal,
          kg_colhido: kg,
          peso_final_g: pesoG,
          sobrevivencia_pct: `${sob}%`,
          fca_real: 1.25,
          obs: obs
        };
      }

      // Adiciona ao início do histórico
      HISTORICO_SAFRAS_DATA.unshift(novaSafra);

      // Sincroniza e re-renderiza tudo
      sincronizarViveirosComPlanilhaReal();
      preencherTabelasAnaliticas();
      renderizarPillsViveirosBiomassa();
      renderizarModuloDespesca();

      fecharModalNovaDespesca();
      alert(`✅ Despesca do ${vivId} registrada com sucesso!\\n${kg} kg colhidos • Faturamento: R$ ${(kg*preco).toLocaleString('pt-BR')}`);
    }

    // ========================================================
    // RENDERIZADOR DA CENTRAL DE PARÂMETROS & CALIBRAÇÃO
    // ========================================================
    let filtroCategoriaParamAtiva = 'TODOS';

    function filtrarCategoriaParametros(cat) {
      filtroCategoriaParamAtiva = cat;
      document.querySelectorAll('.param-filter-btn').forEach(btn => {
        btn.className = 'param-filter-btn px-4 py-2 rounded-xl font-semibold bg-white text-slate-700 hover:bg-slate-100 border border-slate-200 transition whitespace-nowrap';
      });
      const btnAtivo = document.getElementById(`btn-param-filter-${cat}`);
      if (btnAtivo) {
        btnAtivo.className = 'param-filter-btn px-4 py-2 rounded-xl font-bold bg-slate-900 text-white shadow-xs transition whitespace-nowrap';
      }
      renderizarModuloParametros();
    }

    function renderizarModuloParametros() {
      const grid = document.getElementById('grid-cards-parametros');
      if (grid) {
        grid.innerHTML = '';
        const paramsFiltrados = (filtroCategoriaParamAtiva === 'TODOS')
          ? PARAMETROS_SISTEMA_DATA
          : PARAMETROS_SISTEMA_DATA.filter(p => p.categoria === filtroCategoriaParamAtiva);

        paramsFiltrados.forEach(p => {
          const card = document.createElement('div');
          card.className = 'bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3 hover:shadow-md transition';
          card.innerHTML = `
            <div class="flex items-start justify-between gap-2">
              <div>
                <span class="px-2 py-0.5 rounded text-[10px] font-extrabold border ${p.moduloClass}">${p.moduloLabel}</span>
                <h4 class="font-extrabold text-sm text-slate-900 mt-1">${p.nome}</h4>
              </div>
              <span class="font-mono font-black text-xs text-slate-500 bg-slate-100 px-2 py-0.5 rounded">${p.codigo}</span>
            </div>

            <p class="text-xs text-slate-600 font-medium leading-relaxed">${p.significado}</p>

            <div class="p-3 rounded-xl bg-slate-50 border border-slate-200 space-y-2 text-xs">
              <div class="flex items-center justify-between">
                <span class="text-slate-500 font-semibold text-[11px]">Padrão Recomendado (ABCC):</span>
                <span class="font-bold text-slate-700 font-mono">${p.sugerido}</span>
              </div>
              <div class="flex items-center justify-between border-t border-slate-200 pt-1.5">
                <span class="text-teal-950 font-extrabold text-[11px]">Ativo na Fazenda:</span>
                <span class="font-black text-teal-900 font-mono text-sm px-2 py-0.5 rounded bg-teal-100 border border-teal-300">${p.ativo}</span>
              </div>
            </div>

            <div class="text-[10px] text-slate-500 bg-blue-50/50 p-2 rounded-lg border border-blue-100 leading-tight">
              <strong>Impacto no ERP:</strong> ${p.impacto}
            </div>

            <div class="pt-1 flex items-center justify-end">
              <button onclick="abrirModalCalibrarParametro('${p.id}')" class="px-3 py-1.5 rounded-xl bg-teal-50 hover:bg-teal-100 text-teal-800 font-bold text-xs border border-teal-200 transition flex items-center gap-1.5 shadow-2xs">
                <i class="fa-solid fa-pen-to-square"></i> Calibrar Parâmetro
              </button>
            </div>
          `;
          grid.appendChild(card);
        });
      }

      // Preencher Tabela de Áreas dos 15 Viveiros
      renderizarTabelaCalibracaoAreas();
    }

    function renderizarTabelaCalibracaoAreas() {
      const tbody = document.getElementById('tbody-calibracao-areas');
      if (tbody) {
        tbody.innerHTML = '';
        VIVEIROS_DATA.forEach(v => {
          const areaSatHa = (v.areaSateliteM2 ? (v.areaSateliteM2 / 10000).toFixed(2) : (v.area_ha || 0.50));
          const areaSatM2 = v.areaSateliteM2 ? Math.round(v.areaSateliteM2).toLocaleString('pt-BR') : Math.round((v.area_ha || 0.50)*10000).toLocaleString('pt-BR');
          const areaPaiHa = (v.id === 'V-01' || v.id === 'V-02') ? 1.00 : 0.50;
          const areaAtual = (v.area_ha || 0.50);

          const tr = document.createElement('tr');
          tr.className = 'hover:bg-slate-50 transition border-b border-slate-100';
          tr.innerHTML = `
            <td class="p-2.5 font-bold text-slate-900">${v.nome} (${v.id})</td>
            <td class="p-2.5 font-mono text-slate-600">${areaSatM2} m²</td>
            <td class="p-2.5 font-mono font-semibold text-blue-900">${areaSatHa} ha</td>
            <td class="p-2.5 font-mono font-semibold text-amber-900">${areaPaiHa.toFixed(2)} ha</td>
            <td class="p-2.5">
              <input type="number" step="0.01" min="0.1" max="5.0" value="${areaAtual}" id="input-area-viv-${v.id}" onchange="atualizarAreaViveiroIndividual('${v.id}', this.value)" class="w-20 font-mono font-black text-xs p-1.5 rounded-lg border border-teal-400 bg-teal-50/40 text-teal-950 focus:outline-none">
            </td>
            <td class="p-2.5 text-slate-600">1.20 m</td>
            <td class="p-2.5 font-mono text-slate-800 font-bold">${Math.round(areaAtual * 10000 * 1.20).toLocaleString('pt-BR')} m³</td>
            <td class="p-2.5 text-center">
              <div class="flex items-center justify-center gap-1">
                <button onclick="definirAreaFonte('${v.id}', ${areaSatHa})" title="Usar Área Satélite" class="px-2 py-1 rounded bg-blue-50 hover:bg-blue-100 text-blue-800 font-bold text-[10px] border border-blue-200">
                  Satélite
                </button>
                <button onclick="definirAreaFonte('${v.id}', ${areaPaiHa})" title="Usar Área do Pai" class="px-2 py-1 rounded bg-amber-50 hover:bg-amber-100 text-amber-900 font-bold text-[10px] border border-amber-200">
                  Pai
                </button>
              </div>
            </td>
          `;
          tbody.appendChild(tr);
        });
      }
    }

    function definirAreaFonte(vId, valorHa) {
      atualizarAreaViveiroIndividual(vId, valorHa);
      const input = document.getElementById(`input-area-viv-${vId}`);
      if (input) input.value = valorHa;
    }

    function atualizarAreaViveiroIndividual(vId, novoHa) {
      const val = parseFloat(novoHa);
      if (isNaN(val) || val <= 0) return;

      const v = VIVEIROS_DATA.find(x => x.id === vId);
      if (v) {
        v.area_ha = val;
        v.areaHa = val;
        v.area_m2 = val * 10000;
        v.areaAjustadaM2 = val * 10000;
        v.volumeM3 = val * 10000 * (v.profundidadeM || 1.20);
      }
      if (DADOS_PLANILHA_VIVEIROS[vId]) {
        DADOS_PLANILHA_VIVEIROS[vId].area = val;
      }

      sincronizarViveirosComPlanilhaReal();
      preencherTabelasAnaliticas();
    }

    function aplicarAreaEmLote(tipo) {
      VIVEIROS_DATA.forEach(v => {
        let novaArea = 0.50;
        if (tipo === 'SATELITE') {
          novaArea = (v.areaSateliteM2 ? (v.areaSateliteM2 / 10000) : 0.50);
        } else {
          novaArea = (v.id === 'V-01' || v.id === 'V-02') ? 1.00 : 0.50;
        }
        atualizarAreaViveiroIndividual(v.id, novaArea);
      });
      renderizarTabelaCalibracaoAreas();
      alert(`✅ Todas as áreas dos 15 viveiros foram atualizadas para o padrão: ${tipo === 'SATELITE' ? 'Satélite GPS' : 'Área do Pai (Campo)'}`);
    }

    function abrirModalCalibrarParametro(paramId) {
      const p = PARAMETROS_SISTEMA_DATA.find(x => x.id === paramId);
      if (!p) return;
      paramEditandoId = paramId;

      document.getElementById('modal-param-titulo').innerText = `Calibrar: ${p.nome}`;
      document.getElementById('modal-param-modulo').innerText = `${p.moduloLabel} • Código: ${p.codigo}`;
      document.getElementById('modal-param-significado').innerText = p.significado;
      document.getElementById('modal-param-sugerido').innerText = `${p.sugerido} (${p.unidade})`;
      document.getElementById('modal-param-input-ativo').value = p.ativo;

      const modal = document.getElementById('modal-calibrar-parametro');
      if (modal) modal.classList.remove('hidden');
    }

    function fecharModalCalibrarParametro() {
      const modal = document.getElementById('modal-calibrar-parametro');
      if (modal) modal.classList.add('hidden');
      paramEditandoId = null;
    }

    function salvarParametroEditado() {
      if (!paramEditandoId) return;
      const novoValor = document.getElementById('modal-param-input-ativo').value.trim();
      if (!novoValor) return;

      const p = PARAMETROS_SISTEMA_DATA.find(x => x.id === paramEditandoId);
      if (p) {
        p.ativo = novoValor;
      }

      fecharModalCalibrarParametro();
      renderizarModuloParametros();
      alert(`✅ Parâmetro '${p.nome}' calibrado para '${novoValor}' com sucesso!`);
    }

    function restaurarParametrosPadrao() {
      if (!confirm('Deseja restaurar todos os parâmetros ativos para as faixas sugeridas pela literatura técnica (ABCC)?')) return;
      PARAMETROS_SISTEMA_DATA.forEach(p => {
        p.ativo = p.sugerido.split(' ')[0] || p.sugerido;
      });
      renderizarModuloParametros();
      alert('✅ Todos os parâmetros foram restaurados para os padrões técnicos recomendados!');
    }
"""

# Inserir o bloco de despesca e parâmetros antes do fechamento do script principal
p_script_close = html.rfind('</script>')
if p_script_close != -1:
    html = html[:p_script_close] + "\n" + bloco_dados_despesca_parametros_js + "\n  " + html[p_script_close:]
    print("Sucesso: Bloco JavaScript de Despesca, Parâmetros e Safras injetado antes de </script>!")
else:
    print("Erro: </script> não encontrado!")

HTML_PATH.write_text(html, encoding="utf-8")
print(f"dashboard_interativo_prototipo.html atualizado com sucesso! Tamanho final: {len(html)} bytes.")
