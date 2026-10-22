"""Script para injetar o Módulo de Equipe, Vigia Noturno, Escalas, Ocorrências e Custos no HTML."""
import re
import sys
from pathlib import Path

BASE_DIR = Path(r"G:\Meu Drive\ANTIGRAVITY DRIVE\CAMARÃO\ERP CAMARÃO")
HTML_PATH = BASE_DIR / "dashboard_interativo_prototipo.html"
html_content = HTML_PATH.read_text(encoding="utf-8")

# 1. Nova Seção HTML do Módulo de Equipe & Vigia Noturno
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
              <i class="fa-solid fa-users-gear text-violet-600"></i> Gestão de Equipe, Vigia Noturno & Escalas de Campo
            </h2>
            <p class="text-xs text-slate-500">Fazenda Ceará-Mirim/RN • Controle de Turnos, Mapeamento de Folgas, Ocorrências e Custos de Mão de Obra</p>
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
        <!-- GRADE VISUAL INTERATIVA DE HORÁRIOS, FOLGAS E OCORRÊNCIAS-->
        <!-- ======================================================== -->
        <div class="bg-white rounded-3xl p-5 border border-slate-200 shadow-sm space-y-4">
          <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-3 border-b border-slate-100">
            <div>
              <h3 class="text-sm font-bold text-slate-900 flex items-center gap-2">
                <i class="fa-solid fa-calendar-days text-violet-600"></i> Mapa de Escalas, Horários & Mapeamento de Folgas
                <span class="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-violet-100 text-violet-800 border border-violet-200">Clique no dia para editar</span>
              </h3>
              <p class="text-xs text-slate-500">Preenchimento diário de turnos, faltas, apontamento de ocorrências e diárias extras cumpridas.</p>
            </div>

            <!-- Alternador de Visão (Semana vs Mês) -->
            <div class="flex items-center gap-1 bg-slate-100 p-1 rounded-xl text-xs border border-slate-200">
              <button id="btn-visao-semana" onclick="alternarVisualizacaoEscala('semana')" class="px-3 py-1.5 rounded-lg font-bold bg-white text-slate-900 shadow-sm transition">
                <i class="fa-solid fa-calendar-week mr-1 text-violet-600"></i> Semana Atual (7 Dias)
              </button>
              <button id="btn-visao-mes" onclick="alternarVisualizacaoEscala('mes')" class="px-3 py-1.5 rounded-lg font-semibold text-slate-600 hover:text-slate-900 transition">
                <i class="fa-solid fa-calendar mr-1"></i> Mês Completo
              </button>
            </div>
          </div>

          <!-- Legenda de Badges Operacionais -->
          <div class="flex flex-wrap items-center justify-between gap-3 bg-slate-50 p-2.5 rounded-xl border border-slate-200 text-xs text-slate-600">
            <div class="flex flex-wrap items-center gap-3">
              <span class="flex items-center gap-1 font-semibold">
                <span class="px-1.5 py-0.5 rounded text-[10px] font-extrabold bg-blue-100 text-blue-800 border border-blue-200">☀️ Diurno</span> Trabalho Normal
              </span>
              <span class="flex items-center gap-1 font-semibold">
                <span class="px-1.5 py-0.5 rounded text-[10px] font-extrabold bg-indigo-100 text-indigo-800 border border-indigo-200">🌙 Vigia Noturno</span> Ronda Oxigênio
              </span>
              <span class="flex items-center gap-1 font-semibold">
                <span class="px-1.5 py-0.5 rounded text-[10px] font-extrabold bg-slate-200 text-slate-700 border border-slate-300">🏖️ Folga</span> Descanso
              </span>
              <span class="flex items-center gap-1 font-semibold">
                <span class="px-1.5 py-0.5 rounded text-[10px] font-extrabold bg-amber-100 text-amber-800 border border-amber-200">🏥 Atestado</span> Falta Justificada
              </span>
              <span class="flex items-center gap-1 font-semibold">
                <span class="px-1.5 py-0.5 rounded text-[10px] font-extrabold bg-red-100 text-red-800 border border-red-200">❌ Falta</span> Injustificada
              </span>
              <span class="flex items-center gap-1 font-semibold">
                <span class="px-1.5 py-0.5 rounded text-[10px] font-extrabold bg-yellow-100 text-amber-900 border border-yellow-300">⭐ Extra (+R$)</span> Diária Paga
              </span>
              <span class="flex items-center gap-1 font-semibold text-slate-500">
                <span class="text-xs">💬</span> Ocorrência / Nota
              </span>
            </div>
            <span class="text-[11px] text-slate-400 italic">Dica: clique em qualquer célula para alterar turno, lançar diária ou ocorrência.</span>
          </div>

          <!-- Matriz da Grade de Horários -->
          <div class="overflow-x-auto rounded-2xl border border-slate-200 shadow-inner">
            <table class="w-full text-left text-xs border-collapse bg-white">
              <thead id="thead-grade-escala" class="bg-slate-100 text-slate-700 font-bold border-b border-slate-200">
                <!-- Cabeçalho de dias gerado dinamicamente via JS -->
              </thead>
              <tbody id="tbody-grade-escala" class="divide-y divide-slate-100">
                <!-- Linhas dos colaboradores geradas dinamicamente via JS -->
              </tbody>
            </table>
          </div>
        </div>

        <!-- ======================================================== -->
        <!-- TABELA DE CADASTRO, REMUNERAÇÃO E DEMONSTRATIVO MENSAL   -->
        <!-- ======================================================== -->
        <div class="bg-white rounded-3xl p-5 border border-slate-200 shadow-sm space-y-4">
          <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-3 border-b border-slate-100">
            <div>
              <h3 class="text-sm font-bold text-slate-900 flex items-center gap-2">
                <i class="fa-solid fa-address-card text-aco"></i> Cadastro de Colaboradores & Apuração Mensal de Salários
              </h3>
              <p class="text-xs text-slate-500">Gestão cadastral, WhatsApp, Chave PIX e fechamento de remuneração fixa vs diárias extras.</p>
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
                  <td class="py-3 px-3" colspan="5">TOTAL DA FOLHA NO MÊS</td>
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

      </section>"""

# Substituir a seção view-analytics-equipe antiga
padrao_secao = r'<section id="view-analytics-equipe"[\s\S]*?</section>'
if re.search(padrao_secao, html_content):
    html_content = re.sub(padrao_secao, nova_secao_equipe_html.strip(), html_content, count=1)
    print("Seção view-analytics-equipe substituída com sucesso!")
else:
    print("ERRO: Seção view-analytics-equipe não encontrada!")

# 2. Injetar os Novos Modais de Equipe antes do fechamento </body>
novos_modais_equipe_html = """
  <!-- ======================================================== -->
  <!-- MODAL: APONTAMENTO DIÁRIO, OCORRÊNCIAS & DIÁRIAS EXTRAS -->
  <!-- ======================================================== -->
  <div id="modal-apontamento-dia" class="hidden fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
    <div class="bg-white rounded-3xl max-w-lg w-full p-6 shadow-2xl border border-slate-200 transition-all">
      <div class="flex items-center justify-between pb-4 border-b border-slate-100">
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 rounded-2xl bg-violet-50 text-violet-600 flex items-center justify-center font-bold text-lg border border-violet-200">
            <i class="fa-solid fa-calendar-check"></i>
          </div>
          <div>
            <h3 id="modal-apont-titulo" class="text-base font-bold text-slate-900">Apontamento Diário</h3>
            <p id="modal-apont-subtitulo" class="text-xs text-slate-500">Carlos Silva • 22/10/2026</p>
          </div>
        </div>
        <button onclick="fecharModalApontamentoDia()" class="p-2 text-slate-400 hover:text-slate-600 rounded-xl hover:bg-slate-100">
          <i class="fa-solid fa-xmark"></i>
        </button>
      </div>

      <div class="py-4 space-y-4">
        <!-- Turno / Situação -->
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1.5">Turno / Situação do Dia:</label>
          <select id="modal-apont-turno" class="w-full text-xs font-semibold p-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-violet-500 bg-white">
            <option value="DIURNO">☀️ Diurno (Trabalho Normal 06h30 - 17h00)</option>
            <option value="NOTURNO_VIGIA">🌙 Vigia Noturno (Ronda Oxigênio 21h00 - 06h00)</option>
            <option value="FOLGA">🏖️ Folga Semanal / Descanso</option>
            <option value="FALTA_JUSTIFICADA">🏥 Falta Justificada (Atestado Médico / Licença)</option>
            <option value="FALTA_INJUSTIFICADA">❌ Falta Injustificada (Desconto em Folha)</option>
            <option value="FERIAS">🌴 Férias</option>
          </select>
        </div>

        <!-- Seção de Diária / Plantão Extra Cumprido -->
        <div class="p-3.5 rounded-2xl bg-amber-50/70 border border-amber-200 space-y-2.5">
          <div class="flex items-center justify-between">
            <label class="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" id="modal-apont-eh-extra" onchange="toggleInputValorExtra()" class="w-4 h-4 rounded text-amber-600 focus:ring-amber-500 border-slate-300">
              <span class="text-xs font-bold text-amber-950 flex items-center gap-1">
                <i class="fa-solid fa-star text-amber-500"></i> Diária ou Plantão Extra Cumprido
              </span>
            </label>
            <span class="text-[10px] text-amber-700 font-semibold bg-white px-2 py-0.5 rounded-lg border border-amber-200">Soma ao Custo do Mês</span>
          </div>

          <div id="modal-apont-container-valor-extra" class="hidden grid grid-cols-2 gap-2 pt-1">
            <div>
              <label class="block text-[10px] font-bold text-amber-900 mb-0.5">Valor da Diária (R$):</label>
              <input type="number" step="5" id="modal-apont-valor-diaria" class="w-full text-xs font-mono font-bold p-2 rounded-xl border border-amber-300 bg-white" placeholder="80.00">
            </div>
            <div>
              <label class="block text-[10px] font-bold text-amber-900 mb-0.5">Status do Pagamento:</label>
              <select id="modal-apont-status-pagamento" class="w-full text-xs p-2 rounded-xl border border-amber-300 bg-white">
                <option value="A_PAGAR">Pagar no Fechamento</option>
                <option value="PAGO_PIX">Pago via PIX Hoje</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Categoria da Ocorrência -->
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1.5">Categoria da Ocorrência:</label>
          <select id="modal-apont-categoria" class="w-full text-xs p-2.5 rounded-xl border border-slate-300 bg-white">
            <option value="NORMAL">Normal / Sem Ocorrência</option>
            <option value="COBERTURA_TURNO">Cobertura de Turno (Substituiu colega)</option>
            <option value="ATRASO">Atraso de Horário</option>
            <option value="ATESTADO">Atestado Médico Entregue</option>
            <option value="MANUTENCAO_EMERGENCIAL">Manutenção Emergencial de Motores/Aeradores</option>
            <option value="ELOGIO">Elogio / Desempenho Excepcional</option>
            <option value="OUTRO">Outra Ocorrência</option>
          </select>
        </div>

        <!-- Observações / Detalhamento da Ocorrência -->
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1.5">Observações / Detalhamento da Ocorrência:</label>
          <textarea id="modal-apont-obs" rows="3" class="w-full text-xs p-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-violet-500" placeholder="Ex: Cobriu plantão do Carlos que precisou se ausentar para consulta médica."></textarea>
        </div>
      </div>

      <div class="flex items-center justify-end gap-2 pt-3 border-t border-slate-100">
        <button onclick="fecharModalApontamentoDia()" class="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs transition">
          Cancelar
        </button>
        <button onclick="salvarApontamentoDia()" class="px-4 py-2 rounded-xl bg-violet-600 hover:bg-violet-700 text-white font-bold text-xs transition flex items-center gap-1.5 shadow">
          <i class="fa-solid fa-check"></i> Salvar Apontamento
        </button>
      </div>
    </div>
  </div>

  <!-- ======================================================== -->
  <!-- MODAL: CADASTRO / EDIÇÃO DE COLABORADOR                   -->
  <!-- ======================================================== -->
  <div id="modal-cadastro-funcionario" class="hidden fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
    <div class="bg-white rounded-3xl max-w-lg w-full p-6 shadow-2xl border border-slate-200 transition-all max-h-[90vh] overflow-y-auto">
      <div class="flex items-center justify-between pb-4 border-b border-slate-100">
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 rounded-2xl bg-violet-50 text-violet-600 flex items-center justify-center font-bold text-lg border border-violet-200">
            <i class="fa-solid fa-id-badge"></i>
          </div>
          <div>
            <h3 id="modal-func-titulo" class="text-base font-bold text-slate-900">Cadastrar Colaborador</h3>
            <p class="text-xs text-slate-500">Dados cadastrais, contato WhatsApp e remuneração.</p>
          </div>
        </div>
        <button onclick="fecharModalCadastroFuncionario()" class="p-2 text-slate-400 hover:text-slate-600 rounded-xl hover:bg-slate-100">
          <i class="fa-solid fa-xmark"></i>
        </button>
      </div>

      <div class="py-4 space-y-3.5">
        <input type="hidden" id="input-func-id" value="">

        <div class="grid grid-cols-2 gap-3">
          <div class="col-span-2 sm:col-span-1">
            <label class="block text-xs font-bold text-slate-700 mb-1">Nome Completo: *</label>
            <input type="text" id="input-func-nome" class="w-full text-xs p-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-violet-500" placeholder="Ex: Carlos da Silva">
          </div>
          <div class="col-span-2 sm:col-span-1">
            <label class="block text-xs font-bold text-slate-700 mb-1">Apelido de Campo:</label>
            <input type="text" id="input-func-apelido" class="w-full text-xs p-2.5 rounded-xl border border-slate-300" placeholder="Ex: Carlinhos">
          </div>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-xs font-bold text-slate-700 mb-1">Cargo / Função: *</label>
            <select id="input-func-cargo" class="w-full text-xs p-2.5 rounded-xl border border-slate-300 bg-white">
              <option value="Vigia Noturno">Vigia Noturno (Oxigênio)</option>
              <option value="Vigia Noturno Folguista">Vigia Noturno Folguista</option>
              <option value="Arraçoador Principal">Arraçoador Principal</option>
              <option value="Operador de Máquinas e Bombas">Operador de Máquinas e Bombas</option>
              <option value="Apoio de Campo e Arraçoamento">Apoio de Campo e Arraçoamento</option>
              <option value="Encarregado Geral">Encarregado Geral</option>
              <option value="Serviços Gerais">Serviços Gerais</option>
            </select>
          </div>
          <div>
            <label class="block text-xs font-bold text-slate-700 mb-1">Tipo de Contrato: *</label>
            <select id="input-func-contrato" class="w-full text-xs p-2.5 rounded-xl border border-slate-300 bg-white">
              <option value="MENSALISTA">Mensalista (Salário Fixo)</option>
              <option value="DIARISTA">Diarista (Por Turno/Diária)</option>
            </select>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-xs font-bold text-slate-700 mb-1">WhatsApp de Contato: *</label>
            <input type="text" id="input-func-whatsapp" class="w-full text-xs p-2.5 rounded-xl border border-slate-300 font-mono" placeholder="(84) 99876-1100">
          </div>
          <div>
            <label class="block text-xs font-bold text-slate-700 mb-1">Chave PIX:</label>
            <input type="text" id="input-func-pix" class="w-full text-xs p-2.5 rounded-xl border border-slate-300 font-mono" placeholder="CPF, Celular ou E-mail">
          </div>
        </div>

        <!-- Seção Salário e Diária -->
        <div class="p-3.5 rounded-2xl bg-slate-50 border border-slate-200 grid grid-cols-2 gap-3">
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

        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Fazenda Alocada:</label>
          <select id="input-func-fazenda" class="w-full text-xs p-2.5 rounded-xl border border-slate-300 bg-white">
            <option value="FAZ_ARRENDADA">Fazenda Arrendada (Ceará-Mirim/RN)</option>
            <option value="FAZ_HAKKA">Fazenda Hakka (Propriedade Familiar)</option>
            <option value="AMBAS">Ambas as Fazendas (Volante)</option>
          </select>
        </div>

        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Observações:</label>
          <textarea id="input-func-obs" rows="2" class="w-full text-xs p-2 rounded-xl border border-slate-300" placeholder="Horários preferenciais, histórico ou restrições."></textarea>
        </div>
      </div>

      <div class="flex items-center justify-end gap-2 pt-3 border-t border-slate-100">
        <button onclick="fecharModalCadastroFuncionario()" class="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs transition">
          Cancelar
        </button>
        <button onclick="salvarCadastroFuncionario()" class="px-4 py-2 rounded-xl bg-violet-600 hover:bg-violet-700 text-white font-bold text-xs transition flex items-center gap-1.5 shadow">
          <i class="fa-solid fa-save"></i> Salvar Colaborador
        </button>
      </div>
    </div>
  </div>

  <!-- ======================================================== -->
  <!-- MODAL: GERADOR RÁPIDO DE ESCALAS 12x36 E 6x1             -->
  <!-- ======================================================== -->
  <div id="modal-aplicar-template-escala" class="hidden fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
    <div class="bg-white rounded-3xl max-w-md w-full p-6 shadow-2xl border border-slate-200 transition-all">
      <div class="flex items-center justify-between pb-4 border-b border-slate-100">
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 rounded-2xl bg-amber-50 text-amber-600 flex items-center justify-center font-bold text-lg border border-amber-200">
            <i class="fa-solid fa-wand-magic-sparkles"></i>
          </div>
          <div>
            <h3 class="text-base font-bold text-slate-900">Aplicar Escala Automática</h3>
            <p class="text-xs text-slate-500">Padrões operacionais de fazenda de camarão.</p>
          </div>
        </div>
        <button onclick="fecharModalTemplateEscala()" class="p-2 text-slate-400 hover:text-slate-600 rounded-xl hover:bg-slate-100">
          <i class="fa-solid fa-xmark"></i>
        </button>
      </div>

      <div class="py-4 space-y-3.5">
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Modelo de Escala:</label>
          <select id="select-template-tipo" onchange="atualizarOpcoesTemplateEscala()" class="w-full text-xs font-bold p-2.5 rounded-xl border border-slate-300 bg-white">
            <option value="12x36_VIGIAS">Revezamento 12x36 para Vigias Noturnos (1 Noite Sim, 1 Não)</option>
            <option value="6x1_ARRACOADORES">Escala 6x1 Diurna para Arraçoadores (6 Dias Trato, 1 Folga)</option>
          </select>
        </div>

        <div class="p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-600 space-y-1">
          <span id="desc-template-escala" class="font-medium">Alterna os vigias noturnos dia sim / dia não automaticamente para cobrir 100% das noites do mês.</span>
        </div>

        <div id="container-opcao-folga-6x1" class="hidden">
          <label class="block text-xs font-bold text-slate-700 mb-1">Dia Fixo de Folga Semanal:</label>
          <select id="select-dia-folga-6x1" class="w-full text-xs p-2 rounded-xl border border-slate-300 bg-white">
            <option value="6">Domingo</option>
            <option value="5">Sábado</option>
            <option value="0">Segunda-feira</option>
          </select>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-xs font-bold text-slate-700 mb-1">Data Início:</label>
            <input type="date" id="input-template-ini" class="w-full text-xs p-2 rounded-xl border border-slate-300">
          </div>
          <div>
            <label class="block text-xs font-bold text-slate-700 mb-1">Data Fim:</label>
            <input type="date" id="input-template-fim" class="w-full text-xs p-2 rounded-xl border border-slate-300">
          </div>
        </div>
      </div>

      <div class="flex items-center justify-end gap-2 pt-3 border-t border-slate-100">
        <button onclick="fecharModalTemplateEscala()" class="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs transition">
          Cancelar
        </button>
        <button onclick="aplicarTemplateEscala()" class="px-4 py-2 rounded-xl bg-amber-600 hover:bg-amber-700 text-white font-bold text-xs transition flex items-center gap-1.5 shadow">
          <i class="fa-solid fa-check"></i> Gerar Escala
        </button>
      </div>
    </div>
  </div>

  <!-- ======================================================== -->
  <!-- MODAL: CHECK-IN DO VIGIA NOTURNO (RONDA DE OXIGÊNIO)     -->
  <!-- ======================================================== -->
  <div id="modal-checkin-vigia" class="hidden fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
    <div class="bg-white rounded-3xl max-w-sm w-full p-6 shadow-2xl border border-slate-200 transition-all">
      <div class="flex items-center justify-between pb-3 border-b border-slate-100">
        <div class="flex items-center space-x-2.5">
          <div class="w-9 h-9 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center font-bold text-base border border-indigo-200">
            <i class="fa-solid fa-moon"></i>
          </div>
          <div>
            <h3 class="text-sm font-bold text-slate-900">Check-in do Vigia Noturno</h3>
            <p class="text-[11px] text-slate-500">Ronda noturna da madrugada.</p>
          </div>
        </div>
        <button onclick="fecharModalCheckinVigia()" class="p-1.5 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-100">
          <i class="fa-solid fa-xmark"></i>
        </button>
      </div>

      <div class="py-4 space-y-3 text-xs">
        <div>
          <label class="block font-bold text-slate-700 mb-1">Vigia Noturno de Plantão:</label>
          <div id="modal-checkin-nome" class="font-bold text-indigo-900 p-2.5 bg-indigo-50 rounded-xl border border-indigo-200">Carlos Silva (Carlinhos)</div>
        </div>

        <div class="grid grid-cols-2 gap-2">
          <div>
            <label class="block font-bold text-slate-700 mb-1">Horário Entrada:</label>
            <input type="time" id="modal-checkin-hora-ini" value="21:00" class="w-full p-2 rounded-xl border border-slate-300 font-mono font-bold">
          </div>
          <div>
            <label class="block font-bold text-slate-700 mb-1">Previsão Saída:</label>
            <input type="time" id="modal-checkin-hora-fim" value="06:00" class="w-full p-2 rounded-xl border border-slate-300 font-mono font-bold">
          </div>
        </div>

        <div>
          <label class="block font-bold text-slate-700 mb-1">Observações da Ronda:</label>
          <input type="text" id="modal-checkin-obs" class="w-full p-2 rounded-xl border border-slate-300" placeholder="Ex: Motores dos viveiros 1 a 6 conferidos e oxigênio ok.">
        </div>
      </div>

      <div class="flex items-center justify-end gap-2 pt-3 border-t border-slate-100">
        <button onclick="fecharModalCheckinVigia()" class="px-3.5 py-1.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs transition">
          Cancelar
        </button>
        <button onclick="salvarCheckinVigia()" class="px-3.5 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs transition flex items-center gap-1 shadow">
          <i class="fa-solid fa-check"></i> Confirmar Presença
        </button>
      </div>
    </div>
  </div>
"""

if "id=\"modal-apontamento-dia\"" not in html_content:
    last_body = html_content.rfind('</body>')
    html_content = html_content[:last_body] + novos_modais_equipe_html + "\n" + html_content[last_body:]
    print("Modais de Equipe injetados antes de </body> com sucesso!")

# 3. Lógica JavaScript Completa do Módulo de Equipe
funcoes_equipe_js = """
    // ========================================================
    // LÓGICA DO MÓDULO DE EQUIPE, VIGIA NOTURNO, ESCALAS & CUSTOS
    // ========================================================
    let modoEscalaVisualizacao = 'semana'; // 'semana' ou 'mes'
    let pontoSelecionado = null; // { funcionarioId, dataStr }
    let funcionarioEmEdicao = null;

    // Dataset Inicial de Colaboradores da Fazenda Arrendada (Ceará-Mirim/RN)
    let FUNCIONARIOS_DATA = [
      {
        id: 1, nome: 'Carlos Silva', apelido: 'Carlinhos', cargo: 'Vigia Noturno',
        telefone: '(84) 99876-1101', whatsapp: '84998761101', chavePix: 'carlinhos.vigia@email.com',
        tipoContrato: 'MENSALISTA', salarioBase: 1800.0, valorDiariaExtra: 80.0, ativo: true,
        fazenda: 'Fazenda Arrendada', observacoes: 'Vigia titular noturno (ronda de O2 e aeradores). Escala 12x36.'
      },
      {
        id: 2, nome: 'Sebastião Oliveira', apelido: 'Tião', cargo: 'Vigia Noturno Folguista',
        telefone: '(84) 99876-1102', whatsapp: '84998761102', chavePix: '84998761102',
        tipoContrato: 'DIARISTA', salarioBase: 0.0, valorDiariaExtra: 90.0, ativo: true,
        fazenda: 'Fazenda Arrendada', observacoes: 'Vigia folguista e plantonista de apoio. Recebe por plantão noturno.'
      },
      {
        id: 3, nome: 'Francisco Santos', apelido: 'Chico', cargo: 'Arraçoador Principal',
        telefone: '(84) 99876-1103', whatsapp: '84998761103', chavePix: 'chico.camarao@pix.com',
        tipoContrato: 'MENSALISTA', salarioBase: 1650.0, valorDiariaExtra: 75.0, ativo: true,
        fazenda: 'Fazenda Arrendada', observacoes: 'Responsável pelo trato diurno e conferência de bandejas de sobra (0 a 3).'
      },
      {
        id: 4, nome: 'José Ferreira', apelido: 'Zé do Motor', cargo: 'Operador de Máquinas e Bombas',
        telefone: '(84) 99876-1104', whatsapp: '84998761104', chavePix: 'zedomotor@email.com',
        tipoContrato: 'MENSALISTA', salarioBase: 1750.0, valorDiariaExtra: 85.0, ativo: true,
        fazenda: 'Fazenda Arrendada', observacoes: 'Manutenção preventiva de motores, compressores e aeradores de pá.'
      },
      {
        id: 5, nome: 'Antônio Costa', apelido: 'Tonho', cargo: 'Apoio de Campo e Arraçoamento',
        telefone: '(84) 99876-1105', whatsapp: '84998761105', chavePix: 'tonho.costa@pix.com',
        tipoContrato: 'MENSALISTA', salarioBase: 1500.0, valorDiariaExtra: 70.0, ativo: true,
        fazenda: 'Fazenda Arrendada', observacoes: 'Serviços gerais de talude, limpeza de filtros e apoio no trato.'
      }
    ];

    // Dataset Inicial de Escalas e Ocorrências do Mês (Chave: `${funcId}_${YYYY-MM-DD}`)
    let ESCALAS_MAP = {};

    function inicializarEscalasPadrao() {
      const hoje = new Date();
      const ano = hoje.getFullYear();
      const mes = hoje.getMonth();
      const diasNoMes = new Date(ano, mes + 1, 0).getDate();

      // Gerar escala base do mês
      for (let dia = 1; dia <= diasNoMes; dia++) {
        const d = new Date(ano, mes, dia);
        const dataStr = d.toISOString().split('T')[0];
        const diaSemana = d.getDay(); // 0 Dom, 6 Sab

        // Carlinhos (1) dias ímpares vigia, dias pares folga
        const carlinhosVigia = (dia % 2 === 1);
        ESCALAS_MAP[`1_${dataStr}`] = {
          funcionarioId: 1, data: dataStr, turno: carlinhosVigia ? 'NOTURNO_VIGIA' : 'FOLGA',
          ehExtra: false, valorDiaria: 0, status: 'CONFIRMADO',
          categoria: 'NORMAL', obs: carlinhosVigia ? 'Ronda noturna 21h-06h' : ''
        };

        // Tião (2) dias pares vigia (diária R$ 90), dias ímpares folga
        const tiaoVigia = (dia % 2 === 0);
        ESCALAS_MAP[`2_${dataStr}`] = {
          funcionarioId: 2, data: dataStr, turno: tiaoVigia ? 'NOTURNO_VIGIA' : 'FOLGA',
          ehExtra: tiaoVigia, valorDiaria: tiaoVigia ? 90.0 : 0.0, status: 'CONFIRMADO',
          categoria: 'NORMAL', obs: tiaoVigia ? 'Plantão noturno diarista' : ''
        };

        // Chico (3) folga domingo (0)
        const chicoFolga = (diaSemana === 0);
        ESCALAS_MAP[`3_${dataStr}`] = {
          funcionarioId: 3, data: dataStr, turno: chicoFolga ? 'FOLGA' : 'DIURNO',
          ehExtra: false, valorDiaria: 0, status: 'CONFIRMADO',
          categoria: 'NORMAL', obs: chicoFolga ? 'Folga semanal' : 'Trato geral e biometria'
        };

        // Zé do Motor (4) folga sábado (6)
        const zeFolga = (diaSemana === 6);
        ESCALAS_MAP[`4_${dataStr}`] = {
          funcionarioId: 4, data: dataStr, turno: zeFolga ? 'FOLGA' : 'DIURNO',
          ehExtra: false, valorDiaria: 0, status: 'CONFIRMADO',
          categoria: 'NORMAL', obs: zeFolga ? 'Folga semanal' : 'Checagem de motores'
        };

        // Tonho (5) folga segunda (1)
        const tonhoFolga = (diaSemana === 1);
        ESCALAS_MAP[`5_${dataStr}`] = {
          funcionarioId: 5, data: dataStr, turno: tonhoFolga ? 'FOLGA' : 'DIURNO',
          ehExtra: false, valorDiaria: 0, status: 'CONFIRMADO',
          categoria: 'NORMAL', obs: tonhoFolga ? 'Folga semanal' : 'Apoio de campo'
        };
      }

      // Adicionar exemplo realista de ocorrência prévia
      const diaOcorr = new Date(ano, mes, 5).toISOString().split('T')[0];
      if (ESCALAS_MAP[`1_${diaOcorr}`]) {
        ESCALAS_MAP[`1_${diaOcorr}`].ehExtra = true;
        ESCALAS_MAP[`1_${diaOcorr}`].valorDiaria = 80.0;
        ESCALAS_MAP[`1_${diaOcorr}`].categoria = 'COBERTURA_TURNO';
        ESCALAS_MAP[`1_${diaOcorr}`].obs = 'Cobriu plantão extra pós-temporal para checar motores dos viveiros 3 e 4.';
      }
    }

    inicializarEscalasPadrao();

    function alternarVisualizacaoEscala(modo) {
      modoEscalaVisualizacao = modo;
      const btnSem = document.getElementById('btn-visao-semana');
      const btnMes = document.getElementById('btn-visao-mes');

      if (modo === 'semana') {
        if (btnSem) btnSem.className = 'px-3 py-1.5 rounded-lg font-bold bg-white text-slate-900 shadow-sm transition';
        if (btnMes) btnMes.className = 'px-3 py-1.5 rounded-lg font-semibold text-slate-600 hover:text-slate-900 transition';
      } else {
        if (btnMes) btnMes.className = 'px-3 py-1.5 rounded-lg font-bold bg-white text-slate-900 shadow-sm transition';
        if (btnSem) btnSem.className = 'px-3 py-1.5 rounded-lg font-semibold text-slate-600 hover:text-slate-900 transition';
      }
      renderizarGradeEscala();
    }

    function renderizarModuloEquipe() {
      renderizarGradeEscala();
      renderizarTabelaColaboradores();
      atualizarKpisEquipe();
    }

    function obterListaDiasVisualizacao() {
      const hoje = new Date();
      const dias = [];

      if (modoEscalaVisualizacao === 'semana') {
        // Obter de Segunda a Domingo da semana atual
        const diaSemana = hoje.getDay(); // 0 Dom, 1 Seg
        const diffSegunda = diaSemana === 0 ? -6 : 1 - diaSemana;
        const segunda = new Date(hoje);
        segunda.setDate(hoje.getDate() + diffSegunda);

        for (let i = 0; i < 7; i++) {
          const d = new Date(segunda);
          d.setDate(segunda.getDate() + i);
          dias.push(d);
        }
      } else {
        // Mês completo
        const ano = hoje.getFullYear();
        const mes = hoje.getMonth();
        const diasNoMes = new Date(ano, mes + 1, 0).getDate();
        for (let dia = 1; dia <= diasNoMes; dia++) {
          dias.push(new Date(ano, mes, dia));
        }
      }
      return dias;
    }

    function renderizarGradeEscala() {
      const thead = document.getElementById('thead-grade-escala');
      const tbody = document.getElementById('tbody-grade-escala');
      if (!thead || !tbody) return;

      const dias = obterListaDiasVisualizacao();
      const hojeStr = new Date().toISOString().split('T')[0];
      const nomesDias = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'];

      // Montar Cabeçalho
      let thHtml = `
        <tr>
          <th class="py-3 px-3.5 sticky left-0 z-20 bg-slate-100 min-w-[190px]">Colaborador / Função</th>
      `;

      dias.forEach(d => {
        const dataStr = d.toISOString().split('T')[0];
        const isHoje = (dataStr === hojeStr);
        const thClass = isHoje ? 'bg-violet-100 text-violet-900 ring-2 ring-violet-400 font-extrabold' : '';
        thHtml += `
          <th class="py-2.5 px-2 text-center font-bold min-w-[95px] ${thClass}">
            <div class="text-[10px] uppercase text-slate-500">${nomesDias[d.getDay()]}</div>
            <div class="text-xs ${isHoje ? 'text-violet-700 font-black' : 'text-slate-800'}">${d.getDate()}/${d.getMonth() + 1}</div>
            ${isHoje ? '<span class="text-[8px] bg-violet-600 text-white px-1.5 py-0.2 rounded-full uppercase tracking-tighter block mt-0.5">Hoje</span>' : ''}
          </th>
        `;
      });

      thHtml += `
          <th class="py-3 px-3 text-right min-w-[100px]">Extras Mês</th>
          <th class="py-3 px-3 text-right min-w-[110px]">Total Estimado</th>
        </tr>
      `;
      thead.innerHTML = thHtml;

      // Montar Linhas de Cada Colaborador
      tbody.innerHTML = '';
      FUNCIONARIOS_DATA.filter(f => f.ativo).forEach(f => {
        let totalExtrasColab = 0;
        let diasTrabColab = 0;

        // Calcular somatórios do mês
        Object.keys(ESCALAS_MAP).forEach(k => {
          if (k.startsWith(`${f.id}_`)) {
            const item = ESCALAS_MAP[k];
            if (item.ehExtra && item.valorDiaria) totalExtrasColab += item.valorDiaria;
            if (item.turno === 'DIURNO' || item.turno === 'NOTURNO_VIGIA') diasTrabColab++;
          }
        });

        const totalPagar = f.salarioBase + totalExtrasColab;

        let rowHtml = `
          <tr class="hover:bg-slate-50/80 transition">
            <td class="py-2.5 px-3.5 sticky left-0 z-10 bg-white font-bold text-slate-900 border-r border-slate-100">
              <div class="flex items-center gap-2">
                <span class="w-7 h-7 rounded-lg ${f.cargo.includes('Vigia') ? 'bg-indigo-100 text-indigo-700' : 'bg-slate-100 text-slate-700'} flex items-center justify-center text-xs font-bold">
                  <i class="fa-solid ${f.cargo.includes('Vigia') ? 'fa-moon' : 'fa-user'}"></i>
                </span>
                <div>
                  <div class="text-xs font-bold text-slate-900">${f.nome}</div>
                  <div class="text-[10px] text-slate-400 font-normal">${f.apelido ? f.apelido + ' • ' : ''}${f.cargo}</div>
                </div>
              </div>
            </td>
        `;

        dias.forEach(d => {
          const dataStr = d.toISOString().split('T')[0];
          const key = `${f.id}_${dataStr}`;
          const item = ESCALAS_MAP[key] || { turno: 'FOLGA', ehExtra: false, valorDiaria: 0, obs: '' };

          // Badges visuais por turno
          const turnosConfig = {
            DIURNO: { label: '☀️ Diurno', class: 'bg-blue-50 text-blue-700 border-blue-200 hover:bg-blue-100' },
            NOTURNO_VIGIA: { label: '🌙 21h-06h', class: 'bg-indigo-50 text-indigo-700 border-indigo-200 hover:bg-indigo-100 font-black' },
            FOLGA: { label: '🏖️ Folga', class: 'bg-slate-100 text-slate-500 border-slate-200 hover:bg-slate-200' },
            FALTA_JUSTIFICADA: { label: '🏥 Atestado', class: 'bg-amber-50 text-amber-800 border-amber-200 hover:bg-amber-100' },
            FALTA_INJUSTIFICADA: { label: '❌ Falta', class: 'bg-red-50 text-red-700 border-red-200 hover:bg-red-100 font-bold' },
            FERIAS: { label: '🌴 Férias', class: 'bg-emerald-50 text-emerald-700 border-emerald-200 hover:bg-emerald-100' }
          };

          const cfg = turnosConfig[item.turno] || turnosConfig.FOLGA;
          const temObs = item.obs && item.obs.trim().length > 0;
          const isHoje = (dataStr === hojeStr);

          rowHtml += `
            <td class="py-2 px-1 text-center ${isHoje ? 'bg-violet-50/50' : ''}">
              <div onclick="abrirModalApontamentoDia(${f.id}, '${dataStr}')" title="${temObs ? item.obs : 'Clique para alterar turno ou apontar ocorrência'}" class="cursor-pointer p-1.5 rounded-xl border ${cfg.class} transition text-[10px] flex flex-col items-center justify-center gap-0.5 shadow-2xs group relative">
                <span class="truncate max-w-[85px]">${cfg.label}</span>
                ${item.ehExtra ? `<span class="text-[9px] font-extrabold text-amber-700 bg-yellow-200/80 px-1 rounded flex items-center gap-0.5">⭐ +R$ ${Math.round(item.valorDiaria || f.valorDiariaExtra)}</span>` : ''}
                ${temObs ? `<i class="fa-solid fa-comment-dots text-violet-600 text-[10px] mt-0.5" title="${item.obs}"></i>` : ''}
              </div>
            </td>
          `;
        });

        rowHtml += `
            <td class="py-2.5 px-3 text-right font-mono font-bold text-amber-700">
              ${totalExtrasColab > 0 ? '+R$ ' + totalExtrasColab.toLocaleString('pt-BR', { minimumFractionDigits: 2 }) : '-'}
            </td>
            <td class="py-2.5 px-3 text-right font-mono font-extrabold text-emerald-700 bg-emerald-50/40">
              R$ ${totalPagar.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
            </td>
          </tr>
        `;

        tbody.innerHTML += rowHtml;
      });
    }

    function renderizarTabelaColaboradores() {
      const tbody = document.getElementById('tbody-tabela-colaboradores');
      if (!tbody) return;

      tbody.innerHTML = '';
      let somatorioFixo = 0;
      let somatorioExtras = 0;

      FUNCIONARIOS_DATA.filter(f => f.ativo).forEach(f => {
        let extrasMês = 0;
        let faltasMês = 0;

        Object.keys(ESCALAS_MAP).forEach(k => {
          if (k.startsWith(`${f.id}_`)) {
            const item = ESCALAS_MAP[k];
            if (item.ehExtra && item.valorDiaria) extrasMês += item.valorDiaria;
            if (item.turno === 'FALTA_JUSTIFICADA' || item.turno === 'FALTA_INJUSTIFICADA') faltasMês++;
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
    // MODAL DE APONTAMENTO DIÁRIO, OCORRÊNCIA E DIÁRIA EXTRA
    // ========================================================
    function abrirModalApontamentoDia(funcionarioId, dataStr) {
      const f = FUNCIONARIOS_DATA.find(x => x.id === funcionarioId);
      if (!f) return;

      pontoSelecionado = { funcionarioId, dataStr };
      const key = `${funcionarioId}_${dataStr}`;
      const item = ESCALAS_MAP[key] || {
        turno: 'DIURNO', ehExtra: false, valorDiaria: f.valorDiariaExtra || 0,
        categoria: 'NORMAL', obs: ''
      };

      const [ano, mes, dia] = dataStr.split('-');
      document.getElementById('modal-apont-titulo').textContent = `Apontamento — ${f.nome}`;
      document.getElementById('modal-apont-subtitulo').textContent = `${f.apelido ? f.apelido + ' • ' : ''}${f.cargo} • Data: ${dia}/${mes}/${ano}`;

      document.getElementById('modal-apont-turno').value = item.turno || 'DIURNO';
      document.getElementById('modal-apont-eh-extra').checked = !!item.ehExtra;
      document.getElementById('modal-apont-valor-diaria').value = item.valorDiaria || f.valorDiariaExtra || 80.0;
      document.getElementById('modal-apont-categoria').value = item.categoria || 'NORMAL';
      document.getElementById('modal-apont-obs').value = item.obs || '';

      toggleInputValorExtra();
      document.getElementById('modal-apontamento-dia').classList.remove('hidden');
    }

    function fecharModalApontamentoDia() {
      const m = document.getElementById('modal-apontamento-dia');
      if (m) m.classList.add('hidden');
      pontoSelecionado = null;
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
      const ehExtra = document.getElementById('modal-apont-eh-extra').checked;
      const valorDiaria = ehExtra ? (parseFloat(document.getElementById('modal-apont-valor-diaria').value) || (f ? f.valorDiariaExtra : 80.0)) : 0.0;
      const categoria = document.getElementById('modal-apont-categoria').value;
      const obs = document.getElementById('modal-apont-obs').value.trim();

      // 1. Tentar sincronizar com o Backend FastAPI caso online
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

      // 2. Atualizar estado local
      const key = `${funcionarioId}_${dataStr}`;
      ESCALAS_MAP[key] = {
        funcionarioId,
        data: dataStr,
        turno,
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
      const obs = document.getElementById('input-func-obs').value.trim();

      if (!nome) {
        alert('Por favor, informe o nome completo do colaborador.');
        return;
      }

      if (funcionarioEmEdicao) {
        // Atualizar existente
        funcionarioEmEdicao.nome = nome;
        funcionarioEmEdicao.apelido = apelido;
        funcionarioEmEdicao.cargo = cargo;
        funcionarioEmEdicao.tipoContrato = tipoContrato;
        funcionarioEmEdicao.whatsapp = whatsapp;
        funcionarioEmEdicao.chavePix = chavePix;
        funcionarioEmEdicao.salarioBase = salarioBase;
        funcionarioEmEdicao.valorDiariaExtra = valorDiariaExtra;
        funcionarioEmEdicao.observacoes = obs;
      } else {
        // Criar novo
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
          ativo: true,
          observacoes: obs
        });

        // Preencher escala padrão para o novo membro
        const hoje = new Date();
        const diasNoMes = new Date(hoje.getFullYear(), hoje.getMonth() + 1, 0).getDate();
        for (let d = 1; d <= diasNoMes; d++) {
          const dt = new Date(hoje.getFullYear(), hoje.getMonth(), d);
          const dtStr = dt.toISOString().split('T')[0];
          ESCALAS_MAP[`${novoId}_${dtStr}`] = {
            funcionarioId: novoId,
            data: dtStr,
            turno: dt.getDay() === 0 ? 'FOLGA' : 'DIURNO',
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
              ehExtra: isVigia && v.tipoContrato === 'DIARISTA',
              valorDiaria: (isVigia && v.tipoContrato === 'DIARISTA') ? v.valorDiariaExtra : 0,
              obs: isVigia ? 'Plantão Noturno 21h às 06h' : 'Folga 12x36'
            };
          });
        }
      } else {
        // 6x1 Tratadores
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
              ehExtra: false,
              valorDiaria: 0,
              obs: isFolga ? 'Folga semanal 6x1' : 'Trato diurno'
            };
          });
        }
      }

      fecharModalTemplateEscala();
      renderizarModuloEquipe();
      alert(`✅ Escala ${tipo === '12x36_VIGIAS' ? '12x36' : '6x1'} gerada com sucesso para o período!`);
    }

    // ========================================================
    // MODAL DE CHECK-IN DO VIGIA NOTURNO
    // ========================================================
    function abrirModalCheckinVigia() {
      const hojeStr = new Date().toISOString().split('T')[0];
      const ativos = FUNCIONARIOS_DATA.filter(f => f.ativo);
      let vigia = null;

      ativos.forEach(f => {
        const item = ESCALAS_MAP[`${f.id}_${hojeStr}`];
        if (item && item.turno === 'NOTURNO_VIGIA') vigia = f;
      });

      if (!vigia) {
        vigia = ativos.find(f => f.cargo.includes('Vigia')) || ativos[0];
      }

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
          texto += `• *${f.nome}* (${f.apelido || 'Vigia'}) - ${item.obs || 'Ronda de O2'}\\n`;
        }
      });

      texto += `\\n*☀️ EQUIPE NO TURNO DIURNO:*\\n`;
      FUNCIONARIOS_DATA.filter(f => f.ativo).forEach(f => {
        const item = ESCALAS_MAP[`${f.id}_${hojeStr}`];
        if (item && item.turno === 'DIURNO') {
          texto += `• ${f.nome} (${f.cargo})\\n`;
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

# Injetar as funções de equipe antes do fechamento </script>
pos_close_script = html_content.rfind('</script>')
if "renderizarModuloEquipe" not in html_content and pos_close_script != -1:
    html_content = html_content[:pos_close_script] + funcoes_equipe_js + "\n  " + html_content[pos_close_script:]
    print("Funções do Módulo de Equipe injetadas com sucesso!")

# Atualizar a função navegarPara para acionar renderizarModuloEquipe()
padrao_nav_equipe = r"\} else if \(viewId === 'analytics-equipe'\) \{"
sub_nav_equipe = """} else if (viewId === 'analytics-equipe') {
        atualizarHeaderNavegacao('Gestão de Equipe & Vigia Noturno', 'Início > Operação > Equipe');
        renderizarModuloEquipe();"""

if re.search(padrao_nav_equipe, html_content):
    html_content = re.sub(padrao_nav_equipe, sub_nav_equipe, html_content, count=1)
    print("navegarPara atualizada para acionar renderizarModuloEquipe()!")
else:
    # Inserir no bloco de triggers específicos
    pos_trigger = html_content.find("if (viewId === 'dashboard-macro') {")
    if pos_trigger != -1:
        trigger_equipe = """if (viewId === 'analytics-equipe') {
        atualizarHeaderNavegacao('Gestão de Equipe & Vigia Noturno', 'Início > Operação > Equipe');
        renderizarModuloEquipe();
      } else """
        html_content = html_content[:pos_trigger] + trigger_equipe + html_content[pos_trigger:]
        print("Trigger de analytics-equipe inserido em navegarPara!")

# Adicionar chamada renderizarModuloEquipe no DOMContentLoaded
pos_dom = html_content.find("renderizarModuloMapa2D();")
if pos_dom != -1 and "renderizarModuloEquipe();" not in html_content[pos_dom:pos_dom+200]:
    html_content = html_content[:pos_dom+25] + "\n      renderizarModuloEquipe();" + html_content[pos_dom+25:]
    print("renderizarModuloEquipe adicionado ao DOMContentLoaded!")

HTML_PATH.write_text(html_content, encoding="utf-8")
print(f"dashboard_interativo_prototipo.html gravado com sucesso! Tamanho: {len(html_content)} bytes.")
