"""Script para implementar o novo Módulo Mapa dos Viveiros 2D com dupla metragem e numeração do pai."""
import re
import shutil
from pathlib import Path

HTML_PATH = Path(r"G:\Meu Drive\ANTIGRAVITY DRIVE\CAMARÃO\ERP CAMARÃO\dashboard_interativo_prototipo.html")
BACKUP_PATH = Path(r"G:\Meu Drive\ANTIGRAVITY DRIVE\CAMARÃO\ERP CAMARÃO\dashboard_interativo_prototipo.backup_mapa2d.html")

shutil.copy2(HTML_PATH, BACKUP_PATH)
print(f"Backup de segurança criado em {BACKUP_PATH}")

conteudo = HTML_PATH.read_text(encoding="utf-8")

# 1. Nova View Completa: view-viveiros-mapa
nova_secao_mapa = """
      <!-- ======================================================== -->
      <!-- VIEW: MÓDULO MAPA DOS VIVEIROS 2D & CALIBRAÇÃO          -->
      <!-- ======================================================== -->
      <section id="view-viveiros-mapa" class="hidden space-y-6">
        
        <!-- Header da Página do Mapa com Alternador Híbrido -->
        <div class="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4 bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <div class="space-y-1">
            <div class="flex items-center space-x-2 text-xs font-semibold text-aco">
              <span class="cursor-pointer hover:underline" onclick="navegarPara('dashboard-macro')">Dashboard</span>
              <i class="fa-solid fa-chevron-right text-[10px] text-slate-400"></i>
              <span>Topografia</span>
              <i class="fa-solid fa-chevron-right text-[10px] text-slate-400"></i>
              <span class="text-slate-600">Mapa dos Viveiros 2D</span>
            </div>
            <h2 class="text-xl font-bold text-slate-900 flex items-center gap-2">
              <i class="fa-solid fa-map-location-dot text-aco"></i> Mapa dos Viveiros & Mapeamento Topográfico
            </h2>
            <p class="text-xs text-slate-500">Fazenda Ceará-Mirim/RN • Coordenadas: 5°40'17.1"S 35°15'04.2"W • Levantamento Aerofotogramétrico do Google Maps & Calibração de Campo</p>
          </div>

          <!-- Controles do Mapa: Alternador Satélite / Vetorial e Filtros -->
          <div class="flex flex-wrap items-center gap-2">
            <!-- Alternador de Camada (Vetorial vs Satélite) -->
            <div class="bg-slate-100 p-1 rounded-xl flex items-center border border-slate-200 shadow-inner">
              <button id="btn-camada-vetorial" onclick="alternarCamadaMapa('vetorial')" class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition bg-white text-slate-900 shadow-sm">
                <i class="fa-solid fa-layer-group text-aco"></i>
                <span>Vetorial Técnico</span>
              </button>
              <button id="btn-camada-satelite" onclick="alternarCamadaMapa('satelite')" class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold text-slate-600 hover:text-slate-900 transition">
                <i class="fa-solid fa-satellite text-emerald-600"></i>
                <span>🛰️ Imagem de Satélite</span>
              </button>
            </div>

            <!-- Botão Voltar -->
            <button onclick="navegarPara('dashboard-macro')" class="px-3.5 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs transition flex items-center gap-1.5">
              <i class="fa-solid fa-arrow-left"></i> Voltar
            </button>
          </div>
        </div>

        <!-- Cards de Resumo Topográfico da Fazenda -->
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4">
          <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm">
            <span class="text-[11px] font-bold text-slate-500 uppercase flex items-center gap-1">
              <i class="fa-solid fa-satellite text-aco"></i> Área Satélite (Google)
            </span>
            <div id="kpi-topo-area-satelite" class="text-xl sm:text-2xl font-extrabold text-slate-900 mt-1">12,83 ha</div>
            <span class="text-[10px] text-slate-500 block mt-0.5">128.335 m² aerofotogramétricos</span>
          </div>

          <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm border-l-4 border-l-emerald-500">
            <span class="text-[11px] font-bold text-slate-500 uppercase flex items-center gap-1">
              <i class="fa-solid fa-ruler-combined text-emerald-600"></i> Área Calibrada Oficial
            </span>
            <div id="kpi-topo-area-ajustada" class="text-xl sm:text-2xl font-extrabold text-emerald-700 mt-1">12,83 ha</div>
            <span class="text-[10px] text-emerald-600 font-semibold block mt-0.5">Metragem oficial vigente</span>
          </div>

          <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm">
            <span class="text-[11px] font-bold text-slate-500 uppercase flex items-center gap-1">
              <i class="fa-solid fa-water text-blue-500"></i> Volume Total d'Água
            </span>
            <div id="kpi-topo-volume" class="text-xl sm:text-2xl font-extrabold text-blue-700 mt-1">154.002 m³</div>
            <span class="text-[10px] text-slate-500 block mt-0.5">Lâmina média: 1,20m</span>
          </div>

          <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm">
            <span class="text-[11px] font-bold text-slate-500 uppercase flex items-center gap-1">
              <i class="fa-solid fa-boxes-stacked text-purple-600"></i> Estrutura da Fazenda
            </span>
            <div class="text-xl sm:text-2xl font-extrabold text-purple-900 mt-1">10 + 5 Tanques</div>
            <span class="text-[10px] text-slate-500 block mt-0.5">10 Engorda Pai + 2 Berç. + 3 Apoio</span>
          </div>
        </div>

        <!-- CONTAINER DO MAPA 2D (CAMADA HÍBRIDA) -->
        <div class="bg-white rounded-3xl p-5 border border-slate-200 shadow-sm space-y-4">
          
          <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-3 border-b border-slate-100">
            <div>
              <h3 class="text-sm font-bold text-slate-800 flex items-center gap-2">
                <span id="mapa-camada-titulo">Planta Topográfica dos Viveiros (Ceará-Mirim/RN)</span>
                <span class="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-blue-100 text-aco border border-blue-200">Clique para calibrar ou ver zootecnia</span>
              </h3>
              <p class="text-xs text-slate-500">Disposição espacial real dos 10 viveiros numerados pelo seu pai e tanques de apoio.</p>
            </div>

            <!-- Filtros de Setor -->
            <div class="flex items-center gap-1 bg-slate-100 p-1 rounded-xl text-xs">
              <button onclick="filtrarMapaSetor('todos')" id="filter-mapa-todos" class="px-2.5 py-1 rounded-lg font-bold bg-white text-slate-800 shadow-sm">Todos (15)</button>
              <button onclick="filtrarMapaSetor('engorda')" id="filter-mapa-engorda" class="px-2.5 py-1 rounded-lg font-semibold text-slate-600 hover:text-slate-900">Engorda (1 a 10)</button>
              <button onclick="filtrarMapaSetor('bercario')" id="filter-mapa-bercario" class="px-2.5 py-1 rounded-lg font-semibold text-slate-600 hover:text-slate-900">Berçários</button>
              <button onclick="filtrarMapaSetor('apoio')" id="filter-mapa-apoio" class="px-2.5 py-1 rounded-lg font-semibold text-slate-600 hover:text-slate-900">Apoio / Decantação</button>
            </div>
          </div>

          <!-- ÁREA DO MAPA 2D VETORIAL E SATÉLITE -->
          <div class="relative w-full rounded-2xl overflow-hidden border border-slate-200 bg-slate-950 min-h-[640px] flex items-center justify-center p-4">
            
            <!-- Imagem de Satélite Real (Fundo Opcional) -->
            <div id="satelite-background-layer" class="hidden absolute inset-0 z-0 bg-cover bg-center transition-all duration-500 opacity-90" style="background-image: url('assets/mapa_satelite_pai.png');">
              <div class="absolute inset-0 bg-slate-950/40 backdrop-blur-[0.5px]"></div>
            </div>

            <!-- Grid Topográfico em 3 Setores Reais (Oeste, Central e Leste) -->
            <div id="mapa-grid-layout" class="relative z-10 w-full max-w-5xl grid grid-cols-1 md:grid-cols-12 gap-4 items-start">
              
              <!-- SETOR OESTE (Viveiros 10, 9, 8, 7 e Apoios) -->
              <div class="md:col-span-4 space-y-3">
                <div class="flex items-center justify-between px-1">
                  <span class="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
                    <span class="w-2 h-2 rounded-full bg-blue-400"></span> Setor Oeste
                  </span>
                  <span class="text-[10px] text-slate-400 font-mono">Margem Oeste</span>
                </div>

                <div class="space-y-2.5" id="coluna-setor-oeste">
                  <!-- Injetado dinamicamente via JS -->
                </div>
              </div>

              <!-- SETOR CENTRAL (Viveiros 1, 2, 3, 4 - Coluna Central de Alta Biomassa) -->
              <div class="md:col-span-4 space-y-3">
                <div class="flex items-center justify-between px-1">
                  <span class="text-xs font-bold uppercase tracking-wider text-amber-300 flex items-center gap-1.5">
                    <span class="w-2 h-2 rounded-full bg-amber-400 animate-pulse"></span> Setor Central (Principal)
                  </span>
                  <span class="text-[10px] text-slate-400 font-mono">Coluna Central</span>
                </div>

                <div class="space-y-2.5" id="coluna-setor-central">
                  <!-- Injetado dinamicamente via JS -->
                </div>
              </div>

              <!-- SETOR LESTE (Viveiros 5, 6, Berçários e Bacia do Rio) -->
              <div class="md:col-span-4 space-y-3">
                <div class="flex items-center justify-between px-1">
                  <span class="text-xs font-bold uppercase tracking-wider text-emerald-300 flex items-center gap-1.5">
                    <span class="w-2 h-2 rounded-full bg-emerald-400"></span> Setor Leste & Berçários
                  </span>
                  <span class="text-[10px] text-slate-400 font-mono">Junto ao Rio</span>
                </div>

                <div class="space-y-2.5" id="coluna-setor-leste">
                  <!-- Injetado dinamicamente via JS -->
                </div>
              </div>

            </div>

          </div>

          <!-- Legenda do Mapa -->
          <div class="flex flex-wrap items-center justify-between gap-3 pt-2 text-xs text-slate-500">
            <div class="flex flex-wrap items-center gap-4">
              <span class="flex items-center gap-1.5 font-semibold text-slate-700">
                <span class="w-3 h-3 rounded-full bg-emerald-500"></span> 🟢 Ótimo / Parâmetros Estáveis
              </span>
              <span class="flex items-center gap-1.5 font-semibold text-slate-700">
                <span class="w-3 h-3 rounded-full bg-amber-500"></span> 🟡 Atenção (Sobras / Ajuste)
              </span>
              <span class="flex items-center gap-1.5 font-semibold text-slate-700">
                <span class="w-3 h-3 rounded-full bg-red-500 animate-ping"></span> 🔴 Crítico (O₂ < 3.0)
              </span>
              <span class="flex items-center gap-1.5 font-semibold text-slate-700">
                <span class="w-3 h-3 rounded-full bg-slate-300"></span> ⚪ Vazio / Bacia
              </span>
            </div>
            <div class="text-[11px] text-slate-400 italic">
              * Clique em "✏️ Calibrar" no card para alterar a metragem de campo.
            </div>
          </div>

        </div>

        <!-- TABELA DE CALIBRAÇÃO E AUDITORIA TOPOGRÁFICA -->
        <div class="bg-white rounded-3xl p-5 border border-slate-200 shadow-sm space-y-4">
          <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
            <div>
              <h3 class="text-sm font-bold text-slate-900 flex items-center gap-2">
                <i class="fa-solid fa-table-list text-aco"></i> Tabela Oficial de Dimensões dos 15 Tanques
              </h3>
              <p class="text-xs text-slate-500">Comparativo rigoroso entre o levantamento de satélite e as metragens calibradas no campo.</p>
            </div>
            <div class="text-xs text-slate-400 font-mono">
              Base: Mapeamento_e_Cadastro_dos_Viveiros.xlsx
            </div>
          </div>

          <div class="overflow-x-auto rounded-xl border border-slate-200">
            <table class="w-full text-left text-xs border-collapse">
              <thead class="bg-slate-50 text-slate-700 font-bold uppercase text-[10px] tracking-wider border-b border-slate-200">
                <tr>
                  <th class="py-3 px-3">Tanque (Nome do Pai)</th>
                  <th class="py-3 px-3">Cód. Sistema</th>
                  <th class="py-3 px-3">Setor</th>
                  <th class="py-3 px-3 text-right">Área Satélite (Google)</th>
                  <th class="py-3 px-3 text-right text-emerald-800">Área Calibrada</th>
                  <th class="py-3 px-3 text-right">Área (ha)</th>
                  <th class="py-3 px-3 text-right">Prof. Média</th>
                  <th class="py-3 px-3 text-right">Volume d'Água</th>
                  <th class="py-3 px-3">Finalidade</th>
                  <th class="py-3 px-3 text-center">Ações</th>
                </tr>
              </thead>
              <tbody id="tbody-tabela-calibracao-metragens" class="divide-y divide-slate-100">
                <!-- Linhas populadas dinamicamente via JS -->
              </tbody>
            </table>
          </div>
        </div>

      </section>
"""

# Inserir antes da view de biomassa
alvo_biomassa = '<!-- VIEW 2: DETALHAMENTO ANALÍTICO DE BIOMASSA & BIOMETRIA   -->'
if alvo_biomassa in conteudo and 'id="view-viveiros-mapa"' not in conteudo:
    conteudo = conteudo.replace(alvo_biomassa, nova_secao_mapa + "\n      " + alvo_biomassa)
    print("Nova seção view-viveiros-mapa injetada com sucesso!")

# 2. Inserir o Modal de Calibração de Metragem
modal_calibracao = """
  <!-- ======================================================== -->
  <!-- MODAL DE CALIBRAÇÃO DE METRAGEM (SATÉLITE VS CAMPO)      -->
  <!-- ======================================================== -->
  <div id="modal-calibracao-metragem" class="hidden fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
    <div class="bg-white rounded-3xl max-w-lg w-full p-6 shadow-2xl border border-slate-200 transition-all">
      
      <!-- Cabeçalho do Modal -->
      <div class="flex items-center justify-between pb-4 border-b border-slate-100">
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 rounded-2xl bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold text-lg border border-emerald-200">
            <i class="fa-solid fa-ruler-combined"></i>
          </div>
          <div>
            <h3 id="modal-calibrar-titulo" class="text-base font-bold text-slate-900">Calibrar Metragem — Viveiro 1</h3>
            <p id="modal-calibrar-subtitulo" class="text-xs text-slate-500">Tanque Central 1 (C1) • Fazenda Arrendada</p>
          </div>
        </div>
        <button onclick="fecharModalCalibracao()" class="p-2 text-slate-400 hover:text-slate-600 rounded-xl hover:bg-slate-100">
          <i class="fa-solid fa-xmark"></i>
        </button>
      </div>

      <!-- Formulário de Calibração -->
      <div class="py-5 space-y-4">
        
        <!-- Comparativo Satélite vs Ajustada -->
        <div class="grid grid-cols-2 gap-3 p-3.5 rounded-2xl bg-slate-50 border border-slate-200">
          <div>
            <span class="text-[10px] font-bold text-slate-400 uppercase">🛰️ Metragem por Satélite</span>
            <div id="modal-calibrar-satelite-val" class="text-base font-extrabold text-slate-700 mt-0.5">12.600 m²</div>
            <span class="text-[10px] text-slate-400">Referência Google Maps SIG</span>
          </div>
          <div>
            <span class="text-[10px] font-bold text-emerald-700 uppercase">📐 Metragem Calibrada Atual</span>
            <div id="modal-calibrar-atual-val" class="text-base font-extrabold text-emerald-700 mt-0.5">12.600 m²</div>
            <span id="modal-calibrar-origem-txt" class="text-[10px] text-emerald-600">Medição oficial vigente</span>
          </div>
        </div>

        <!-- Inputs de Alteração -->
        <div class="space-y-3">
          <div>
            <label class="block text-xs font-bold text-slate-700 mb-1">
              Nova Área Medida no Campo (m²):
            </label>
            <div class="relative">
              <input type="number" step="10" id="input-calibrar-area-m2" oninput="recalcularPreviaCalibracao()" class="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:border-emerald-500 font-mono text-sm font-bold text-slate-800 shadow-inner">
              <span class="absolute right-3.5 top-2.5 text-xs font-bold text-slate-400">m²</span>
            </div>
            <p class="text-[10px] text-slate-400 mt-1">Insira a metragem apurada por trena, drone ou topografia.</p>
          </div>

          <div>
            <label class="block text-xs font-bold text-slate-700 mb-1">
              Profundidade Média Útil (metros):
            </label>
            <div class="relative">
              <input type="number" step="0.05" id="input-calibrar-profundidade" oninput="recalcularPreviaCalibracao()" class="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:border-emerald-500 font-mono text-sm font-bold text-slate-800 shadow-inner">
              <span class="absolute right-3.5 top-2.5 text-xs font-bold text-slate-400">m</span>
            </div>
          </div>

          <div>
            <label class="block text-xs font-bold text-slate-700 mb-1">
              Observação / Método de Medição:
            </label>
            <input type="text" id="input-calibrar-observacoes" placeholder="Ex: Medido com trena a laser e balizas" class="w-full px-3.5 py-2 rounded-xl border border-slate-300 focus:outline-none focus:border-emerald-500 text-xs text-slate-700">
          </div>
        </div>

        <!-- Painel de Recálculo em Tempo Real (Impacto Zootécnico) -->
        <div class="p-3.5 rounded-2xl bg-emerald-50/70 border border-emerald-200/80 space-y-1.5">
          <span class="text-[10px] font-bold uppercase tracking-wider text-emerald-800 flex items-center gap-1">
            <i class="fa-solid fa-calculator"></i> Impacto Zootécnico em Tempo Real
          </span>
          <div class="grid grid-cols-3 gap-2 text-center pt-1">
            <div class="bg-white p-2 rounded-xl border border-emerald-100">
              <span class="text-[9px] font-bold text-slate-400 block uppercase">Área (ha)</span>
              <strong id="previa-calc-ha" class="text-xs font-extrabold text-slate-800">1,26 ha</strong>
            </div>
            <div class="bg-white p-2 rounded-xl border border-emerald-100">
              <span class="text-[9px] font-bold text-slate-400 block uppercase">Volume d'Água</span>
              <strong id="previa-calc-vol" class="text-xs font-extrabold text-blue-700">15.120 m³</strong>
            </div>
            <div class="bg-white p-2 rounded-xl border border-emerald-100">
              <span class="text-[9px] font-bold text-slate-400 block uppercase">Variação Satélite</span>
              <strong id="previa-calc-dif" class="text-xs font-extrabold text-emerald-700">0.0%</strong>
            </div>
          </div>
        </div>

      </div>

      <!-- Rodapé com Botões de Ação -->
      <div class="pt-3 border-t border-slate-100 flex items-center justify-between">
        <button onclick="restaurarMetragemSatelite()" class="px-3.5 py-2 rounded-xl text-xs font-semibold text-slate-500 hover:text-slate-800 hover:bg-slate-100 transition">
          Restaurar Satélite
        </button>
        <div class="flex items-center space-x-2">
          <button onclick="fecharModalCalibracao()" class="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold transition">
            Cancelar
          </button>
          <button id="btn-salvar-calibracao" onclick="salvarCalibracaoMetragem()" class="px-5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold shadow transition flex items-center gap-1.5">
            <i class="fa-solid fa-floppy-disk"></i> Salvar Calibração
          </button>
        </div>
      </div>

    </div>
  </div>
"""

if 'id="modal-calibracao-metragem"' not in conteudo:
    conteudo = conteudo.replace("</body>", f"{modal_calibracao}\n</body>")
    print("Modal de calibração de metragem injetado!")

# Salva o arquivo temporário
HTML_PATH.write_text(conteudo, encoding="utf-8")
print("HTML atualizado com a estrutura do novo módulo!")
