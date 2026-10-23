"""
Script para transformar a visualização de horários no estilo Google Agenda,
permitir configurar a jornada de trabalho dos colaboradores e colocar a tabela
de salários no topo conforme solicitado pelo usuário.
"""
import re
import sys
from pathlib import Path

BASE_DIR = Path(r"G:\Meu Drive\ANTIGRAVITY DRIVE\CAMARÃO\ERP CAMARÃO")
HTML_PATH = BASE_DIR / "dashboard_interativo_prototipo.html"
html_content = HTML_PATH.read_text(encoding="utf-8")

# 1. Nova Seção HTML do Módulo de Equipe
nova_secao_equipe_html = """      <!-- ======================================================== -->
      <!-- VIEW: MÓDULO DE EQUIPE, VIGIA NOTURNO, ESCALAS & CUSTOS  -->
      <!-- ======================================================== -->
      <section id="view-analytics-equipe" class="hidden space-y-6">
        
        <!-- Header da Página de Equipe com Ações Rápidas -->
        <div class="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4 bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <div class="space-y-1">
            <div class="flex items-center space-x-2 text-xs font-semibold text-aco">
              <span class="cursor-pointer hover:underline" onclick="navegarPara('dashboard-macro')">Dashboard</span>
              <i class="fa-solid fa-chevron-right text-[10px] text-slate-400"></i>
              <span>Operação</span>
              <i class="fa-solid fa-chevron-right text-[10px] text-slate-400"></i>
              <span class="text-slate-600">Equipe & Vigia Noturno</span>
            </div>
            <h2 class="text-xl font-bold text-slate-900 flex items-center gap-2">
              <i class="fa-solid fa-users-gear text-violet-600"></i> Gestão de Equipe, Vigia Noturno & Jornada de Trabalho
            </h2>
            <p class="text-xs text-slate-500">Fazenda Ceará-Mirim/RN • Controle de Jornadas de Trabalho, Escala Estilo Google Agenda e Custos de Mão de Obra</p>
          </div>

          <!-- Ações Rápidas de Equipe -->
          <div class="flex flex-wrap items-center gap-2">
            <button onclick="abrirModalNovoColaborador()" class="px-3.5 py-2 rounded-xl bg-violet-600 hover:bg-violet-700 text-white font-bold text-xs transition flex items-center gap-1.5 shadow-sm">
              <i class="fa-solid fa-user-plus"></i> Novo Colaborador
            </button>
            <button onclick="abrirModalTemplateEscala()" class="px-3.5 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs transition flex items-center gap-1.5 border border-slate-200">
              <i class="fa-solid fa-wand-magic-sparkles text-amber-600"></i> Escala 12x36 / 6x1
            </button>
            <button onclick="enviarEscalaWhatsApp()" class="px-3.5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs transition flex items-center gap-1.5 shadow-sm">
              <i class="fab fa-whatsapp"></i> Enviar Escala
            </button>
            <button onclick="navegarPara('dashboard-macro')" class="px-3.5 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs transition flex items-center gap-1.5">
              <i class="fa-solid fa-arrow-left"></i> Voltar
            </button>
          </div>
        </div>

        <!-- 4 Cards de Resumo Operacional e Financeiro -->
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
          <!-- Card 1: Equipe Hoje -->
          <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm">
            <span class="text-[11px] font-bold text-slate-500 uppercase flex items-center gap-1.5">
              <i class="fa-solid fa-users text-violet-600"></i> Equipe em Campo Hoje
            </span>
            <div id="kpi-equipe-total" class="text-xl sm:text-2xl font-extrabold text-slate-900 mt-1">5 Colaboradores</div>
            <span id="kpi-equipe-sub-total" class="text-[10px] text-slate-500 block mt-0.5">4 Mensalistas • 1 Diarista</span>
          </div>

          <!-- Card 2: Vigia Noturno Hoje -->
          <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm border-l-4 border-l-indigo-600">
            <div class="flex items-center justify-between">
              <span class="text-[11px] font-bold text-slate-500 uppercase flex items-center gap-1.5">
                <i class="fa-solid fa-moon text-indigo-600"></i> Vigia Noturno Hoje
              </span>
              <span id="badge-vigia-status" class="px-2 py-0.5 rounded-full text-[9px] font-extrabold bg-indigo-100 text-indigo-800">21h às 06h</span>
            </div>
            <div id="kpi-vigia-nome" class="text-lg sm:text-xl font-extrabold text-indigo-900 mt-1 truncate">Carlos Silva (Carlinhos)</div>
            <div class="flex items-center justify-between mt-1 text-[10px]">
              <span id="kpi-vigia-obs" class="text-slate-500">Ronda de O₂ e aeradores</span>
              <button onclick="abrirModalCheckinVigia()" class="text-indigo-600 hover:text-indigo-800 font-bold hover:underline flex items-center gap-1">
                <i class="fa-solid fa-user-clock text-[9px]"></i> Check-in
              </button>
            </div>
          </div>

          <!-- Card 3: Custo Mensal Previsto -->
          <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm border-l-4 border-l-emerald-500">
            <span class="text-[11px] font-bold text-slate-500 uppercase flex items-center gap-1.5">
              <i class="fa-solid fa-sack-dollar text-emerald-600"></i> Custo da Folha (Mês)
            </span>
            <div id="kpi-custo-folha-total" class="text-xl sm:text-2xl font-extrabold text-emerald-700 mt-1">R$ 7.020,00</div>
            <span id="kpi-custo-folha-sub" class="text-[10px] text-emerald-600 font-semibold block mt-0.5">Fixos: R$ 6.700 • Extras: R$ 320 (R$ 547/ha)</span>
          </div>

          <!-- Card 4: Folgas & Ocorrências -->
          <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm">
            <span class="text-[11px] font-bold text-slate-500 uppercase flex items-center gap-1.5">
              <i class="fa-solid fa-umbrella-beach text-amber-500"></i> Folgas & Ocorrências
            </span>
            <div id="kpi-folgas-hoje" class="text-xl sm:text-2xl font-extrabold text-amber-700 mt-1">1 de Folga Hoje</div>
            <span id="kpi-folgas-sub" class="text-[10px] text-slate-500 block mt-0.5">Tonho (Semanal) • 2 Ocorrências no Mês</span>
          </div>
        </div>

        <!-- ======================================================== -->
        <!-- SEÇÃO NO TOPO: CADASTRO DE COLABORADORES & APURAÇÃO      -->
        <!-- (Conforme solicitado pelo usuário, posicionada no topo)  -->
        <!-- ======================================================== -->
        <div class="bg-white rounded-3xl p-5 border border-slate-200 shadow-sm space-y-4">
          <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-3 border-b border-slate-100">
            <div>
              <h3 class="text-sm font-bold text-slate-900 flex items-center gap-2">
                <i class="fa-solid fa-address-card text-aco"></i> Cadastro de Colaboradores & Apuração Mensal de Salários
              </h3>
              <p class="text-xs text-slate-500">Gestão cadastral, WhatsApp, Chave PIX, jornada de trabalho e fechamento de remuneração fixa vs diárias extras.</p>
            </div>
            <button onclick="abrirModalNovoColaborador()" class="px-3 py-1.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs transition border border-slate-200 flex items-center gap-1">
              <i class="fa-solid fa-plus text-violet-600"></i> Adicionar Membro
            </button>
          </div>

          <div class="overflow-x-auto">
            <table class="w-full text-left text-xs border-collapse">
              <thead>
                <tr class="bg-slate-50 text-slate-500 font-semibold border-b border-slate-200">
                  <th class="py-3 px-3">Colaborador</th>
                  <th class="py-3 px-3">Cargo / Função</th>
                  <th class="py-3 px-3">Jornada Padrão</th>
                  <th class="py-3 px-3">Contato WhatsApp</th>
                  <th class="py-3 px-3">Chave PIX</th>
                  <th class="py-3 px-3">Contrato</th>
                  <th class="py-3 px-3 text-right">Salário Base</th>
                  <th class="py-3 px-3 text-right">Valor Diária Extra</th>
                  <th class="py-3 px-3 text-right">Extras no Mês</th>
                  <th class="py-3 px-3 text-right font-extrabold text-emerald-800">Total a Pagar</th>
                  <th class="py-3 px-3 text-center">Ações</th>
                </tr>
              </thead>
              <tbody id="tbody-tabela-colaboradores" class="divide-y divide-slate-100 font-sans">
                <!-- Injetado dinamicamente via JS -->
              </tbody>
              <tfoot class="bg-slate-50/90 font-bold text-slate-800 border-t-2 border-slate-300">
                <tr>
                  <td class="py-3 px-3" colspan="6">TOTAL DA FOLHA NO MÊS</td>
                  <td id="tfoot-total-fixo" class="py-3 px-3 text-right font-mono text-slate-700">R$ 6.700,00</td>
                  <td class="py-3 px-3"></td>
                  <td id="tfoot-total-extras" class="py-3 px-3 text-right font-mono text-amber-700 font-bold">+R$ 320,00</td>
                  <td id="tfoot-total-geral" class="py-3 px-3 text-right font-mono text-emerald-700 font-extrabold text-sm">R$ 7.020,00</td>
                  <td class="py-3 px-3"></td>
                </tr>
              </tfoot>
            </table>
          </div>
        </div>

        <!-- ======================================================== -->
        <!-- SEÇÃO: AGENDA DE HORÁRIOS & ESCALAS (ESTILO GOOGLE AGENDA)-->
        <!-- ======================================================== -->
        <div class="bg-white rounded-3xl p-5 border border-slate-200 shadow-sm space-y-4">
          
          <!-- Barra de Navegação Estilo Google Agenda -->
          <div class="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4 pb-4 border-b border-slate-200">
            
            <div class="flex items-center space-x-3">
              <!-- Ícone Google Agenda -->
              <div class="w-10 h-10 rounded-2xl bg-blue-600 text-white flex flex-col items-center justify-center font-bold shadow-md">
                <span class="text-[9px] uppercase tracking-tighter -mb-1 opacity-80" id="google-agenda-dia-semana-label">QUI</span>
                <span class="text-base font-black leading-none" id="google-agenda-dia-numero-label">22</span>
              </div>

              <div>
                <div class="flex items-center space-x-2">
                  <h3 class="text-base font-bold text-slate-900" id="google-agenda-titulo-mes">Outubro de 2026</h3>
                  <span class="text-xs text-slate-400 font-normal" id="google-agenda-subtitulo-periodo">• Semana Atual</span>
                </div>
                <div class="flex items-center space-x-1.5 mt-0.5">
                  <button onclick="navegarSemanaGoogleAgenda(-1)" title="Semana Anterior" class="w-7 h-7 rounded-lg hover:bg-slate-100 text-slate-600 flex items-center justify-center transition border border-slate-200">
                    <i class="fa-solid fa-chevron-left text-xs"></i>
                  </button>
                  <button onclick="irParaHojeGoogleAgenda()" class="px-2.5 py-1 rounded-lg hover:bg-slate-100 text-slate-700 font-bold text-xs transition border border-slate-200">
                    Hoje
                  </button>
                  <button onclick="navegarSemanaGoogleAgenda(1)" title="Próxima Semana" class="w-7 h-7 rounded-lg hover:bg-slate-100 text-slate-600 flex items-center justify-center transition border border-slate-200">
                    <i class="fa-solid fa-chevron-right text-xs"></i>
                  </button>
                </div>
              </div>
            </div>

            <!-- Filtros de Colaborador (Cores do Google Calendar) & Seletor de Modo -->
            <div class="flex flex-wrap items-center gap-2">
              <div class="flex items-center gap-1.5 bg-slate-50 p-1.5 rounded-xl border border-slate-200">
                <span class="text-[11px] font-bold text-slate-400 px-1"><i class="fa-solid fa-filter text-[10px]"></i> Ver:</span>
                <button onclick="filtrarColaboradorGoogleAgenda('todos')" id="filtro-agenda-todos" class="px-2.5 py-1 rounded-lg text-xs font-bold bg-slate-900 text-white transition shadow-sm">Todos</button>
                <button onclick="filtrarColaboradorGoogleAgenda(1)" id="filtro-agenda-1" class="px-2.5 py-1 rounded-lg text-xs font-semibold bg-indigo-50 text-indigo-700 hover:bg-indigo-100 transition border border-indigo-200 flex items-center gap-1">
                  <span class="w-2 h-2 rounded-full bg-indigo-600"></span> Carlinhos
                </button>
                <button onclick="filtrarColaboradorGoogleAgenda(2)" id="filtro-agenda-2" class="px-2.5 py-1 rounded-lg text-xs font-semibold bg-amber-50 text-amber-700 hover:bg-amber-100 transition border border-amber-200 flex items-center gap-1">
                  <span class="w-2 h-2 rounded-full bg-amber-500"></span> Tião
                </button>
                <button onclick="filtrarColaboradorGoogleAgenda(3)" id="filtro-agenda-3" class="px-2.5 py-1 rounded-lg text-xs font-semibold bg-blue-50 text-blue-700 hover:bg-blue-100 transition border border-blue-200 flex items-center gap-1">
                  <span class="w-2 h-2 rounded-full bg-blue-600"></span> Chico
                </button>
                <button onclick="filtrarColaboradorGoogleAgenda(4)" id="filtro-agenda-4" class="px-2.5 py-1 rounded-lg text-xs font-semibold bg-emerald-50 text-emerald-700 hover:bg-emerald-100 transition border border-emerald-200 flex items-center gap-1">
                  <span class="w-2 h-2 rounded-full bg-emerald-600"></span> Zé
                </button>
                <button onclick="filtrarColaboradorGoogleAgenda(5)" id="filtro-agenda-5" class="px-2.5 py-1 rounded-lg text-xs font-semibold bg-orange-50 text-orange-700 hover:bg-orange-100 transition border border-orange-200 flex items-center gap-1">
                  <span class="w-2 h-2 rounded-full bg-orange-500"></span> Tonho
                </button>
              </div>

              <!-- Alternador entre Semana Google Agenda e Matriz Mensal -->
              <div class="flex items-center gap-1 bg-slate-100 p-1 rounded-xl text-xs border border-slate-200">
                <button id="btn-visao-agenda" onclick="alternarModoVisualizacaoEscala('agenda')" class="px-3 py-1.5 rounded-lg font-bold bg-white text-slate-900 shadow-sm transition flex items-center gap-1">
                  <i class="fa-solid fa-calendar-days text-blue-600"></i> Semana (Agenda)
                </button>
                <button id="btn-visao-matriz" onclick="alternarModoVisualizacaoEscala('matriz')" class="px-3 py-1.5 rounded-lg font-semibold text-slate-600 hover:text-slate-900 transition flex items-center gap-1">
                  <i class="fa-solid fa-table-cells text-slate-400"></i> Matriz Mensal
                </button>
              </div>
            </div>
          </div>

          <!-- CONTAINER 1: VISUALIZAÇÃO ESTILO GOOGLE AGENDA -->
          <div id="container-google-agenda" class="space-y-2">
            
            <!-- Linha de Folgas e Eventos de Dia Inteiro -->
            <div class="bg-slate-50 p-2.5 rounded-2xl border border-slate-200">
              <div class="text-[10px] font-bold text-slate-400 uppercase mb-1.5 flex items-center gap-1">
                <i class="fa-solid fa-umbrella-beach text-amber-500"></i> Folgas, Férias & Atestados da Semana:
              </div>
              <div id="google-agenda-all-day-row" class="grid grid-cols-7 gap-1.5 text-center text-xs">
                <!-- Injetado dinamicamente via JS -->
              </div>
            </div>

            <!-- Grid de Horários Vertical com as 24 Horas -->
            <div id="google-agenda-scroll-container" class="relative max-h-[580px] overflow-y-auto rounded-2xl border border-slate-200 bg-white shadow-inner">
              
              <!-- Cabeçalho Fixo dos Dias da Semana -->
              <div class="sticky top-0 z-30 bg-white/95 backdrop-blur-md border-b border-slate-200 grid grid-cols-12 text-center py-2 shadow-xs">
                <div class="col-span-1 text-[10px] text-slate-400 font-mono flex items-center justify-center">GMT-03</div>
                <div id="google-agenda-dias-header" class="col-span-11 grid grid-cols-7 gap-0">
                  <!-- DOM, SEG, TER... Injetado via JS -->
                </div>
              </div>

              <!-- Corpo dos Horários e Blocos de Trabalho -->
              <div class="relative grid grid-cols-12 min-w-[700px]">
                
                <!-- Coluna de Horas na Esquerda (00:00 a 23:00) -->
                <div class="col-span-1 border-r border-slate-200 bg-slate-50/50 select-none">
                  <div class="h-[52px] text-[10px] text-slate-400 font-mono flex items-start justify-end pr-2 pt-1 border-b border-slate-100">00:00</div>
                  <div class="h-[52px] text-[10px] text-slate-400 font-mono flex items-start justify-end pr-2 pt-1 border-b border-slate-100">02:00</div>
                  <div class="h-[52px] text-[10px] text-slate-400 font-mono flex items-start justify-end pr-2 pt-1 border-b border-slate-100">04:00</div>
                  <div class="h-[52px] text-[10px] text-slate-400 font-mono flex items-start justify-end pr-2 pt-1 border-b border-slate-100">06:00</div>
                  <div class="h-[52px] text-[10px] text-slate-400 font-mono flex items-start justify-end pr-2 pt-1 border-b border-slate-100">07:00</div>
                  <div class="h-[52px] text-[10px] text-slate-400 font-mono flex items-start justify-end pr-2 pt-1 border-b border-slate-100">08:00</div>
                  <div class="h-[52px] text-[10px] text-slate-400 font-mono flex items-start justify-end pr-2 pt-1 border-b border-slate-100">09:00</div>
                  <div class="h-[52px] text-[10px] text-slate-400 font-mono flex items-start justify-end pr-2 pt-1 border-b border-slate-100">10:00</div>
                  <div class="h-[52px] text-[10px] text-slate-400 font-mono flex items-start justify-end pr-2 pt-1 border-b border-slate-100">11:00</div>
                  <div class="h-[52px] text-[10px] text-slate-400 font-mono flex items-start justify-end pr-2 pt-1 border-b border-slate-100">12:00</div>
                  <div class="h-[52px] text-[10px] text-slate-400 font-mono flex items-start justify-end pr-2 pt-1 border-b border-slate-100">13:00</div>
                  <div class="h-[52px] text-[10px] text-slate-400 font-mono flex items-start justify-end pr-2 pt-1 border-b border-slate-100">14:00</div>
                  <div class="h-[52px] text-[10px] text-slate-400 font-mono flex items-start justify-end pr-2 pt-1 border-b border-slate-100">15:00</div>
                  <div class="h-[52px] text-[10px] text-slate-400 font-mono flex items-start justify-end pr-2 pt-1 border-b border-slate-100">16:00</div>
                  <div class="h-[52px] text-[10px] text-slate-400 font-mono flex items-start justify-end pr-2 pt-1 border-b border-slate-100">17:00</div>
                  <div class="h-[52px] text-[10px] text-slate-400 font-mono flex items-start justify-end pr-2 pt-1 border-b border-slate-100">18:00</div>
                  <div class="h-[52px] text-[10px] text-slate-400 font-mono flex items-start justify-end pr-2 pt-1 border-b border-slate-100">19:00</div>
                  <div class="h-[52px] text-[10px] text-slate-400 font-mono flex items-start justify-end pr-2 pt-1 border-b border-slate-100">20:00</div>
                  <div class="h-[52px] text-[10px] text-slate-400 font-mono flex items-start justify-end pr-2 pt-1 border-b border-slate-100">21:00</div>
                  <div class="h-[52px] text-[10px] text-slate-400 font-mono flex items-start justify-end pr-2 pt-1 border-b border-slate-100">22:00</div>
                  <div class="h-[52px] text-[10px] text-slate-400 font-mono flex items-start justify-end pr-2 pt-1 border-b border-slate-100">23:00</div>
                </div>

                <!-- 7 Colunas para os Dias da Semana (com grid e eventos posicionados) -->
                <div id="google-agenda-corpo-colunas" class="col-span-11 grid grid-cols-7 relative">
                  <!-- Injetado dinamicamente via JS -->
                </div>

              </div>
            </div>

            <!-- Legenda Inferior da Agenda -->
            <div class="flex flex-wrap items-center justify-between gap-3 pt-2 text-xs text-slate-500">
              <div class="flex items-center gap-3">
                <span class="flex items-center gap-1"><span class="w-3 h-3 rounded bg-blue-500"></span> <strong>06:30 - 17:00:</strong> Trato & Campo Diurno</span>
                <span class="flex items-center gap-1"><span class="w-3 h-3 rounded bg-indigo-600"></span> <strong>21:00 - 06:00:</strong> Vigia Noturno (12x36)</span>
                <span class="flex items-center gap-1"><span class="w-3 h-3 rounded bg-amber-500"></span> <strong>⭐ Extra:</strong> Diária Adicional Paga</span>
              </div>
              <span class="text-[11px] text-slate-400 italic">* Clique em qualquer bloco para editar o horário da jornada ou registrar ocorrência.</span>
            </div>

          </div>

          <!-- CONTAINER 2: VISUALIZAÇÃO MATRIZ MENSAL (OPÇÃO COMPLEMENTAR) -->
          <div id="container-matriz-mensal" class="hidden space-y-4">
            <div class="overflow-x-auto rounded-2xl border border-slate-200 shadow-inner">
              <table class="w-full text-left text-xs border-collapse bg-white">
                <thead id="thead-grade-escala" class="bg-slate-100 text-slate-700 font-bold border-b border-slate-200">
                  <!-- Injetado via JS -->
                </thead>
                <tbody id="tbody-grade-escala" class="divide-y divide-slate-100">
                  <!-- Injetado via JS -->
                </tbody>
              </table>
            </div>
          </div>

        </div>

      </section>"""

# Substituir a seção view-analytics-equipe antiga
padrao_secao = r'<section id="view-analytics-equipe"[\s\S]*?</section>'
if re.search(padrao_secao, html_content):
    html_content = re.sub(padrao_secao, nova_secao_equipe_html.strip(), html_content, count=1)
    print("Seção view-analytics-equipe atualizada com a tabela de salários no topo e a Google Agenda!")
else:
    print("ERRO: Seção view-analytics-equipe não encontrada!")

# Atualizar o Modal de Cadastro para incluir a Jornada Padrão de Trabalho
novo_campo_jornada_cadastro = """        <!-- Seção Salário, Diária e Jornada de Trabalho -->
        <div class="p-3.5 rounded-2xl bg-slate-50 border border-slate-200 space-y-3">
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-[11px] font-bold text-slate-700 mb-1">Salário Fixo Mensal (R$):</label>
              <input type="number" step="50" id="input-func-salario" class="w-full text-xs font-mono font-bold p-2 rounded-xl border border-slate-300" placeholder="1800.00">
              <span class="text-[9px] text-slate-400">R$ 0 para diaristas puros</span>
            </div>
            <div>
              <label class="block text-[11px] font-bold text-slate-700 mb-1">Valor da Diária Extra (R$):</label>
              <input type="number" step="5" id="input-func-diaria" class="w-full text-xs font-mono font-bold p-2 rounded-xl border border-slate-300 text-amber-700" placeholder="80.00">
              <span class="text-[9px] text-slate-400">Pago por plantão extra</span>
            </div>
          </div>

          <!-- Jornada Padrão de Trabalho -->
          <div class="pt-2 border-t border-slate-200/80">
            <label class="block text-[11px] font-bold text-slate-800 mb-1 flex items-center gap-1.5">
              <i class="fa-solid fa-clock text-violet-600"></i> Jornada de Trabalho Habitual:
            </label>
            <div class="grid grid-cols-2 gap-2">
              <div>
                <label class="block text-[10px] text-slate-500 mb-0.5">Horário Entrada:</label>
                <input type="time" id="input-func-jornada-ini" value="06:30" class="w-full text-xs font-mono font-bold p-2 rounded-xl border border-slate-300 bg-white">
              </div>
              <div>
                <label class="block text-[10px] text-slate-500 mb-0.5">Horário Saída:</label>
                <input type="time" id="input-func-jornada-fim" value="17:00" class="w-full text-xs font-mono font-bold p-2 rounded-xl border border-slate-300 bg-white">
              </div>
            </div>
          </div>
        </div>"""

padrao_salario_cadastro = r'<!-- Seção Salário e Diária -->[\s\S]*?</div>\s*</div>'
if re.search(padrao_salario_cadastro, html_content):
    html_content = re.sub(padrao_salario_cadastro, novo_campo_jornada_cadastro.strip(), html_content, count=1)
    print("Campos de jornada de trabalho adicionados ao modal de cadastro!")

# Atualizar o Modal de Apontamento Diário para permitir configurar horário de entrada e saída
novo_campos_horarios_apontamento = """        <!-- Turno / Situação -->
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1.5">Turno / Situação do Dia:</label>
          <select id="modal-apont-turno" onchange="sugerirHorariosPorTurno()" class="w-full text-xs font-semibold p-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-violet-500 bg-white">
            <option value="DIURNO">☀️ Diurno (Trabalho Normal)</option>
            <option value="NOTURNO_VIGIA">🌙 Vigia Noturno (Ronda Oxigênio)</option>
            <option value="FOLGA">🏖️ Folga Semanal / Descanso</option>
            <option value="FALTA_JUSTIFICADA">🏥 Falta Justificada (Atestado Médico / Licença)</option>
            <option value="FALTA_INJUSTIFICADA">❌ Falta Injustificada (Desconto em Folha)</option>
            <option value="FERIAS">🌴 Férias</option>
          </select>
        </div>

        <!-- Horário da Jornada de Trabalho no Dia -->
        <div id="container-horarios-apontamento" class="p-3.5 rounded-2xl bg-blue-50/60 border border-blue-200 space-y-2">
          <label class="block text-xs font-bold text-blue-950 flex items-center gap-1.5">
            <i class="fa-solid fa-clock text-blue-600"></i> Horário da Jornada de Trabalho:
          </label>
          <div class="grid grid-cols-2 gap-2">
            <div>
              <label class="block text-[10px] font-bold text-blue-800 mb-0.5">Início do Turno:</label>
              <input type="time" id="modal-apont-hora-ini" value="06:30" class="w-full text-xs font-mono font-bold p-2 rounded-xl border border-blue-300 bg-white">
            </div>
            <div>
              <label class="block text-[10px] font-bold text-blue-800 mb-0.5">Término do Turno:</label>
              <input type="time" id="modal-apont-hora-fim" value="17:00" class="w-full text-xs font-mono font-bold p-2 rounded-xl border border-blue-300 bg-white">
            </div>
          </div>
          <div class="flex items-center gap-1.5 pt-1 text-[10px]">
            <span class="text-blue-700 font-bold">Atalhos:</span>
            <button type="button" onclick="definirHorarioJornadaRapida('06:30', '17:00', 'DIURNO')" class="px-2 py-0.5 rounded bg-white border border-blue-200 text-blue-800 hover:bg-blue-100">☀️ 06:30-17:00</button>
            <button type="button" onclick="definirHorarioJornadaRapida('21:00', '06:00', 'NOTURNO_VIGIA')" class="px-2 py-0.5 rounded bg-white border border-indigo-200 text-indigo-800 hover:bg-indigo-100">🌙 21:00-06:00</button>
            <button type="button" onclick="definirHorarioJornadaRapida('07:00', '16:30', 'DIURNO')" class="px-2 py-0.5 rounded bg-white border border-emerald-200 text-emerald-800 hover:bg-emerald-100">⚙️ 07:00-16:30</button>
          </div>
        </div>"""

padrao_turno_apontamento = r'<!-- Turno / Situação -->[\s\S]*?</select>\s*</div>'
if re.search(padrao_turno_apontamento, html_content):
    html_content = re.sub(padrao_turno_apontamento, novo_campos_horarios_apontamento.strip(), html_content, count=1)
    print("Campos de horários de jornada adicionados ao modal de apontamento!")

# 4. Substituição do Script de Equipe pela versão completa com o motor Google Agenda
funcoes_equipe_agenda_js = """
    // ========================================================
    // MOTOR DE JORNADA DE TRABALHO & GOOGLE AGENDA DA FAZENDA
    // ========================================================
    let modoVisualizacaoEscalaAtual = 'agenda'; // 'agenda' (Google Calendar) ou 'matriz'
    let dataInicioSemanaAgenda = null;         // Domingo da semana exibida
    let filtroColaboradorId = 'todos';         // 'todos' ou ID do colaborador
    let pontoSelecionado = null;
    let funcionarioEmEdicao = null;

    // Cores temáticas por colaborador (paleta Google Calendar)
    const CORES_COLABORADORES = {
      1: { nome: 'Carlinhos', bg: 'bg-indigo-600', bgLight: 'bg-indigo-50 text-indigo-900 border-indigo-400', border: 'border-l-indigo-600', hex: '#4F46E5' },
      2: { nome: 'Tião', bg: 'bg-amber-500', bgLight: 'bg-amber-50 text-amber-900 border-amber-400', border: 'border-l-amber-500', hex: '#F59E0B' },
      3: { nome: 'Chico', bg: 'bg-blue-600', bgLight: 'bg-blue-50 text-blue-900 border-blue-400', border: 'border-l-blue-600', hex: '#2563EB' },
      4: { nome: 'Zé do Motor', bg: 'bg-emerald-600', bgLight: 'bg-emerald-50 text-emerald-900 border-emerald-400', border: 'border-l-emerald-600', hex: '#059669' },
      5: { nome: 'Tonho', bg: 'bg-orange-600', bgLight: 'bg-orange-50 text-orange-900 border-orange-400', border: 'border-l-orange-600', hex: '#EA580C' }
    };

    let FUNCIONARIOS_DATA = [
      {
        id: 1, nome: 'Carlos Silva', apelido: 'Carlinhos', cargo: 'Vigia Noturno',
        telefone: '(84) 99876-1101', whatsapp: '84998761101', chavePix: 'carlinhos.vigia@email.com',
        tipoContrato: 'MENSALISTA', salarioBase: 1800.0, valorDiariaExtra: 80.0, ativo: true,
        jornadaIni: '21:00', jornadaFim: '06:00', jornadaDesc: '21h às 06h (12x36)',
        fazenda: 'Fazenda Arrendada', observacoes: 'Vigia titular noturno (ronda de O2 e aeradores). Escala 12x36.'
      },
      {
        id: 2, nome: 'Sebastião Oliveira', apelido: 'Tião', cargo: 'Vigia Noturno Folguista',
        telefone: '(84) 99876-1102', whatsapp: '84998761102', chavePix: '84998761102',
        tipoContrato: 'DIARISTA', salarioBase: 0.0, valorDiariaExtra: 90.0, ativo: true,
        jornadaIni: '21:00', jornadaFim: '06:00', jornadaDesc: '21h às 06h (Plantões)',
        fazenda: 'Fazenda Arrendada', observacoes: 'Vigia folguista e plantonista de apoio. Recebe por plantão noturno.'
      },
      {
        id: 3, nome: 'Francisco Santos', apelido: 'Chico', cargo: 'Arraçoador Principal',
        telefone: '(84) 99876-1103', whatsapp: '84998761103', chavePix: 'chico.camarao@pix.com',
        tipoContrato: 'MENSALISTA', salarioBase: 1650.0, valorDiariaExtra: 75.0, ativo: true,
        jornadaIni: '06:30', jornadaFim: '17:00', jornadaDesc: '06h30 às 17h00 (6x1)',
        fazenda: 'Fazenda Arrendada', observacoes: 'Responsável pelo trato diurno e conferência de bandejas de sobra (0 a 3).'
      },
      {
        id: 4, nome: 'José Ferreira', apelido: 'Zé do Motor', cargo: 'Operador de Máquinas e Bombas',
        telefone: '(84) 99876-1104', whatsapp: '84998761104', chavePix: 'zedomotor@email.com',
        tipoContrato: 'MENSALISTA', salarioBase: 1750.0, valorDiariaExtra: 85.0, ativo: true,
        jornadaIni: '07:00', jornadaFim: '16:30', jornadaDesc: '07h00 às 16h30 (6x1)',
        fazenda: 'Fazenda Arrendada', observacoes: 'Manutenção preventiva de motores, compressores e aeradores de pá.'
      },
      {
        id: 5, nome: 'Antônio Costa', apelido: 'Tonho', cargo: 'Apoio de Campo e Arraçoamento',
        telefone: '(84) 99876-1105', whatsapp: '84998761105', chavePix: 'tonho.costa@pix.com',
        tipoContrato: 'MENSALISTA', salarioBase: 1500.0, valorDiariaExtra: 70.0, ativo: true,
        jornadaIni: '06:30', jornadaFim: '16:30', jornadaDesc: '06h30 às 16h30 (6x1)',
        fazenda: 'Fazenda Arrendada', observacoes: 'Serviços gerais de talude, limpeza de filtros e apoio no trato.'
      }
    ];

    let ESCALAS_MAP = {};

    function inicializarEscalasPadrao() {
      const hoje = new Date();
      const ano = hoje.getFullYear();
      const mes = hoje.getMonth();
      const diasNoMes = new Date(ano, mes + 1, 0).getDate();

      // Gerar escala base do mês com horários exatos de jornada
      for (let dia = 1; dia <= diasNoMes; dia++) {
        const d = new Date(ano, mes, dia);
        const dataStr = d.toISOString().split('T')[0];
        const diaSemana = d.getDay(); // 0 Dom, 6 Sab

        // Carlinhos (1) dias ímpares vigia (21h-06h), dias pares folga
        const carlinhosVigia = (dia % 2 === 1);
        ESCALAS_MAP[`1_${dataStr}`] = {
          funcionarioId: 1, data: dataStr, turno: carlinhosVigia ? 'NOTURNO_VIGIA' : 'FOLGA',
          horaIni: carlinhosVigia ? '21:00' : null, horaFim: carlinhosVigia ? '06:00' : null,
          ehExtra: false, valorDiaria: 0, status: 'CONFIRMADO',
          categoria: 'NORMAL', obs: carlinhosVigia ? 'Ronda de O2 e motores' : ''
        };

        // Tião (2) dias pares vigia (diária R$ 90), dias ímpares folga
        const tiaoVigia = (dia % 2 === 0);
        ESCALAS_MAP[`2_${dataStr}`] = {
          funcionarioId: 2, data: dataStr, turno: tiaoVigia ? 'NOTURNO_VIGIA' : 'FOLGA',
          horaIni: tiaoVigia ? '21:00' : null, horaFim: tiaoVigia ? '06:00' : null,
          ehExtra: tiaoVigia, valorDiaria: tiaoVigia ? 90.0 : 0.0, status: 'CONFIRMADO',
          categoria: 'NORMAL', obs: tiaoVigia ? 'Plantão noturno diarista' : ''
        };

        // Chico (3) folga domingo (0)
        const chicoFolga = (diaSemana === 0);
        ESCALAS_MAP[`3_${dataStr}`] = {
          funcionarioId: 3, data: dataStr, turno: chicoFolga ? 'FOLGA' : 'DIURNO',
          horaIni: chicoFolga ? null : '06:30', horaFim: chicoFolga ? null : '17:00',
          ehExtra: false, valorDiaria: 0, status: 'CONFIRMADO',
          categoria: 'NORMAL', obs: chicoFolga ? 'Folga semanal' : 'Trato e bandejas'
        };

        // Zé do Motor (4) folga sábado (6)
        const zeFolga = (diaSemana === 6);
        ESCALAS_MAP[`4_${dataStr}`] = {
          funcionarioId: 4, data: dataStr, turno: zeFolga ? 'FOLGA' : 'DIURNO',
          horaIni: zeFolga ? null : '07:00', horaFim: zeFolga ? null : '16:30',
          ehExtra: false, valorDiaria: 0, status: 'CONFIRMADO',
          categoria: 'NORMAL', obs: zeFolga ? 'Folga semanal' : 'Checagem de motores'
        };

        // Tonho (5) folga segunda (1)
        const tonhoFolga = (diaSemana === 1);
        ESCALAS_MAP[`5_${dataStr}`] = {
          funcionarioId: 5, data: dataStr, turno: tonhoFolga ? 'FOLGA' : 'DIURNO',
          horaIni: tonhoFolga ? null : '06:30', horaFim: tonhoFolga ? null : '16:30',
          ehExtra: false, valorDiaria: 0, status: 'CONFIRMADO',
          categoria: 'NORMAL', obs: tonhoFolga ? 'Folga semanal' : 'Apoio de campo'
        };
      }

      // Ocorrência realista de exemplo
      const diaOcorr = new Date(ano, mes, 5).toISOString().split('T')[0];
      if (ESCALAS_MAP[`1_${diaOcorr}`]) {
        ESCALAS_MAP[`1_${diaOcorr}`].ehExtra = true;
        ESCALAS_MAP[`1_${diaOcorr}`].valorDiaria = 80.0;
        ESCALAS_MAP[`1_${diaOcorr}`].categoria = 'COBERTURA_TURNO';
        ESCALAS_MAP[`1_${diaOcorr}`].obs = 'Cobriu plantão extra pós-temporal.';
      }

      // Iniciar a semana da Google Agenda no Domingo da semana atual
      irParaHojeGoogleAgenda();
    }

    inicializarEscalasPadrao();

    function irParaHojeGoogleAgenda() {
      const hoje = new Date();
      const diaSemana = hoje.getDay(); // 0 = Domingo
      const d = new Date(hoje);
      d.setDate(hoje.getDate() - diaSemana);
      d.setHours(0, 0, 0, 0);
      dataInicioSemanaAgenda = d;
      renderizarModuloEquipe();
    }

    function navegarSemanaGoogleAgenda(delta) {
      if (!dataInicioSemanaAgenda) irParaHojeGoogleAgenda();
      dataInicioSemanaAgenda.setDate(dataInicioSemanaAgenda.getDate() + (delta * 7));
      renderizarModuloEquipe();
    }

    function alternarModoVisualizacaoEscala(modo) {
      modoVisualizacaoEscalaAtual = modo;
      const btnAgenda = document.getElementById('btn-visao-agenda');
      const btnMatriz = document.getElementById('btn-visao-matriz');
      const contAgenda = document.getElementById('container-google-agenda');
      const contMatriz = document.getElementById('container-matriz-mensal');

      if (modo === 'agenda') {
        if (btnAgenda) btnAgenda.className = 'px-3 py-1.5 rounded-lg font-bold bg-white text-slate-900 shadow-sm transition flex items-center gap-1';
        if (btnMatriz) btnMatriz.className = 'px-3 py-1.5 rounded-lg font-semibold text-slate-600 hover:text-slate-900 transition flex items-center gap-1';
        if (contAgenda) contAgenda.classList.remove('hidden');
        if (contMatriz) contMatriz.classList.add('hidden');
        renderizarGoogleAgendaView();
      } else {
        if (btnMatriz) btnMatriz.className = 'px-3 py-1.5 rounded-lg font-bold bg-white text-slate-900 shadow-sm transition flex items-center gap-1';
        if (btnAgenda) btnAgenda.className = 'px-3 py-1.5 rounded-lg font-semibold text-slate-600 hover:text-slate-900 transition flex items-center gap-1';
        if (contMatriz) contMatriz.classList.remove('hidden');
        if (contAgenda) contAgenda.classList.add('hidden');
        renderizarMatrizMensalView();
      }
    }

    function filtrarColaboradorGoogleAgenda(colabId) {
      filtroColaboradorId = colabId;
      const botoes = ['todos', 1, 2, 3, 4, 5];
      botoes.forEach(b => {
        const el = document.getElementById(`filtro-agenda-${b}`);
        if (el) {
          if (b === colabId) {
            el.className = 'px-2.5 py-1 rounded-lg text-xs font-bold bg-slate-900 text-white transition shadow-sm';
          } else {
            el.className = 'px-2.5 py-1 rounded-lg text-xs font-semibold bg-slate-100 text-slate-600 hover:text-slate-900 transition border border-slate-200';
          }
        }
      });
      renderizarGoogleAgendaView();
    }

    function renderizarModuloEquipe() {
      renderizarTabelaColaboradores();
      atualizarKpisEquipe();
      if (modoVisualizacaoEscalaAtual === 'agenda') {
        renderizarGoogleAgendaView();
      } else {
        renderizarMatrizMensalView();
      }
    }

    // ========================================================
    // RENDERIZADOR ESTILO GOOGLE AGENDA
    // ========================================================
    function renderizarGoogleAgendaView() {
      if (!dataInicioSemanaAgenda) irParaHojeGoogleAgenda();

      const hoje = new Date();
      const hojeStr = hoje.toISOString().split('T')[0];

      // Atualizar ícone e títulos do topo
      const nomesDiasAbrev = ['DOM', 'SEG', 'TER', 'QUA', 'QUI', 'SEX', 'SÁB'];
      const mesesNomes = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'];

      const elHojeIconSem = document.getElementById('google-agenda-dia-semana-label');
      const elHojeIconNum = document.getElementById('google-agenda-dia-numero-label');
      if (elHojeIconSem) elHojeIconSem.textContent = nomesDiasAbrev[hoje.getDay()];
      if (elHojeIconNum) elHojeIconNum.textContent = hoje.getDate();

      const fimSemana = new Date(dataInicioSemanaAgenda);
      fimSemana.setDate(dataInicioSemanaAgenda.getDate() + 6);

      const mesNome = mesesNomes[dataInicioSemanaAgenda.getMonth()];
      const anoNum = dataInicioSemanaAgenda.getFullYear();
      const elTitMes = document.getElementById('google-agenda-titulo-mes');
      const elSubPer = document.getElementById('google-agenda-subtitulo-periodo');
      if (elTitMes) elTitMes.textContent = `${mesNome} de ${anoNum}`;
      if (elSubPer) elSubPer.textContent = `• ${dataInicioSemanaAgenda.getDate()} a ${fimSemana.getDate()} de ${mesesNomes[fimSemana.getMonth()]}`;

      // Montar Cabeçalho de Dias da Semana (exatamente como Google Agenda)
      const headerDias = document.getElementById('google-agenda-dias-header');
      const allDayRow = document.getElementById('google-agenda-all-day-row');
      const colunasBody = document.getElementById('google-agenda-corpo-colunas');

      if (!headerDias || !colunasBody) return;

      headerDias.innerHTML = '';
      if (allDayRow) allDayRow.innerHTML = '';
      colunasBody.innerHTML = '';

      const diasSemana = [];
      for (let i = 0; i < 7; i++) {
        const d = new Date(dataInicioSemanaAgenda);
        d.setDate(dataInicioSemanaAgenda.getDate() + i);
        diasSemana.push(d);
      }

      // 1. Cabeçalho dos 7 Dias
      diasSemana.forEach(d => {
        const dStr = d.toISOString().split('T')[0];
        const isHoje = (dStr === hojeStr);

        headerDias.innerHTML += `
          <div class="py-1 text-center border-r border-slate-100 last:border-r-0">
            <span class="text-[10px] font-bold tracking-wider uppercase ${isHoje ? 'text-blue-600 font-extrabold' : 'text-slate-500'}">
              ${nomesDiasAbrev[d.getDay()]}.
            </span>
            <div class="mt-0.5">
              ${isHoje 
                ? `<span class="w-7 h-7 rounded-full bg-blue-600 text-white font-extrabold text-xs flex items-center justify-center mx-auto shadow-sm">${d.getDate()}</span>`
                : `<span class="text-xs font-bold text-slate-800">${d.getDate()}</span>`
              }
            </div>
          </div>
        `;

        // Linha de Folgas / Eventos All-day
        if (allDayRow) {
          let folgasNoDiaHtml = '';
          FUNCIONARIOS_DATA.filter(f => f.ativo).forEach(f => {
            const item = ESCALAS_MAP[`${f.id}_${dStr}`];
            if (item && item.turno === 'FOLGA') {
              folgasNoDiaHtml += `
                <div onclick="abrirModalApontamentoDia(${f.id}, '${dStr}')" title="${f.nome}: Folga" class="cursor-pointer truncate px-1.5 py-0.5 rounded-md bg-slate-200/90 hover:bg-slate-300 text-[9px] font-semibold text-slate-700 mb-0.5 border border-slate-300">
                  🏖️ ${f.apelido || f.nome.split(' ')[0]}
                </div>
              `;
            } else if (item && item.turno === 'FALTA_JUSTIFICADA') {
              folgasNoDiaHtml += `
                <div onclick="abrirModalApontamentoDia(${f.id}, '${dStr}')" title="${f.nome}: Atestado Médico" class="cursor-pointer truncate px-1.5 py-0.5 rounded-md bg-amber-100 hover:bg-amber-200 text-[9px] font-bold text-amber-800 mb-0.5 border border-amber-300">
                  🏥 ${f.apelido || f.nome.split(' ')[0]} (Atestado)
                </div>
              `;
            } else if (item && item.turno === 'FALTA_INJUSTIFICADA') {
              folgasNoDiaHtml += `
                <div onclick="abrirModalApontamentoDia(${f.id}, '${dStr}')" title="${f.nome}: Falta Injustificada" class="cursor-pointer truncate px-1.5 py-0.5 rounded-md bg-red-100 hover:bg-red-200 text-[9px] font-bold text-red-800 mb-0.5 border border-red-300">
                  ❌ ${f.apelido || f.nome.split(' ')[0]} (Falta)
                </div>
              `;
            }
          });

          allDayRow.innerHTML += `
            <div class="min-h-[28px] border-r border-slate-200/80 last:border-r-0 px-1">
              ${folgasNoDiaHtml || '<span class="text-[9px] text-slate-300 block py-1">-</span>'}
            </div>
          `;
        }
      });

      // 2. Montar Colunas Verticais com os 21 slots de Horário e Blocos de Trabalho
      const horasMarcas = [0, 2, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23];
      const slotHeight = 52; // altura de cada slot em px

      diasSemana.forEach((d, diaIdx) => {
        const dStr = d.toISOString().split('T')[0];
        const isHoje = (dStr === hojeStr);

        let colunaHtml = `
          <div class="relative border-r border-slate-200 last:border-r-0 ${isHoje ? 'bg-blue-50/20' : ''}" style="height: ${horasMarcas.length * slotHeight}px;">
        `;

        // Linhas de grid horizontal para cada hora
        horasMarcas.forEach(h => {
          colunaHtml += `
            <div onclick="clicarSlotVazioGoogleAgenda('${dStr}', '${String(h).padStart(2, '0')}:00')" class="h-[52px] border-b border-slate-100 hover:bg-slate-50/60 transition cursor-pointer"></div>
          `;
        });

        // Eventos e Blocos de Trabalho para este dia
        FUNCIONARIOS_DATA.filter(f => f.ativo).forEach(f => {
          if (filtroColaboradorId !== 'todos' && f.id !== filtroColaboradorId) return;

          const item = ESCALAS_MAP[`${f.id}_${dStr}`];
          if (!item || item.turno === 'FOLGA' || item.turno === 'FERIAS') return;

          const cor = CORES_COLABORADORES[f.id] || CORES_COLABORADORES[3];

          // Determinar início e fim da jornada
          let horaIniStr = item.horaIni || f.jornadaIni || '06:30';
          let horaFimStr = item.horaFim || f.jornadaFim || '17:00';

          const [hIniH, hIniM] = horaIniStr.split(':').map(Number);
          const [hFimH, hFimM] = horaFimStr.split(':').map(Number);

          const hIniDec = hIniH + (hIniM / 60);
          let hFimDec = hFimH + (hFimM / 60);
          if (hFimDec <= hIniDec) hFimDec += 24; // caso passe da meia-noite

          // Mapear posição no grid (aproximação para altura vertical de 52px por marca de 1h)
          // Referência: 00h é topo (0px). 06h é 6 * 52px. 21h é 21 * 52px.
          const topPx = Math.max(0, Math.min(horasMarcas.length * slotHeight - 40, (hIniDec / 24) * (horasMarcas.length * slotHeight)));
          let duracaoHoras = Math.min(14, hFimDec - hIniDec);
          const heightPx = Math.max(38, (duracaoHoras / 24) * (horasMarcas.length * slotHeight));

          const temObs = item.obs && item.obs.trim().length > 0;

          colunaHtml += `
            <div onclick="event.stopPropagation(); abrirModalApontamentoDia(${f.id}, '${dStr}')"
                 style="top: ${topPx}px; height: ${heightPx}px;"
                 class="absolute inset-x-1 rounded-xl p-1.5 border-l-4 ${cor.border} ${cor.bgLight} shadow-xs hover:shadow-md transition cursor-pointer overflow-hidden flex flex-col justify-between z-10 group">
              <div>
                <div class="flex items-center justify-between gap-1 leading-tight">
                  <span class="font-extrabold text-[11px] truncate text-slate-900">${f.apelido || f.nome}</span>
                  <span class="text-[9px] font-mono px-1 rounded bg-white/80 font-bold">${horaIniStr}-${horaFimStr}</span>
                </div>
                <div class="text-[10px] text-slate-600 truncate mt-0.5 font-medium">${f.cargo}</div>
              </div>

              <div class="flex items-center justify-between mt-1 text-[9px] pt-0.5 border-t border-black/5">
                ${item.ehExtra ? `<span class="font-extrabold text-amber-800 bg-yellow-200/90 px-1 rounded flex items-center gap-0.5">⭐ +R$ ${Math.round(item.valorDiaria || f.valorDiariaExtra)}</span>` : `<span class="opacity-75">${item.turno === 'NOTURNO_VIGIA' ? '🌙 Vigia O₂' : '☀️ Diurno'}</span>`}
                ${temObs ? `<i class="fa-solid fa-comment-dots text-violet-700 text-[10px]" title="${item.obs}"></i>` : ''}
              </div>
            </div>
          `;
        });

        colunaHtml += `</div>`;
        colunasBody.innerHTML += colunaHtml;
      });

      // Auto-rolar para visualização de 06:00 (início do dia operacional)
      const scrollEl = document.getElementById('google-agenda-scroll-container');
      if (scrollEl && !scrollEl.dataset.scrolled) {
        scrollEl.scrollTop = 3 * slotHeight; // posiciona em 06:00
        scrollEl.dataset.scrolled = 'true';
      }
    }

    function clicarSlotVazioGoogleAgenda(dataStr, horaStr) {
      // Abre modal de apontamento sugerindo o primeiro colaborador ou selecionado
      const colabId = (filtroColaboradorId !== 'todos') ? filtroColaboradorId : 3; // Chico como padrão
      abrirModalApontamentoDia(colabId, dataStr);
      const inputIni = document.getElementById('modal-apont-hora-ini');
      if (inputIni) inputIni.value = horaStr;
    }

    // ========================================================
    // RENDERIZADOR MATRIZ MENSAL (COMPLEMENTAR)
    // ========================================================
    function renderizarMatrizMensalView() {
      const thead = document.getElementById('thead-grade-escala');
      const tbody = document.getElementById('tbody-grade-escala');
      if (!thead || !tbody) return;

      const hoje = new Date();
      const ano = hoje.getFullYear();
      const mes = hoje.getMonth();
      const diasNoMes = new Date(ano, mes + 1, 0).getDate();
      const hojeStr = hoje.toISOString().split('T')[0];
      const nomesDiasAbrev = ['D', 'S', 'T', 'Q', 'Q', 'S', 'S'];

      let thHtml = `<tr><th class="py-3 px-3.5 sticky left-0 z-20 bg-slate-100 min-w-[190px]">Colaborador</th>`;
      for (let dia = 1; dia <= diasNoMes; dia++) {
        const d = new Date(ano, mes, dia);
        const dataStr = d.toISOString().split('T')[0];
        const isHoje = (dataStr === hojeStr);
        thHtml += `
          <th class="py-2 px-1 text-center font-bold min-w-[36px] ${isHoje ? 'bg-blue-100 text-blue-900 font-extrabold' : ''}">
            <span class="text-[9px] text-slate-400 block">${nomesDiasAbrev[d.getDay()]}</span>
            <span class="text-[11px]">${dia}</span>
          </th>
        `;
      }
      thHtml += `<th class="py-3 px-3 text-right">Extras</th><th class="py-3 px-3 text-right">Total</th></tr>`;
      thead.innerHTML = thHtml;

      tbody.innerHTML = '';
      FUNCIONARIOS_DATA.filter(f => f.ativo).forEach(f => {
        let extrasColab = 0;
        let rowHtml = `
          <tr class="hover:bg-slate-50/80 transition">
            <td class="py-2 px-3 sticky left-0 z-10 bg-white font-bold text-slate-900 border-r border-slate-100">
              <div class="text-xs font-bold">${f.nome}</div>
              <div class="text-[10px] text-slate-400">${f.jornadaDesc || f.cargo}</div>
            </td>
        `;

        for (let dia = 1; dia <= diasNoMes; dia++) {
          const d = new Date(ano, mes, dia);
          const dataStr = d.toISOString().split('T')[0];
          const item = ESCALAS_MAP[`${f.id}_${dataStr}`] || { turno: 'FOLGA' };
          if (item.ehExtra && item.valorDiaria) extrasColab += item.valorDiaria;

          const turnosIcones = {
            DIURNO: '☀️',
            NOTURNO_VIGIA: '🌙',
            FOLGA: '🏖️',
            FALTA_JUSTIFICADA: '🏥',
            FALTA_INJUSTIFICADA: '❌',
            FERIAS: '🌴'
          };
          const icon = turnosIcones[item.turno] || '🏖️';

          rowHtml += `
            <td onclick="abrirModalApontamentoDia(${f.id}, '${dataStr}')" class="py-1.5 px-0.5 text-center cursor-pointer hover:bg-slate-100 transition text-[11px]">
              ${icon}${item.ehExtra ? '⭐' : ''}
            </td>
          `;
        }

        const totalPagar = f.salarioBase + extrasColab;
        rowHtml += `
            <td class="py-2 px-2 text-right font-mono font-bold text-amber-700">+R$ ${extrasColab.toFixed(0)}</td>
            <td class="py-2 px-2 text-right font-mono font-extrabold text-emerald-700 bg-emerald-50/40">R$ ${totalPagar.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</td>
          </tr>
        `;
        tbody.innerHTML += rowHtml;
      });
    }

    // ========================================================
    // TABELA DE CADASTRO E SALÁRIOS (NO TOPO)
    // ========================================================
    function renderizarTabelaColaboradores() {
      const tbody = document.getElementById('tbody-tabela-colaboradores');
      if (!tbody) return;

      tbody.innerHTML = '';
      let somatorioFixo = 0;
      let somatorioExtras = 0;

      FUNCIONARIOS_DATA.filter(f => f.ativo).forEach(f => {
        let extrasMês = 0;
        Object.keys(ESCALAS_MAP).forEach(k => {
          if (k.startsWith(`${f.id}_`)) {
            const item = ESCALAS_MAP[k];
            if (item.ehExtra && item.valorDiaria) extrasMês += item.valorDiaria;
          }
        });

        somatorioFixo += f.salarioBase;
        somatorioExtras += extrasMês;
        const totalPagar = f.salarioBase + extrasMês;

        tbody.innerHTML += `
          <tr class="hover:bg-slate-50/80 transition">
            <td class="py-2.5 px-3 font-bold text-slate-900">
              <div class="flex items-center gap-2">
                <span class="w-6 h-6 rounded-lg ${f.cargo.includes('Vigia') ? 'bg-indigo-100 text-indigo-700' : 'bg-slate-100 text-slate-700'} flex items-center justify-center text-xs font-bold">
                  ${f.nome.charAt(0)}
                </span>
                <div>
                  <strong>${f.nome}</strong>
                  ${f.apelido ? `<span class="text-slate-400 font-normal text-[11px] block">("${f.apelido}")</span>` : ''}
                </div>
              </div>
            </td>
            <td class="py-2.5 px-3 text-slate-700">
              <span class="px-2 py-0.5 rounded-md text-[10px] font-bold ${f.cargo.includes('Vigia') ? 'bg-indigo-100 text-indigo-800' : 'bg-slate-100 text-slate-700'}">
                ${f.cargo}
              </span>
            </td>
            <td class="py-2.5 px-3 text-slate-700 font-mono text-[11px]">
              <span class="px-2 py-0.5 rounded-lg bg-blue-50 text-blue-900 border border-blue-200 font-bold flex items-center gap-1 w-max">
                <i class="fa-solid fa-clock text-[9px] text-blue-600"></i> ${f.jornadaIni || '06:30'} às ${f.jornadaFim || '17:00'}
              </span>
            </td>
            <td class="py-2.5 px-3">
              ${f.whatsapp ? `
                <a href="https://wa.me/55${f.whatsapp.replace(/\\D/g, '')}" target="_blank" class="inline-flex items-center gap-1.5 px-2 py-1 rounded-lg bg-emerald-50 text-emerald-700 hover:bg-emerald-100 font-mono font-semibold text-[11px] transition">
                  <i class="fab fa-whatsapp text-emerald-600"></i> ${f.telefone || f.whatsapp}
                </a>` : '<span class="text-slate-400">-</span>'}
            </td>
            <td class="py-2.5 px-3 font-mono text-[11px] text-slate-600">${f.chavePix || '-'}</td>
            <td class="py-2.5 px-3">
              <span class="px-2 py-0.5 rounded-full text-[10px] font-extrabold ${f.tipoContrato === 'MENSALISTA' ? 'bg-blue-100 text-blue-800' : 'bg-amber-100 text-amber-800'}">
                ${f.tipoContrato}
              </span>
            </td>
            <td class="py-2.5 px-3 text-right font-mono font-bold text-slate-800">
              ${f.salarioBase > 0 ? 'R$ ' + f.salarioBase.toLocaleString('pt-BR', { minimumFractionDigits: 2 }) : '<span class="text-slate-400 font-normal">Diarista puro</span>'}
            </td>
            <td class="py-2.5 px-3 text-right font-mono text-slate-600">
              ${f.valorDiariaExtra > 0 ? 'R$ ' + f.valorDiariaExtra.toFixed(2) : '-'}
            </td>
            <td class="py-2.5 px-3 text-right font-mono font-bold text-amber-700">
              ${extrasMês > 0 ? '+R$ ' + extrasMês.toFixed(2) : '-'}
            </td>
            <td class="py-2.5 px-3 text-right font-mono font-extrabold text-emerald-700 bg-emerald-50/40">
              R$ ${totalPagar.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
            </td>
            <td class="py-2.5 px-3 text-center">
              <button onclick="abrirModalEditarColaborador(${f.id})" class="px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-[11px] transition">
                ✏️ Editar
              </button>
            </td>
          </tr>
        `;
      });

      const totalGeral = somatorioFixo + somatorioExtras;
      const elFixo = document.getElementById('tfoot-total-fixo');
      const elExt = document.getElementById('tfoot-total-extras');
      const elGer = document.getElementById('tfoot-total-geral');

      if (elFixo) elFixo.textContent = `R$ ${somatorioFixo.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`;
      if (elExt) elExt.textContent = `+R$ ${somatorioExtras.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`;
      if (elGer) elGer.textContent = `R$ ${totalGeral.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`;
    }

    function atualizarKpisEquipe() {
      const hojeStr = new Date().toISOString().split('T')[0];
      const ativos = FUNCIONARIOS_DATA.filter(f => f.ativo);

      // 1. Equipe Hoje
      const elTot = document.getElementById('kpi-equipe-total');
      const elSubTot = document.getElementById('kpi-equipe-sub-total');
      if (elTot) elTot.textContent = `${ativos.length} Colaboradores`;
      const mensalistas = ativos.filter(f => f.tipoContrato === 'MENSALISTA').length;
      const diaristas = ativos.filter(f => f.tipoContrato === 'DIARISTA').length;
      if (elSubTot) elSubTot.textContent = `${mensalistas} Mensalistas • ${diaristas} Diarista(s)`;

      // 2. Vigia Noturno Hoje
      let vigiaHojeNome = 'Nenhum vigia agendado';
      let vigiaHojeStatus = '21h às 06h';
      let vigiaObs = 'Ronda de O2 e aeradores';

      ativos.forEach(f => {
        const item = ESCALAS_MAP[`${f.id}_${hojeStr}`];
        if (item && item.turno === 'NOTURNO_VIGIA') {
          vigiaHojeNome = `${f.nome} (${f.apelido || 'Vigia'})`;
          vigiaHojeStatus = item.status === 'CONFIRMADO' ? '🟢 Presente' : '21h às 06h';
          if (item.obs) vigiaObs = item.obs;
        }
      });

      const elVigiaNome = document.getElementById('kpi-vigia-nome');
      const elBadgeVigia = document.getElementById('badge-vigia-status');
      const elVigiaObs = document.getElementById('kpi-vigia-obs');

      if (elVigiaNome) elVigiaNome.textContent = vigiaHojeNome;
      if (elBadgeVigia) elBadgeVigia.textContent = vigiaHojeStatus;
      if (elVigiaObs) elVigiaObs.textContent = vigiaObs;

      // 3. Custo Total Folha Mês
      let totalFixo = ativos.reduce((acc, f) => acc + (f.salarioBase || 0), 0);
      let totalExtras = 0;
      let totalOcorrencias = 0;

      Object.keys(ESCALAS_MAP).forEach(k => {
        const item = ESCALAS_MAP[k];
        if (item.ehExtra && item.valorDiaria) totalExtras += item.valorDiaria;
        if (item.categoria && item.categoria !== 'NORMAL') totalOcorrencias++;
      });

      const custoTotal = totalFixo + totalExtras;
      const custoPorHa = (custoTotal / 12.83).toFixed(0);

      const elCustoTot = document.getElementById('kpi-custo-folha-total');
      const elCustoSub = document.getElementById('kpi-custo-folha-sub');
      if (elCustoTot) elCustoTot.textContent = `R$ ${custoTotal.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`;
      if (elCustoSub) elCustoSub.textContent = `Fixos: R$ ${totalFixo.toLocaleString('pt-BR')} • Extras: R$ ${totalExtras.toLocaleString('pt-BR')} (R$ ${custoPorHa}/ha)`;

      // 4. Folgas Hoje
      let folgasHoje = 0;
      let nomesFolga = [];
      ativos.forEach(f => {
        const item = ESCALAS_MAP[`${f.id}_${hojeStr}`];
        if (item && item.turno === 'FOLGA') {
          folgasHoje++;
          nomesFolga.push(f.apelido || f.nome.split(' ')[0]);
        }
      });

      const elFolgasHoje = document.getElementById('kpi-folgas-hoje');
      const elFolgasSub = document.getElementById('kpi-folgas-sub');
      if (elFolgasHoje) elFolgasHoje.textContent = `${folgasHoje} de Folga Hoje`;
      if (elFolgasSub) elFolgasSub.textContent = `${nomesFolga.join(', ') || 'Ninguém de folga'} • ${totalOcorrencias} Ocorrência(s) no Mês`;
    }

    // ========================================================
    // MODAL DE APONTAMENTO DIÁRIO E JORNADA DE TRABALHO
    // ========================================================
    function abrirModalApontamentoDia(funcionarioId, dataStr) {
      const f = FUNCIONARIOS_DATA.find(x => x.id === funcionarioId);
      if (!f) return;

      pontoSelecionado = { funcionarioId, dataStr };
      const key = `${funcionarioId}_${dataStr}`;
      const item = ESCALAS_MAP[key] || {
        turno: 'DIURNO', ehExtra: false, valorDiaria: f.valorDiariaExtra || 0,
        horaIni: f.jornadaIni || '06:30', horaFim: f.jornadaFim || '17:00',
        categoria: 'NORMAL', obs: ''
      };

      const [ano, mes, dia] = dataStr.split('-');
      document.getElementById('modal-apont-titulo').textContent = `Apontamento — ${f.nome}`;
      document.getElementById('modal-apont-subtitulo').textContent = `${f.apelido ? f.apelido + ' • ' : ''}${f.cargo} • Data: ${dia}/${mes}/${ano}`;

      document.getElementById('modal-apont-turno').value = item.turno || 'DIURNO';
      document.getElementById('modal-apont-hora-ini').value = item.horaIni || f.jornadaIni || '06:30';
      document.getElementById('modal-apont-hora-fim').value = item.horaFim || f.jornadaFim || '17:00';
      document.getElementById('modal-apont-eh-extra').checked = !!item.ehExtra;
      document.getElementById('modal-apont-valor-diaria').value = item.valorDiaria || f.valorDiariaExtra || 80.0;
      document.getElementById('modal-apont-categoria').value = item.categoria || 'NORMAL';
      document.getElementById('modal-apont-obs').value = item.obs || '';

      toggleInputValorExtra();
      sugerirHorariosPorTurno();
      document.getElementById('modal-apontamento-dia').classList.remove('hidden');
    }

    function fecharModalApontamentoDia() {
      const m = document.getElementById('modal-apontamento-dia');
      if (m) m.classList.add('hidden');
      pontoSelecionado = null;
    }

    function sugerirHorariosPorTurno() {
      const turno = document.getElementById('modal-apont-turno').value;
      const boxHorarios = document.getElementById('container-horarios-apontamento');
      const inputIni = document.getElementById('modal-apont-hora-ini');
      const inputFim = document.getElementById('modal-apont-hora-fim');

      if (turno === 'FOLGA' || turno === 'FERIAS') {
        if (boxHorarios) boxHorarios.classList.add('hidden');
      } else {
        if (boxHorarios) boxHorarios.classList.remove('hidden');
        if (turno === 'NOTURNO_VIGIA' && inputIni && inputFim) {
          inputIni.value = '21:00';
          inputFim.value = '06:00';
        } else if (turno === 'DIURNO' && inputIni && inputFim && inputIni.value === '21:00') {
          inputIni.value = '06:30';
          inputFim.value = '17:00';
        }
      }
    }

    function definirHorarioJornadaRapida(ini, fim, turno) {
      document.getElementById('modal-apont-hora-ini').value = ini;
      document.getElementById('modal-apont-hora-fim').value = fim;
      document.getElementById('modal-apont-turno').value = turno;
      sugerirHorariosPorTurno();
    }

    function toggleInputValorExtra() {
      const chk = document.getElementById('modal-apont-eh-extra');
      const box = document.getElementById('modal-apont-container-valor-extra');
      if (box) {
        if (chk && chk.checked) {
          box.classList.remove('hidden');
        } else {
          box.classList.add('hidden');
        }
      }
    }

    async function salvarApontamentoDia() {
      if (!pontoSelecionado) return;

      const { funcionarioId, dataStr } = pontoSelecionado;
      const f = FUNCIONARIOS_DATA.find(x => x.id === funcionarioId);
      const turno = document.getElementById('modal-apont-turno').value;
      const horaIni = (turno === 'FOLGA' || turno === 'FERIAS') ? null : document.getElementById('modal-apont-hora-ini').value;
      const horaFim = (turno === 'FOLGA' || turno === 'FERIAS') ? null : document.getElementById('modal-apont-hora-fim').value;
      const ehExtra = document.getElementById('modal-apont-eh-extra').checked;
      const valorDiaria = ehExtra ? (parseFloat(document.getElementById('modal-apont-valor-diaria').value) || (f ? f.valorDiariaExtra : 80.0)) : 0.0;
      const categoria = document.getElementById('modal-apont-categoria').value;
      const obs = document.getElementById('modal-apont-obs').value.trim();

      // Sincronizar com o backend FastAPI se disponível
      if (backendOnline) {
        try {
          await fetch(`${API_BASE_URL}/equipe/escalas/apontamento`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-Fazenda-Id': 'FAZ_ARRENDADA'
            },
            body: JSON.stringify({
              funcionario_id: funcionarioId,
              data: dataStr,
              turno: turno,
              eh_extra: ehExtra,
              valor_diaria_aplicado: valorDiaria,
              categoria_ocorrencia: categoria,
              observacoes: obs
            })
          });
        } catch (e) {
          console.warn('Backend indisponível, aplicando localmente:', e);
        }
      }

      // Atualizar estado local
      const key = `${funcionarioId}_${dataStr}`;
      ESCALAS_MAP[key] = {
        funcionarioId,
        data: dataStr,
        turno,
        horaIni,
        horaFim,
        ehExtra,
        valorDiaria,
        categoria,
        obs,
        status: 'CONFIRMADO'
      };

      fecharModalApontamentoDia();
      renderizarModuloEquipe();
    }

    // ========================================================
    // MODAL DE CADASTRO / EDIÇÃO DE FUNCIONÁRIO
    // ========================================================
    function abrirModalNovoColaborador() {
      funcionarioEmEdicao = null;
      document.getElementById('modal-func-titulo').textContent = 'Cadastrar Colaborador';
      document.getElementById('input-func-id').value = '';
      document.getElementById('input-func-nome').value = '';
      document.getElementById('input-func-apelido').value = '';
      document.getElementById('input-func-cargo').value = 'Arraçoador Principal';
      document.getElementById('input-func-contrato').value = 'MENSALISTA';
      document.getElementById('input-func-whatsapp').value = '';
      document.getElementById('input-func-pix').value = '';
      document.getElementById('input-func-salario').value = '1650';
      document.getElementById('input-func-diaria').value = '75';
      const jIni = document.getElementById('input-func-jornada-ini');
      const jFim = document.getElementById('input-func-jornada-fim');
      if (jIni) jIni.value = '06:30';
      if (jFim) jFim.value = '17:00';
      document.getElementById('input-func-obs').value = '';
      document.getElementById('modal-cadastro-funcionario').classList.remove('hidden');
    }

    function abrirModalEditarColaborador(id) {
      const f = FUNCIONARIOS_DATA.find(x => x.id === id);
      if (!f) return;
      funcionarioEmEdicao = f;

      document.getElementById('modal-func-titulo').textContent = `Editar — ${f.nome}`;
      document.getElementById('input-func-id').value = f.id;
      document.getElementById('input-func-nome').value = f.nome;
      document.getElementById('input-func-apelido').value = f.apelido || '';
      document.getElementById('input-func-cargo').value = f.cargo;
      document.getElementById('input-func-contrato').value = f.tipoContrato;
      document.getElementById('input-func-whatsapp').value = f.whatsapp || '';
      document.getElementById('input-func-pix').value = f.chavePix || '';
      document.getElementById('input-func-salario').value = f.salarioBase;
      document.getElementById('input-func-diaria').value = f.valorDiariaExtra;
      const jIni = document.getElementById('input-func-jornada-ini');
      const jFim = document.getElementById('input-func-jornada-fim');
      if (jIni) jIni.value = f.jornadaIni || '06:30';
      if (jFim) jFim.value = f.jornadaFim || '17:00';
      document.getElementById('input-func-obs').value = f.observacoes || '';

      document.getElementById('modal-cadastro-funcionario').classList.remove('hidden');
    }

    function fecharModalCadastroFuncionario() {
      const m = document.getElementById('modal-cadastro-funcionario');
      if (m) m.classList.add('hidden');
    }

    async function salvarCadastroFuncionario() {
      const nome = document.getElementById('input-func-nome').value.trim();
      const apelido = document.getElementById('input-func-apelido').value.trim();
      const cargo = document.getElementById('input-func-cargo').value;
      const tipoContrato = document.getElementById('input-func-contrato').value;
      const whatsapp = document.getElementById('input-func-whatsapp').value.trim();
      const chavePix = document.getElementById('input-func-pix').value.trim();
      const salarioBase = parseFloat(document.getElementById('input-func-salario').value) || 0.0;
      const valorDiariaExtra = parseFloat(document.getElementById('input-func-diaria').value) || 0.0;
      const jIni = document.getElementById('input-func-jornada-ini') ? document.getElementById('input-func-jornada-ini').value : '06:30';
      const jFim = document.getElementById('input-func-jornada-fim') ? document.getElementById('input-func-jornada-fim').value : '17:00';
      const obs = document.getElementById('input-func-obs').value.trim();

      if (!nome) {
        alert('Por favor, informe o nome completo do colaborador.');
        return;
      }

      if (funcionarioEmEdicao) {
        funcionarioEmEdicao.nome = nome;
        funcionarioEmEdicao.apelido = apelido;
        funcionarioEmEdicao.cargo = cargo;
        funcionarioEmEdicao.tipoContrato = tipoContrato;
        funcionarioEmEdicao.whatsapp = whatsapp;
        funcionarioEmEdicao.chavePix = chavePix;
        funcionarioEmEdicao.salarioBase = salarioBase;
        funcionarioEmEdicao.valorDiariaExtra = valorDiariaExtra;
        funcionarioEmEdicao.jornadaIni = jIni;
        funcionarioEmEdicao.jornadaFim = jFim;
        funcionarioEmEdicao.jornadaDesc = `${jIni} às ${jFim}`;
        funcionarioEmEdicao.observacoes = obs;
      } else {
        const novoId = Math.max(...FUNCIONARIOS_DATA.map(x => x.id), 0) + 1;
        FUNCIONARIOS_DATA.push({
          id: novoId,
          nome,
          apelido,
          cargo,
          tipoContrato,
          whatsapp,
          chavePix,
          salarioBase,
          valorDiariaExtra,
          jornadaIni: jIni,
          jornadaFim: jFim,
          jornadaDesc: `${jIni} às ${jFim}`,
          ativo: true,
          observacoes: obs
        });

        // Preencher escala padrão
        const hoje = new Date();
        const diasNoMes = new Date(hoje.getFullYear(), hoje.getMonth() + 1, 0).getDate();
        for (let d = 1; d <= diasNoMes; d++) {
          const dt = new Date(hoje.getFullYear(), hoje.getMonth(), d);
          const dtStr = dt.toISOString().split('T')[0];
          ESCALAS_MAP[`${novoId}_${dtStr}`] = {
            funcionarioId: novoId,
            data: dtStr,
            turno: dt.getDay() === 0 ? 'FOLGA' : 'DIURNO',
            horaIni: dt.getDay() === 0 ? null : jIni,
            horaFim: dt.getDay() === 0 ? null : jFim,
            ehExtra: false,
            valorDiaria: 0,
            obs: ''
          };
        }
      }

      fecharModalCadastroFuncionario();
      renderizarModuloEquipe();
      alert(`✅ Colaborador ${nome} salvo com sucesso!`);
    }

    // ========================================================
    // MODAL DE APLICAÇÃO DE TEMPLATES 12x36 E 6x1
    // ========================================================
    function abrirModalTemplateEscala() {
      const hoje = new Date();
      const ini = new Date(hoje.getFullYear(), hoje.getMonth(), 1).toISOString().split('T')[0];
      const fim = new Date(hoje.getFullYear(), hoje.getMonth() + 1, 0).toISOString().split('T')[0];

      document.getElementById('input-template-ini').value = ini;
      document.getElementById('input-template-fim').value = fim;
      atualizarOpcoesTemplateEscala();
      document.getElementById('modal-aplicar-template-escala').classList.remove('hidden');
    }

    function fecharModalTemplateEscala() {
      const m = document.getElementById('modal-aplicar-template-escala');
      if (m) m.classList.add('hidden');
    }

    function atualizarOpcoesTemplateEscala() {
      const tipo = document.getElementById('select-template-tipo').value;
      const desc = document.getElementById('desc-template-escala');
      const boxFolga = document.getElementById('container-opcao-folga-6x1');

      if (tipo === '12x36_VIGIAS') {
        if (desc) desc.textContent = 'Alterna os vigias noturnos dia sim / dia não automaticamente para cobrir 100% das noites do mês (21h às 06h).';
        if (boxFolga) boxFolga.classList.add('hidden');
      } else {
        if (desc) desc.textContent = 'Aplica escala diurna 6x1 com 1 folga semanal fixa para a equipe de arraçoamento e campo.';
        if (boxFolga) boxFolga.classList.remove('hidden');
      }
    }

    async function aplicarTemplateEscala() {
      const tipo = document.getElementById('select-template-tipo').value;
      const dtIni = document.getElementById('input-template-ini').value;
      const dtFim = document.getElementById('input-template-fim').value;
      const diaFolga = parseInt(document.getElementById('select-dia-folga-6x1').value || '6');

      if (!dtIni || !dtFim) {
        alert('Por favor, selecione as datas de início e fim.');
        return;
      }

      const d1 = new Date(dtIni + 'T00:00:00');
      const d2 = new Date(dtFim + 'T00:00:00');
      const deltaDias = Math.round((d2 - d1) / (1000 * 60 * 60 * 24)) + 1;

      if (tipo === '12x36_VIGIAS') {
        const vigias = FUNCIONARIOS_DATA.filter(f => f.cargo.includes('Vigia'));
        if (vigias.length < 2) {
          alert('Necessário ter ao menos 2 vigias cadastrados para a escala 12x36.');
          return;
        }

        for (let i = 0; i < deltaDias; i++) {
          const cur = new Date(d1);
          cur.setDate(d1.getDate() + i);
          const curStr = cur.toISOString().split('T')[0];
          const vigiaAtivoIdx = i % vigias.length;

          vigias.forEach((v, idx) => {
            const isVigia = (idx === vigiaAtivoIdx);
            ESCALAS_MAP[`${v.id}_${curStr}`] = {
              funcionarioId: v.id,
              data: curStr,
              turno: isVigia ? 'NOTURNO_VIGIA' : 'FOLGA',
              horaIni: isVigia ? '21:00' : null,
              horaFim: isVigia ? '06:00' : null,
              ehExtra: isVigia && v.tipoContrato === 'DIARISTA',
              valorDiaria: (isVigia && v.tipoContrato === 'DIARISTA') ? v.valorDiariaExtra : 0,
              obs: isVigia ? 'Plantão Noturno 21h às 06h' : 'Folga 12x36'
            };
          });
        }
      } else {
        const tratadores = FUNCIONARIOS_DATA.filter(f => !f.cargo.includes('Vigia'));
        for (let i = 0; i < deltaDias; i++) {
          const cur = new Date(d1);
          cur.setDate(d1.getDate() + i);
          const curStr = cur.toISOString().split('T')[0];
          const isFolga = (cur.getDay() === diaFolga);

          tratadores.forEach(t => {
            ESCALAS_MAP[`${t.id}_${curStr}`] = {
              funcionarioId: t.id,
              data: curStr,
              turno: isFolga ? 'FOLGA' : 'DIURNO',
              horaIni: isFolga ? null : (t.jornadaIni || '06:30'),
              horaFim: isFolga ? null : (t.jornadaFim || '17:00'),
              ehExtra: false,
              valorDiaria: 0,
              obs: isFolga ? 'Folga semanal 6x1' : 'Trato diurno'
            };
          });
        }
      }

      fecharModalTemplateEscala();
      renderizarModuloEquipe();
      alert(`✅ Escala ${tipo === '12x36_VIGIAS' ? '12x36' : '6x1'} gerada com sucesso!`);
    }

    // ========================================================
    // CHECK-IN DO VIGIA NOTURNO
    // ========================================================
    function abrirModalCheckinVigia() {
      const hojeStr = new Date().toISOString().split('T')[0];
      const ativos = FUNCIONARIOS_DATA.filter(f => f.ativo);
      let vigia = null;

      ativos.forEach(f => {
        const item = ESCALAS_MAP[`${f.id}_${hojeStr}`];
        if (item && item.turno === 'NOTURNO_VIGIA') vigia = f;
      });

      if (!vigia) vigia = ativos.find(f => f.cargo.includes('Vigia')) || ativos[0];

      document.getElementById('modal-checkin-nome').textContent = `${vigia.nome} (${vigia.apelido || vigia.cargo})`;
      document.getElementById('modal-checkin-hora-ini').value = '20:55';
      document.getElementById('modal-checkin-obs').value = 'Motores e oxigênio conferidos e estáveis.';
      document.getElementById('modal-checkin-vigia').classList.remove('hidden');
    }

    function fecharModalCheckinVigia() {
      const m = document.getElementById('modal-checkin-vigia');
      if (m) m.classList.add('hidden');
    }

    function salvarCheckinVigia() {
      const hojeStr = new Date().toISOString().split('T')[0];
      const horaIni = document.getElementById('modal-checkin-hora-ini').value;
      const obs = document.getElementById('modal-checkin-obs').value.trim();

      const ativos = FUNCIONARIOS_DATA.filter(f => f.ativo);
      ativos.forEach(f => {
        const item = ESCALAS_MAP[`${f.id}_${hojeStr}`];
        if (item && item.turno === 'NOTURNO_VIGIA') {
          item.status = 'CONFIRMADO';
          item.obs = `Check-in às ${horaIni}. ${obs}`;
        }
      });

      fecharModalCheckinVigia();
      renderizarModuloEquipe();
      alert(`✅ Presença do vigia noturno confirmada às ${horaIni}!`);
    }

    function enviarEscalaWhatsApp() {
      const hoje = new Date();
      const hojeStr = hoje.toISOString().split('T')[0];
      const [ano, mes, dia] = hojeStr.split('-');

      let texto = `*📋 ESCALA DE TRABALHO DA FAZENDA — ${dia}/${mes}/${ano}*\\n\\n`;
      texto += `*🌙 VIGIA NOTURNO HOJE (21h às 06h):*\\n`;

      FUNCIONARIOS_DATA.filter(f => f.ativo).forEach(f => {
        const item = ESCALAS_MAP[`${f.id}_${hojeStr}`];
        if (item && item.turno === 'NOTURNO_VIGIA') {
          texto += `• *${f.nome}* (${f.apelido || 'Vigia'}) - ${item.horaIni || '21:00'} às ${item.horaFim || '06:00'}\\n`;
        }
      });

      texto += `\\n*☀️ EQUIPE NO TURNO DIURNO:*\\n`;
      FUNCIONARIOS_DATA.filter(f => f.ativo).forEach(f => {
        const item = ESCALAS_MAP[`${f.id}_${hojeStr}`];
        if (item && item.turno === 'DIURNO') {
          texto += `• ${f.nome} (${f.cargo}) — ${item.horaIni || '06:30'} às ${item.horaFim || '17:00'}\\n`;
        }
      });

      texto += `\\n*🏖️ FOLGAS DO DIA:*\\n`;
      FUNCIONARIOS_DATA.filter(f => f.ativo).forEach(f => {
        const item = ESCALAS_MAP[`${f.id}_${hojeStr}`];
        if (item && item.turno === 'FOLGA') {
          texto += `• ${f.nome} (Folga regulamentar)\\n`;
        }
      });

      texto += `\\n_Fazenda Ceará-Mirim/RN • Sistema ERP Camarão_`;
      const url = `https://api.whatsapp.com/send?text=${encodeURIComponent(texto)}`;
      window.open(url, '_blank');
    }
"""

# Substituir bloco JavaScript antigo pelo novo com Google Agenda
padrao_js_equipe = r"// ========================================================\s*// LÓGICA DO MÓDULO DE EQUIPE, VIGIA NOTURNO, ESCALAS & CUSTOS[\s\S]*?function enviarEscalaWhatsApp\(\) \{[\s\S]*?window\.open\(url, '_blank'\);\s*\}"
if re.search(padrao_js_equipe, html_content):
    html_content = re.sub(padrao_js_equipe, lambda m: funcoes_equipe_agenda_js.strip(), html_content, count=1)
    print("Motor JavaScript atualizado com suporte completo ao Google Agenda e Jornadas de Trabalho!")
else:
    pos_close = html_content.rfind('</script>')
    html_content = html_content[:pos_close] + funcoes_equipe_agenda_js + "\n  " + html_content[pos_close:]
    print("Motor JavaScript injetado antes de </script>!")

HTML_PATH.write_text(html_content, encoding="utf-8")
print(f"dashboard_interativo_prototipo.html gravado com sucesso! Tamanho final: {len(html_content)} bytes.")
