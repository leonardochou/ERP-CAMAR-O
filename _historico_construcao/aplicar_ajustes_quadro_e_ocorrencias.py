"""
Script para:
1. Reduzir o tamanho vertical do quadro da Google Agenda (de 580px/52px para 360px/36px);
2. Adicionar abaixo da agenda um campo completo para listagem de ocorrências
   (faltas, diárias, extras, reclamações, atestados e coberturas);
3. Adicionar modal para cadastrar novas ocorrências e integração com WhatsApp e recálculo da folha.
"""
import re
import shutil
from pathlib import Path

BASE_DIR = Path(r"G:\Meu Drive\ANTIGRAVITY DRIVE\CAMARÃO\ERP CAMARÃO")
HTML_PATH = BASE_DIR / "dashboard_interativo_prototipo.html"
BACKUP_PATH = BASE_DIR / "dashboard_interativo_prototipo.backup_antes_ocorrencias.html"

# Fazer backup
shutil.copy2(HTML_PATH, BACKUP_PATH)
print(f"Backup criado com sucesso em: {BACKUP_PATH}")

html_content = HTML_PATH.read_text(encoding="utf-8")

# ==============================================================================
# 1. REDUZIR O TAMANHO DO QUADRO DA GOOGLE AGENDA
# ==============================================================================
# A. Trocar max-h-[580px] por max-h-[360px]
html_content = html_content.replace('max-h-[580px]', 'max-h-[360px]')

# B. Trocar divs de hora de h-[52px] para h-[36px]
html_content = html_content.replace('h-[52px]', 'h-[36px]')

# C. Linha de folgas mais compacta
html_content = html_content.replace(
    'class="bg-slate-50 p-2.5 rounded-2xl border border-slate-200"',
    'class="bg-slate-50 p-2 rounded-xl border border-slate-200"'
)

print("Ajuste de dimensões do quadro Google Agenda aplicado (max-h-[360px] e slots h-[36px]).")

# ==============================================================================
# 2. INSERIR O PAINEL DE OCORRÊNCIAS ABAIXO DO QUADRO DA AGENDA
# ==============================================================================
painel_ocorrencias_html = """
        <!-- ============================================================== -->
        <!-- SEÇÃO 3: REGISTRO & LISTAGEM DE OCORRÊNCIAS DA EQUIPE          -->
        <!-- (Faltas, Diárias, Extras, Reclamações, Atestados e Coberturas) -->
        <!-- ============================================================== -->
        <div id="painel-ocorrencias-equipe" class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          
          <!-- Cabeçalho do Painel de Ocorrências com Botão de Ação -->
          <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-3 border-b border-slate-100">
            <div>
              <div class="flex items-center gap-2">
                <span class="w-2.5 h-2.5 rounded-full bg-amber-500"></span>
                <h3 class="text-base font-bold text-slate-900 flex items-center gap-2">
                  <i class="fa-solid fa-clipboard-list text-amber-600"></i> Registro Geral de Ocorrências, Extras & Faltas
                </h3>
              </div>
              <p class="text-xs text-slate-500 mt-0.5">
                Histórico operacional da fazenda: plantões extras pagos, faltas, atestados médicos, advertências e reclamações de campo
              </p>
            </div>

            <!-- Botão de Ação Rápida -->
            <div class="flex items-center gap-2">
              <button onclick="abrirModalNovaOcorrencia()" class="px-3.5 py-2 rounded-xl bg-amber-600 hover:bg-amber-700 text-white font-bold text-xs transition flex items-center gap-1.5 shadow-sm">
                <i class="fa-solid fa-plus-circle"></i> Nova Ocorrência
              </button>
            </div>
          </div>

          <!-- Mini Cards de Resumo Rápido das Ocorrências do Mês -->
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div class="p-3 rounded-xl bg-slate-50 border border-slate-200">
              <span class="text-[10px] font-bold text-slate-500 uppercase flex items-center gap-1">
                <i class="fa-solid fa-list-check text-slate-600"></i> Total no Mês
              </span>
              <div id="kpi-ocorrencias-total" class="text-lg font-extrabold text-slate-900 mt-0.5">5 Registros</div>
              <span class="text-[9px] text-slate-400">Outubro de 2026</span>
            </div>

            <div class="p-3 rounded-xl bg-amber-50/70 border border-amber-200">
              <span class="text-[10px] font-bold text-amber-800 uppercase flex items-center gap-1">
                <i class="fa-solid fa-star text-amber-600"></i> Diárias Extras Pagas
              </span>
              <div id="kpi-ocorrencias-extras" class="text-lg font-extrabold text-amber-900 mt-0.5">2 Extras (+R$ 165)</div>
              <span class="text-[9px] text-amber-700">Somadas na folha líquida</span>
            </div>

            <div class="p-3 rounded-xl bg-red-50/70 border border-red-200">
              <span class="text-[10px] font-bold text-red-800 uppercase flex items-center gap-1">
                <i class="fa-solid fa-user-xmark text-red-600"></i> Faltas Registradas
              </span>
              <div id="kpi-ocorrencias-faltas" class="text-lg font-extrabold text-red-900 mt-0.5">1 Falta • 1 Atestado</div>
              <span class="text-[9px] text-red-700">-R$ 35,00 em desconto</span>
            </div>

            <div class="p-3 rounded-xl bg-orange-50/70 border border-orange-200">
              <span class="text-[10px] font-bold text-orange-800 uppercase flex items-center gap-1">
                <i class="fa-solid fa-triangle-exclamation text-orange-600"></i> Reclamações & Alertas
              </span>
              <div id="kpi-ocorrencias-reclamacoes" class="text-lg font-extrabold text-orange-900 mt-0.5">1 Notificação</div>
              <span class="text-[9px] text-orange-700">Conduta / zootecnia</span>
            </div>
          </div>

          <!-- Barra de Filtros em Chips -->
          <div class="flex flex-wrap items-center justify-between gap-2 pt-1">
            <div class="flex flex-wrap items-center gap-1.5 text-xs">
              <span class="text-[11px] font-bold text-slate-400 mr-1">Filtrar:</span>
              <button onclick="filtrarOcorrencias('TODAS')" id="filtro-ocorr-TODAS" class="px-2.5 py-1 rounded-lg font-bold bg-slate-900 text-white shadow-xs transition">
                Todas
              </button>
              <button onclick="filtrarOcorrencias('EXTRA')" id="filtro-ocorr-EXTRA" class="px-2.5 py-1 rounded-lg font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200 border border-slate-200 transition flex items-center gap-1">
                ⭐ Diárias Extras
              </button>
              <button onclick="filtrarOcorrencias('FALTA')" id="filtro-ocorr-FALTA" class="px-2.5 py-1 rounded-lg font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200 border border-slate-200 transition flex items-center gap-1">
                ❌ Faltas
              </button>
              <button onclick="filtrarOcorrencias('ATESTADO')" id="filtro-ocorr-ATESTADO" class="px-2.5 py-1 rounded-lg font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200 border border-slate-200 transition flex items-center gap-1">
                🏥 Atestados
              </button>
              <button onclick="filtrarOcorrencias('RECLAMACAO')" id="filtro-ocorr-RECLAMACAO" class="px-2.5 py-1 rounded-lg font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200 border border-slate-200 transition flex items-center gap-1">
                ⚠️ Reclamações & Conduta
              </button>
              <button onclick="filtrarOcorrencias('COBERTURA')" id="filtro-ocorr-COBERTURA" class="px-2.5 py-1 rounded-lg font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200 border border-slate-200 transition flex items-center gap-1">
                🔄 Coberturas / Manutenção
              </button>
            </div>

            <div class="text-[11px] text-slate-400">
              Mostrando <strong id="cont-ocorrencias-exibidas" class="text-slate-700">5</strong> ocorrência(s)
            </div>
          </div>

          <!-- Tabela Responsiva de Ocorrências -->
          <div class="overflow-x-auto rounded-xl border border-slate-200">
            <table class="w-full text-left text-xs border-collapse bg-white">
              <thead class="bg-slate-50 text-slate-600 font-bold border-b border-slate-200 uppercase text-[10px] tracking-wider">
                <tr>
                  <th class="py-3 px-3">Data</th>
                  <th class="py-3 px-3">Colaborador</th>
                  <th class="py-3 px-3">Categoria / Tipo</th>
                  <th class="py-3 px-3 min-w-[280px]">Descrição & Relato Operacional</th>
                  <th class="py-3 px-3 text-right">Impacto na Folha</th>
                  <th class="py-3 px-3 text-center">Status</th>
                  <th class="py-3 px-3 text-center">Ações</th>
                </tr>
              </thead>
              <tbody id="tbody-ocorrencias" class="divide-y divide-slate-100">
                <!-- Injetado dinamicamente via JS -->
              </tbody>
            </table>
          </div>

        </div>
"""

# Inserir antes de fechar a section view-analytics-equipe
# Procuramos onde fecha o container anterior da escala e fecha a seção
padrao_fim_secao_equipe = r'(<!-- CONTAINER 2: VISUALIZAÇÃO MATRIZ MENSAL[\s\S]*?</div>\s*</div>\s*)(</section>)'

if re.search(padrao_fim_secao_equipe, html_content):
    html_content = re.sub(padrao_fim_secao_equipe, rf'\g<1>\n{painel_ocorrencias_html}\n      \g<2>', html_content, count=1)
    print("Painel de Ocorrências inserido com sucesso abaixo da agenda!")
else:
    print("ERRO ao localizar fechamento da seção de equipe!")

# ==============================================================================
# 3. ADICIONAR O MODAL DE NOVA OCORRÊNCIA (#modal-nova-ocorrencia)
# ==============================================================================
modal_nova_ocorrencia_html = """
  <!-- ============================================================== -->
  <!-- MODAL: REGISTRAR NOVA OCORRÊNCIA / EXTRA / FALTA / RECLAMAÇÃO  -->
  <!-- ============================================================== -->
  <div id="modal-nova-ocorrencia" class="hidden fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
    <div class="bg-white rounded-3xl max-w-lg w-full shadow-2xl border border-slate-200 overflow-hidden animate-in fade-in zoom-in-95 duration-150">
      
      <!-- Cabeçalho do Modal -->
      <div class="p-5 bg-gradient-to-r from-amber-600 to-orange-700 text-white flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 rounded-2xl bg-white/10 backdrop-blur-md flex items-center justify-center text-lg font-bold">
            <i class="fa-solid fa-clipboard-check"></i>
          </div>
          <div>
            <h3 class="font-bold text-base">Registrar Ocorrência de Campo</h3>
            <p class="text-xs text-amber-100">Faltas, diárias extras, atestados médicos e advertências</p>
          </div>
        </div>
        <button onclick="fecharModalNovaOcorrencia()" class="text-white/70 hover:text-white transition">
          <i class="fa-solid fa-xmark text-lg"></i>
        </button>
      </div>

      <!-- Formulário do Modal -->
      <form onsubmit="event.preventDefault(); salvarNovaOcorrencia();" class="p-6 space-y-4 text-xs max-h-[80vh] overflow-y-auto">
        
        <!-- Seleção de Colaborador e Data -->
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block font-bold text-slate-700 mb-1">Colaborador:</label>
            <select id="modal-ocorr-colab" class="w-full text-xs font-semibold p-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-amber-500 bg-white" required>
              <option value="1">Carlinhos (Vigia Noturno)</option>
              <option value="2">Tião (Vigia Folguista)</option>
              <option value="3" selected>Chico (Arraçoador Principal)</option>
              <option value="4">Zé do Motor (Operador)</option>
              <option value="5">Tonho (Apoio de Campo)</option>
            </select>
          </div>
          <div>
            <label class="block font-bold text-slate-700 mb-1">Data do Fato:</label>
            <input type="date" id="modal-ocorr-data" class="w-full text-xs font-bold p-2.5 rounded-xl border border-slate-300 bg-white" required>
          </div>
        </div>

        <!-- Categoria / Tipo de Ocorrência -->
        <div>
          <label class="block font-bold text-slate-700 mb-1">Tipo da Ocorrência:</label>
          <select id="modal-ocorr-tipo" onchange="aoMudarTipoOcorrencia()" class="w-full text-xs font-semibold p-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-amber-500 bg-white" required>
            <option value="EXTRA">⭐ Diária Extra Cumprida (Plantão adicional com valor a pagar)</option>
            <option value="FALTA_INJUSTIFICADA">❌ Falta Injustificada (Sem aviso / Desconto na folha)</option>
            <option value="ATESTADO">🏥 Falta Justificada (Atestado Médico / Licença)</option>
            <option value="RECLAMACAO">⚠️ Reclamação / Alerta de Conduta / Zootecnia</option>
            <option value="COBERTURA">🔄 Cobertura Emergencial de Turno / Plantão de Colega</option>
            <option value="MANUTENCAO">⚙️ Manutenção Noturna Emergencial (Bombas/Aeradores)</option>
          </select>
        </div>

        <!-- Impacto Financeiro (Acréscimo, Desconto ou Neutro) -->
        <div class="p-3.5 rounded-2xl bg-amber-50/60 border border-amber-200 space-y-2">
          <label class="block font-bold text-amber-950 flex items-center justify-between">
            <span class="flex items-center gap-1.5"><i class="fa-solid fa-coins text-amber-600"></i> Impacto na Folha de Pagamento:</span>
            <span id="label-tipo-impacto" class="text-[10px] px-2 py-0.5 rounded-full font-bold bg-amber-200 text-amber-900">Acréscimo</span>
          </label>
          <div class="grid grid-cols-2 gap-3 items-center">
            <div>
              <label class="block text-[10px] text-amber-800 mb-0.5 font-semibold">Valor em R$:</label>
              <input type="number" step="5" id="modal-ocorr-valor" value="80" class="w-full text-xs font-mono font-bold p-2 rounded-xl border border-amber-300 bg-white" placeholder="80.00">
            </div>
            <div>
              <label class="block text-[10px] text-amber-800 mb-0.5 font-semibold">Horário / Turno (opcional):</label>
              <input type="text" id="modal-ocorr-horario" placeholder="ex: 21:00 às 06:00" class="w-full text-xs p-2 rounded-xl border border-amber-300 bg-white">
            </div>
          </div>
        </div>

        <!-- Descrição / Relato Operacional Detalhado -->
        <div>
          <label class="block font-bold text-slate-700 mb-1">Descrição / Relato Operacional dos Fatos:</label>
          <textarea id="modal-ocorr-descricao" rows="3" class="w-full text-xs p-3 rounded-xl border border-slate-300 focus:ring-2 focus:ring-amber-500 bg-white" placeholder="Descreva os fatos ocorridos com riqueza de detalhes (ex: Cobriu o plantão do vigia titular durante queda de energia; Sobra crônica de ração no V-04; Atestado odontológico apresentado)..." required></textarea>
        </div>

        <!-- Botões de Ação -->
        <div class="flex items-center justify-end space-x-2 pt-3 border-t border-slate-100">
          <button type="button" onclick="fecharModalNovaOcorrencia()" class="px-4 py-2 rounded-xl text-slate-600 hover:bg-slate-100 font-bold transition">
            Cancelar
          </button>
          <button type="submit" class="px-5 py-2 rounded-xl bg-amber-600 hover:bg-amber-700 text-white font-bold transition flex items-center gap-1.5 shadow-sm">
            <i class="fa-solid fa-save"></i> Salvar Ocorrência
          </button>
        </div>

      </form>
    </div>
  </div>
"""

# Inserir modal antes de fechar o </body>
pos_body_close = html_content.rfind('</body>')
if pos_body_close != -1:
    html_content = html_content[:pos_body_close] + modal_nova_ocorrencia_html + "\n" + html_content[pos_body_close:]
    print("Modal de Nova Ocorrência inserido antes de </body>!")
else:
    print("ERRO ao localizar </body>!")

# ==============================================================================
# 4. ATUALIZAR O JAVASCRIPT: REDUZIR ALTURA E INTEGRAR OCORRÊNCIAS
# ==============================================================================
# Ajustar a função renderizarGoogleAgendaView para slotHeight = 36 e heightPx = Math.max(28, ...)
html_content = html_content.replace('const slotHeight = 52;', 'const slotHeight = 36;')
html_content = html_content.replace('h-[52px] border-b', 'h-[36px] border-b')
html_content = html_content.replace('const heightPx = Math.max(38,', 'const heightPx = Math.max(26,')
html_content = html_content.replace('min-w-[700px]', 'min-w-[650px]')

# Código JS das Ocorrências
codigo_js_ocorrencias = """
    // ========================================================
    // MOTOR DE OCORRÊNCIAS DA EQUIPE (FALTAS, EXTRAS, RECLAMAÇÕES)
    // ========================================================
    let filtroOcorrenciaAtivo = 'TODAS';

    let OCORRENCIAS_DATA = [
      {
        id: 1,
        funcionarioId: 1,
        data: new Date().toISOString().split('T')[0], // Hoje
        tipo: 'EXTRA',
        categoriaLabel: '⭐ Diária Extra Cumprida',
        categoriaClass: 'bg-amber-100 text-amber-900 border border-amber-300',
        icone: 'fa-star text-amber-600',
        horario: '21:00 às 06:00',
        valorImpacto: 80.0,
        tipoImpacto: 'ACRESCIMO',
        status: 'REGISTRADO',
        descricao: 'Plantão noturno extra cumprido para acompanhar oxigenação intensiva após queda de energia na rede da Cosern às 02h40.'
      },
      {
        id: 2,
        funcionarioId: 3,
        data: '2026-10-20',
        tipo: 'RECLAMACAO',
        categoriaLabel: '⚠️ Reclamação / Conduta',
        categoriaClass: 'bg-orange-100 text-orange-900 border border-orange-300',
        icone: 'fa-triangle-exclamation text-orange-600',
        horario: '15:30',
        valorImpacto: 0.0,
        tipoImpacto: 'NEUTRO',
        status: 'NOTIFICADO',
        descricao: 'Sobra excessiva de ração no viveiro V-04 (nível 3 em duas bandejas). Colaborador alertado verbalmente para respeitar o corte de 50% recomendado.'
      },
      {
        id: 3,
        funcionarioId: 5,
        data: '2026-10-19',
        tipo: 'FALTA_INJUSTIFICADA',
        categoriaLabel: '❌ Falta Injustificada',
        categoriaClass: 'bg-red-100 text-red-900 border border-red-300',
        icone: 'fa-user-xmark text-red-600',
        horario: '06:30 às 11:30',
        valorImpacto: -35.0,
        tipoImpacto: 'DESCONTO',
        status: 'DESCONTADO',
        descricao: 'Ausência no turno da manhã sem comunicação prévia ao encarregado. Aplicado desconto proporcional de meio expediente na folha.'
      },
      {
        id: 4,
        funcionarioId: 4,
        data: '2026-10-16',
        tipo: 'MANUTENCAO',
        categoriaLabel: '⚙️ Manutenção Emergencial',
        categoriaClass: 'bg-emerald-100 text-emerald-900 border border-emerald-300',
        icone: 'fa-wrench text-emerald-600',
        horario: '23:30 às 01:00',
        valorImpacto: 85.0,
        tipoImpacto: 'ACRESCIMO',
        status: 'REGISTRADO',
        descricao: 'Acionado às 23h30 para substituição da correia partida no aerador de 2cv do viveiro V-07. Equipamento restabelecido sem anóxia.'
      },
      {
        id: 5,
        funcionarioId: 2,
        data: '2026-10-14',
        tipo: 'ATESTADO',
        categoriaLabel: '🏥 Falta Justificada (Atestado)',
        categoriaClass: 'bg-blue-100 text-blue-900 border border-blue-300',
        icone: 'fa-notes-medical text-blue-600',
        horario: 'Dia todo',
        valorImpacto: 0.0,
        tipoImpacto: 'NEUTRO',
        status: 'ARQUIVADO',
        descricao: 'Apresentou atestado médico de 1 dia relativo a atendimento odontológico de emergência no posto de Ceará-Mirim. Turno coberto por Carlinhos.'
      }
    ];

    function renderizarPainelOcorrencias(filtro = filtroOcorrenciaAtivo) {
      filtroOcorrenciaAtivo = filtro;
      const tbody = document.getElementById('tbody-ocorrencias');
      if (!tbody) return;

      const hojeStr = new Date().toISOString().split('T')[0];

      // Filtrar itens
      const filtrados = OCORRENCIAS_DATA.filter(item => {
        if (filtro === 'TODAS') return true;
        if (filtro === 'EXTRA') return item.tipo === 'EXTRA';
        if (filtro === 'FALTA') return item.tipo === 'FALTA_INJUSTIFICADA';
        if (filtro === 'ATESTADO') return item.tipo === 'ATESTADO';
        if (filtro === 'RECLAMACAO') return item.tipo === 'RECLAMACAO';
        if (filtro === 'COBERTURA') return item.tipo === 'COBERTURA' || item.tipo === 'MANUTENCAO';
        return true;
      });

      // Atualizar contador
      const contEl = document.getElementById('cont-ocorrencias-exibidas');
      if (contEl) contEl.innerText = filtrados.length;

      // Atualizar KPIs do resumo
      let totalExtras = 0;
      let somaExtras = 0;
      let totalFaltasInjust = 0;
      let totalAtestados = 0;
      let totalReclamacoes = 0;
      let somaDescontos = 0;

      OCORRENCIAS_DATA.forEach(o => {
        if (o.tipo === 'EXTRA' || o.tipo === 'MANUTENCAO') {
          totalExtras++;
          somaExtras += Math.max(0, o.valorImpacto);
        } else if (o.tipo === 'FALTA_INJUSTIFICADA') {
          totalFaltasInjust++;
          somaDescontos += Math.abs(o.valorImpacto);
        } else if (o.tipo === 'ATESTADO') {
          totalAtestados++;
        } else if (o.tipo === 'RECLAMACAO') {
          totalReclamacoes++;
        }
      });

      const kpiTot = document.getElementById('kpi-ocorrencias-total');
      if (kpiTot) kpiTot.innerText = `${OCORRENCIAS_DATA.length} Registros`;

      const kpiExt = document.getElementById('kpi-ocorrencias-extras');
      if (kpiExt) kpiExt.innerText = `${totalExtras} Extras (+R$ ${Math.round(somaExtras)})`;

      const kpiFal = document.getElementById('kpi-ocorrencias-faltas');
      if (kpiFal) kpiFal.innerText = `${totalFaltasInjust} Falta • ${totalAtestados} Atestado`;

      const kpiRec = document.getElementById('kpi-ocorrencias-reclamacoes');
      if (kpiRec) kpiRec.innerText = `${totalReclamacoes} Notificação`;

      if (filtrados.length === 0) {
        tbody.innerHTML = `
          <tr>
            <td colspan="7" class="py-8 text-center text-slate-400">
              <i class="fa-solid fa-clipboard-check text-2xl text-slate-300 block mb-1"></i>
              Nenhuma ocorrência encontrada para o filtro selecionado.
            </td>
          </tr>
        `;
        return;
      }

      // Ordenar por data decrescente
      filtrados.sort((a, b) => b.data.localeCompare(a.data));

      let rowsHtml = '';
      filtrados.forEach(item => {
        const func = FUNCIONARIOS_DATA.find(f => f.id === item.funcionarioId) || { nome: 'Desconhecido', cargo: 'Operacional', apelido: 'Colaborador' };
        const cor = CORES_COLABORADORES[item.funcionarioId] || { bg: 'bg-slate-600', hex: '#475569' };

        const isHoje = (item.data === hojeStr);
        const [ano, mes, dia] = item.data.split('-');
        const dataFmt = `${dia}/${mes}/${ano}`;

        let impactoHtml = '<span class="text-slate-400 font-mono">R$ 0,00</span>';
        if (item.tipoImpacto === 'ACRESCIMO' || item.valorImpacto > 0) {
          impactoHtml = `<span class="font-extrabold text-amber-700 font-mono bg-amber-50 px-2 py-0.5 rounded-lg border border-amber-200">+ R$ ${item.valorImpacto.toFixed(2)}</span>`;
        } else if (item.tipoImpacto === 'DESCONTO' || item.valorImpacto < 0) {
          impactoHtml = `<span class="font-extrabold text-red-700 font-mono bg-red-50 px-2 py-0.5 rounded-lg border border-red-200">- R$ ${Math.abs(item.valorImpacto).toFixed(2)}</span>`;
        }

        let statusBadge = `<span class="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-emerald-100 text-emerald-800">✅ Registrado na Folha</span>`;
        if (item.status === 'NOTIFICADO') {
          statusBadge = `<span class="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-orange-100 text-orange-800">⚠️ Notificado Verbal</span>`;
        } else if (item.status === 'ARQUIVADO') {
          statusBadge = `<span class="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-blue-100 text-blue-800">📁 Atestado Arquivado</span>`;
        } else if (item.status === 'DESCONTADO') {
          statusBadge = `<span class="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-red-100 text-red-800">❌ Desconto em Folha</span>`;
        }

        rowsHtml += `
          <tr class="hover:bg-slate-50/70 transition">
            <!-- Data -->
            <td class="py-3 px-3 whitespace-nowrap">
              <span class="font-bold text-slate-900">${dataFmt}</span>
              ${isHoje ? '<span class="ml-1 text-[9px] font-extrabold px-1.5 py-0.2 rounded bg-blue-100 text-blue-800">Hoje</span>' : ''}
              ${item.horario ? `<div class="text-[10px] text-slate-400 font-mono">${item.horario}</div>` : ''}
            </td>

            <!-- Colaborador -->
            <td class="py-3 px-3">
              <div class="flex items-center space-x-2">
                <div class="w-7 h-7 rounded-full ${cor.bg} text-white flex items-center justify-center font-extrabold text-xs shadow-xs">
                  ${(func.apelido || func.nome).substring(0, 1)}
                </div>
                <div>
                  <div class="font-bold text-slate-900">${func.nome}</div>
                  <div class="text-[10px] text-slate-500 font-medium">${func.cargo}</div>
                </div>
              </div>
            </td>

            <!-- Categoria / Tipo -->
            <td class="py-3 px-3 whitespace-nowrap">
              <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[10px] font-bold ${item.categoriaClass}">
                <i class="fa-solid ${item.icone}"></i> ${item.categoriaLabel}
              </span>
            </td>

            <!-- Descrição e Relato -->
            <td class="py-3 px-3">
              <p class="text-xs text-slate-700 leading-snug font-medium max-w-xl">${item.descricao}</p>
            </td>

            <!-- Impacto na Folha -->
            <td class="py-3 px-3 text-right whitespace-nowrap">
              ${impactoHtml}
            </td>

            <!-- Status -->
            <td class="py-3 px-3 text-center whitespace-nowrap">
              ${statusBadge}
            </td>

            <!-- Ações -->
            <td class="py-3 px-3 text-center whitespace-nowrap">
              <div class="flex items-center justify-center space-x-1.5">
                <button onclick="enviarOcorrenciaWhatsApp(${item.id})" title="Enviar via WhatsApp" class="w-7 h-7 rounded-lg bg-emerald-50 text-emerald-700 hover:bg-emerald-600 hover:text-white transition flex items-center justify-center border border-emerald-200">
                  <i class="fab fa-whatsapp"></i>
                </button>
                <button onclick="excluirOcorrencia(${item.id})" title="Remover Ocorrência" class="w-7 h-7 rounded-lg bg-red-50 text-red-600 hover:bg-red-600 hover:text-white transition flex items-center justify-center border border-red-200">
                  <i class="fa-solid fa-trash-can"></i>
                </button>
              </div>
            </td>
          </tr>
        `;
      });

      tbody.innerHTML = rowsHtml;
    }

    function filtrarOcorrencias(tipo) {
      const botoes = ['TODAS', 'EXTRA', 'FALTA', 'ATESTADO', 'RECLAMACAO', 'COBERTURA'];
      botoes.forEach(b => {
        const el = document.getElementById(`filtro-ocorr-${b}`);
        if (el) {
          if (b === tipo) {
            el.className = 'px-2.5 py-1 rounded-lg font-bold bg-slate-900 text-white shadow-xs transition';
          } else {
            el.className = 'px-2.5 py-1 rounded-lg font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200 border border-slate-200 transition flex items-center gap-1';
          }
        }
      });
      renderizarPainelOcorrencias(tipo);
    }

    function abrirModalNovaOcorrencia(colabId = null, dataStr = null) {
      const hojeStr = new Date().toISOString().split('T')[0];
      const dataInput = document.getElementById('modal-ocorr-data');
      if (dataInput) dataInput.value = dataStr || hojeStr;

      const colabSelect = document.getElementById('modal-ocorr-colab');
      if (colabSelect && colabId) colabSelect.value = colabId;

      document.getElementById('modal-ocorr-tipo').value = 'EXTRA';
      document.getElementById('modal-ocorr-valor').value = '80';
      document.getElementById('modal-ocorr-horario').value = '';
      document.getElementById('modal-ocorr-descricao').value = '';

      aoMudarTipoOcorrencia();
      document.getElementById('modal-nova-ocorrencia').classList.remove('hidden');
    }

    function fecharModalNovaOcorrencia() {
      const m = document.getElementById('modal-nova-ocorrencia');
      if (m) m.classList.add('hidden');
    }

    function aoMudarTipoOcorrencia() {
      const tipo = document.getElementById('modal-ocorr-tipo').value;
      const valorInput = document.getElementById('modal-ocorr-valor');
      const labelImpacto = document.getElementById('label-tipo-impacto');

      if (tipo === 'EXTRA' || tipo === 'COBERTURA' || tipo === 'MANUTENCAO') {
        if (valorInput) valorInput.value = '80';
        if (labelImpacto) {
          labelImpacto.innerText = 'Acréscimo a Pagar';
          labelImpacto.className = 'text-[10px] px-2 py-0.5 rounded-full font-bold bg-amber-200 text-amber-900';
        }
      } else if (tipo === 'FALTA_INJUSTIFICADA') {
        if (valorInput) valorInput.value = '60';
        if (labelImpacto) {
          labelImpacto.innerText = 'Desconto em Folha';
          labelImpacto.className = 'text-[10px] px-2 py-0.5 rounded-full font-bold bg-red-200 text-red-900';
        }
      } else {
        if (valorInput) valorInput.value = '0';
        if (labelImpacto) {
          labelImpacto.innerText = 'Neutro (Sem Impacto)';
          labelImpacto.className = 'text-[10px] px-2 py-0.5 rounded-full font-bold bg-slate-200 text-slate-800';
        }
      }
    }

    function salvarNovaOcorrencia() {
      const colabId = parseInt(document.getElementById('modal-ocorr-colab').value);
      const dataStr = document.getElementById('modal-ocorr-data').value;
      const tipo = document.getElementById('modal-ocorr-tipo').value;
      let valor = parseFloat(document.getElementById('modal-ocorr-valor').value) || 0;
      const horario = document.getElementById('modal-ocorr-horario').value.trim();
      const descricao = document.getElementById('modal-ocorr-descricao').value.trim();

      if (!dataStr || !descricao) {
        alert('Por favor, preencha a data e o relato da ocorrência.');
        return;
      }

      let catLabel = 'Ocorrência';
      let catClass = 'bg-slate-100 text-slate-800 border border-slate-300';
      let icone = 'fa-clipboard-check';
      let tipoImp = 'NEUTRO';
      let status = 'REGISTRADO';

      if (tipo === 'EXTRA') {
        catLabel = '⭐ Diária Extra Cumprida';
        catClass = 'bg-amber-100 text-amber-900 border border-amber-300';
        icone = 'fa-star text-amber-600';
        tipoImp = 'ACRESCIMO';
      } else if (tipo === 'FALTA_INJUSTIFICADA') {
        catLabel = '❌ Falta Injustificada';
        catClass = 'bg-red-100 text-red-900 border border-red-300';
        icone = 'fa-user-xmark text-red-600';
        tipoImp = 'DESCONTO';
        valor = -Math.abs(valor);
        status = 'DESCONTADO';
      } else if (tipo === 'ATESTADO') {
        catLabel = '🏥 Falta Justificada (Atestado)';
        catClass = 'bg-blue-100 text-blue-900 border border-blue-300';
        icone = 'fa-notes-medical text-blue-600';
        tipoImp = 'NEUTRO';
        valor = 0;
        status = 'ARQUIVADO';
      } else if (tipo === 'RECLAMACAO') {
        catLabel = '⚠️ Reclamação / Conduta';
        catClass = 'bg-orange-100 text-orange-900 border border-orange-300';
        icone = 'fa-triangle-exclamation text-orange-600';
        tipoImp = 'NEUTRO';
        valor = 0;
        status = 'NOTIFICADO';
      } else if (tipo === 'COBERTURA') {
        catLabel = '🔄 Cobertura de Turno';
        catClass = 'bg-indigo-100 text-indigo-900 border border-indigo-300';
        icone = 'fa-user-clock text-indigo-600';
        tipoImp = 'ACRESCIMO';
      } else if (tipo === 'MANUTENCAO') {
        catLabel = '⚙️ Manutenção Noturna';
        catClass = 'bg-emerald-100 text-emerald-900 border border-emerald-300';
        icone = 'fa-wrench text-emerald-600';
        tipoImp = 'ACRESCIMO';
      }

      // Adicionar à lista
      const novoId = Date.now();
      OCORRENCIAS_DATA.unshift({
        id: novoId,
        funcionarioId: colabId,
        data: dataStr,
        tipo: tipo,
        categoriaLabel: catLabel,
        categoriaClass: catClass,
        icone: icone,
        horario: horario,
        valorImpacto: valor,
        tipoImpacto: tipoImp,
        status: status,
        descricao: descricao
      });

      // Se for extra ou falta, sincronizar também no ESCALAS_MAP da agenda
      const escalaKey = `${colabId}_${dataStr}`;
      if (ESCALAS_MAP[escalaKey]) {
        if (tipo === 'EXTRA' || tipo === 'COBERTURA' || tipo === 'MANUTENCAO') {
          ESCALAS_MAP[escalaKey].ehExtra = true;
          ESCALAS_MAP[escalaKey].valorDiaria = Math.abs(valor);
        } else if (tipo === 'FALTA_INJUSTIFICADA') {
          ESCALAS_MAP[escalaKey].turno = 'FALTA_INJUSTIFICADA';
        } else if (tipo === 'ATESTADO') {
          ESCALAS_MAP[escalaKey].turno = 'FALTA_JUSTIFICADA';
        }
        ESCALAS_MAP[escalaKey].obs = descricao;
      }

      fecharModalNovaOcorrencia();
      renderizarModuloEquipe();
      alert('✅ Ocorrência registrada com sucesso no histórico da fazenda!');
    }

    function excluirOcorrencia(id) {
      if (!confirm('Deseja realmente remover este registro de ocorrência?')) return;
      OCORRENCIAS_DATA = OCORRENCIAS_DATA.filter(o => o.id !== id);
      renderizarPainelOcorrencias();
      atualizarKpisEquipe();
      renderizarTabelaColaboradores();
    }

    function enviarOcorrenciaWhatsApp(id) {
      const o = OCORRENCIAS_DATA.find(item => item.id === id);
      if (!o) return;
      const func = FUNCIONARIOS_DATA.find(f => f.id === o.funcionarioId);
      const tel = func && func.whatsapp ? func.whatsapp.replace(/\D/g, '') : '';

      const [ano, mes, dia] = o.data.split('-');
      const dataFmt = `${dia}/${mes}/${ano}`;

      let msg = `*📋 REGISTRO DE OCORRÊNCIA — FAZENDA CEARÁ-MIRIM/RN*\\n\\n`;
      msg += `• *Colaborador:* ${func ? func.nome : 'Colaborador'}\\n`;
      msg += `• *Data:* ${dataFmt}\\n`;
      msg += `• *Tipo:* ${o.categoriaLabel}\\n`;
      if (o.horario) msg += `• *Horário:* ${o.horario}\\n`;
      msg += `• *Relato:* ${o.descricao}\\n`;
      if (o.valorImpacto > 0) msg += `• *Impacto Financeiro:* + R$ ${o.valorImpacto.toFixed(2)} (Acréscimo Folha)\\n`;
      if (o.valorImpacto < 0) msg += `• *Impacto Financeiro:* - R$ ${Math.abs(o.valorImpacto).toFixed(2)} (Desconto Folha)\\n`;
      msg += `\\n_Registrado no Sistema ERP Camarão_`;

      const url = tel ? `https://wa.me/55${tel}?text=${encodeURIComponent(msg)}` : `https://api.whatsapp.com/send?text=${encodeURIComponent(msg)}`;
      window.open(url, '_blank');
    }
"""

# Injetar a chamada renderizarPainelOcorrencias() dentro de renderizarModuloEquipe()
html_content = html_content.replace(
    'function renderizarModuloEquipe() {',
    'function renderizarModuloEquipe() {\n      renderizarPainelOcorrencias();'
)

# Injetar o bloco de funções de ocorrência antes de </script>
pos_close_script = html_content.rfind('</script>')
if pos_close_script != -1:
    html_content = html_content[:pos_close_script] + "\n" + codigo_js_ocorrencias + "\n  " + html_content[pos_close_script:]
    print("Funções JS de Ocorrências inseridas antes de </script>!")
else:
    print("ERRO ao localizar </script>!")

HTML_PATH.write_text(html_content, encoding="utf-8")
print(f"Arquivo final gravado com sucesso! Tamanho: {len(html_content)} bytes.")
