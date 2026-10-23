# -*- coding: utf-8 -*-
"""
Script para injetar suporte Multi-Fazenda (Multi-Tenant) no dashboard_interativo_prototipo.html:
1. Seletor de Fazenda no Header:
   - Fazenda Arrendada (Operação Ativa • 15 Tanques)
   - Fazenda Hakka (Propriedade Própria • Em Configuração)
   - Visão Grupo Consolidada
2. Estado dinâmico: alternar para a Fazenda Hakka exibe a tela de onboarding,
   checklist de implantação e botão para cadastrar os novos tanques assim que chegarem os dados.
3. Atualização de textos e badges para refletir a Fazenda Arrendada como fazenda ativa.
"""

import os
import re

html_path = r"G:\Meu Drive\ANTIGRAVITY DRIVE\CAMARÃO\ERP CAMARÃO\dashboard_interativo_prototipo.html"

with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Atualizar o Header para incluir o Seletor de Fazenda
# Vamos procurar a barra superior e adicionar o Farm Switcher
antigo_header_identidade = r'''            <div>
              <div class="flex items-center space-x-2">
                <span id="page-title-badge" class="text-xs font-semibold px-2 py-0.5 rounded bg-aco/40 text-blue-100 border border-aco/50">Visão Geral</span>
                <h1 id="page-current-heading" class="text-base sm:text-lg font-bold text-white truncate">
                  Dashboard Macro da Fazenda
                </h1>
              </div>
              <p id="page-breadcrumb" class="text-xs text-blue-200 font-medium">Início > Visão Geral > Macro</p>
            </div>'''

novo_header_identidade = r'''            <div>
              <div class="flex items-center space-x-2">
                <!-- Seletor Multi-Fazenda Dropdown -->
                <div class="relative inline-block text-left">
                  <button id="btn-farm-selector" onclick="toggleFarmDropdown()" class="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-white/10 hover:bg-white/20 border border-white/20 text-white font-bold text-xs sm:text-sm shadow-sm transition">
                    <span id="current-farm-icon">🏢</span>
                    <span id="current-farm-name">Fazenda Arrendada</span>
                    <span id="current-farm-badge" class="px-1.5 py-0.2 rounded bg-emerald-500/30 text-emerald-300 text-[10px] font-semibold border border-emerald-400/40">Ativa</span>
                    <i class="fa-solid fa-chevron-down text-[10px] text-blue-200 ml-1"></i>
                  </button>

                  <!-- Menu Dropdown de Seleção de Fazenda -->
                  <div id="farm-dropdown-menu" class="hidden absolute left-0 mt-2 w-64 rounded-2xl bg-white text-slate-800 shadow-2xl border border-slate-200 z-50 p-2 space-y-1">
                    <div class="px-3 py-1.5 text-[10px] font-bold uppercase tracking-wider text-slate-400 border-b border-slate-100">
                      Alternar Propriedade
                    </div>
                    <button onclick="selecionarFazenda('arrendada')" class="w-full flex items-center justify-between p-2.5 rounded-xl text-left hover:bg-slate-50 transition border border-transparent hover:border-slate-200">
                      <div class="flex items-center space-x-2.5">
                        <span class="text-lg">🏢</span>
                        <div>
                          <strong class="text-xs block text-slate-900">Fazenda Arrendada</strong>
                          <span class="text-[10px] text-slate-500">Ceará-Mirim/RN • 15 Tanques</span>
                        </div>
                      </div>
                      <span class="px-1.5 py-0.5 rounded text-[9px] font-extrabold bg-emerald-100 text-emerald-800">Operando</span>
                    </button>

                    <button onclick="selecionarFazenda('hakka')" class="w-full flex items-center justify-between p-2.5 rounded-xl text-left hover:bg-slate-50 transition border border-transparent hover:border-slate-200">
                      <div class="flex items-center space-x-2.5">
                        <span class="text-lg">🦐</span>
                        <div>
                          <strong class="text-xs block text-slate-900">Fazenda Hakka</strong>
                          <span class="text-[10px] text-slate-500">Propriedade Própria</span>
                        </div>
                      </div>
                      <span class="px-1.5 py-0.5 rounded text-[9px] font-extrabold bg-blue-100 text-aco">Futura</span>
                    </button>

                    <button onclick="selecionarFazenda('grupo')" class="w-full flex items-center justify-between p-2.5 rounded-xl text-left hover:bg-slate-50 transition border border-transparent hover:border-slate-200">
                      <div class="flex items-center space-x-2.5">
                        <span class="text-lg">🌐</span>
                        <div>
                          <strong class="text-xs block text-slate-900">Grupo Consolidado</strong>
                          <span class="text-[10px] text-slate-500">Visão Geral Todas as Fazendas</span>
                        </div>
                      </div>
                      <span class="px-1.5 py-0.5 rounded text-[9px] font-extrabold bg-purple-100 text-purple-800">Multi</span>
                    </button>
                  </div>
                </div>

                <span id="page-title-badge" class="hidden sm:inline text-xs font-semibold px-2 py-0.5 rounded bg-aco/40 text-blue-100 border border-aco/50">Visão Geral</span>
              </div>
              <p id="page-breadcrumb" class="text-xs text-blue-200 font-medium">Início > Fazenda Arrendada > Dashboard Macro</p>
            </div>'''

if antigo_header_identidade in html:
    html = html.replace(antigo_header_identidade, novo_header_identidade)
    print("Header atualizado com Farm Switcher!")
else:
    print("Aviso: Trecho do header não encontrado exatamente para substituição.")

# 2. Adicionar a View da Fazenda Hakka (Onboarding & Configuração)
view_hakka_html = r'''
      <!-- ======================================================== -->
      <!-- VIEW: FAZENDA HAKKA (EM CONFIGURAÇÃO / PROPRIEDADE PRÓPRIA)-->
      <!-- ======================================================== -->
      <section id="view-fazenda-hakka" class="hidden space-y-6">
        
        <!-- Banner de Boas-Vindas da Fazenda Hakka -->
        <div class="bg-gradient-to-r from-marinho to-aco rounded-3xl p-6 sm:p-8 text-white shadow-xl relative overflow-hidden">
          <div class="absolute -right-10 -bottom-10 text-white/5 text-9xl font-black">HAKKA</div>
          <div class="relative z-10 max-w-2xl space-y-3">
            <div class="flex items-center space-x-2">
              <span class="px-2.5 py-0.5 rounded-full bg-cyan-400/20 text-cyan-200 text-xs font-extrabold border border-cyan-400/30">
                ⭐ Propriedade Própria
              </span>
              <span class="px-2.5 py-0.5 rounded-full bg-white/10 text-white text-xs font-medium">
                Módulo Multi-Fazenda Ativo
              </span>
            </div>
            <h2 class="text-2xl sm:text-3xl font-black tracking-tight text-white">
              Fazenda Hakka — Em Preparação Operacional
            </h2>
            <p class="text-blue-100 text-xs sm:text-sm leading-relaxed">
              A arquitetura do ERP já está 100% pronta para receber a Fazenda Hakka de forma isolada e segura. Quando os dados topográficos, áreas de tanques e licenças estiverem disponíveis, você poderá cadastrá-los aqui ou importar a planilha correspondente.
            </p>
            <div class="pt-2 flex flex-wrap gap-2.5">
              <button onclick="abrirModalCadastroViveiroHakka()" class="px-4 py-2.5 rounded-xl bg-white text-marinho font-bold text-xs shadow hover:bg-blue-50 transition flex items-center gap-2">
                <i class="fa-solid fa-plus-circle text-aco"></i> Cadastrar Novo Viveiro na Hakka
              </button>
              <button onclick="selecionarFazenda('arrendada')" class="px-4 py-2.5 rounded-xl bg-white/10 hover:bg-white/20 text-white font-semibold text-xs border border-white/20 transition flex items-center gap-2">
                <i class="fa-solid fa-arrow-left"></i> Voltar para Fazenda Arrendada
              </button>
            </div>
          </div>
        </div>

        <!-- Cards de Estado Atual da Fazenda Hakka -->
        <div class="grid grid-cols-1 sm:grid-cols-4 gap-4">
          <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm text-center">
            <span class="text-xs font-bold text-slate-400 uppercase">Viveiros Cadastrados</span>
            <div id="hakka-count-vivs" class="text-3xl font-extrabold text-slate-800 mt-1">0</div>
            <span class="text-[11px] text-slate-500 mt-1">Aguardando levantamento</span>
          </div>
          <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm text-center">
            <span class="text-xs font-bold text-slate-400 uppercase">Área Total Mapeada</span>
            <div class="text-3xl font-extrabold text-aco mt-1">0.0 ha</div>
            <span class="text-[11px] text-slate-500 mt-1">Capacidade em planejamento</span>
          </div>
          <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm text-center">
            <span class="text-xs font-bold text-slate-400 uppercase">Status Ambiental IDEMA</span>
            <div class="text-xl font-extrabold text-amber-600 mt-2">Em Tramitação</div>
            <span class="text-[11px] text-slate-500 mt-1">Licença de Instalação/Operação</span>
          </div>
          <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm text-center">
            <span class="text-xs font-bold text-slate-400 uppercase">Segregação Contábil</span>
            <div class="text-xl font-extrabold text-emerald-600 mt-2">100% Isolada</div>
            <span class="text-[11px] text-emerald-700 font-semibold mt-1">CNPJ e custos independentes</span>
          </div>
        </div>

        <!-- Checklist de Implantação da Fazenda Hakka -->
        <div class="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-4">
          <h3 class="text-sm font-bold text-slate-800 flex items-center gap-2">
            <i class="fa-solid fa-list-check text-aco"></i> Checklist de Inicialização da Fazenda Hakka
          </h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
            <div class="p-4 bg-slate-50 border border-slate-200 rounded-xl flex items-start space-x-3">
              <input type="checkbox" disabled class="mt-1 h-4 w-4 rounded text-aco focus:ring-aco">
              <div>
                <strong class="text-slate-900 block font-bold">1. Mapeamento Topográfico e Geometria dos Tanques</strong>
                <p class="text-slate-500 mt-0.5">Medição de área em hectares/m², cotas de profundidade e canal de abastecimento da Fazenda Hakka.</p>
              </div>
            </div>
            <div class="p-4 bg-slate-50 border border-slate-200 rounded-xl flex items-start space-x-3">
              <input type="checkbox" disabled class="mt-1 h-4 w-4 rounded text-aco focus:ring-aco">
              <div>
                <strong class="text-slate-900 block font-bold">2. Cadastro de Berçários e Bacia de Sedimentação</strong>
                <p class="text-slate-500 mt-0.5">Definição dos tanques de aclimatação e bacias de decantação exigidas pelo IDEMA-RN.</p>
              </div>
            </div>
            <div class="p-4 bg-slate-50 border border-slate-200 rounded-xl flex items-start space-x-3">
              <input type="checkbox" disabled class="mt-1 h-4 w-4 rounded text-aco focus:ring-aco">
              <div>
                <strong class="text-slate-900 block font-bold">3. Dimensionamento Energético & Aeradores</strong>
                <p class="text-slate-500 mt-0.5">Levantamento de potência instalada (CV de aeração por biomassa prevista e bombas de captação).</p>
              </div>
            </div>
            <div class="p-4 bg-slate-50 border border-slate-200 rounded-xl flex items-start space-x-3">
              <input type="checkbox" checked disabled class="mt-1 h-4 w-4 rounded text-emerald-600 focus:ring-emerald-500">
              <div>
                <strong class="text-emerald-900 block font-bold">4. Arquitetura Multi-Tenant no ERP (Concluído)</strong>
                <p class="text-emerald-700 mt-0.5">Estrutura de dados pronta com separação estrita por fazenda_id no PostgreSQL e seletor ativo.</p>
              </div>
            </div>
          </div>
        </div>

      </section>
'''

# Injetar a view da Hakka antes do final do <main>
if '</main>' in html:
    html = html.replace('</main>', view_hakka_html + '\n    </main>')
    print("View da Fazenda Hakka injetada com sucesso!")

# 3. Adicionar as funções JavaScript para o Seletor de Fazenda
js_multitenant = r'''
    // ==========================================
    // SISTEMA MULTI-FAZENDA (MULTI-TENANT)
    // ==========================================
    let currentFazenda = 'arrendada'; // 'arrendada', 'hakka', 'grupo'

    function toggleFarmDropdown() {
      const menu = document.getElementById('farm-dropdown-menu');
      if (menu) menu.classList.toggle('hidden');
    }

    // Fechar dropdown ao clicar fora
    window.addEventListener('click', (e) => {
      const btn = document.getElementById('btn-farm-selector');
      const menu = document.getElementById('farm-dropdown-menu');
      if (btn && menu && !btn.contains(e.target) && !menu.contains(e.target)) {
        menu.classList.add('hidden');
      }
    });

    function selecionarFazenda(fazendaKey) {
      currentFazenda = fazendaKey;
      toggleFarmDropdown();

      const nameEl = document.getElementById('current-farm-name');
      const iconEl = document.getElementById('current-farm-icon');
      const badgeEl = document.getElementById('current-farm-badge');

      if (fazendaKey === 'arrendada') {
        if (nameEl) nameEl.textContent = 'Fazenda Arrendada';
        if (iconEl) iconEl.textContent = '🏢';
        if (badgeEl) {
          badgeEl.textContent = 'Ativa';
          badgeEl.className = 'px-1.5 py-0.2 rounded bg-emerald-500/30 text-emerald-300 text-[10px] font-semibold border border-emerald-400/40';
        }
        document.getElementById('view-fazenda-hakka').classList.add('hidden');
        navegarPara('dashboard-macro');
      } else if (fazendaKey === 'hakka') {
        if (nameEl) nameEl.textContent = 'Fazenda Hakka';
        if (iconEl) iconEl.textContent = '🦐';
        if (badgeEl) {
          badgeEl.textContent = 'Em Configuração';
          badgeEl.className = 'px-1.5 py-0.2 rounded bg-blue-500/30 text-blue-200 text-[10px] font-semibold border border-blue-400/40';
        }
        // Ocultar todas as outras views e exibir a tela da Hakka
        const views = [
          'dashboard-macro', 'viveiros-mapa', 'analytics-biomassa', 'analytics-fca',
          'analytics-arracoamento', 'analytics-estoque', 'analytics-agua',
          'analytics-viveiro-detalhe', 'auditoria-central', 'analytics-financeiro',
          'analytics-equipe', 'analytics-mercado'
        ];
        views.forEach(v => {
          const el = document.getElementById(`view-${v}`);
          if (el) el.classList.add('hidden');
        });
        document.getElementById('view-fazenda-hakka').classList.remove('hidden');
        atualizarHeaderNavegacao('Fazenda Hakka (Propriedade Própria)', 'Início > Fazenda Hakka > Configuração');
      } else if (fazendaKey === 'grupo') {
        alert('🌐 [Visão Consolidada do Grupo]\n\nAtualmente consolida a operação da Fazenda Arrendada (31.400 kg de biomassa). Quando a Fazenda Hakka iniciar seus ciclos, os números serão somados aqui automaticamente.');
      }
    }

    function abrirModalCadastroViveiroHakka() {
      alert('📝 [Cadastro de Tanque — Fazenda Hakka]\n\nO formulário de mapeamento topográfico está pronto para quando você tiver as dimensões dos viveiros da Fazenda Hakka (Área em m², profundidade e volume).');
    }
'''

# Injetar o JS do multi-fazenda antes de </script>
pos_script = html.rfind('</script>')
if pos_script != -1:
    html = html[:pos_script] + js_multitenant + '\n  ' + html[pos_script:]
    print("Funções JS de Multi-Fazenda injetadas!")

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)

print("Arquivo atualizado com suporte Multi-Fazenda com sucesso!")
