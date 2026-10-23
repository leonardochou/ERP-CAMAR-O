# -*- coding: utf-8 -*-
"""
Script de aprimoramento de visibilidade do Módulo Contábil no Dashboard Macro.
Adiciona o Super Card Executivo de Contabilidade & DRE diretamente na tela inicial do ERP Camarão.
"""

import sys
from pathlib import Path

HTML_PATH = Path(r"g:\Meu Drive\ANTIGRAVITY DRIVE\CAMARÃO\ERP CAMARÃO\dashboard_interativo_prototipo.html")

def main():
    if not HTML_PATH.exists():
        print(f"Erro: Arquivo {HTML_PATH} não encontrado.")
        sys.exit(1)

    content = HTML_PATH.read_text(encoding="utf-8")

    # 1. Atualizar sub-barra de status operacional com atalho para DRE
    target_subbarra = '''          <span class="flex items-center gap-1 text-slate-700 cursor-pointer hover:text-aco transition" onclick="navegarPara('analytics-estoque')">
            <i class="fa-solid fa-warehouse text-slate-500"></i>
            Estoque: <strong class="text-slate-900">380 sacos</strong> (14 dias)
          </span>'''
    
    replace_subbarra = '''          <span class="flex items-center gap-1 text-slate-700 cursor-pointer hover:text-aco transition" onclick="navegarPara('analytics-estoque')">
            <i class="fa-solid fa-warehouse text-slate-500"></i>
            Estoque: <strong class="text-slate-900">380 sacos</strong> (14 dias)
          </span>
          <span class="text-slate-300">|</span>
          <span class="flex items-center gap-1 text-slate-700 cursor-pointer hover:text-emerald-700 transition" onclick="navegarPara('analytics-financeiro')" title="Clique para abrir o Hub Contábil, DRE e Livro Diário">
            <i class="fa-solid fa-scale-unbalanced-flip text-amber-500"></i>
            DRE Safra 2026/2: <strong class="text-emerald-700 font-mono font-bold">Lucro +R$ 61.089</strong> (18.6%)
          </span>'''

    if target_subbarra in content:
        content = content.replace(target_subbarra, replace_subbarra)
        print("[OK] Sub-barra de status atualizada com atalho contabil.")
    else:
        print("[Aviso] target_subbarra nao localizado exatamente.")

    # 2. Inserir Painel Executivo Contábil logo abaixo da Régua de Produção no Dashboard Macro
    target_macro_pos = '''          </div>
        </div>

        <!-- ======================================================== -->
        <!-- 2. PAINEL RÁPIDO DE MANEJO DIÁRIO (OPERACIONAL)         -->'''

    bloco_contabil_macro = '''          </div>
        </div>

        <!-- ======================================================== -->
        <!-- 1.5 CONTROLADORIA, DRE & FLUXO DE CAIXA DA SAFRA        -->
        <!-- ======================================================== -->
        <div class="bg-gradient-to-br from-slate-900 via-slate-800 to-marinho text-white rounded-3xl p-6 shadow-xl border border-slate-700/60 relative overflow-hidden">
          <!-- Efeito decorativo de fundo -->
          <div class="absolute -right-10 -bottom-10 w-64 h-64 bg-amber-500/10 rounded-full blur-3xl pointer-events-none"></div>
          <div class="absolute top-0 right-1/4 w-40 h-40 bg-emerald-500/10 rounded-full blur-2xl pointer-events-none"></div>

          <div class="relative z-10 flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4 border-b border-white/10 pb-4 mb-5">
            <div class="space-y-1">
              <div class="flex items-center gap-2">
                <span class="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-wider bg-emerald-500/20 text-emerald-300 border border-emerald-400/30 flex items-center gap-1.5">
                  <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                  Módulo Contábil & Notas dos Pais Conectado
                </span>
                <span class="text-xs text-slate-400">• Safra 2026/2</span>
              </div>
              <h2 class="text-lg sm:text-xl font-extrabold text-white flex items-center gap-2">
                <i class="fa-solid fa-scale-unbalanced-flip text-amber-400"></i>
                Controladoria, DRE & Saúde Financeira da Fazenda
              </h2>
              <p class="text-xs text-slate-300">
                Integração com <code class="px-1.5 py-0.5 rounded bg-white/10 text-amber-200 font-mono">Registro_de_Custos_e_Contas.xlsx</code>, triagem inteligente de recibos e bloqueio anti-duplicidade estrito.
              </p>
            </div>

            <!-- Botões de Acesso Rápido ao Hub Contábil -->
            <div class="flex flex-wrap items-center gap-2">
              <button onclick="navegarPara('analytics-financeiro')" class="px-4 py-2.5 rounded-xl bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-black text-xs transition shadow-lg flex items-center gap-2 cursor-pointer">
                <i class="fa-solid fa-chart-pie"></i> Acessar Hub Contábil (DRE & Contas) ➔
              </button>
              <button onclick="navegarPara('analytics-ged')" class="px-3.5 py-2.5 rounded-xl bg-white/10 hover:bg-white/20 text-white font-bold text-xs transition border border-white/15 flex items-center gap-1.5 cursor-pointer">
                <i class="fa-solid fa-folder-tree text-cyan-300"></i> Fotos dos Pais & Drive
              </button>
            </div>
          </div>

          <!-- Cards das 4 Métricas Principais da DRE & Caixa -->
          <div class="relative z-10 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            
            <!-- Card 1: Faturamento / Receita Bruta -->
            <div onclick="navegarPara('analytics-financeiro')" class="cursor-pointer bg-white/5 hover:bg-white/10 border border-white/10 hover:border-emerald-400/50 rounded-2xl p-4 transition group">
              <div class="flex items-center justify-between text-xs text-slate-400 mb-1">
                <span class="font-bold uppercase tracking-wider text-emerald-300 flex items-center gap-1.5">
                  <i class="fa-solid fa-money-bill-wave text-emerald-400"></i> Receita Bruta (Safra)
                </span>
                <span class="text-[10px] text-slate-400">4 Romaneios</span>
              </div>
              <div id="kpi-macro-contabil-receita" class="text-2xl font-black text-white font-mono my-1">
                R$ 329.080,00
              </div>
              <div class="text-[11px] text-slate-300 flex items-center justify-between">
                <span>Total Faturado 2026/2</span>
                <span class="text-emerald-400 font-bold group-hover:translate-x-0.5 transition">Ver DRE ➔</span>
              </div>
            </div>

            <!-- Card 2: Custos Pagos & Despesas -->
            <div onclick="navegarPara('analytics-financeiro')" class="cursor-pointer bg-white/5 hover:bg-white/10 border border-white/10 hover:border-amber-400/50 rounded-2xl p-4 transition group">
              <div class="flex items-center justify-between text-xs text-slate-400 mb-1">
                <span class="font-bold uppercase tracking-wider text-amber-300 flex items-center gap-1.5">
                  <i class="fa-solid fa-receipt text-amber-400"></i> Custos & Despesas DRE
                </span>
                <span class="text-[10px] text-amber-300/80">Custos Pagos</span>
              </div>
              <div id="kpi-macro-contabil-custos" class="text-2xl font-black text-amber-200 font-mono my-1">
                R$ 265.450,00
              </div>
              <div class="text-[11px] text-slate-300 flex items-center justify-between">
                <span>Ração, Energia, Folha & PL</span>
                <span class="text-amber-400 font-bold group-hover:translate-x-0.5 transition">Plano de Contas ➔</span>
              </div>
            </div>

            <!-- Card 3: Lucro Líquido Realizado (DRE) -->
            <div onclick="navegarPara('analytics-financeiro')" class="cursor-pointer bg-white/5 hover:bg-white/10 border border-white/10 hover:border-emerald-400/50 rounded-2xl p-4 transition group">
              <div class="flex items-center justify-between text-xs text-slate-400 mb-1">
                <span class="font-bold uppercase tracking-wider text-emerald-300 flex items-center gap-1.5">
                  <i class="fa-solid fa-trophy text-emerald-400"></i> Lucro Líquido (DRE)
                </span>
                <span class="px-1.5 py-0.2 rounded bg-emerald-500/20 text-emerald-300 text-[10px] font-bold">18,6% Margem</span>
              </div>
              <div id="kpi-macro-contabil-lucro" class="text-2xl font-black text-emerald-400 font-mono my-1">
                R$ 61.089,00
              </div>
              <div class="text-[11px] text-slate-300 flex items-center justify-between">
                <span id="kpi-macro-contabil-lucro-margem">Competência / Safra 2026/2</span>
                <span class="text-emerald-400 font-bold group-hover:translate-x-0.5 transition">Detalhar ➔</span>
              </div>
            </div>

            <!-- Card 4: Saldo de Caixa & Integridade Anti-Duplicidade -->
            <div onclick="navegarPara('analytics-ged')" class="cursor-pointer bg-white/5 hover:bg-white/10 border border-white/10 hover:border-cyan-400/50 rounded-2xl p-4 transition group">
              <div class="flex items-center justify-between text-xs text-slate-400 mb-1">
                <span class="font-bold uppercase tracking-wider text-cyan-300 flex items-center gap-1.5">
                  <i class="fa-solid fa-shield-check text-cyan-400"></i> Caixa & Triagem IA
                </span>
                <span class="text-[10px] text-cyan-300/80">Anti-Duplicidade</span>
              </div>
              <div id="kpi-macro-contabil-saldo-caixa" class="text-2xl font-black text-cyan-200 font-mono my-1">
                R$ 63.630,00
              </div>
              <div class="text-[11px] text-slate-300 flex items-center justify-between">
                <span>25 Notas • 0 Duplicatas</span>
                <span class="text-cyan-400 font-bold group-hover:translate-x-0.5 transition">Ver GED ➔</span>
              </div>
            </div>

          </div>

          <!-- Rodapé de Status do Ecossistema dos Pais -->
          <div class="relative z-10 mt-4 pt-3 border-t border-white/10 flex flex-wrap items-center justify-between gap-3 text-xs text-slate-300">
            <div class="flex items-center gap-3">
              <span class="flex items-center gap-1.5 text-emerald-300 font-semibold">
                <i class="fa-solid fa-circle-check"></i> 25 Lançamentos na Planilha Oficial
              </span>
              <span class="text-slate-500">•</span>
              <span class="flex items-center gap-1.5 text-blue-200">
                <i class="fa-solid fa-shield-halved text-cyan-400"></i> Bloqueio Estrito Ativo (Mesmo Valor + Fornecedor + Vencimento)
              </span>
              <span class="text-slate-500">•</span>
              <span class="flex items-center gap-1.5 text-amber-200">
                <i class="fa-solid fa-clock-rotate-left text-amber-400"></i> Backup Diário em 03_BACKUPS_DIARIOS
              </span>
            </div>
            <div class="flex items-center gap-2">
              <span class="text-[11px] text-slate-400">Alocação por viveiro decidida por você:</span>
              <button onclick="navegarPara('analytics-financeiro')" class="text-amber-300 hover:text-white font-bold underline text-xs cursor-pointer">
                Direcionar Custos para Viveiros ➔
              </button>
            </div>
          </div>
        </div>

        <!-- ======================================================== -->
        <!-- 2. PAINEL RÁPIDO DE MANEJO DIÁRIO (OPERACIONAL)         -->'''

    if target_macro_pos in content:
        content = content.replace(target_macro_pos, bloco_contabil_macro)
        print("[OK] Bloco executivo de Contabilidade & DRE inserido na tela Macro inicial.")
    else:
        print("[Erro] target_macro_pos nao encontrado!")
        sys.exit(1)

    # 3. Atualizar função recarregarVisoesContabeis para sincronizar também os novos KPIs Macro
    target_kpi_func = '''      if (elCai) elCai.textContent = formatarMoedaBR(saldoCaixa);
      if (elPen) elPen.textContent = formatarMoedaBR(saidasPend);

      const badgeDedup = document.getElementById('badge-contabil-dedup');'''

    replace_kpi_func = '''      if (elCai) elCai.textContent = formatarMoedaBR(saldoCaixa);
      if (elPen) elPen.textContent = formatarMoedaBR(saidasPend);

      // Atualiza também os cards do Dashboard Macro na tela inicial
      const elMacroRec = document.getElementById('kpi-macro-contabil-receita');
      const elMacroCus = document.getElementById('kpi-macro-contabil-custos');
      const elMacroLuc = document.getElementById('kpi-macro-contabil-lucro');
      const elMacroLucMargem = document.getElementById('kpi-macro-contabil-lucro-margem');
      const elMacroCai = document.getElementById('kpi-macro-contabil-saldo-caixa');

      if (elMacroRec) elMacroRec.textContent = formatarMoedaBR(recBruta);
      if (elMacroCus) elMacroCus.textContent = formatarMoedaBR(totalCustosDre);
      if (elMacroLuc) {
        elMacroLuc.textContent = formatarMoedaBR(lucroLiq);
        elMacroLuc.className = `text-2xl font-black font-mono my-1 ${lucroLiq >= 0 ? 'text-emerald-400' : 'text-rose-400'}`;
      }
      if (elMacroLucMargem) {
        const margemPct = recBruta > 0 ? ((lucroLiq / recBruta) * 100).toFixed(1) : '0.0';
        elMacroLucMargem.textContent = `Margem Líquida: ${margemPct}% (${regime === 'COMPETENCIA' ? 'Competência' : 'Caixa'})`;
      }
      if (elMacroCai) elMacroCai.textContent = formatarMoedaBR(saldoCaixa);

      const badgeDedup = document.getElementById('badge-contabil-dedup');'''

    if target_kpi_func in content:
        content = content.replace(target_kpi_func, replace_kpi_func)
        print("[OK] Funcao recarregarVisoesContabeis() atualizada para alimentar o Dashboard Macro.")
    else:
        print("[Aviso] target_kpi_func nao localizado exatamente.")

    HTML_PATH.write_text(content, encoding="utf-8")
    print(f"[Sucesso] Arquivo {HTML_PATH.name} atualizado com exito.")

if __name__ == "__main__":
    main()
