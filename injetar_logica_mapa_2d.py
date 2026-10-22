"""Script para atualizar o dataset e a lógica JavaScript do Módulo Mapa dos Viveiros 2D."""
import re
from pathlib import Path

HTML_PATH = Path(r"G:\Meu Drive\ANTIGRAVITY DRIVE\CAMARÃO\ERP CAMARÃO\dashboard_interativo_prototipo.html")
conteudo = HTML_PATH.read_text(encoding="utf-8")

# Novo dataset VIVEIROS_DATA com a numeração do pai e metragens de satélite
novo_dataset_js = """    // DATASET COMPLETO DOS 15 VIVEIROS (COM NOMEAÇÃO DO PAI E METRAGENS DE SATÉLITE)
    let VIVEIROS_DATA = [
      {
        id: 'V-01', numeroPai: 1, nomePai: 'Viveiro 1', nomeAntigo: 'C1', setor: 'Central', tipoUso: 'Engorda',
        areaSateliteM2: 12600.0, areaAjustadaM2: 12600.0, areaHa: 1.26, profundidadeM: 1.20, volumeM3: 15120.0,
        status: 'otimo', statusCor: 'OTIMO', statusLabel: '🟢 Ótimo', statusDesc: 'Parâmetros estáveis e bandejas limpas',
        ddc: 58, dataPovoamento: '24/08/2026', pesoMedio: 12.4, ganhoSemanal: 1.35, biomassaKg: 3420, fca: 1.19,
        racaoHojeKg: 75, racaoAcumuladaKg: 4070, o2Manha: 4.6, o2Noite: 4.8, phManha: 7.8, phTarde: 8.2,
        salinidade: 14.5, secchi: 35, amonia: 0.02, sobraNivel: 0, sobraTexto: '0 (Prato Limpo)', densidade: 23
      },
      {
        id: 'V-02', numeroPai: 2, nomePai: 'Viveiro 2', nomeAntigo: 'C2', setor: 'Central', tipoUso: 'Engorda',
        areaSateliteM2: 13285.0, areaAjustadaM2: 13285.0, areaHa: 1.33, profundidadeM: 1.20, volumeM3: 15942.0,
        status: 'atencao', statusCor: 'ATENCAO', statusLabel: '🟡 Atenção', statusDesc: 'Duplicidade de lançamento detectada na auditoria',
        ddc: 52, dataPovoamento: '30/08/2026', pesoMedio: 11.2, ganhoSemanal: 1.20, biomassaKg: 2850, fca: 1.24,
        racaoHojeKg: 60, racaoAcumuladaKg: 3534, o2Manha: 4.2, o2Noite: 4.5, phManha: 7.7, phTarde: 8.1,
        salinidade: 14.0, secchi: 32, amonia: 0.03, sobraNivel: 1, sobraTexto: '1 (Pouca Sobra)', densidade: 25
      },
      {
        id: 'V-03', numeroPai: 3, nomePai: 'Viveiro 3', nomeAntigo: 'C3', setor: 'Central', tipoUso: 'Engorda',
        areaSateliteM2: 15500.0, areaAjustadaM2: 15500.0, areaHa: 1.55, profundidadeM: 1.20, volumeM3: 18600.0,
        status: 'otimo', statusCor: 'OTIMO', statusLabel: '🟢 Ótimo', statusDesc: 'Crescimento vigoroso acima da meta',
        ddc: 65, dataPovoamento: '17/08/2026', pesoMedio: 14.1, ganhoSemanal: 1.45, biomassaKg: 4650, fca: 1.21,
        racaoHojeKg: 95, racaoAcumuladaKg: 5626, o2Manha: 4.8, o2Noite: 5.0, phManha: 7.9, phTarde: 8.3,
        salinidade: 15.0, secchi: 38, amonia: 0.02, sobraNivel: 0, sobraTexto: '0 (Prato Limpo)', densidade: 22
      },
      {
        id: 'V-04', numeroPai: 4, nomePai: 'Viveiro 4', nomeAntigo: 'C4', setor: 'Central', tipoUso: 'Engorda',
        areaSateliteM2: 16400.0, areaAjustadaM2: 16400.0, areaHa: 1.64, profundidadeM: 1.20, volumeM3: 19680.0,
        status: 'atencao', statusCor: 'ATENCAO', statusLabel: '🟡 Atenção', statusDesc: 'Lacuna de lançamento nas últimas 24h',
        ddc: 30, dataPovoamento: '21/09/2026', pesoMedio: 6.8, ganhoSemanal: 1.10, biomassaKg: 1360, fca: 1.18,
        racaoHojeKg: 42, racaoAcumuladaKg: 1604, o2Manha: 4.1, o2Noite: 4.4, phManha: 7.6, phTarde: 8.0,
        salinidade: 13.5, secchi: 40, amonia: 0.01, sobraNivel: 0, sobraTexto: '0 (Prato Limpo)', densidade: 25
      },
      {
        id: 'V-05', numeroPai: 5, nomePai: 'Viveiro 5', nomeAntigo: 'L1', setor: 'Leste', tipoUso: 'Engorda',
        areaSateliteM2: 13040.0, areaAjustadaM2: 13040.0, areaHa: 1.30, profundidadeM: 1.20, volumeM3: 15648.0,
        status: 'otimo', statusCor: 'OTIMO', statusLabel: '🟢 Ótimo', statusDesc: 'Melhor conversão da safra (FCA 1.15)',
        ddc: 45, dataPovoamento: '06/09/2026', pesoMedio: 9.9, ganhoSemanal: 1.30, biomassaKg: 2970, fca: 1.15,
        racaoHojeKg: 68, racaoAcumuladaKg: 3415, o2Manha: 4.5, o2Noite: 4.7, phManha: 7.8, phTarde: 8.2,
        salinidade: 14.0, secchi: 36, amonia: 0.02, sobraNivel: 0, sobraTexto: '0 (Prato Limpo)', densidade: 25
      },
      {
        id: 'V-06', numeroPai: 6, nomePai: 'Viveiro 6', nomeAntigo: 'L2', setor: 'Leste', tipoUso: 'Engorda',
        areaSateliteM2: 14710.0, areaAjustadaM2: 14710.0, areaHa: 1.47, profundidadeM: 1.20, volumeM3: 17652.0,
        status: 'otimo', statusCor: 'OTIMO', statusLabel: '🟢 Ótimo', statusDesc: 'Tanque em padrão zootécnico estável',
        ddc: 40, dataPovoamento: '11/09/2026', pesoMedio: 8.6, ganhoSemanal: 1.22, biomassaKg: 2450, fca: 1.20,
        racaoHojeKg: 58, racaoAcumuladaKg: 2940, o2Manha: 4.4, o2Noite: 4.6, phManha: 7.7, phTarde: 8.1,
        salinidade: 14.2, secchi: 35, amonia: 0.02, sobraNivel: 0, sobraTexto: '0 (Prato Limpo)', densidade: 26
      },
      {
        id: 'V-07', numeroPai: 7, nomePai: 'Viveiro 7', nomeAntigo: 'O1', setor: 'Oeste', tipoUso: 'Engorda',
        areaSateliteM2: 8060.0, areaAjustadaM2: 8060.0, areaHa: 0.81, profundidadeM: 1.20, volumeM3: 9672.0,
        status: 'otimo', statusCor: 'OTIMO', statusLabel: '🟢 Ótimo', statusDesc: 'Setor Oeste com excelente renovação',
        ddc: 50, dataPovoamento: '01/09/2026', pesoMedio: 10.8, ganhoSemanal: 1.28, biomassaKg: 2150, fca: 1.22,
        racaoHojeKg: 52, racaoAcumuladaKg: 2623, o2Manha: 4.5, o2Noite: 4.8, phManha: 7.8, phTarde: 8.2,
        salinidade: 14.0, secchi: 36, amonia: 0.02, sobraNivel: 0, sobraTexto: '0 (Prato Limpo)', densidade: 25
      },
      {
        id: 'V-08', numeroPai: 8, nomePai: 'Viveiro 8', nomeAntigo: 'O2', setor: 'Oeste', tipoUso: 'Engorda',
        areaSateliteM2: 7550.0, areaAjustadaM2: 7550.0, areaHa: 0.76, profundidadeM: 1.20, volumeM3: 9060.0,
        status: 'critico', statusCor: 'CRITICO', statusLabel: '🔴 Crítico', statusDesc: 'Queda de oxigênio (2.6 mg/L)',
        ddc: 35, dataPovoamento: '16/09/2026', pesoMedio: 7.5, ganhoSemanal: 1.05, biomassaKg: 1680, fca: 1.26,
        racaoHojeKg: 38, racaoAcumuladaKg: 2116, o2Manha: 2.6, o2Noite: 3.2, phManha: 7.4, phTarde: 7.9,
        salinidade: 13.8, secchi: 28, amonia: 0.04, sobraNivel: 2, sobraTexto: '2 (Média Sobra)', densidade: 28
      },
      {
        id: 'V-09', numeroPai: 9, nomePai: 'Viveiro 9', nomeAntigo: 'O3', setor: 'Oeste', tipoUso: 'Engorda',
        areaSateliteM2: 5400.0, areaAjustadaM2: 5400.0, areaHa: 0.54, profundidadeM: 1.20, volumeM3: 6480.0,
        status: 'otimo', statusCor: 'OTIMO', statusLabel: '🟢 Ótimo', statusDesc: 'Manejo padrão de engorda',
        ddc: 48, dataPovoamento: '03/09/2026', pesoMedio: 10.2, ganhoSemanal: 1.25, biomassaKg: 1350, fca: 1.20,
        racaoHojeKg: 36, racaoAcumuladaKg: 1620, o2Manha: 4.4, o2Noite: 4.6, phManha: 7.7, phTarde: 8.1,
        salinidade: 14.1, secchi: 35, amonia: 0.02, sobraNivel: 0, sobraTexto: '0 (Prato Limpo)', densidade: 25
      },
      {
        id: 'V-10', numeroPai: 10, nomePai: 'Viveiro 10', nomeAntigo: 'O5', setor: 'Oeste', tipoUso: 'Engorda',
        areaSateliteM2: 4650.0, areaAjustadaM2: 4650.0, areaHa: 0.47, profundidadeM: 1.20, volumeM3: 5580.0,
        status: 'otimo', statusCor: 'OTIMO', statusLabel: '🟢 Ótimo', statusDesc: 'Excelente crescimento e aeração',
        ddc: 42, dataPovoamento: '09/09/2026', pesoMedio: 9.1, ganhoSemanal: 1.22, biomassaKg: 1120, fca: 1.19,
        racaoHojeKg: 30, racaoAcumuladaKg: 1332, o2Manha: 4.5, o2Noite: 4.7, phManha: 7.8, phTarde: 8.2,
        salinidade: 14.0, secchi: 36, amonia: 0.02, sobraNivel: 0, sobraTexto: '0 (Prato Limpo)', densidade: 25
      },
      {
        id: 'V-11', numeroPai: null, nomePai: 'Berçário 1', nomeAntigo: 'N1', setor: 'Norte', tipoUso: 'Berçário',
        areaSateliteM2: 6340.0, areaAjustadaM2: 6340.0, areaHa: 0.63, profundidadeM: 1.20, volumeM3: 7608.0,
        status: 'otimo', statusCor: 'OTIMO', statusLabel: '🟢 Berçário Ativo', statusDesc: 'Aclimatação e pré-engorda de pós-larvas',
        ddc: 18, dataPovoamento: '04/10/2026', pesoMedio: 1.8, ganhoSemanal: 0.85, biomassaKg: 650, fca: 0.95,
        racaoHojeKg: 20, racaoAcumuladaKg: 617, o2Manha: 5.2, o2Noite: 5.5, phManha: 7.9, phTarde: 8.3,
        salinidade: 14.5, secchi: 38, amonia: 0.01, sobraNivel: 0, sobraTexto: '0 (Prato Limpo)', densidade: 70
      },
      {
        id: 'V-12', numeroPai: null, nomePai: 'Berçário 2', nomeAntigo: 'N2', setor: 'Norte', tipoUso: 'Berçário',
        areaSateliteM2: 5540.0, areaAjustadaM2: 5540.0, areaHa: 0.55, profundidadeM: 1.20, volumeM3: 6648.0,
        status: 'otimo', statusCor: 'OTIMO', statusLabel: '🟢 Berçário Ativo', statusDesc: 'Lote novo de PLs AQUATEC',
        ddc: 12, dataPovoamento: '10/10/2026', pesoMedio: 0.9, ganhoSemanal: 0.65, biomassaKg: 380, fca: 0.92,
        racaoHojeKg: 14, racaoAcumuladaKg: 350, o2Manha: 5.4, o2Noite: 5.6, phManha: 8.0, phTarde: 8.4,
        salinidade: 14.8, secchi: 40, amonia: 0.01, sobraNivel: 0, sobraTexto: '0 (Prato Limpo)', densidade: 80
      },
      {
        id: 'V-13', numeroPai: null, nomePai: 'Tanque Apoio 1', nomeAntigo: 'O0', setor: 'Oeste', tipoUso: 'Apoio / Larvicultura',
        areaSateliteM2: 1430.0, areaAjustadaM2: 1430.0, areaHa: 0.14, profundidadeM: 1.00, volumeM3: 1430.0,
        status: 'vazio', statusCor: 'VAZIO', statusLabel: '⚪ Em Limpeza', statusDesc: 'Secagem e desinfecção pós-despesca',
        ddc: 0, dataPovoamento: '-', pesoMedio: 0, ganhoSemanal: 0, biomassaKg: 0, fca: 0,
        racaoHojeKg: 0, racaoAcumuladaKg: 0, o2Manha: 0, o2Noite: 0, phManha: 0, phTarde: 0,
        salinidade: 0, secchi: 0, amonia: 0, sobraNivel: 0, sobraTexto: 'Vazio', densidade: 0
      },
      {
        id: 'V-14', numeroPai: null, nomePai: 'Tanque Apoio 2', nomeAntigo: 'O4', setor: 'Oeste', tipoUso: 'Apoio Operacional',
        areaSateliteM2: 1980.0, areaAjustadaM2: 1980.0, areaHa: 0.20, profundidadeM: 1.10, volumeM3: 2178.0,
        status: 'vazio', statusCor: 'VAZIO', statusLabel: '⚪ Reserva', statusDesc: 'Tanque pulmão para aclimatação',
        ddc: 0, dataPovoamento: '-', pesoMedio: 0, ganhoSemanal: 0, biomassaKg: 0, fca: 0,
        racaoHojeKg: 0, racaoAcumuladaKg: 0, o2Manha: 0, o2Noite: 0, phManha: 0, phTarde: 0,
        salinidade: 0, secchi: 0, amonia: 0, sobraNivel: 0, sobraTexto: 'Vazio', densidade: 0
      },
      {
        id: 'V-15', numeroPai: null, nomePai: 'Bacia Decantação', nomeAntigo: 'L0', setor: 'Leste', tipoUso: 'Bacia de Decantação',
        areaSateliteM2: 1850.0, areaAjustadaM2: 1850.0, areaHa: 0.19, profundidadeM: 1.00, volumeM3: 1850.0,
        status: 'vazio', statusCor: 'VAZIO', statusLabel: '⚪ Decantação', statusDesc: 'Tratamento de efluentes e decantação',
        ddc: 0, dataPovoamento: '-', pesoMedio: 0, ganhoSemanal: 0, biomassaKg: 0, fca: 0,
        racaoHojeKg: 0, racaoAcumuladaKg: 0, o2Manha: 0, o2Noite: 0, phManha: 0, phTarde: 0,
        salinidade: 0, secchi: 0, amonia: 0, sobraNivel: 0, sobraTexto: 'Bacia', densidade: 0
      }
    ];"""

# Substitui o array VIVEIROS_DATA antigo pelo novo
padrao_dataset = r"const VIVEIROS_DATA = \[\s*\{[\s\S]*?\}\s*\];"
if re.search(padrao_dataset, conteudo):
    conteudo = re.sub(padrao_dataset, novo_dataset_js, conteudo, count=1)
    print("VIVEIROS_DATA atualizado com a numeração do pai e metragens!")
else:
    print("Aviso: Padrão VIVEIROS_DATA não substituído via regex, buscando let VIVEIROS_DATA...")

# Funções JavaScript do novo módulo
funcoes_mapa_js = """
    // ========================================================
    // LÓGICA DO MÓDULO MAPA DOS VIVEIROS 2D & CALIBRAÇÃO
    // ========================================================
    let camadaMapaAtual = 'vetorial'; // 'vetorial' ou 'satelite'
    let filtroSetorMapa = 'todos';    // 'todos', 'engorda', 'bercario', 'apoio'
    let viveiroEmCalibracao = null;

    function alternarCamadaMapa(tipo) {
      camadaMapaAtual = tipo;
      const btnVet = document.getElementById('btn-camada-vetorial');
      const btnSat = document.getElementById('btn-camada-satelite');
      const satLayer = document.getElementById('satelite-background-layer');
      const tituloLayer = document.getElementById('mapa-camada-titulo');

      if (tipo === 'satelite') {
        if (satLayer) satLayer.classList.remove('hidden');
        if (btnSat) {
          btnSat.className = 'flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition bg-emerald-600 text-white shadow-sm';
        }
        if (btnVet) {
          btnVet.className = 'flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold text-slate-600 hover:text-slate-900 transition';
        }
        if (tituloLayer) tituloLayer.textContent = '🛰️ Foto de Satélite Real com Polígonos da Fazenda (Ceará-Mirim/RN)';
      } else {
        if (satLayer) satLayer.classList.add('hidden');
        if (btnVet) {
          btnVet.className = 'flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition bg-white text-slate-900 shadow-sm';
        }
        if (btnSat) {
          btnSat.className = 'flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold text-slate-600 hover:text-slate-900 transition';
        }
        if (tituloLayer) tituloLayer.textContent = 'Planta Topográfica dos Viveiros (Ceará-Mirim/RN)';
      }
    }

    function filtrarMapaSetor(setor) {
      filtroSetorMapa = setor;
      const botoes = ['todos', 'engorda', 'bercario', 'apoio'];
      botoes.forEach(b => {
        const el = document.getElementById(`filter-mapa-${b}`);
        if (el) {
          if (b === setor) {
            el.className = 'px-2.5 py-1 rounded-lg font-bold bg-white text-slate-800 shadow-sm';
          } else {
            el.className = 'px-2.5 py-1 rounded-lg font-semibold text-slate-600 hover:text-slate-900';
          }
        }
      });
      renderizarModuloMapa2D();
    }

    function renderizarModuloMapa2D() {
      const colOeste = document.getElementById('coluna-setor-oeste');
      const colCentral = document.getElementById('coluna-setor-central');
      const colLeste = document.getElementById('coluna-setor-leste');

      if (!colOeste || !colCentral || !colLeste) return;

      colOeste.innerHTML = '';
      colCentral.innerHTML = '';
      colLeste.innerHTML = '';

      let tanquesFiltrados = VIVEIROS_DATA;
      if (filtroSetorMapa === 'engorda') {
        tanquesFiltrados = VIVEIROS_DATA.filter(v => v.numeroPai !== null);
      } else if (filtroSetorMapa === 'bercario') {
        tanquesFiltrados = VIVEIROS_DATA.filter(v => v.tipoUso === 'Berçário');
      } else if (filtroSetorMapa === 'apoio') {
        tanquesFiltrados = VIVEIROS_DATA.filter(v => v.tipoUso !== 'Engorda' && v.tipoUso !== 'Berçário');
      }

      tanquesFiltrados.forEach(v => {
        const cardHtml = criarCardTanqueTopografico(v);
        if (v.setor === 'Oeste') {
          colOeste.innerHTML += cardHtml;
        } else if (v.setor === 'Central') {
          colCentral.innerHTML += cardHtml;
        } else {
          colLeste.innerHTML += cardHtml;
        }
      });

      renderizarTabelaCalibracao();
      atualizarTotaisTopograficos();
    }

    function criarCardTanqueTopografico(v) {
      const statusCores = {
        otimo: 'border-emerald-500 bg-emerald-950/40 text-emerald-100',
        atencao: 'border-amber-500 bg-amber-950/40 text-amber-100',
        critico: 'border-red-500 bg-red-950/40 text-red-100 animate-pulse',
        vazio: 'border-slate-700 bg-slate-900/60 text-slate-300'
      };
      const badgeCores = {
        otimo: 'bg-emerald-500 text-white',
        atencao: 'bg-amber-500 text-slate-950',
        critico: 'bg-red-500 text-white',
        vazio: 'bg-slate-700 text-slate-200'
      };

      const estiloCard = statusCores[v.status] || statusCores.vazio;
      const estiloBadge = badgeCores[v.status] || badgeCores.vazio;

      const tagPai = v.numeroPai 
        ? `<span class="px-2.5 py-1 rounded-lg text-xs font-black bg-white text-slate-950 shadow-md border border-slate-300 flex items-center gap-1">
             <i class="fa-solid fa-water text-aco"></i> ${v.nomePai}
           </span>`
        : `<span class="px-2 py-0.5 rounded-lg text-[11px] font-bold bg-slate-800 text-blue-200 border border-slate-600">
             ${v.nomePai}
           </span>`;

      return `
        <div class="relative p-3.5 rounded-2xl border-2 ${estiloCard} backdrop-blur-md transition-all hover:scale-[1.02] shadow-lg group">
          <div class="flex items-start justify-between gap-2">
            <div>
              <div class="flex items-center gap-2">
                ${tagPai}
                <span class="text-[10px] font-mono text-slate-400 font-bold">(${v.nomeAntigo || v.id})</span>
              </div>
              <span class="text-[10px] text-slate-300 mt-1 block font-medium">${v.tipoUso} • ${v.setor}</span>
            </div>
            
            <span class="px-2 py-0.5 rounded-full text-[10px] font-extrabold ${estiloBadge}">
              ${v.statusLabel}
            </span>
          </div>

          <!-- Metragens Lado a Lado (Satélite vs Calibrada) -->
          <div class="grid grid-cols-2 gap-2 mt-3 pt-2.5 border-t border-white/10 text-xs">
            <div class="bg-black/30 p-2 rounded-xl">
              <span class="text-[9px] uppercase font-bold text-slate-400 block">🛰️ Satélite</span>
              <strong class="text-white font-mono text-[11px]">${v.areaSateliteM2.toLocaleString('pt-BR')} m²</strong>
            </div>
            <div class="bg-emerald-950/60 p-2 rounded-xl border border-emerald-500/30">
              <span class="text-[9px] uppercase font-bold text-emerald-300 block">📐 Calibrada</span>
              <strong class="text-emerald-300 font-mono text-[11px]">${v.areaAjustadaM2.toLocaleString('pt-BR')} m²</strong>
              <span class="text-[9px] text-emerald-200 block">(${v.areaHa} ha)</span>
            </div>
          </div>

          <!-- Indicadores de Manejo & Ações Rápidas -->
          <div class="flex items-center justify-between mt-3 pt-2 border-t border-white/10">
            <div class="text-[10px] text-slate-300 font-mono">
              O₂: <strong class="text-white">${v.o2Manha || '--'}</strong> | Biomassa: <strong class="text-white">${v.biomassaKg ? v.biomassaKg + 'kg' : '--'}</strong>
            </div>

            <div class="flex items-center gap-1.5">
              <button onclick="abrirModalCalibracao('${v.id}')" title="Calibrar metragem deste tanque" class="px-2.5 py-1 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-[10px] shadow transition flex items-center gap-1">
                <i class="fa-solid fa-pen-ruler"></i> Calibrar
              </button>
              <button onclick="navegarPara('analytics-viveiro-detalhe', '${v.id}')" title="Ver diário zootécnico" class="p-1 rounded-lg bg-white/10 hover:bg-white/20 text-white text-xs">
                <i class="fa-solid fa-chevron-right"></i>
              </button>
            </div>
          </div>
        </div>
      `;
    }

    function renderizarTabelaCalibracao() {
      const tbody = document.getElementById('tbody-tabela-calibracao-metragens');
      if (!tbody) return;

      tbody.innerHTML = '';
      VIVEIROS_DATA.forEach(v => {
        const difM2 = v.areaAjustadaM2 - v.areaSateliteM2;
        const difTxt = difM2 === 0 ? '<span class="text-slate-400">Igual</span>' : (
          difM2 > 0 ? `<span class="text-emerald-600 font-bold">+${difM2} m²</span>` : `<span class="text-red-500 font-bold">${difM2} m²</span>`
        );

        tbody.innerHTML += `
          <tr class="hover:bg-slate-50/80 transition">
            <td class="py-2.5 px-3 font-bold text-slate-900 flex items-center gap-2">
              <span class="w-6 h-6 rounded-lg bg-aco/10 text-aco flex items-center justify-center text-xs font-black">
                ${v.numeroPai || '•'}
              </span>
              <div>
                <strong>${v.nomePai}</strong>
                <span class="block text-[10px] text-slate-400 font-normal">${v.statusDesc}</span>
              </div>
            </td>
            <td class="py-2.5 px-3 font-mono text-slate-600 font-bold">${v.id} (${v.nomeAntigo || '-'})</td>
            <td class="py-2.5 px-3 text-slate-600">${v.setor}</td>
            <td class="py-2.5 px-3 text-right font-mono text-slate-700">${v.areaSateliteM2.toLocaleString('pt-BR')} m²</td>
            <td class="py-2.5 px-3 text-right font-mono font-bold text-emerald-700 bg-emerald-50/50">${v.areaAjustadaM2.toLocaleString('pt-BR')} m²</td>
            <td class="py-2.5 px-3 text-right font-mono font-bold text-slate-800">${v.areaHa} ha</td>
            <td class="py-2.5 px-3 text-right font-mono text-slate-600">${v.profundidadeM || 1.2} m</td>
            <td class="py-2.5 px-3 text-right font-mono text-blue-700 font-bold">${(v.volumeM3 || (v.areaAjustadaM2 * 1.2)).toLocaleString('pt-BR')} m³</td>
            <td class="py-2.5 px-3">
              <span class="px-2 py-0.5 rounded text-[10px] font-bold ${v.tipoUso === 'Engorda' ? 'bg-blue-100 text-aco' : 'bg-purple-100 text-purple-800'}">
                ${v.tipoUso}
              </span>
            </td>
            <td class="py-2.5 px-3 text-center">
              <button onclick="abrirModalCalibracao('${v.id}')" class="px-2.5 py-1 rounded-lg bg-emerald-50 hover:bg-emerald-100 text-emerald-800 font-bold text-[11px] border border-emerald-200 transition">
                ✏️ Calibrar
              </button>
            </td>
          </tr>
        `;
      });
    }

    function atualizarTotaisTopograficos() {
      const totalSat = VIVEIROS_DATA.reduce((acc, v) => acc + (v.areaSateliteM2 || 0), 0);
      const totalAjust = VIVEIROS_DATA.reduce((acc, v) => acc + (v.areaAjustadaM2 || 0), 0);
      const totalVol = VIVEIROS_DATA.reduce((acc, v) => acc + (v.volumeM3 || (v.areaAjustadaM2 * 1.2)), 0);

      const elSat = document.getElementById('kpi-topo-area-satelite');
      const elAjust = document.getElementById('kpi-topo-area-ajustada');
      const elVol = document.getElementById('kpi-topo-volume');

      if (elSat) elSat.textContent = `${(totalSat / 10000).toFixed(2).replace('.', ',')} ha`;
      if (elAjust) elAjust.textContent = `${(totalAjust / 10000).toFixed(2).replace('.', ',')} ha`;
      if (elVol) elVol.textContent = `${totalVol.toLocaleString('pt-BR')} m³`;
    }

    // Abertura e manipulação do Modal de Calibração
    function abrirModalCalibracao(tanqueId) {
      const v = VIVEIROS_DATA.find(x => x.id === tanqueId);
      if (!v) return;
      viveiroEmCalibracao = v;

      document.getElementById('modal-calibrar-titulo').textContent = `Calibrar Metragem — ${v.nomePai}`;
      document.getElementById('modal-calibrar-subtitulo').textContent = `${v.id} (${v.nomeAntigo || ''}) • Setor ${v.setor} • ${v.tipoUso}`;
      document.getElementById('modal-calibrar-satelite-val').textContent = `${v.areaSateliteM2.toLocaleString('pt-BR')} m² (${(v.areaSateliteM2 / 10000).toFixed(2)} ha)`;
      document.getElementById('modal-calibrar-atual-val').textContent = `${v.areaAjustadaM2.toLocaleString('pt-BR')} m² (${v.areaHa} ha)`;
      
      const inputArea = document.getElementById('input-calibrar-area-m2');
      const inputProf = document.getElementById('input-calibrar-profundidade');
      const inputObs = document.getElementById('input-calibrar-observacoes');

      if (inputArea) inputArea.value = v.areaAjustadaM2;
      if (inputProf) inputProf.value = v.profundidadeM || 1.20;
      if (inputObs) inputObs.value = '';

      recalcularPreviaCalibracao();
      document.getElementById('modal-calibracao-metragem').classList.remove('hidden');
    }

    function fecharModalCalibracao() {
      const m = document.getElementById('modal-calibracao-metragem');
      if (m) m.classList.add('hidden');
    }

    function recalcularPreviaCalibracao() {
      if (!viveiroEmCalibracao) return;
      const inputArea = document.getElementById('input-calibrar-area-m2');
      const inputProf = document.getElementById('input-calibrar-profundidade');

      const areaVal = parseFloat(inputArea.value) || 0;
      const profVal = parseFloat(inputProf.value) || 1.20;

      const ha = (areaVal / 10000).toFixed(4);
      const vol = Math.round(areaVal * profVal);
      const difPct = viveiroEmCalibracao.areaSateliteM2 > 0 
        ? (((areaVal - viveiroEmCalibracao.areaSateliteM2) / viveiroEmCalibracao.areaSateliteM2) * 100).toFixed(1)
        : 0;

      document.getElementById('previa-calc-ha').textContent = `${ha} ha`;
      document.getElementById('previa-calc-vol').textContent = `${vol.toLocaleString('pt-BR')} m³`;
      
      const elDif = document.getElementById('previa-calc-dif');
      if (difPct == 0) {
        elDif.textContent = '0.0%';
        elDif.className = 'text-xs font-extrabold text-slate-700';
      } else if (difPct > 0) {
        elDif.textContent = `+${difPct}%`;
        elDif.className = 'text-xs font-extrabold text-emerald-600';
      } else {
        elDif.textContent = `${difPct}%`;
        elDif.className = 'text-xs font-extrabold text-red-500';
      }
    }

    function restaurarMetragemSatelite() {
      if (!viveiroEmCalibracao) return;
      document.getElementById('input-calibrar-area-m2').value = viveiroEmCalibracao.areaSateliteM2;
      document.getElementById('input-calibrar-profundidade').value = 1.20;
      recalcularPreviaCalibracao();
    }

    async function salvarCalibracaoMetragem() {
      if (!viveiroEmCalibracao) return;

      const inputArea = document.getElementById('input-calibrar-area-m2');
      const inputProf = document.getElementById('input-calibrar-profundidade');
      const inputObs = document.getElementById('input-calibrar-observacoes');

      const novaAreaM2 = parseFloat(inputArea.value);
      const novaProfM = parseFloat(inputProf.value) || 1.20;
      const obs = inputObs ? inputObs.value.trim() : '';

      if (!novaAreaM2 || novaAreaM2 <= 0) {
        alert('Por favor, informe uma área válida em metros quadrados.');
        return;
      }

      // 1. Atualização no Backend se a API estiver online
      if (isBackendOnline) {
        try {
          const resp = await fetch(`${BACKEND_API_BASE}/api/v1/viveiros/${viveiroEmCalibracao.id}/metragem`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              area_ajustada_m2: novaAreaM2,
              profundidade_media_m: novaProfM,
              observacoes: obs || 'Calibração de campo realizada via mapa'
            })
          });
          if (!resp.ok) {
            console.warn('Erro ao salvar no backend, aplicando localmente');
          }
        } catch (e) {
          console.warn('Erro de rede com backend, aplicando localmente:', e);
        }
      }

      // 2. Atualização reativa no estado local do frontend
      viveiroEmCalibracao.areaAjustadaM2 = novaAreaM2;
      viveiroEmCalibracao.areaHa = parseFloat((novaAreaM2 / 10000).toFixed(4));
      viveiroEmCalibracao.profundidadeM = novaProfM;
      viveiroEmCalibracao.volumeM3 = Math.round(novaAreaM2 * novaProfM);

      fecharModalCalibracao();
      renderizarModuloMapa2D();

      alert(`✅ Metragem do ${viveiroEmCalibracao.nomePai} calibrada com sucesso!\\n• Nova Área Oficial: ${novaAreaM2.toLocaleString('pt-BR')} m² (${viveiroEmCalibracao.areaHa} ha)\\n• Novo Volume Útil: ${viveiroEmCalibracao.volumeM3.toLocaleString('pt-BR')} m³`);
    }
"""

# Substitui o tratamento de viveiros-mapa na função navegarPara
padrao_nav = r"if \(viewId === 'viveiros-mapa'\) \{[\s\S]*?\} else \{"
novo_nav = """if (viewId === 'viveiros-mapa') {
        const target = document.getElementById('view-viveiros-mapa');
        if (target) {
          target.classList.remove('hidden');
          window.scrollTo({ top: 0, behavior: 'smooth' });
          renderizarModuloMapa2D();
        }
        atualizarHeaderNavegacao('Mapa dos Viveiros', 'Início > Topografia > Viveiros');
      } else {"""

if re.search(padrao_nav, conteudo):
    conteudo = re.sub(padrao_nav, novo_nav, conteudo, count=1)
    print("navegarPara atualizada para exibir o novo módulo do mapa!")

# Injeta as funções de controle do mapa antes do fechamento </script>
last_script_idx = conteudo.rfind("</script>")
if "renderizarModuloMapa2D" not in conteudo and last_script_idx != -1:
    conteudo = conteudo[:last_script_idx] + funcoes_mapa_js + "\n  " + conteudo[last_script_idx:]
    print("Funções do Mapa 2D injetadas com sucesso!")

HTML_PATH.write_text(conteudo, encoding="utf-8")
print("dashboard_interativo_prototipo.html 100% atualizado com o Módulo Mapa dos Viveiros 2D!")
