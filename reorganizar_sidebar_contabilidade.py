# -*- coding: utf-8 -*-
"""
Script para reorganizar os módulos contábeis na barra lateral esquerda (Sidebar)
e estruturar as 6 demonstrações solicitadas pelo usuário:
- Resumo Contábil
- DRE
- Fluxo de Caixa
- Plano de Contas
- Lançamentos
- Notas, Drive & Backup (GED)

Além disso, remove o bloco do Dashboard Macro e o atalho da sub-barra, atendendo
à instrução: "não precisa ser no dashboard agora".
"""

import sys
from pathlib import Path

HTML_PATH = Path(r"g:\Meu Drive\ANTIGRAVITY DRIVE\CAMARÃO\ERP CAMARÃO\dashboard_interativo_prototipo.html")

def main():
    if not HTML_PATH.exists():
        print(f"Erro: Arquivo {HTML_PATH} nao encontrado.")
        sys.exit(1)

    content = HTML_PATH.read_text(encoding="utf-8")

    # -------------------------------------------------------------------------
    # 1. Limpar sub-barra de status operacional (remover atalho de DRE adicionado)
    # -------------------------------------------------------------------------
    old_subbarra = '''          <span class="flex items-center gap-1 text-slate-700 cursor-pointer hover:text-aco transition" onclick="navegarPara('analytics-estoque')">
            <i class="fa-solid fa-warehouse text-slate-500"></i>
            Estoque: <strong class="text-slate-900">380 sacos</strong> (14 dias)
          </span>
          <span class="text-slate-300">|</span>
          <span class="flex items-center gap-1 text-slate-700 cursor-pointer hover:text-emerald-700 transition" onclick="navegarPara('analytics-financeiro')" title="Clique para abrir o Hub Contábil, DRE e Livro Diário">
            <i class="fa-solid fa-scale-unbalanced-flip text-amber-500"></i>
            DRE Safra 2026/2: <strong class="text-emerald-700 font-mono font-bold">Lucro +R$ 61.089</strong> (18.6%)
          </span>'''

    clean_subbarra = '''          <span class="flex items-center gap-1 text-slate-700 cursor-pointer hover:text-aco transition" onclick="navegarPara('analytics-estoque')">
            <i class="fa-solid fa-warehouse text-slate-500"></i>
            Estoque: <strong class="text-slate-900">380 sacos</strong> (14 dias)
          </span>'''

    if old_subbarra in content:
        content = content.replace(old_subbarra, clean_subbarra)
        print("[OK] Sub-barra restaurada ao padrao limpo.")

    # -------------------------------------------------------------------------
    # 2. Remover bloco de contabilidade do Dashboard Macro
    # -------------------------------------------------------------------------
    macro_start = '        <!-- ======================================================== -->\n        <!-- 1.5 CONTROLADORIA, DRE & FLUXO DE CAIXA DA SAFRA        -->'
    macro_end = '        <!-- ======================================================== -->\n        <!-- 2. PAINEL RÁPIDO DE MANEJO DIÁRIO (OPERACIONAL)         -->'

    if macro_start in content and macro_end in content:
        idx_s = content.find(macro_start)
        idx_e = content.find(macro_end)
        content = content[:idx_s] + content[idx_e:]
        print("[OK] Bloco contabil removido do Dashboard Macro (foco na coluna da esquerda).")
    else:
        print("[Aviso] Bloco do Dashboard Macro nao localizado por delimitadores exatos.")

    # -------------------------------------------------------------------------
    # 3. Atualizar a Sidebar na coluna da esquerda
    # -------------------------------------------------------------------------
    old_sidebar_bloco = '''        <!-- Bloco 3: Suprimentos & Controladoria -->
        <div class="sidebar-section-title px-3 pt-4 pb-1 text-[10px] font-bold uppercase tracking-wider text-blue-300/70">
          Gestão & Controladoria
        </div>
        <button onclick="navegarPara('analytics-estoque')" id="nav-analytics-estoque" class="nav-item w-full flex items-center space-x-3 px-3 py-2.5 rounded-xl font-medium text-blue-200 hover:text-white hover:bg-white/10 transition">
          <i class="fa-solid fa-boxes-stacked w-5 text-center text-orange-300"></i>
          <span class="sidebar-label">Estoque de Ração</span>
        </button>
        <button onclick="navegarPara('analytics-financeiro')" id="nav-analytics-financeiro" class="nav-item w-full flex items-center space-x-3 px-3 py-2.5 rounded-xl font-medium text-blue-200 hover:text-white hover:bg-white/10 transition">
          <i class="fa-solid fa-sack-dollar w-5 text-center text-yellow-300"></i>
          <span class="sidebar-label">Custos, DRE & Contas</span>
        </button>
        <button onclick="navegarPara('analytics-equipe')" id="nav-analytics-equipe" class="nav-item w-full flex items-center space-x-3 px-3 py-2.5 rounded-xl font-medium text-blue-200 hover:text-white hover:bg-white/10 transition">
          <i class="fa-solid fa-users-gear w-5 text-center text-violet-300"></i>
          <span class="sidebar-label">Equipe & Vigia Noturno</span>
        </button>
        <button onclick="navegarPara('analytics-mercado')" id="nav-analytics-mercado" class="nav-item w-full flex items-center space-x-3 px-3 py-2.5 rounded-xl font-medium text-blue-200 hover:text-white hover:bg-white/10 transition">
          <i class="fa-solid fa-arrow-trend-up w-5 text-center text-emerald-300"></i>
          <span class="sidebar-label">Cotações ABCC & Mercado</span>
        </button>
        <button onclick="navegarPara('analytics-ged')" id="nav-analytics-ged" class="nav-item w-full flex items-center space-x-3 px-3 py-2.5 rounded-xl font-medium text-blue-200 hover:text-white hover:bg-white/10 transition">
          <i class="fa-solid fa-folder-open w-5 text-center text-amber-200"></i>
          <span class="sidebar-label">GED & Notas / IDEMA</span>
        </button>'''

    new_sidebar_bloco = '''        <!-- Bloco 3: Gestão & Operação -->
        <div class="sidebar-section-title px-3 pt-4 pb-1 text-[10px] font-bold uppercase tracking-wider text-blue-300/70">
          Gestão & Operação
        </div>
        <button onclick="navegarPara('analytics-estoque')" id="nav-analytics-estoque" class="nav-item w-full flex items-center space-x-3 px-3 py-2 rounded-xl font-medium text-blue-200 hover:text-white hover:bg-white/10 transition">
          <i class="fa-solid fa-boxes-stacked w-5 text-center text-orange-300"></i>
          <span class="sidebar-label">Estoque de Ração</span>
        </button>
        <button onclick="navegarPara('analytics-equipe')" id="nav-analytics-equipe" class="nav-item w-full flex items-center space-x-3 px-3 py-2 rounded-xl font-medium text-blue-200 hover:text-white hover:bg-white/10 transition">
          <i class="fa-solid fa-users-gear w-5 text-center text-violet-300"></i>
          <span class="sidebar-label">Equipe & Vigia Noturno</span>
        </button>
        <button onclick="navegarPara('analytics-mercado')" id="nav-analytics-mercado" class="nav-item w-full flex items-center space-x-3 px-3 py-2 rounded-xl font-medium text-blue-200 hover:text-white hover:bg-white/10 transition">
          <i class="fa-solid fa-arrow-trend-up w-5 text-center text-emerald-300"></i>
          <span class="sidebar-label">Cotações ABCC & Mercado</span>
        </button>

        <!-- Bloco 4: Contabilidade -->
        <div class="sidebar-section-title px-3 pt-4 pb-1 text-[10px] font-bold uppercase tracking-wider text-blue-300/70 flex items-center justify-between">
          <span class="flex items-center gap-1.5"><i class="fa-solid fa-scale-unbalanced-flip text-amber-400"></i> Contabilidade</span>
          <span class="px-1.5 py-0.2 rounded bg-amber-400/20 text-amber-300 text-[9px] font-extrabold font-mono">2026/2</span>
        </div>
        <button onclick="navegarPara('contabil-resumo')" id="nav-contabil-resumo" class="nav-item w-full flex items-center space-x-3 px-3 py-2 rounded-xl font-medium text-blue-200 hover:text-white hover:bg-white/10 transition">
          <i class="fa-solid fa-chart-pie w-5 text-center text-amber-300"></i>
          <span class="sidebar-label">Resumo Contábil</span>
        </button>
        <button onclick="navegarPara('contabil-dre')" id="nav-contabil-dre" class="nav-item w-full flex items-center space-x-3 px-3 py-2 rounded-xl font-medium text-blue-200 hover:text-white hover:bg-white/10 transition">
          <i class="fa-solid fa-file-invoice-dollar w-5 text-center text-emerald-400"></i>
          <span class="sidebar-label">DRE</span>
        </button>
        <button onclick="navegarPara('contabil-fluxo')" id="nav-contabil-fluxo" class="nav-item w-full flex items-center space-x-3 px-3 py-2 rounded-xl font-medium text-blue-200 hover:text-white hover:bg-white/10 transition">
          <i class="fa-solid fa-money-bill-trend-up w-5 text-center text-cyan-300"></i>
          <span class="sidebar-label">Fluxo de Caixa</span>
        </button>
        <button onclick="navegarPara('contabil-plano')" id="nav-contabil-plano" class="nav-item w-full flex items-center space-x-3 px-3 py-2 rounded-xl font-medium text-blue-200 hover:text-white hover:bg-white/10 transition">
          <i class="fa-solid fa-sitemap w-5 text-center text-yellow-300"></i>
          <span class="sidebar-label">Plano de Contas</span>
        </button>
        <button onclick="navegarPara('contabil-lancamentos')" id="nav-contabil-lancamentos" class="nav-item w-full flex items-center space-x-3 px-3 py-2 rounded-xl font-medium text-blue-200 hover:text-white hover:bg-white/10 transition">
          <i class="fa-solid fa-book-journal-whills w-5 text-center text-indigo-300"></i>
          <span class="sidebar-label">Lançamentos</span>
        </button>
        <button onclick="navegarPara('contabil-ged')" id="nav-contabil-ged" class="nav-item w-full flex items-center justify-between px-3 py-2 rounded-xl font-medium text-blue-200 hover:text-white hover:bg-white/10 transition">
          <div class="flex items-center space-x-3 truncate">
            <i class="fa-solid fa-folder-tree w-5 text-center text-amber-200"></i>
            <span class="sidebar-label truncate">Notas, Drive & Backup</span>
          </div>
          <span class="px-1.5 py-0.5 rounded text-[9px] font-extrabold bg-emerald-500/30 text-emerald-300">GED</span>
        </button>'''

    if old_sidebar_bloco in content:
        content = content.replace(old_sidebar_bloco, new_sidebar_bloco)
        print("[OK] Sidebar reestruturada com modulo Contabilidade e as 6 opcoes de demonstracao.")
    else:
        print("[Erro] old_sidebar_bloco nao encontrado!")
        sys.exit(1)

    # -------------------------------------------------------------------------
    # 4. Atualizar a Barra de Abas Internas da view-analytics-financeiro
    # -------------------------------------------------------------------------
    old_abas_internas = '''          <!-- Navegação entre as 4 Abas Clássicas -->
          <div class="flex flex-wrap items-center gap-1.5 bg-slate-100 p-1.5 rounded-2xl border border-slate-200 w-full lg:w-auto">
            <button id="btn-tab-contabil-plano" onclick="alternarAbaContabil('plano')" class="px-3.5 py-2 rounded-xl text-xs font-extrabold transition flex items-center gap-1.5 bg-marinho text-white shadow-sm">
              <i class="fa-solid fa-Sitemap text-cyan-300"></i> 1. Plano de Contas & Livro Diário
            </button>
            <button id="btn-tab-contabil-dre" onclick="alternarAbaContabil('dre')" class="px-3.5 py-2 rounded-xl text-xs font-bold transition flex items-center gap-1.5 text-slate-600 hover:text-slate-900">
              <i class="fa-solid fa-file-invoice-dollar text-amber-600"></i> 2. DRE Contábil
            </button>
            <button id="btn-tab-contabil-fluxo" onclick="alternarAbaContabil('fluxo')" class="px-3.5 py-2 rounded-xl text-xs font-bold transition flex items-center gap-1.5 text-slate-600 hover:text-slate-900">
              <i class="fa-solid fa-money-bill-trend-up text-emerald-600"></i> 3. Fluxo de Caixa
            </button>
            <button id="btn-tab-contabil-ged" onclick="alternarAbaContabil('ged')" class="px-3.5 py-2 rounded-xl text-xs font-bold transition flex items-center gap-1.5 text-slate-600 hover:text-slate-900">
              <i class="fa-solid fa-folder-tree text-blue-600"></i> 4. Importação Excel, GED & Backup
              <span id="badge-contabil-dedup" class="px-1.5 py-0.5 rounded-full text-[10px] font-extrabold bg-emerald-100 text-emerald-800">0 dup</span>
            </button>
          </div>'''

    new_abas_internas = '''          <!-- Navegação entre as 6 Demonstrações Contábeis -->
          <div class="flex flex-wrap items-center gap-1.5 bg-slate-100 p-1.5 rounded-2xl border border-slate-200 w-full lg:w-auto">
            <button id="btn-tab-contabil-resumo" onclick="alternarAbaContabil('resumo')" class="px-3 py-1.5 rounded-xl text-xs font-bold transition flex items-center gap-1.5 bg-marinho text-white shadow-sm">
              <i class="fa-solid fa-chart-pie text-amber-300"></i> Resumo Contábil
            </button>
            <button id="btn-tab-contabil-dre" onclick="alternarAbaContabil('dre')" class="px-3 py-1.5 rounded-xl text-xs font-bold transition flex items-center gap-1.5 text-slate-600 hover:text-slate-900">
              <i class="fa-solid fa-file-invoice-dollar text-emerald-600"></i> DRE
            </button>
            <button id="btn-tab-contabil-fluxo" onclick="alternarAbaContabil('fluxo')" class="px-3 py-1.5 rounded-xl text-xs font-bold transition flex items-center gap-1.5 text-slate-600 hover:text-slate-900">
              <i class="fa-solid fa-money-bill-trend-up text-cyan-600"></i> Fluxo de Caixa
            </button>
            <button id="btn-tab-contabil-plano" onclick="alternarAbaContabil('plano')" class="px-3 py-1.5 rounded-xl text-xs font-bold transition flex items-center gap-1.5 text-slate-600 hover:text-slate-900">
              <i class="fa-solid fa-sitemap text-yellow-600"></i> Plano de Contas
            </button>
            <button id="btn-tab-contabil-lancamentos" onclick="alternarAbaContabil('lancamentos')" class="px-3 py-1.5 rounded-xl text-xs font-bold transition flex items-center gap-1.5 text-slate-600 hover:text-slate-900">
              <i class="fa-solid fa-book-journal-whills text-indigo-600"></i> Lançamentos
            </button>
            <button id="btn-tab-contabil-ged" onclick="alternarAbaContabil('ged')" class="px-3 py-1.5 rounded-xl text-xs font-bold transition flex items-center gap-1.5 text-slate-600 hover:text-slate-900">
              <i class="fa-solid fa-folder-tree text-blue-600"></i> Notas, Drive & Backup
              <span id="badge-contabil-dedup" class="px-1.5 py-0.5 rounded-full text-[10px] font-extrabold bg-emerald-100 text-emerald-800">0 dup</span>
            </button>
          </div>'''

    if old_abas_internas in content:
        content = content.replace(old_abas_internas, new_abas_internas)
        print("[OK] Barra de abas internas atualizada com as 6 demonstracoes.")
    else:
        print("[Erro] old_abas_internas nao encontrado!")
        sys.exit(1)

    # -------------------------------------------------------------------------
    # 5. Estruturar as Subviews Contábeis:
    #    - subview-contabil-resumo (NOVA: KPIs + Painel da Safra + Resumo Viveiros)
    #    - subview-contabil-plano (apenas a tabela hierárquica)
    #    - subview-contabil-lancamentos (NOVA: Livro Diário com filtros e tabela)
    # -------------------------------------------------------------------------
    old_plano_subview_marker = '''        <!-- ================================================================ -->
        <!-- ABA 1: PLANO DE CONTAS HIERÁRQUICO & LIVRO DIÁRIO               -->
        <!-- ================================================================ -->
        <div id="subview-contabil-plano" class="space-y-6">'''

    new_subviews_resumo_e_plano = '''        <!-- ================================================================ -->
        <!-- DEMONSTRAÇÃO 1: RESUMO CONTÁBIL DA SAFRA (PAINEL GERAL)         -->
        <!-- ================================================================ -->
        <div id="subview-contabil-resumo" class="space-y-6">
          
          <!-- Painel Executivo da Safra 2026/2 -->
          <div class="grid grid-cols-1 lg:grid-cols-3 gap-5">
            
            <!-- Bloco 1: Indicadores Sintéticos de Lucro & Margens -->
            <div class="bg-white rounded-3xl p-5 border border-slate-200 shadow-sm space-y-4">
              <div class="flex items-center justify-between border-b border-slate-100 pb-2.5">
                <h3 class="text-xs font-extrabold uppercase tracking-wider text-slate-800 flex items-center gap-2">
                  <i class="fa-solid fa-scale-balanced text-aco"></i> Indicadores de Desempenho
                </h3>
                <span class="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-emerald-100 text-emerald-800">Safra Ativa</span>
              </div>
              <div class="space-y-3 text-xs">
                <div class="flex items-center justify-between p-2.5 rounded-xl bg-slate-50 border border-slate-100">
                  <span class="text-slate-600 font-medium">Margem Operacional (EBITDA):</span>
                  <strong id="resumo-card-margem-ebitda" class="font-mono text-slate-900 font-bold">R$ 61.089,00 (18.6%)</strong>
                </div>
                <div class="flex items-center justify-between p-2.5 rounded-xl bg-slate-50 border border-slate-100">
                  <span class="text-slate-600 font-medium">Contas a Receber (Safra):</span>
                  <strong class="font-mono text-emerald-700 font-bold">R$ 57.500,00</strong>
                </div>
                <div class="flex items-center justify-between p-2.5 rounded-xl bg-slate-50 border border-slate-100">
                  <span class="text-slate-600 font-medium">Contas a Pagar (Abertas):</span>
                  <strong class="font-mono text-amber-700 font-bold">R$ 42.340,00</strong>
                </div>
                <div class="flex items-center justify-between p-2.5 rounded-xl bg-slate-50 border border-slate-100">
                  <span class="text-slate-600 font-medium">Taxa de Liquidação de Caixa:</span>
                  <strong class="font-mono text-cyan-800 font-bold">86.2% Pago</strong>
                </div>
              </div>
            </div>

            <!-- Bloco 2: Integridade e Status do Drive dos Pais -->
            <div class="bg-white rounded-3xl p-5 border border-slate-200 shadow-sm space-y-4">
              <div class="flex items-center justify-between border-b border-slate-100 pb-2.5">
                <h3 class="text-xs font-extrabold uppercase tracking-wider text-slate-800 flex items-center gap-2">
                  <i class="fa-solid fa-shield-check text-emerald-600"></i> Segurança & Triagem IA
                </h3>
                <span class="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-blue-100 text-blue-800">Drive Sync</span>
              </div>
              <div class="space-y-3 text-xs">
                <div class="p-2.5 rounded-xl bg-emerald-50/70 border border-emerald-200 flex items-center justify-between">
                  <div class="flex items-center gap-2">
                    <i class="fa-solid fa-circle-check text-emerald-600"></i>
                    <span class="font-medium text-emerald-900">Lançamentos Sincronizados:</span>
                  </div>
                  <strong class="font-mono font-bold text-emerald-800">25 Notas</strong>
                </div>
                <div class="p-2.5 rounded-xl bg-blue-50/70 border border-blue-200 flex items-center justify-between">
                  <div class="flex items-center gap-2">
                    <i class="fa-solid fa-filter-circle-xmark text-aco"></i>
                    <span class="font-medium text-blue-900">Duplicatas Bloqueadas:</span>
                  </div>
                  <strong id="resumo-card-dup-bloqueadas" class="font-mono font-bold text-aco">0 redundâncias</strong>
                </div>
                <div class="p-2.5 rounded-xl bg-amber-50/70 border border-amber-200 flex items-center justify-between">
                  <div class="flex items-center gap-2">
                    <i class="fa-solid fa-clock-rotate-left text-amber-600"></i>
                    <span class="font-medium text-amber-900">Último Backup Diário:</span>
                  </div>
                  <strong class="font-mono text-amber-800 font-bold">2026-10-23</strong>
                </div>
              </div>
            </div>

            <!-- Bloco 3: Ações Rápidas da Controladoria -->
            <div class="bg-gradient-to-br from-slate-900 to-marinho text-white rounded-3xl p-5 shadow-sm space-y-4 flex flex-col justify-between">
              <div>
                <div class="flex items-center justify-between border-b border-white/10 pb-2">
                  <h3 class="text-xs font-extrabold uppercase tracking-wider text-amber-300 flex items-center gap-2">
                    <i class="fa-solid fa-bolt"></i> Atalhos Contábeis
                  </h3>
                  <span class="text-[10px] text-slate-400">1-Clique</span>
                </div>
                <p class="text-xs text-slate-300 mt-2">
                  Navegue rapidamente entre as demonstrações contábeis oficiais da Fazenda Arrendada.
                </p>
              </div>
              <div class="grid grid-cols-2 gap-2 text-xs">
                <button onclick="alternarAbaContabil('dre')" class="p-2.5 rounded-xl bg-white/10 hover:bg-white/20 transition text-left font-bold border border-white/10 flex items-center gap-2">
                  <i class="fa-solid fa-file-invoice-dollar text-emerald-400"></i> Ver DRE
                </button>
                <button onclick="alternarAbaContabil('fluxo')" class="p-2.5 rounded-xl bg-white/10 hover:bg-white/20 transition text-left font-bold border border-white/10 flex items-center gap-2">
                  <i class="fa-solid fa-money-bill-trend-up text-cyan-400"></i> Ver Caixa
                </button>
                <button onclick="alternarAbaContabil('plano')" class="p-2.5 rounded-xl bg-white/10 hover:bg-white/20 transition text-left font-bold border border-white/10 flex items-center gap-2">
                  <i class="fa-solid fa-sitemap text-yellow-400"></i> Contas
                </button>
                <button onclick="alternarAbaContabil('lancamentos')" class="p-2.5 rounded-xl bg-white/10 hover:bg-white/20 transition text-left font-bold border border-white/10 flex items-center gap-2">
                  <i class="fa-solid fa-book-journal-whills text-indigo-400"></i> Lançamentos
                </button>
              </div>
            </div>

          </div>

          <!-- Resumo Contábil por Centro de Custo / Viveiro -->
          <div class="bg-white rounded-3xl p-5 border border-slate-200 shadow-sm space-y-4">
            <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 pb-3 border-b border-slate-100">
              <div>
                <h3 class="text-sm font-extrabold text-slate-900 flex items-center gap-2">
                  <i class="fa-solid fa-bullseye text-aco"></i> Distribuição Contábil por Centro de Custo / Viveiro
                </h3>
                <p class="text-xs text-slate-500">
                  Consolidação automática dos lançamentos direcionados para cada viveiro versus os custos gerais da fazenda.
                </p>
              </div>
              <button onclick="alternarAbaContabil('lancamentos')" class="text-xs font-bold text-aco hover:underline flex items-center gap-1">
                Direcionar Mais Viveiros no Diário <i class="fa-solid fa-arrow-right text-[10px]"></i>
              </button>
            </div>

            <div class="overflow-x-auto">
              <table class="w-full text-left text-xs border-collapse">
                <thead>
                  <tr class="bg-slate-50 text-slate-700 font-bold border-b border-slate-200">
                    <th class="py-2.5 px-3">Centro de Custo / Viveiro</th>
                    <th class="py-2.5 px-3 text-center">Lançamentos</th>
                    <th class="py-2.5 px-3 text-right text-emerald-700">Receitas Alocadas (R$)</th>
                    <th class="py-2.5 px-3 text-right text-rose-700">Custos Alocados (R$)</th>
                    <th class="py-2.5 px-3 text-right font-extrabold">Saldo do Viveiro (R$)</th>
                    <th class="py-2.5 px-3 text-center">Ação Rápida</th>
                  </tr>
                </thead>
                <tbody id="tbody-contabil-resumo-viveiros" class="divide-y divide-slate-100">
                  <!-- Gerado dinamicamente via JS -->
                </tbody>
              </table>
            </div>
          </div>

        </div>

        <!-- ================================================================ -->
        <!-- DEMONSTRAÇÃO 4: PLANO DE CONTAS HIERÁRQUICO (5 GRUPOS)          -->
        <!-- ================================================================ -->
        <div id="subview-contabil-plano" class="hidden space-y-6">'''

    if old_plano_subview_marker in content:
        content = content.replace(old_plano_subview_marker, new_subviews_resumo_e_plano)
        print("[OK] subview-contabil-resumo criada com sucesso e subview-contabil-plano ajustada.")
    else:
        print("[Erro] old_plano_subview_marker nao encontrado!")
        sys.exit(1)

    # Agora separar a tabela de Livro Diário para virar a subview-contabil-lancamentos
    old_livro_diario_marker = '''          <!-- Livro Diário Contábil (Razão de Lançamentos + Seletor de Viveiro em 1 Clique) -->
          <div class="bg-white rounded-3xl p-5 border border-slate-200 shadow-sm space-y-4">'''

    # O Livro Diário agora fecha a subview-contabil-plano e abre a subview-contabil-lancamentos
    new_livro_diario_block = '''        </div>

        <!-- ================================================================ -->
        <!-- DEMONSTRAÇÃO 5: LANÇAMENTOS CONTÁBEIS & LIVRO DIÁRIO            -->
        <!-- ================================================================ -->
        <div id="subview-contabil-lancamentos" class="hidden space-y-6">
          <div class="bg-white rounded-3xl p-5 border border-slate-200 shadow-sm space-y-4">'''

    if old_livro_diario_marker in content:
        content = content.replace(old_livro_diario_marker, new_livro_diario_block)
        print("[OK] subview-contabil-lancamentos criada com sucesso separada do Plano de Contas.")
    else:
        print("[Erro] old_livro_diario_marker nao encontrado!")
        sys.exit(1)

    # -------------------------------------------------------------------------
    # 6. Atualizar JavaScript: navegarPara, alternarAbaContabil e dados de resumo
    # -------------------------------------------------------------------------
    # Vamos ler o trecho de navegarPara e alternarAbaContabil
    target_navegar_para = '''      // Tratar se for analytics-ged: abre o Hub Contábil direto na Aba 4 (GED, Excel & Backups)
      if (viewId === 'analytics-ged') {
        const target = document.getElementById('view-analytics-financeiro');
        if (target) {
          target.classList.remove('hidden');
          window.scrollTo({ top: 0, behavior: 'smooth' });
          alternarAbaContabil('ged');
        }
        atualizarHeaderNavegacao('GED, Importação Excel & Backups Contábeis', 'Início > Controladoria > GED & Backups');
        return;
      }'''

    replace_navegar_para = '''      // Tratar navegacao para as 6 demonstracoes contabeis especificas
      const mapaContabilViews = {
        'contabil-resumo': { aba: 'resumo', titulo: 'Resumo Contábil da Fazenda', breadcrumb: 'Início > Contabilidade > Resumo Geral' },
        'contabil-dre': { aba: 'dre', titulo: 'Demonstração do Resultado do Exercício (DRE)', breadcrumb: 'Início > Contabilidade > DRE' },
        'contabil-fluxo': { aba: 'fluxo', titulo: 'Fluxo de Caixa (Tesouraria)', breadcrumb: 'Início > Contabilidade > Fluxo de Caixa' },
        'contabil-plano': { aba: 'plano', titulo: 'Plano de Contas Hierárquico', breadcrumb: 'Início > Contabilidade > Plano de Contas' },
        'contabil-lancamentos': { aba: 'lancamentos', titulo: 'Lançamentos Contábeis & Livro Diário', breadcrumb: 'Início > Contabilidade > Lançamentos' },
        'contabil-ged': { aba: 'ged', titulo: 'Notas dos Pais, Drive & Backups', breadcrumb: 'Início > Contabilidade > Notas & GED' },
        'analytics-ged': { aba: 'ged', titulo: 'Notas dos Pais, Drive & Backups', breadcrumb: 'Início > Contabilidade > Notas & GED' },
        'analytics-financeiro': { aba: 'resumo', titulo: 'Hub de Contabilidade & Finanças', breadcrumb: 'Início > Contabilidade > Visão Geral' }
      };

      if (mapaContabilViews[viewId]) {
        const conf = mapaContabilViews[viewId];
        const target = document.getElementById('view-analytics-financeiro');
        if (target) {
          target.classList.remove('hidden');
          window.scrollTo({ top: 0, behavior: 'smooth' });
          alternarAbaContabil(conf.aba);
        }
        atualizarHeaderNavegacao(conf.titulo, conf.breadcrumb);

        // Atualizar destaque na Sidebar
        document.querySelectorAll('.nav-item').forEach(btn => {
          btn.classList.remove('bg-aco', 'text-white', 'shadow-sm');
          btn.classList.add('text-blue-200');
        });
        const activeNavBtn = document.getElementById(`nav-${viewId}`) || document.getElementById(`nav-contabil-${conf.aba}`);
        if (activeNavBtn) {
          activeNavBtn.classList.remove('text-blue-200');
          activeNavBtn.classList.add('bg-aco', 'text-white', 'shadow-sm');
        }
        return;
      }'''

    if target_navegar_para in content:
        content = content.replace(target_navegar_para, replace_navegar_para)
        print("[OK] navegarPara() atualizada para orquestrar as 6 visoes contabeis.")
    else:
        print("[Erro] target_navegar_para nao encontrado!")
        sys.exit(1)

    # Atualizar alternarAbaContabil para as 6 abas
    target_alternar_aba = '''    function alternarAbaContabil(aba) {
      CONTABIL_ABA_ATIVA = aba;
      const abas = ['plano', 'dre', 'fluxo', 'ged'];
      abas.forEach(a => {
        const sub = document.getElementById(`subview-contabil-${a}`);
        const btn = document.getElementById(`btn-tab-contabil-${a}`);
        if (sub) {
          if (a === aba) sub.classList.remove('hidden');
          else sub.classList.add('hidden');
        }
        if (btn) {
          if (a === aba) {
            btn.className = 'px-3.5 py-2 rounded-xl text-xs font-extrabold transition flex items-center gap-1.5 bg-marinho text-white shadow-sm';
          } else {
            btn.className = 'px-3.5 py-2 rounded-xl text-xs font-bold transition flex items-center gap-1.5 text-slate-600 hover:text-slate-900';
          }
        }
      });
      recarregarVisoesContabeis();
    }'''

    replace_alternar_aba = '''    function alternarAbaContabil(aba) {
      CONTABIL_ABA_ATIVA = aba;
      const abas = ['resumo', 'dre', 'fluxo', 'plano', 'lancamentos', 'ged'];
      abas.forEach(a => {
        const sub = document.getElementById(`subview-contabil-${a}`);
        const btn = document.getElementById(`btn-tab-contabil-${a}`);
        if (sub) {
          if (a === aba) sub.classList.remove('hidden');
          else sub.classList.add('hidden');
        }
        if (btn) {
          if (a === aba) {
            btn.className = 'px-3 py-1.5 rounded-xl text-xs font-bold transition flex items-center gap-1.5 bg-marinho text-white shadow-sm';
          } else {
            btn.className = 'px-3 py-1.5 rounded-xl text-xs font-bold transition flex items-center gap-1.5 text-slate-600 hover:text-slate-900';
          }
        }
      });

      // Sincronizar tambem a barra lateral (Sidebar)
      document.querySelectorAll('.nav-item').forEach(btn => {
        btn.classList.remove('bg-aco', 'text-white', 'shadow-sm');
        btn.classList.add('text-blue-200');
      });
      const activeNavBtn = document.getElementById(`nav-contabil-${aba}`);
      if (activeNavBtn) {
        activeNavBtn.classList.remove('text-blue-200');
        activeNavBtn.classList.add('bg-aco', 'text-white', 'shadow-sm');
      }

      // Atualiza breadcrumb no topo
      const titulosMap = {
        'resumo': ['Resumo Contábil da Fazenda', 'Início > Contabilidade > Resumo Geral'],
        'dre': ['Demonstração do Resultado do Exercício (DRE)', 'Início > Contabilidade > DRE'],
        'fluxo': ['Fluxo de Caixa (Tesouraria)', 'Início > Contabilidade > Fluxo de Caixa'],
        'plano': ['Plano de Contas Hierárquico', 'Início > Contabilidade > Plano de Contas'],
        'lancamentos': ['Lançamentos Contábeis & Livro Diário', 'Início > Contabilidade > Lançamentos'],
        'ged': ['Notas dos Pais, Drive & Backups', 'Início > Contabilidade > Notas & GED']
      };
      if (titulosMap[aba]) {
        atualizarHeaderNavegacao(titulosMap[aba][0], titulosMap[aba][1]);
      }

      recarregarVisoesContabeis();
    }'''

    if target_alternar_aba in content:
        content = content.replace(target_alternar_aba, replace_alternar_aba)
        print("[OK] alternarAbaContabil() atualizada com as 6 demonstracoes e sincronizacao bidirecional com a Sidebar.")
    else:
        print("[Erro] target_alternar_aba nao encontrado!")
        sys.exit(1)

    # -------------------------------------------------------------------------
    # 7. Adicionar renderizarResumoContabilViveiros() em recarregarVisoesContabeis()
    # -------------------------------------------------------------------------
    target_render_call = '''      renderizarTabelaPlanoContas(lista);
      renderizarTabelaLivroDiario();
      renderizarVisaoDreContabil(recBruta, deducoes, recLiquida, custosVar, margemContrib, despFixas, ebitda, resFin, lucroLiq, regime, filtroViv);
      renderizarVisaoFluxoCaixa(lista);
      renderizarVisaoGedEBackups(lista);'''

    replace_render_call = '''      renderizarTabelaPlanoContas(lista);
      renderizarTabelaLivroDiario();
      renderizarVisaoDreContabil(recBruta, deducoes, recLiquida, custosVar, margemContrib, despFixas, ebitda, resFin, lucroLiq, regime, filtroViv);
      renderizarVisaoFluxoCaixa(lista);
      renderizarVisaoGedEBackups(lista);
      renderizarResumoContabilViveiros(lista);'''

    if target_render_call in content:
        content = content.replace(target_render_call, replace_render_call)
        print("[OK] renderizarResumoContabilViveiros chamada adicionada em recarregarVisoesContabeis().")
    else:
        print("[Aviso] target_render_call nao localizado exatamente.")

    # -------------------------------------------------------------------------
    # 8. Injetar a funcao renderizarResumoContabilViveiros() no script
    # -------------------------------------------------------------------------
    func_resumo_code = '''
    function renderizarResumoContabilViveiros(lista) {
      const tbody = document.getElementById('tbody-contabil-resumo-viveiros');
      if (!tbody) return;

      const centros = {};
      centros['Geral da Fazenda'] = { receitas: 0, custos: 0, qtd: 0 };
      for (let i = 1; i <= 15; i++) {
        const idViv = `V-${String(i).padStart(2, '0')}`;
        centros[idViv] = { receitas: 0, custos: 0, qtd: 0 };
      }

      lista.forEach(l => {
        const c = l.centro_custo_viveiro || 'Geral da Fazenda';
        if (!centros[c]) centros[c] = { receitas: 0, custos: 0, qtd: 0 };
        const val = Number(l.valor_rs || 0);
        centros[c].qtd++;
        if (l.tipo_movimento === 'ENTRADA') centros[c].receitas += val;
        else centros[c].custos += val;
      });

      // Ordenar: primeiro os que tem movimentacao, depois o restante
      const keys = Object.keys(centros).sort((a, b) => {
        const totalA = centros[a].receitas + centros[a].custos;
        const totalB = centros[b].receitas + centros[b].custos;
        if (totalA > 0 && totalB === 0) return -1;
        if (totalA === 0 && totalB > 0) return 1;
        return a.localeCompare(b);
      });

      tbody.innerHTML = keys.map(k => {
        const item = centros[k];
        const saldo = item.receitas - item.custos;
        const isGeral = k === 'Geral da Fazenda';
        const badgeCor = isGeral ? 'bg-slate-100 text-slate-700' : 'bg-blue-100 text-aco font-bold';
        return `
          <tr class="hover:bg-slate-50 transition border-b border-slate-100">
            <td class="py-2.5 px-3 font-semibold text-slate-800 flex items-center gap-2">
              <span class="px-2 py-0.5 rounded-lg text-xs ${badgeCor}">${k}</span>
              ${isGeral ? '<span class="text-[10px] text-slate-400">(Rateio Geral)</span>' : ''}
            </td>
            <td class="py-2.5 px-3 text-center font-mono font-bold text-slate-600">${item.qtd}</td>
            <td class="py-2.5 px-3 text-right font-mono font-bold text-emerald-700">${formatarMoedaBR(item.receitas)}</td>
            <td class="py-2.5 px-3 text-right font-mono font-bold text-rose-700">${formatarMoedaBR(item.custos)}</td>
            <td class="py-2.5 px-3 text-right font-mono font-extrabold ${saldo >= 0 ? 'text-emerald-700' : 'text-rose-600'}">
              ${formatarMoedaBR(saldo)}
            </td>
            <td class="py-2.5 px-3 text-center">
              <button onclick="filtrarEDirecionarViveiroLivro('${k}')" class="px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-aco hover:text-white text-slate-700 font-bold text-[10px] transition">
                Filtrar no Diário ➔
              </button>
            </td>
          </tr>
        `;
      }).join('');
    }

    function filtrarEDirecionarViveiroLivro(nomeViv) {
      alternarAbaContabil('lancamentos');
      const sel = document.getElementById('select-contabil-viveiro-filtro');
      if (sel) {
        sel.value = nomeViv;
        recarregarVisoesContabeis();
      }
    }
'''

    target_injection_point = '    function renderizarTabelaPlanoContas(lista) {'
    if target_injection_point in content:
        content = content.replace(target_injection_point, func_resumo_code + '\n    function renderizarTabelaPlanoContas(lista) {')
        print("[OK] Funcoes renderizarResumoContabilViveiros() e filtrarEDirecionarViveiroLivro() injetadas.")
    else:
        print("[Aviso] target_injection_point nao localizado.")

    HTML_PATH.write_text(content, encoding="utf-8")
    print(f"[Sucesso] Arquivo {HTML_PATH.name} reorganizado com exito.")

if __name__ == "__main__":
    main()
