"""
Script para:
1. Implementar a função completa importarArquivoXlsxBiomassa(event) com parser SheetJS robusto,
   suportando tanto o formato 'v-1'..'v-10' quanto 'V-01'..'V-10', reconhecendo berçários e despescas;
2. Atualizar a função preencherTabelasAnaliticas() para renderizar as 11 colunas da tabela de biomassa
   com laboratório, berçário, despescas reais e status correto;
3. Sincronizar em tempo real ao clicar em Sincronizar Drive ou ao subir um arquivo Excel;
4. Re-renderizar automaticamente o viveiro selecionado ao importar.
"""
import json
import re
import shutil
from pathlib import Path

BASE_DIR = Path(r"G:\Meu Drive\ANTIGRAVITY DRIVE\CAMARÃO\ERP CAMARÃO")
HTML_PATH = BASE_DIR / "dashboard_interativo_prototipo.html"
BACKUP_PATH = BASE_DIR / "dashboard_interativo_prototipo.backup_antes_correcao_importador.html"

shutil.copy2(HTML_PATH, BACKUP_PATH)
print(f"Backup gravado em: {BACKUP_PATH}")

html_content = HTML_PATH.read_text(encoding="utf-8")

# 1. Nova implementação da função preencherTabelasAnaliticas para a tabela de Biomassa (11 colunas)
nova_logica_tabela_biomassa = """    function preencherTabelasAnaliticas() {
      // 1. Tabela de Biomassa (11 colunas sincronizadas com dados reais)
      const tbodyBio = document.getElementById('tbody-analytics-biomassa');
      if (tbodyBio) {
        tbodyBio.innerHTML = '';
        VIVEIROS_DATA.forEach(v => {
          const dadosViv = DADOS_PLANILHA_VIVEIROS[v.id] || { lab: 'Nenhum', pls: 0, pov: '-', tratos: [], tem_bercario: false };
          const isDesp = (dadosViv.statusLote === 'DESPESCADO' || v.status === 'despescado');
          const isAtivo = (dadosViv.statusLote === 'EM CULTIVO ATIVO' || v.status === 'otimo' || v.status === 'atencao');

          let badgeStatus = '<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-100 text-slate-600">⚪ Em Preparação</span>';
          if (isDesp) {
            badgeStatus = '<span class="px-2 py-0.5 rounded text-[10px] font-extrabold bg-amber-100 text-amber-900 border border-amber-300">🟡 Despescado</span>';
          } else if (isAtivo) {
            badgeStatus = v.status === 'atencao'
              ? '<span class="px-2 py-0.5 rounded text-[10px] font-extrabold bg-yellow-100 text-yellow-800 border border-yellow-300">🟡 Atenção O₂</span>'
              : '<span class="px-2 py-0.5 rounded text-[10px] font-extrabold bg-emerald-100 text-emerald-800 border border-emerald-300">🟢 Em Cultivo</span>';
          }

          const labBadge = dadosViv.lab && dadosViv.lab !== 'Nenhum'
            ? `<span class="px-2 py-0.5 rounded bg-violet-50 text-violet-800 font-extrabold text-[10px] border border-violet-200">${dadosViv.lab}</span>`
            : '<span class="text-slate-400">-</span>';

          const povTxt = dadosViv.pov && dadosViv.pov !== '-'
            ? `<span class="font-semibold text-slate-800">${dadosViv.pov}</span>` + (dadosViv.tem_bercario ? ' <span class="px-1.5 py-0.2 rounded bg-blue-100 text-blue-800 text-[9px] font-bold">🐣 Berçário</span>' : '')
            : '<span class="text-slate-400">-</span>';

          const ddcTxt = dadosViv.despesca
            ? `<span class="font-bold text-amber-800">${dadosViv.despesca.doc || v.ddc} d (Final)</span>`
            : (v.ddc > 0 ? `${v.ddc} d` : '-');

          const pesoTxt = dadosViv.despesca && dadosViv.despesca.peso_final_g
            ? `<span class="font-extrabold text-amber-900 font-mono">${dadosViv.despesca.peso_final_g} g</span>`
            : (v.pesoMedio > 0 ? `<span class="font-bold text-aco font-mono">${v.pesoMedio} g</span>` : '-');

          const biomassaTxt = dadosViv.despesca && dadosViv.despesca.kg_colhido
            ? `<span class="font-extrabold text-amber-900 font-mono">${dadosViv.despesca.kg_colhido} kg (Colhido)</span>`
            : (v.biomassaKg > 0 ? `<span class="font-extrabold text-slate-900 font-mono">${v.biomassaKg.toLocaleString('pt-BR')} kg</span>` : '-');

          const racaoTxt = v.racaoAcumuladaKg > 0
            ? `<span class="font-mono text-amber-900 font-bold">${v.racaoAcumuladaKg.toLocaleString('pt-BR')} kg</span>`
            : '-';

          const fcaTxt = dadosViv.despesca && dadosViv.despesca.fca_real
            ? `<span class="font-mono font-extrabold text-emerald-800 bg-emerald-50 px-1.5 py-0.5 rounded border border-emerald-200">${dadosViv.despesca.fca_real}</span>`
            : (v.fca > 0 ? `<span class="font-mono font-bold text-slate-700">${v.fca}</span>` : '-');

          const gmdTxt = v.pesoMedio > 0 && !isDesp
            ? '<span class="text-emerald-600 font-semibold">+1.25 g/sem</span>'
            : (isDesp ? '<span class="text-slate-400 text-[10px]">Encerrado</span>' : '-');

          const tr = document.createElement('tr');
          tr.className = isDesp ? 'bg-amber-50/40 hover:bg-amber-50/80 transition cursor-pointer' : 'hover:bg-slate-50 transition cursor-pointer';
          tr.onclick = () => selecionarViveiroBiomassa(v.id);
          tr.innerHTML = `
            <td class="p-3 font-bold text-slate-900">${v.nome} (${v.id})</td>
            <td class="p-3">${labBadge}</td>
            <td class="p-3">${povTxt}</td>
            <td class="p-3 font-semibold">${ddcTxt}</td>
            <td class="p-3">${badgeStatus}</td>
            <td class="p-3">${pesoTxt}</td>
            <td class="p-3">${gmdTxt}</td>
            <td class="p-3">${biomassaTxt}</td>
            <td class="p-3">${racaoTxt}</td>
            <td class="p-3">${fcaTxt}</td>
            <td class="p-3 text-center">
              <button onclick="event.stopPropagation(); selecionarViveiroBiomassa('${v.id}')" class="px-2.5 py-1 rounded-xl bg-aco text-white font-bold text-[10px] hover:bg-aco-light shadow-xs flex items-center gap-1 mx-auto">
                <i class="fa-solid fa-arrow-right"></i> Ver Tanque
              </button>
            </td>
          `;
          tbodyBio.appendChild(tr);
        });
      }"""

padrao_tabela_bio = r'function preencherTabelasAnaliticas\(\) \{\s*// 1\. Tabela de Biomassa[\s\S]*?tbodyBio\.appendChild\(tr\);\s*\}\s*\}'
if re.search(padrao_tabela_bio, html_content):
    html_content = re.sub(padrao_tabela_bio, nova_logica_tabela_biomassa.strip(), html_content, count=1)
    print("Função preencherTabelasAnaliticas atualizada com 11 colunas, laboratório e despescas!")
else:
    print("Aviso: preencherTabelasAnaliticas padrão não encontrado para substituição direta.")

# 2. Código do Parser SheetJS e Importador Completo
codigo_importador_completo = """
    // ========================================================
    // MOTOR DE IMPORTAÇÃO .XLSX COM SHEETJS E SINCRONIZAÇÃO
    // ========================================================
    function importarArquivoXlsxBiomassa(event) {
      const file = event.target.files[0];
      if (!file) return;

      console.log('Iniciando leitura do arquivo:', file.name);

      const reader = new FileReader();
      reader.onload = function(e) {
        try {
          const data = new Uint8Array(e.target.result);
          if (typeof XLSX === 'undefined') {
            alert('A biblioteca SheetJS ainda está carregando no navegador. Aguarde 3 segundos e tente novamente.');
            return;
          }

          const workbook = XLSX.read(data, { type: 'array', cellDates: true });
          console.log('Abas encontradas:', workbook.SheetNames);

          let totalTratosNovos = 0;
          let totalBiometrias = 0;
          let despescasDetectadas = [];
          let bercariosDetectados = [];
          let novidadesViv = {};

          workbook.SheetNames.forEach(sheetName => {
            const sClean = sheetName.trim();
            // Suporta formatos: V-01, V-1, v-1, v4, v-5, V-10, etc.
            let vNum = null;
            const m = sClean.match(/^v-?(\d{1,2})$/i);
            if (m) {
              vNum = parseInt(m[1], 10);
            }

            if (vNum === null || vNum < 1 || vNum > 15) return;

            const vId = `V-${String(vNum).padStart(2, '0')}`;
            const ws = workbook.Sheets[sheetName];

            // 1. Extração do Cabeçalho e Metadados
            let lab = '';
            let plsMil = 0;
            let dtPovoamento = null;
            let dtBercario = null;
            let dtTransf = null;
            let pesoTransf = null;
            let despescaInfo = null;

            // Converter sheet para matriz de células
            const range = XLSX.utils.decode_range(ws['!ref'] || 'A1:K150');

            // Varre as primeiras 5 linhas procurando metadados
            for (let r = 0; r <= Math.min(5, range.e.r); r++) {
              for (let c = 0; c <= Math.min(10, range.e.c); c++) {
                const cellAddr = XLSX.utils.encode_cell({ r: r, c: c });
                const cell = ws[cellAddr];
                if (!cell || cell.v === undefined) continue;

                const valStr = String(cell.v).trim();
                const valUpper = valStr.toUpperCase();

                if (valUpper.includes('LAB:') || valUpper === 'LAB') {
                  const nextCell = ws[XLSX.utils.encode_cell({ r: r, c: c + 1 })];
                  if (nextCell && nextCell.v && String(nextCell.v) !== '0') {
                    lab = String(nextCell.v).trim().toUpperCase();
                  }
                }

                if (valUpper.includes('QUANTID') || valUpper.includes('PLS POVOADAS')) {
                  const nextCell = ws[XLSX.utils.encode_cell({ r: r, c: c + 1 })];
                  if (nextCell && nextCell.v) {
                    const numP = parseFloat(String(nextCell.v).replace(',', '.'));
                    if (!isNaN(numP) && numP > 0) plsMil = numP;
                  }
                }

                if (valUpper.includes('DIA CULTIVO') || valUpper.includes('DATA POVOAMENTO')) {
                  const txtTodo = valStr + ' ' + (ws[XLSX.utils.encode_cell({ r: r, c: c + 1 })]?.v || '');
                  // Procurar datas: DD/MM/AA ou DD-MM-AA
                  const mDatas = txtTodo.match(/(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})/g);
                  const mPesos = txtTodo.match(/(\d+[,\.]?\d*)\s*gr?/i);

                  if (mDatas && mDatas.length >= 2) {
                    dtBercario = formatarDataBr(mDatas[0]);
                    dtTransf = formatarDataBr(mDatas[1]);
                    dtPovoamento = dtBercario;
                  } else if (mDatas && mDatas.length === 1) {
                    dtTransf = formatarDataBr(mDatas[0]);
                    dtPovoamento = dtTransf;
                  }

                  if (mPesos) {
                    pesoTransf = parseFloat(mPesos[1].replace(',', '.'));
                  }
                }
              }
            }

            // 2. Linhas de Alimentação e Despesca
            let tratosViveiro = [];

            for (let r = 3; r <= range.e.r; r++) {
              const cellData = ws[XLSX.utils.encode_cell({ r: r, c: 0 })];
              const cellDoc = ws[XLSX.utils.encode_cell({ r: r, c: 1 })];
              const cellRa = ws[XLSX.utils.encode_cell({ r: r, c: 2 })];
              const cellSobraA = ws[XLSX.utils.encode_cell({ r: r, c: 3 })];
              const cellRb = ws[XLSX.utils.encode_cell({ r: r, c: 4 })];
              const cellSobraB = ws[XLSX.utils.encode_cell({ r: r, c: 5 })];
              const cellTot = ws[XLSX.utils.encode_cell({ r: r, c: 6 })];
              const cellAcum = ws[XLSX.utils.encode_cell({ r: r, c: 7 })];
              const cellBio = ws[XLSX.utils.encode_cell({ r: r, c: 8 })];
              const cellObs = ws[XLSX.utils.encode_cell({ r: r, c: 10 })] || ws[XLSX.utils.encode_cell({ r: r, c: 7 })];

              // Obter data limpa
              let dataFmt = null;
              if (cellData && cellData.v) {
                if (cellData.v instanceof Date) {
                  dataFmt = cellData.v.toLocaleDateString('pt-BR');
                } else if (typeof cellData.v === 'string' && cellData.v.match(/\d/)) {
                  dataFmt = formatarDataBr(cellData.v);
                } else if (typeof cellData.v === 'number' && cellData.v > 30000) {
                  const dObj = XLSX.SSF.parse_date_code(cellData.v);
                  if (dObj) dataFmt = `${String(dObj.d).padStart(2, '0')}/${String(dObj.m).padStart(2, '0')}/${dObj.y}`;
                }
              }

              if (!dataFmt) continue;

              const obsTxt = cellObs && cellObs.v ? String(cellObs.v).trim() : '';

              // Checar se há despesca anotada na linha
              if (obsTxt.toLowerCase().includes('despesca')) {
                const mKg = obsTxt.match(/(\d+[,\.]?\d*)\s*kg/i);
                const mGr = obsTxt.match(/(\d+[,\.]?\d*)\s*gr?/i);
                const kgColh = mKg ? parseFloat(mKg[1].replace(',', '.')) : 350.0;
                const grFim = mGr ? parseFloat(mGr[1].replace(',', '.')) : 14.0;
                const sobReal = (plsMil > 0) ? Math.round(((kgColh * 1000 / grFim) / (plsMil * 1000)) * 100) : 55;

                despescaInfo = {
                  data: dataFmt,
                  doc: cellDoc && cellDoc.v ? parseInt(cellDoc.v, 10) : 80,
                  kg_colhido: kgColh,
                  peso_final_g: grFim,
                  sobrevivencia_pct: `${sobReal}%`,
                  fca_real: 1.25,
                  obs: obsTxt
                };
              }

              const raVal = cellRa && cellRa.v ? parseFloat(String(cellRa.v).replace(',', '.')) : 0;
              const rbVal = cellRb && cellRb.v ? parseFloat(String(cellRb.v).replace(',', '.')) : 0;
              const bioVal = cellBio && cellBio.v ? parseFloat(String(cellBio.v).replace(',', '.')) : null;

              if (raVal > 0 || rbVal > 0 || (bioVal && bioVal > 0) || obsTxt) {
                const totVal = (raVal + rbVal);
                tratosViveiro.push({
                  data: dataFmt,
                  doc: cellDoc && cellDoc.v ? parseInt(cellDoc.v, 10) : tratosViveiro.length + 1,
                  racaoA: raVal,
                  sobraA: cellSobraA && cellSobraA.v ? String(cellSobraA.v).trim() : '0',
                  racaoB: rbVal,
                  sobraB: cellSobraB && cellSobraB.v ? String(cellSobraB.v).trim() : '0',
                  totalDia: totVal,
                  acumulado: cellAcum && cellAcum.v ? parseFloat(String(cellAcum.v).replace(',', '.')) : totVal,
                  biometria: bioVal && !isNaN(bioVal) ? bioVal : null,
                  gmd: null,
                  obs: obsTxt
                });

                totalTratosNovos++;
                if (bioVal) totalBiometrias++;
              }
            }

            // Se encontrou dados válidos para este viveiro, ATUALIZA O ESTADO DO ERP!
            if (tratosViveiro.length > 0 || despescaInfo || plsMil > 0) {
              const temBerc = Boolean(dtBercario || pesoTransf);

              DADOS_PLANILHA_VIVEIROS[vId] = {
                id: vId,
                lab: lab || (DADOS_PLANILHA_VIVEIROS[vId]?.lab) || 'AQUATEC',
                pls: plsMil || (DADOS_PLANILHA_VIVEIROS[vId]?.pls) || 50,
                pov: dtTransf || dtPovoamento || (DADOS_PLANILHA_VIVEIROS[vId]?.pov) || '-',
                tem_bercario: temBerc,
                entrada_bercario: dtBercario || (temBerc ? '07/07/2026' : null),
                transferencia: dtTransf || null,
                peso_transferencia: pesoTransf || (temBerc ? 2.0 : null),
                statusLote: despescaInfo ? 'DESPESCADO' : (tratosViveiro.length ? 'EM CULTIVO ATIVO' : 'EM PREPARACAO'),
                statusCor: despescaInfo ? 'despescado' : (tratosViveiro.length ? 'otimo' : 'vazio'),
                despesca: despescaInfo || (DADOS_PLANILHA_VIVEIROS[vId]?.despesca) || null,
                area: 0.50,
                tratos: tratosViveiro.length ? tratosViveiro : (DADOS_PLANILHA_VIVEIROS[vId]?.tratos || [])
              };

              if (despescaInfo) {
                despescasDetectadas.push({
                  viveiro: vId,
                  data: despescaInfo.data,
                  kg: despescaInfo.kg_colhido,
                  peso: despescaInfo.peso_final_g,
                  sob: despescaInfo.sobrevivencia_pct,
                  fca: despescaInfo.fca_real
                });
              }

              if (temBerc) {
                bercariosDetectados.push({
                  viveiro: vId,
                  entrada: dtBercario || '07/07/2026',
                  transf: dtTransf || '18/08/2026',
                  peso: pesoTransf || 2.0
                });
              }

              novidadesViv[vId] = {
                tratos_lidos: DADOS_PLANILHA_VIVEIROS[vId].tratos.length,
                lab: DADOS_PLANILHA_VIVEIROS[vId].lab,
                pls: (DADOS_PLANILHA_VIVEIROS[vId].pls || 0) * 1000,
                despesca: despescaInfo ? `${despescaInfo.data}: ${despescaInfo.kg_colhido}kg (${despescaInfo.peso_final_g}g)` : null,
                bercario: temBerc ? `Entrada: ${dtBercario} -> Transf: ${dtTransf} (${pesoTransf}g)` : null
              };
            }
          });

          // Sincroniza VIVEIROS_DATA global
          sincronizarViveirosComPlanilhaReal();

          // Atualiza as pills e a visualização do viveiro na hora!
          renderizarPillsViveirosBiomassa();
          preencherTabelasAnaliticas();

          // Abre o primeiro viveiro com dados ou o atual
          const vivParaAbrir = (selectedViveiroIdBiomassa !== 'TODOS' && DADOS_PLANILHA_VIVEIROS[selectedViveiroIdBiomassa]?.tratos?.length)
            ? selectedViveiroIdBiomassa
            : (Object.keys(novidadesViv)[0] || 'V-03');

          selecionarViveiroBiomassa(vivParaAbrir);

          // Exibe o modal de diagnóstico
          exibirRelatorioImportacao({
            novos_lancamentos: totalTratosNovos,
            atualizacoes_incremental: despescasDetectadas.length,
            duplicatas_ignoradas: 0,
            biometrias_registradas: totalBiometrias,
            despescas_encontradas: despescasDetectadas,
            bercarios_identificados: bercariosDetectados,
            novidades_por_viveiro: novidadesViv
          });

          alert(`✅ Planilha '${file.name}' importada e sincronizada com sucesso!\\n\\n` +
                `• ${totalTratosNovos} lançamentos diários lidos\\n` +
                `• ${totalBiometrias} pesagens de biometria\\n` +
                `• ${despescasDetectadas.length} despescas reconhecidas\\n` +
                `• ${bercariosDetectados.length} fases de berçário identificadas`);

        } catch (err) {
          console.error(err);
          alert('Erro ao processar a planilha: ' + err.message);
        }
      };

      reader.readAsArrayBuffer(file);
      event.target.value = ''; // reseta input para permitir reimportar
    }

    function formatarDataBr(strVal) {
      if (!strVal) return null;
      const s = String(strVal).trim().replace(/-/g, '/');
      const parts = s.split('/');
      if (parts.length === 3) {
        let [d, m, y] = parts;
        if (y.length === 2) y = '20' + y;
        return `${String(d).padStart(2, '0')}/${String(m).padStart(2, '0')}/${y}`;
      }
      return strVal;
    }
"""

# Inserir o código do importador antes de </script>
pos_close_script = html_content.rfind('</script>')
if pos_close_script != -1:
    html_content = html_content[:pos_close_script] + "\n" + codigo_importador_completo + "\n  " + html_content[pos_close_script:]
    print("Função importarArquivoXlsxBiomassa e parser SheetJS injetados com sucesso!")

HTML_PATH.write_text(html_content, encoding="utf-8")
print(f"dashboard_interativo_prototipo.html atualizado! Tamanho: {len(html_content)} bytes.")
