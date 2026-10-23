"""
Script para modernizar o Dashboard Principal (view-dashboard-macro):
1. Remove o bloco de auditoria (#secao-auditoria);
2. Substitui os KPIs antigos pela Régua de Produção nos 3 Horizontes (Atual, Ano 2026 e Suprimentos);
3. Adiciona o Painel Rápido de Manejo Diário (Arraçoamento de Hoje e Radar de Água / Janela de Despesca);
4. Reformula a Seção dos 15 Viveiros com filtros inteligentes e Cards Modernos interativos;
5. Atualiza renderizarMapaViveiros() e filtrarViveiros() no JavaScript.
"""
import shutil
from pathlib import Path

BASE_DIR = Path(r"G:\Meu Drive\ANTIGRAVITY DRIVE\CAMARÃO\ERP CAMARÃO")
HTML_PATH = BASE_DIR / "dashboard_interativo_prototipo.html"
BACKUP_PATH = BASE_DIR / "dashboard_interativo_prototipo.backup_antes_modernizacao_macro.html"

shutil.copy2(HTML_PATH, BACKUP_PATH)
print(f"Backup gravado em: {BACKUP_PATH}")

html = HTML_PATH.read_text(encoding="utf-8")

# 1. Localizar o início de view-dashboard-macro e o fim do banner pai
p_macro = html.find('id="view-dashboard-macro"')
if p_macro == -1: p_macro = html.find('view-dashboard-macro')

p_pai_banner_end = html.find('</div>', html.find('id="view-pai-banner"', p_macro)) + 6
# Localizar o fim da seção view-dashboard-macro
p_secao_mapa = html.find('id="secao-mapa-viveiros"', p_macro)
p_macro_close = html.find('</section>', p_secao_mapa)

novo_conteudo_dashboard_macro = """

        <!-- ======================================================== -->
        <!-- 1. RÉGUA DE PRODUÇÃO NOS TRÊS HORIZONTES                -->
        <!-- ======================================================== -->
        <div>
          <div class="flex items-center justify-between mb-3">
            <h2 class="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-2">
              <i class="fa-solid fa-chart-line text-aco"></i> Desempenho da Produção & Manejo da Fazenda
              <span class="text-[11px] font-normal text-slate-400 capitalize">(Acompanhamento executivo e zootécnico diário)</span>
            </h2>
            <span class="text-xs text-aco font-semibold flex items-center gap-1 hover:underline cursor-pointer" onclick="navegarPara('analytics-despesca')">
              Ver histórico de safras <i class="fa-solid fa-arrow-right text-[10px]"></i>
            </span>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            
            <!-- Card 1: Produção Atual em Água -->
            <div onclick="navegarPara('analytics-biomassa')" class="clickable-kpi bg-white rounded-2xl p-5 border border-slate-200 shadow-sm relative overflow-hidden group hover:border-aco hover:shadow-md transition">
              <div class="absolute top-0 right-0 w-28 h-28 bg-blue-50 rounded-bl-full -mr-6 -mt-6 transition group-hover:bg-blue-100"></div>
              
              <div class="flex items-center justify-between text-slate-500 mb-2 relative z-10">
                <span class="text-xs font-extrabold uppercase tracking-wider text-slate-700 flex items-center gap-1.5">
                  <i class="fa-solid fa-shrimp text-aco text-sm"></i> Produção Atual em Água
                </span>
                <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-200">
                  🟢 4 Viveiros Ativos
                </span>
              </div>

              <div class="flex items-baseline space-x-2 relative z-10 my-1">
                <span id="kpi-macro-biomassa-atual" class="text-3xl font-black text-slate-900 font-mono">28.500</span>
                <span class="text-sm font-bold text-slate-500">kg vivos</span>
              </div>

              <div class="text-xs font-semibold text-slate-500 relative z-10 mb-2">
                Valor biológico est.: <strong class="text-emerald-800 font-mono">R$ 627.000</strong> (R$ 22/kg)
              </div>

              <div class="pt-2 border-t border-slate-100 flex items-center justify-between text-[11px] relative z-10">
                <span class="text-emerald-700 font-bold flex items-center gap-1">
                  <i class="fa-solid fa-arrow-trend-up"></i> +1.250 kg/semana
                </span>
                <span class="text-aco font-bold group-hover:translate-x-0.5 transition flex items-center gap-1">
                  Ver Tanques <i class="fa-solid fa-chevron-right text-[9px]"></i>
                </span>
              </div>
            </div>

            <!-- Card 2: Produção da Safra / Ano 2026 -->
            <div onclick="navegarPara('analytics-despesca')" class="clickable-kpi bg-white rounded-2xl p-5 border border-slate-200 shadow-sm relative overflow-hidden group hover:border-indigo-400 hover:shadow-md transition">
              <div class="absolute top-0 right-0 w-28 h-28 bg-indigo-50 rounded-bl-full -mr-6 -mt-6 transition group-hover:bg-indigo-100"></div>
              
              <div class="flex items-center justify-between text-slate-500 mb-2 relative z-10">
                <span class="text-xs font-extrabold uppercase tracking-wider text-indigo-950 flex items-center gap-1.5">
                  <i class="fa-solid fa-award text-indigo-600 text-sm"></i> Produção Ano 2026 (Colhida)
                </span>
                <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-indigo-100 text-indigo-800 border border-indigo-200">
                  🏆 3 Safras Concluídas
                </span>
              </div>

              <div class="flex items-baseline space-x-2 relative z-10 my-1">
                <span id="kpi-macro-colheita-ano" class="text-3xl font-black text-indigo-950 font-mono">1.363</span>
                <span class="text-sm font-bold text-slate-500">kg despescados</span>
              </div>

              <div class="text-xs font-semibold text-slate-500 relative z-10 mb-2">
                Receita bruta real: <strong class="text-emerald-700 font-mono">R$ 31.172</strong> (Média R$ 22,87/kg)
              </div>

              <div class="pt-2 border-t border-slate-100 flex items-center justify-between text-[11px] relative z-10">
                <span class="text-teal-700 font-extrabold flex items-center gap-1">
                  <i class="fa-solid fa-scale-balanced"></i> FCA Médio: 1.21
                </span>
                <span class="text-indigo-600 font-bold group-hover:translate-x-0.5 transition flex items-center gap-1">
                  Despescas & Vendas <i class="fa-solid fa-chevron-right text-[9px]"></i>
                </span>
              </div>
            </div>

            <!-- Card 3: Arraçoamento do Dia & Estoque -->
            <div onclick="navegarPara('analytics-arracoamento')" class="clickable-kpi bg-white rounded-2xl p-5 border border-slate-200 shadow-sm relative overflow-hidden group hover:border-amber-400 hover:shadow-md transition">
              <div class="absolute top-0 right-0 w-28 h-28 bg-amber-50 rounded-bl-full -mr-6 -mt-6 transition group-hover:bg-amber-100"></div>
              
              <div class="flex items-center justify-between text-slate-500 mb-2 relative z-10">
                <span class="text-xs font-extrabold uppercase tracking-wider text-amber-950 flex items-center gap-1.5">
                  <i class="fa-solid fa-wheat-awn text-amber-600 text-sm"></i> Consumo de Ração Hoje
                </span>
                <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-900 border border-amber-200">
                  🌾 ~27.4 sacos/dia
                </span>
              </div>

              <div class="flex items-baseline space-x-2 relative z-10 my-1">
                <span id="kpi-macro-racao-hoje" class="text-3xl font-black text-amber-950 font-mono">685</span>
                <span class="text-sm font-bold text-slate-500">kg previstos</span>
              </div>

              <div class="text-xs font-semibold text-slate-500 relative z-10 mb-2">
                Estoque no galpão: <strong class="text-slate-800 font-mono">14 Dias</strong> (380 sacos Guabi 35%)
              </div>

              <div class="pt-2 border-t border-slate-100 flex items-center justify-between text-[11px] relative z-10">
                <span class="text-amber-800 font-bold flex items-center gap-1">
                  <i class="fa-solid fa-clock"></i> 2 Turnos Programados
                </span>
                <span class="text-amber-700 font-bold group-hover:translate-x-0.5 transition flex items-center gap-1">
                  Ver Bandejas <i class="fa-solid fa-chevron-right text-[9px]"></i>
                </span>
              </div>
            </div>

          </div>
        </div>

        <!-- ======================================================== -->
        <!-- 2. PAINEL RÁPIDO DE MANEJO DIÁRIO (OPERACIONAL)         -->
        <!-- ======================================================== -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
          
          <!-- Bloco A: Tratos do Dia & Bandejas -->
          <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
            <div class="flex items-center justify-between border-b border-slate-100 pb-2.5">
              <div class="flex items-center gap-2">
                <div class="w-8 h-8 rounded-lg bg-amber-100 text-amber-700 flex items-center justify-center text-sm">
                  <i class="fa-solid fa-bowl-food"></i>
                </div>
                <div>
                  <h3 class="text-xs font-bold text-slate-900 uppercase tracking-wider">Arraçoamento & Tratos de Hoje</h3>
                  <p class="text-[10px] text-slate-400">Distribuição nos turnos e leitura das bandejas de sobra</p>
                </div>
              </div>
              <button onclick="navegarPara('analytics-arracoamento')" class="text-xs font-bold text-aco hover:underline flex items-center gap-1">
                Tabela Completa <i class="fa-solid fa-arrow-right text-[9px]"></i>
              </button>
            </div>

            <div class="grid grid-cols-2 gap-3 text-xs">
              <div class="p-3 rounded-xl bg-amber-50/60 border border-amber-200/70 space-y-1">
                <span class="text-[10px] font-bold text-amber-900 uppercase flex items-center gap-1">
                  <i class="fa-solid fa-sun text-amber-500"></i> Trato A (Manhã - 07h)
                </span>
                <div class="text-lg font-black text-amber-950 font-mono">350 kg</div>
                <span class="text-[10px] text-emerald-700 font-semibold flex items-center gap-1">
                  <i class="fa-solid fa-circle-check"></i> 100% Lançado & Limpo
                </span>
              </div>

              <div class="p-3 rounded-xl bg-amber-50/60 border border-amber-200/70 space-y-1">
                <span class="text-[10px] font-bold text-amber-900 uppercase flex items-center gap-1">
                  <i class="fa-solid fa-cloud-sun text-amber-600"></i> Trato B (Tarde - 16h)
                </span>
                <div class="text-lg font-black text-amber-950 font-mono">335 kg</div>
                <span class="text-[10px] text-slate-600 font-medium">
                  Programado para distribuição
                </span>
              </div>
            </div>

            <!-- Alerta de Sobras de Bandejas -->
            <div class="p-2.5 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-between text-xs">
              <div class="flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-amber-500"></span>
                <span class="text-slate-700 font-medium text-[11px]">
                  <strong>1 Viveiro com Sobra Moderada:</strong> V-08 registrou Sobra Nível 2 (10-20%).
                </span>
              </div>
              <span class="text-[10px] font-bold text-amber-800 bg-amber-100 px-2 py-0.5 rounded border border-amber-200">
                Corte de 10% Recomendado
              </span>
            </div>
          </div>

          <!-- Bloco B: Radar Crítico da Água & Próximas Despescas -->
          <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
            <div class="flex items-center justify-between border-b border-slate-100 pb-2.5">
              <div class="flex items-center gap-2">
                <div class="w-8 h-8 rounded-lg bg-cyan-100 text-cyan-700 flex items-center justify-center text-sm">
                  <i class="fa-solid fa-heart-pulse"></i>
                </div>
                <div>
                  <h3 class="text-xs font-bold text-slate-900 uppercase tracking-wider">Radar de Água & Janela de Despesca</h3>
                  <p class="text-[10px] text-slate-400">Parâmetros noturnos críticos e lotes prontos para colheita</p>
                </div>
              </div>
              <button onclick="navegarPara('analytics-agua')" class="text-xs font-bold text-aco hover:underline flex items-center gap-1">
                Ver Medições <i class="fa-solid fa-arrow-right text-[9px]"></i>
              </button>
            </div>

            <div class="grid grid-cols-2 gap-3 text-xs">
              <!-- Radar Oxigênio -->
              <div class="p-3 rounded-xl bg-blue-50/60 border border-blue-200/70 space-y-1">
                <span class="text-[10px] font-bold text-blue-900 uppercase flex items-center gap-1">
                  <i class="fa-solid fa-droplet text-cyan-500"></i> Menor O₂ Madrugada
                </span>
                <div class="text-lg font-black text-slate-900 font-mono">
                  3.1 mg/L <span class="text-xs font-bold text-amber-600">(V-08)</span>
                </div>
                <span class="text-[10px] text-amber-700 font-semibold flex items-center gap-1">
                  <i class="fa-solid fa-triangle-exclamation"></i> Aerador acionado das 03h às 06h
                </span>
              </div>

              <!-- Janela de Despesca -->
              <div class="p-3 rounded-xl bg-indigo-50/60 border border-indigo-200/70 space-y-1">
                <span class="text-[10px] font-bold text-indigo-900 uppercase flex items-center gap-1">
                  <i class="fa-solid fa-trophy text-indigo-500"></i> Despescas Recentes
                </span>
                <div class="text-lg font-black text-indigo-950 font-mono">
                  3 Tanques <span class="text-xs font-bold text-emerald-600">(Concluídos)</span>
                </div>
                <span class="text-[10px] text-slate-600 font-medium">
                  V-03 (13.5g), V-05 (17.2g), V-06 (14.0g)
                </span>
              </div>
            </div>

            <!-- Status do Estuário Ceará-Mirim -->
            <div class="p-2.5 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-between text-xs">
              <div class="flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
                <span class="text-slate-700 font-medium text-[11px]">
                  <strong>Captação do Rio Ceará-Mirim:</strong> Maré alta às 15h40 • Salinidade 15 ppt • pH 7.8
                </span>
              </div>
              <span class="text-[10px] font-bold text-emerald-800 bg-emerald-100 px-2 py-0.5 rounded border border-emerald-200">
                Água Excelente
              </span>
            </div>
          </div>

        </div>

        <!-- ======================================================== -->
        <!-- 3. VISÃO INTELIGENTE & MODERNA DOS 15 VIVEIROS           -->
        <!-- ======================================================== -->
        <div id="secao-mapa-viveiros" class="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-4">
          <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-slate-100 pb-3">
            <div>
              <h3 class="text-base font-extrabold text-slate-900 flex items-center gap-2">
                <i class="fa-solid fa-grip text-aco"></i> Monitoramento Operacional dos 15 Viveiros
              </h3>
              <p class="text-xs text-slate-500">Cards inteligentes com biometria, consumo de ração e status zootécnico. Clique para abrir a ficha do viveiro.</p>
            </div>

            <!-- Filtros Rápidos por Status com Contadores -->
            <div class="flex flex-wrap items-center gap-1.5 text-xs bg-slate-100 p-1 rounded-xl">
              <button onclick="filtrarViveiros('todos')" id="filter-todos" class="px-2.5 py-1 rounded-lg font-bold bg-white text-slate-800 shadow-sm">
                Todos (<span id="count-viv-todos">15</span>)
              </button>
              <button onclick="filtrarViveiros('otimo')" id="filter-otimo" class="px-2.5 py-1 rounded-lg font-medium text-slate-600 hover:text-slate-900">
                🟢 Em Cultivo (<span id="count-viv-otimo">4</span>)
              </button>
              <button onclick="filtrarViveiros('despescado')" id="filter-despescado" class="px-2.5 py-1 rounded-lg font-medium text-slate-600 hover:text-slate-900">
                🟡 Despescados (<span id="count-viv-desp">3</span>)
              </button>
              <button onclick="filtrarViveiros('bercario')" id="filter-bercario" class="px-2.5 py-1 rounded-lg font-medium text-slate-600 hover:text-slate-900">
                🐣 Berçários (<span id="count-viv-berc">4</span>)
              </button>
              <button onclick="filtrarViveiros('vazio')" id="filter-vazio" class="px-2.5 py-1 rounded-lg font-medium text-slate-600 hover:text-slate-900">
                ⚪ Em Preparação (<span id="count-viv-vazio">4</span>)
              </button>
            </div>
          </div>

          <!-- Grid com os 15 Cards de Viveiros Modernos -->
          <div id="grid-mapa-viveiros" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3.5 pt-1">
            <!-- Injetado dinamicamente via JS com cards inteligentes -->
          </div>
        </div>
"""

# Substituir o miolo de view-dashboard-macro
html_novo = html[:p_pai_banner_end] + novo_conteudo_dashboard_macro + "\n      " + html[p_macro_close:]
print("Sucesso: Estrutura HTML do view-dashboard-macro modernizada!")

# ==============================================================================
# 2. ATUALIZAR FUNÇÃO renderizarMapaViveiros() e filtrarViveiros() NO JS
# ==============================================================================
idx_func_mapa = html_novo.find('function renderizarMapaViveiros()')
idx_func_mapa_end = html_novo.find('// 4. Central de Notificações', idx_func_mapa)
if idx_func_mapa_end == -1:
    idx_func_mapa_end = html_novo.find('function abrirModalPreenchimentoRapido', idx_func_mapa)

nova_funcao_mapa_js = """function renderizarMapaViveiros() {
      const grid = document.getElementById('grid-mapa-viveiros');
      if (!grid) return;
      grid.innerHTML = '';

      // 1. Atualizar Contadores dos Filtros
      let countCultivo = 0;
      let countDesp = 0;
      let countBerc = 0;
      let countPrep = 0;

      VIVEIROS_DATA.forEach(v => {
        const dados = DADOS_PLANILHA_VIVEIROS[v.id] || {};
        const isDesp = (dados.statusLote === 'DESPESCADO' || v.status === 'despescado');
        const isBerc = Boolean(dados.tem_bercario);
        const isAtivo = (dados.statusLote === 'EM CULTIVO ATIVO' || v.status === 'otimo' || v.status === 'atencao');

        if (isDesp) countDesp++;
        else if (isAtivo) {
          countCultivo++;
          if (isBerc) countBerc++;
        } else {
          countPrep++;
        }
      });

      const elCAll = document.getElementById('count-viv-todos');
      const elCCult = document.getElementById('count-viv-otimo');
      const elCDesp = document.getElementById('count-viv-desp');
      const elCBerc = document.getElementById('count-viv-berc');
      const elCPrep = document.getElementById('count-viv-vazio');

      if (elCAll) elCAll.innerText = VIVEIROS_DATA.length;
      if (elCCult) elCCult.innerText = countCultivo;
      if (elCDesp) elCDesp.innerText = countDesp;
      if (elCBerc) elCBerc.innerText = countBerc;
      if (elCPrep) elCPrep.innerText = countPrep;

      // 2. Filtragem dos Viveiros
      const filtrados = VIVEIROS_DATA.filter(v => {
        const dados = DADOS_PLANILHA_VIVEIROS[v.id] || {};
        const isDesp = (dados.statusLote === 'DESPESCADO' || v.status === 'despescado');
        const isBerc = Boolean(dados.tem_bercario);
        const isAtivo = (dados.statusLote === 'EM CULTIVO ATIVO' || v.status === 'otimo' || v.status === 'atencao');

        if (currentFilter === 'todos') return true;
        if (currentFilter === 'otimo') return isAtivo && !isDesp;
        if (currentFilter === 'despescado') return isDesp;
        if (currentFilter === 'bercario') return isBerc && isAtivo;
        if (currentFilter === 'vazio') return !isAtivo && !isDesp;
        return true;
      });

      // 3. Renderizar Cards Inteligentes e Modernos
      filtrados.forEach(v => {
        const dados = DADOS_PLANILHA_VIVEIROS[v.id] || { lab: 'Nenhum', pls: 0, pov: '-', tratos: [] };
        const isDesp = (dados.statusLote === 'DESPESCADO' || v.status === 'despescado');
        const isAtivo = (dados.statusLote === 'EM CULTIVO ATIVO' || v.status === 'otimo' || v.status === 'atencao');
        const isBerc = Boolean(dados.tem_bercario);

        let borderClass = 'border-slate-200 hover:border-slate-400';
        let bgHeader = 'bg-slate-100 text-slate-700';
        let badgeStatus = '<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-200 text-slate-700">⚪ Preparo</span>';

        if (isDesp) {
          borderClass = 'border-amber-300 hover:border-amber-500 shadow-amber-50/50 bg-amber-50/20';
          bgHeader = 'bg-amber-100/70 text-amber-950 border-b border-amber-200';
          badgeStatus = '<span class="px-2 py-0.5 rounded text-[10px] font-extrabold bg-amber-200 text-amber-900 border border-amber-300">🟡 Despescado</span>';
        } else if (isAtivo) {
          if (v.status === 'atencao') {
            borderClass = 'border-yellow-300 hover:border-yellow-500 shadow-yellow-50/50';
            bgHeader = 'bg-yellow-100/70 text-yellow-950 border-b border-yellow-200';
            badgeStatus = '<span class="px-2 py-0.5 rounded text-[10px] font-extrabold bg-yellow-200 text-yellow-900 border border-yellow-300">🟡 O₂ Atenção</span>';
          } else {
            borderClass = 'border-emerald-300 hover:border-emerald-500 shadow-emerald-50/50';
            bgHeader = 'bg-emerald-100/70 text-emerald-950 border-b border-emerald-200';
            badgeStatus = '<span class="px-2 py-0.5 rounded text-[10px] font-extrabold bg-emerald-200 text-emerald-900 border border-emerald-300">🟢 Em Cultivo</span>';
          }
        }

        const labTag = dados.lab && dados.lab !== 'Nenhum'
          ? `<span class="px-1.5 py-0.2 rounded text-[9px] font-black bg-violet-100 text-violet-800 border border-violet-200">${dados.lab}</span>`
          : '';

        const card = document.createElement('div');
        card.className = `clickable-kpi bg-white rounded-2xl border ${borderClass} shadow-sm overflow-hidden flex flex-col justify-between transition group hover:shadow-md cursor-pointer`;
        card.onclick = () => {
          navegarPara('analytics-biomassa');
          selecionarViveiroBiomassa(v.id);
        };

        let mioloHtml = '';

        if (isDesp && dados.despesca) {
          // Card Especial Despescado
          mioloHtml = `
            <div class="p-3 space-y-2 text-xs">
              <div class="flex items-center justify-between text-slate-500 text-[11px]">
                <span>Área: <strong class="text-slate-800">${v.area_ha || 0.50} ha</strong></span>
                <span class="text-amber-800 font-bold">${dados.despesca.doc || v.ddc} d (Final)</span>
              </div>

              <div class="p-2 rounded-xl bg-amber-50 border border-amber-200/80 space-y-1">
                <div class="flex items-center justify-between">
                  <span class="text-[10px] font-bold text-amber-900 uppercase">Colheita Real:</span>
                  <span class="font-black text-amber-950 font-mono text-sm">${dados.despesca.kg_colhido} kg</span>
                </div>
                <div class="flex items-center justify-between text-[11px]">
                  <span class="text-slate-600">Peso Final:</span>
                  <span class="font-extrabold text-amber-900 font-mono">${dados.despesca.peso_final_g} g</span>
                </div>
              </div>

              <div class="flex items-center justify-between text-[11px] pt-1 border-t border-slate-100">
                <span class="text-slate-500">FCA Real: <strong class="text-emerald-700 font-mono">${dados.despesca.fca_real || 1.25}</strong></span>
                <span class="text-slate-500">Sobr.: <strong class="text-slate-800">${dados.despesca.sobrevivencia_pct || '-'}</strong></span>
              </div>
            </div>
          `;
        } else if (isAtivo) {
          // Card Em Cultivo Ativo
          const o2Val = (v.id === 'V-08') ? 3.1 : 5.4;
          mioloHtml = `
            <div class="p-3 space-y-2 text-xs">
              <div class="flex items-center justify-between text-slate-500 text-[11px]">
                <span>Área: <strong class="text-slate-800">${v.area_ha || 0.50} ha</strong></span>
                <span>DDC: <strong class="text-slate-800">${v.ddc || 40} d</strong></span>
              </div>

              <div class="grid grid-cols-2 gap-1.5 p-2 rounded-xl bg-slate-50 border border-slate-100 text-center">
                <div>
                  <span class="text-[9px] font-bold text-slate-400 uppercase block">Peso Médio</span>
                  <span class="font-black text-aco font-mono text-xs">${v.pesoMedio > 0 ? v.pesoMedio + ' g' : '11.5 g'}</span>
                </div>
                <div>
                  <span class="text-[9px] font-bold text-slate-400 uppercase block">Biomassa Est.</span>
                  <span class="font-extrabold text-slate-800 font-mono text-xs">${v.biomassaKg > 0 ? v.biomassaKg.toLocaleString('pt-BR') + ' kg' : '2.100 kg'}</span>
                </div>
              </div>

              <div class="flex items-center justify-between text-[11px] pt-1 border-t border-slate-100">
                <span class="text-slate-500">Ração Hoje: <strong class="text-amber-800 font-mono">${v.racaoHojeKg || 25} kg</strong></span>
                <span class="text-slate-500">O₂: <strong class="${o2Val < 3.5 ? 'text-amber-600 font-black' : 'text-slate-800 font-mono'}">${o2Val} mg/L</strong></span>
              </div>
            </div>
          `;
        } else {
          // Card em Preparação / Vazio
          mioloHtml = `
            <div class="p-3 space-y-2 text-xs text-center text-slate-400">
              <div class="text-[11px] text-slate-500">Área: <strong class="text-slate-700">${v.area_ha || 0.50} ha</strong></div>
              <div class="p-3 rounded-xl bg-slate-50 border border-slate-100 my-2">
                <i class="fa-solid fa-water-ladder text-slate-300 text-lg mb-1 block"></i>
                <span class="text-[10px] text-slate-500 font-medium">Secagem de fundo e calagem programada</span>
              </div>
              <div class="text-[10px] font-semibold text-slate-400">Disponível para próximo lote</div>
            </div>
          `;
        }

        card.innerHTML = `
          <div>
            <div class="${bgHeader} px-3 py-2 flex items-center justify-between">
              <div class="flex items-center space-x-1.5">
                <span class="font-black text-xs text-slate-900">${v.nome}</span>
                ${labTag}
              </div>
              ${badgeStatus}
            </div>

            ${mioloHtml}
          </div>

          <div class="px-3 py-1.5 bg-slate-50/70 border-t border-slate-100 flex items-center justify-between text-[10px]">
            <span class="font-bold text-slate-500">${isBerc ? '🐣 Berçário' : 'Engorda'}</span>
            <span class="font-bold text-aco group-hover:underline flex items-center gap-1">
              Ver Tanque <i class="fa-solid fa-arrow-right text-[8px]"></i>
            </span>
          </div>
        `;

        grid.appendChild(card);
      });
    }

    function filtrarViveiros(status) {
      currentFilter = status;
      ['todos', 'otimo', 'despescado', 'bercario', 'vazio'].forEach(s => {
        const btn = document.getElementById(`filter-${s}`);
        if (btn) {
          if (s === status) {
            btn.className = 'px-2.5 py-1 rounded-lg font-bold bg-white text-slate-900 shadow-sm border border-slate-200';
          } else {
            btn.className = 'px-2.5 py-1 rounded-lg font-medium text-slate-600 hover:text-slate-900';
          }
        }
      });
      renderizarMapaViveiros();
    }
"""

if idx_func_mapa != -1 and idx_func_mapa_end != -1:
    html_novo = html_novo[:idx_func_mapa] + nova_funcao_mapa_js + "\n\n    " + html_novo[idx_func_mapa_end:]
    print("Sucesso: Funções renderizarMapaViveiros() e filtrarViveiros() atualizadas no JavaScript!")
else:
    print(f"Aviso: Não foi possível localizar os limites exatos da função mapa: {idx_func_mapa}, {idx_func_mapa_end}")

HTML_PATH.write_text(html_novo, encoding="utf-8")
print(f"dashboard_interativo_prototipo.html atualizado com sucesso! Novo tamanho: {len(html_novo)} bytes.")
