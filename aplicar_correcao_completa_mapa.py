"""
Script definitivo para corrigir e injetar o Módulo Mapa dos Viveiros 2D,
Foto de Satélite Real (Pai 1 a 10) e Dupla Metragem no dashboard_interativo_prototipo.html
"""
import re
import sys
from pathlib import Path

BASE_DIR = Path(r"G:\Meu Drive\ANTIGRAVITY DRIVE\CAMARÃO\ERP CAMARÃO")
HTML_PATH = BASE_DIR / "dashboard_interativo_prototipo.html"
B64_PATH = BASE_DIR / "assets" / "mapa_satelite_pai.b64.txt"

# 1. Carregar Base64 da imagem de satélite
if not B64_PATH.exists():
    raise FileNotFoundError(f"Arquivo Base64 não encontrado em {B64_PATH}")

b64_data = B64_PATH.read_text(encoding="utf-8").strip()
img_src = f"data:image/png;base64,{b64_data}"
print(f"Base64 carregado: {len(b64_data)} caracteres.")

html_content = HTML_PATH.read_text(encoding="utf-8")

# 2. Novo Dataset VIVEIROS_DATA com 100% de retrocompatibilidade
novo_dataset_js = """    // ========================================================
    // DATASET OFICIAL DOS 15 VIVEIROS (NUMERAÇÃO DO PAI 1 A 10 & DUPLA METRAGEM)
    // ========================================================
    let VIVEIROS_DATA = [
      {
        id: 'V-01', numeroPai: 1, nomePai: 'Viveiro 1', nomeAntigo: 'C1', nome: 'Viveiro 1',
        setor: 'Central', tipoUso: 'Engorda', tipo: 'engorda',
        areaSateliteM2: 12600.0, areaAjustadaM2: 12600.0, area_m2: 12600.0, areaHa: 1.26, area_ha: 1.26,
        profundidadeM: 1.20, volumeM3: 15120.0,
        status: 'otimo', statusCor: 'OTIMO', statusLabel: '🟢 Ótimo', statusDesc: 'Parâmetros estáveis e bandejas limpas',
        ddc: 58, dataPovoamento: '24/08/2026', pesoMedio: 12.4, ganhoSemanal: 1.35, biomassaKg: 3420, fca: 1.19,
        racaoHojeKg: 75, racaoAcumuladaKg: 4070, o2Manha: 4.6, o2Noite: 4.8, phManha: 7.8, phTarde: 8.2,
        salinidade: 14.5, secchi: 35, amonia: 0.02, sobraNivel: 0, sobraTexto: '0 (Prato Limpo)', densidade: 23
      },
      {
        id: 'V-02', numeroPai: 2, nomePai: 'Viveiro 2', nomeAntigo: 'C2', nome: 'Viveiro 2',
        setor: 'Central', tipoUso: 'Engorda', tipo: 'engorda',
        areaSateliteM2: 13285.0, areaAjustadaM2: 13285.0, area_m2: 13285.0, areaHa: 1.33, area_ha: 1.33,
        profundidadeM: 1.20, volumeM3: 15942.0,
        status: 'atencao', statusCor: 'ATENCAO', statusLabel: '🟡 Atenção', statusDesc: 'Duplicidade de lançamento detectada na auditoria',
        ddc: 52, dataPovoamento: '30/08/2026', pesoMedio: 11.2, ganhoSemanal: 1.20, biomassaKg: 2850, fca: 1.24,
        racaoHojeKg: 60, racaoAcumuladaKg: 3534, o2Manha: 4.2, o2Noite: 4.5, phManha: 7.7, phTarde: 8.1,
        salinidade: 14.0, secchi: 32, amonia: 0.03, sobraNivel: 1, sobraTexto: '1 (Pouca Sobra)', densidade: 25
      },
      {
        id: 'V-03', numeroPai: 3, nomePai: 'Viveiro 3', nomeAntigo: 'C3', nome: 'Viveiro 3',
        setor: 'Central', tipoUso: 'Engorda', tipo: 'engorda',
        areaSateliteM2: 15500.0, areaAjustadaM2: 15500.0, area_m2: 15500.0, areaHa: 1.55, area_ha: 1.55,
        profundidadeM: 1.20, volumeM3: 18600.0,
        status: 'critico', statusCor: 'CRITICO', statusLabel: '🔴 Crítico', statusDesc: 'Anóxia noturna (O2 2.6 mg/L) detectada',
        ddc: 65, dataPovoamento: '17/08/2026', pesoMedio: 14.8, ganhoSemanal: 1.45, biomassaKg: 4200, fca: 1.32,
        racaoHojeKg: 85, racaoAcumuladaKg: 5544, o2Manha: 2.6, o2Noite: 3.1, phManha: 7.5, phTarde: 8.0,
        salinidade: 15.0, secchi: 25, amonia: 0.08, sobraNivel: 2, sobraTexto: '2 (Média Sobra)', densidade: 22
      },
      {
        id: 'V-04', numeroPai: 4, nomePai: 'Viveiro 4', nomeAntigo: 'C4', nome: 'Viveiro 4',
        setor: 'Central', tipoUso: 'Engorda', tipo: 'engorda',
        areaSateliteM2: 16400.0, areaAjustadaM2: 16400.0, area_m2: 16400.0, areaHa: 1.64, area_ha: 1.64,
        profundidadeM: 1.20, volumeM3: 19680.0,
        status: 'otimo', statusCor: 'OTIMO', statusLabel: '🟢 Ótimo', statusDesc: 'Crescimento vigoroso e apetite elevado',
        ddc: 45, dataPovoamento: '06/09/2026', pesoMedio: 9.8, ganhoSemanal: 1.40, biomassaKg: 2600, fca: 1.15,
        racaoHojeKg: 55, racaoAcumuladaKg: 2990, o2Manha: 5.1, o2Noite: 5.4, phManha: 7.9, phTarde: 8.3,
        salinidade: 14.8, secchi: 38, amonia: 0.01, sobraNivel: 0, sobraTexto: '0 (Prato Limpo)', densidade: 27
      },
      {
        id: 'V-05', numeroPai: 5, nomePai: 'Viveiro 5', nomeAntigo: 'L1', nome: 'Viveiro 5',
        setor: 'Leste', tipoUso: 'Engorda', tipo: 'engorda',
        areaSateliteM2: 13040.0, areaAjustadaM2: 13040.0, area_m2: 13040.0, areaHa: 1.304, area_ha: 1.304,
        profundidadeM: 1.20, volumeM3: 15648.0,
        status: 'otimo', statusCor: 'OTIMO', statusLabel: '🟢 Ótimo', statusDesc: 'Biometria acima da curva esperada',
        ddc: 62, dataPovoamento: '20/08/2026', pesoMedio: 13.9, ganhoSemanal: 1.50, biomassaKg: 3850, fca: 1.21,
        racaoHojeKg: 80, racaoAcumuladaKg: 4658, o2Manha: 4.8, o2Noite: 5.0, phManha: 7.8, phTarde: 8.2,
        salinidade: 14.2, secchi: 36, amonia: 0.02, sobraNivel: 0, sobraTexto: '0 (Prato Limpo)', densidade: 24
      },
      {
        id: 'V-06', numeroPai: 6, nomePai: 'Viveiro 6', nomeAntigo: 'L2', nome: 'Viveiro 6',
        setor: 'Leste', tipoUso: 'Engorda', tipo: 'engorda',
        areaSateliteM2: 14710.0, areaAjustadaM2: 14710.0, area_m2: 14710.0, areaHa: 1.471, area_ha: 1.471,
        profundidadeM: 1.20, volumeM3: 17652.0,
        status: 'atencao', statusCor: 'ATENCAO', statusLabel: '🟡 Atenção', statusDesc: 'Sobra moderada na bandeja 3 da tarde',
        ddc: 38, dataPovoamento: '13/09/2026', pesoMedio: 7.9, ganhoSemanal: 1.10, biomassaKg: 1950, fca: 1.28,
        racaoHojeKg: 45, racaoAcumuladaKg: 2496, o2Manha: 4.3, o2Noite: 4.6, phManha: 7.7, phTarde: 8.1,
        salinidade: 13.9, secchi: 33, amonia: 0.04, sobraNivel: 1, sobraTexto: '1 (Pouca Sobra)', densidade: 28
      },
      {
        id: 'V-07', numeroPai: 7, nomePai: 'Viveiro 7', nomeAntigo: 'O1', nome: 'Viveiro 7',
        setor: 'Oeste', tipoUso: 'Engorda', tipo: 'engorda',
        areaSateliteM2: 8060.0, areaAjustadaM2: 8060.0, area_m2: 8060.0, areaHa: 0.806, area_ha: 0.806,
        profundidadeM: 1.20, volumeM3: 9672.0,
        status: 'otimo', statusCor: 'OTIMO', statusLabel: '🟢 Ótimo', statusDesc: 'Excelente taxa de sobrevivência',
        ddc: 70, dataPovoamento: '12/08/2026', pesoMedio: 15.6, ganhoSemanal: 1.30, biomassaKg: 2900, fca: 1.22,
        racaoHojeKg: 60, racaoAcumuladaKg: 3538, o2Manha: 4.9, o2Noite: 5.2, phManha: 7.8, phTarde: 8.3,
        salinidade: 14.5, secchi: 35, amonia: 0.02, sobraNivel: 0, sobraTexto: '0 (Prato Limpo)', densidade: 25
      },
      {
        id: 'V-08', numeroPai: 8, nomePai: 'Viveiro 8', nomeAntigo: 'O2', nome: 'Viveiro 8',
        setor: 'Oeste', tipoUso: 'Engorda', tipo: 'engorda',
        areaSateliteM2: 7550.0, areaAjustadaM2: 7550.0, area_m2: 7550.0, areaHa: 0.755, area_ha: 0.755,
        profundidadeM: 1.20, volumeM3: 9060.0,
        status: 'atencao', statusCor: 'ATENCAO', statusLabel: '🟡 Atenção', statusDesc: 'Alimentação não registrada ontem (dia esquecido)',
        ddc: 30, dataPovoamento: '21/09/2026', pesoMedio: 6.2, ganhoSemanal: 1.15, biomassaKg: 1350, fca: 1.20,
        racaoHojeKg: 30, racaoAcumuladaKg: 1620, o2Manha: 4.4, o2Noite: 4.7, phManha: 7.6, phTarde: 8.0,
        salinidade: 14.1, secchi: 34, amonia: 0.03, sobraNivel: 1, sobraTexto: '1 (Pouca Sobra)', densidade: 30
      },
      {
        id: 'V-09', numeroPai: 9, nomePai: 'Viveiro 9', nomeAntigo: 'O3', nome: 'Viveiro 9',
        setor: 'Oeste', tipoUso: 'Engorda', tipo: 'engorda',
        areaSateliteM2: 5400.0, areaAjustadaM2: 5400.0, area_m2: 5400.0, areaHa: 0.54, area_ha: 0.54,
        profundidadeM: 1.20, volumeM3: 6480.0,
        status: 'otimo', statusCor: 'OTIMO', statusLabel: '🟢 Ótimo', statusDesc: 'Lote povoado recentemente em adaptação',
        ddc: 22, dataPovoamento: '29/09/2026', pesoMedio: 4.5, ganhoSemanal: 1.05, biomassaKg: 780, fca: 1.12,
        racaoHojeKg: 20, racaoAcumuladaKg: 873, o2Manha: 5.2, o2Noite: 5.5, phManha: 7.9, phTarde: 8.2,
        salinidade: 14.3, secchi: 40, amonia: 0.01, sobraNivel: 0, sobraTexto: '0 (Prato Limpo)', densidade: 32
      },
      {
        id: 'V-10', numeroPai: 10, nomePai: 'Viveiro 10', nomeAntigo: 'O5', nome: 'Viveiro 10',
        setor: 'Oeste', tipoUso: 'Engorda', tipo: 'engorda',
        areaSateliteM2: 4650.0, areaAjustadaM2: 4650.0, area_m2: 4650.0, areaHa: 0.465, area_ha: 0.465,
        profundidadeM: 1.20, volumeM3: 5580.0,
        status: 'vazio', statusCor: 'VAZIO', statusLabel: '⚪ Preparo', statusDesc: 'Drenado, calagem e secagem de fundo',
        ddc: 0, dataPovoamento: '-', pesoMedio: 0, ganhoSemanal: 0, biomassaKg: 0, fca: 0,
        racaoHojeKg: 0, racaoAcumuladaKg: 0, o2Manha: 0, o2Noite: 0, phManha: 0, phTarde: 0,
        salinidade: 0, secchi: 0, amonia: 0, sobraNivel: 0, sobraTexto: 'Sem Ração', densidade: 0
      },
      {
        id: 'V-11', numeroPai: null, nomePai: 'Berçário 1', nomeAntigo: 'N1', nome: 'Berçário 1',
        setor: 'Leste', tipoUso: 'Berçário', tipo: 'bercario',
        areaSateliteM2: 6340.0, areaAjustadaM2: 6340.0, area_m2: 6340.0, areaHa: 0.634, area_ha: 0.634,
        profundidadeM: 1.00, volumeM3: 6340.0,
        status: 'otimo', statusCor: 'OTIMO', statusLabel: '🟢 Ativo', statusDesc: 'Pós-larvas PL-10 em berçário intensivo',
        ddc: 14, dataPovoamento: '07/10/2026', pesoMedio: 0.85, ganhoSemanal: 0.35, biomassaKg: 280, fca: 0.98,
        racaoHojeKg: 12, racaoAcumuladaKg: 274, o2Manha: 5.6, o2Noite: 5.8, phManha: 8.0, phTarde: 8.3,
        salinidade: 14.0, secchi: 42, amonia: 0.01, sobraNivel: 0, sobraTexto: '0 (Prato Limpo)', densidade: 80
      },
      {
        id: 'V-12', numeroPai: null, nomePai: 'Berçário 2', nomeAntigo: 'N2', nome: 'Berçário 2',
        setor: 'Leste', tipoUso: 'Berçário', tipo: 'bercario',
        areaSateliteM2: 5540.0, areaAjustadaM2: 5540.0, area_m2: 5540.0, areaHa: 0.554, area_ha: 0.554,
        profundidadeM: 1.00, volumeM3: 5540.0,
        status: 'vazio', statusCor: 'VAZIO', statusLabel: '⚪ Vazio', statusDesc: 'Higienização e desinfecção pós-transferência',
        ddc: 0, dataPovoamento: '-', pesoMedio: 0, ganhoSemanal: 0, biomassaKg: 0, fca: 0,
        racaoHojeKg: 0, racaoAcumuladaKg: 0, o2Manha: 0, o2Noite: 0, phManha: 0, phTarde: 0,
        salinidade: 0, secchi: 0, amonia: 0, sobraNivel: 0, sobraTexto: 'Sem Ração', densidade: 0
      },
      {
        id: 'V-13', numeroPai: null, nomePai: 'Tanque Apoio 1', nomeAntigo: 'O0', nome: 'Tanque Apoio 1',
        setor: 'Oeste', tipoUso: 'Apoio', tipo: 'apoio',
        areaSateliteM2: 1430.0, areaAjustadaM2: 1430.0, area_m2: 1430.0, areaHa: 0.143, area_ha: 0.143,
        profundidadeM: 1.20, volumeM3: 1716.0,
        status: 'otimo', statusCor: 'OTIMO', statusLabel: '🟢 Reservatório', statusDesc: 'Reservatório de água sedimentada',
        ddc: 0, dataPovoamento: '-', pesoMedio: 0, ganhoSemanal: 0, biomassaKg: 0, fca: 0,
        racaoHojeKg: 0, racaoAcumuladaKg: 0, o2Manha: 5.0, o2Noite: 5.2, phManha: 7.8, phTarde: 8.0,
        salinidade: 14.5, secchi: 45, amonia: 0.01, sobraNivel: 0, sobraTexto: 'Apoio Hídrico', densidade: 0
      },
      {
        id: 'V-14', numeroPai: null, nomePai: 'Tanque Apoio 2', nomeAntigo: 'O4', nome: 'Tanque Apoio 2',
        setor: 'Oeste', tipoUso: 'Apoio', tipo: 'apoio',
        areaSateliteM2: 1980.0, areaAjustadaM2: 1980.0, area_m2: 1980.0, areaHa: 0.198, area_ha: 0.198,
        profundidadeM: 1.20, volumeM3: 2376.0,
        status: 'vazio', statusCor: 'VAZIO', statusLabel: '⚪ Secando', statusDesc: 'Apoio em manutenção de talude',
        ddc: 0, dataPovoamento: '-', pesoMedio: 0, ganhoSemanal: 0, biomassaKg: 0, fca: 0,
        racaoHojeKg: 0, racaoAcumuladaKg: 0, o2Manha: 0, o2Noite: 0, phManha: 0, phTarde: 0,
        salinidade: 0, secchi: 0, amonia: 0, sobraNivel: 0, sobraTexto: 'Sem Ração', densidade: 0
      },
      {
        id: 'V-15', numeroPai: null, nomePai: 'Bacia Decantação', nomeAntigo: 'L0', nome: 'Bacia Decantação',
        setor: 'Leste', tipoUso: 'Decantação', tipo: 'bacia',
        areaSateliteM2: 1850.0, areaAjustadaM2: 1850.0, area_m2: 1850.0, areaHa: 0.185, area_ha: 0.185,
        profundidadeM: 1.50, volumeM3: 2775.0,
        status: 'vazio', statusCor: 'VAZIO', statusLabel: '⚪ Efluente', statusDesc: 'Bacia de clarificação e decantação (compliance IDEMA)',
        ddc: 0, dataPovoamento: '-', pesoMedio: 0, ganhoSemanal: 0, biomassaKg: 0, fca: 0,
        racaoHojeKg: 0, racaoAcumuladaKg: 0, o2Manha: 0, o2Noite: 0, phManha: 0, phTarde: 0,
        salinidade: 0, secchi: 0, amonia: 0, sobraNivel: 0, sobraTexto: 'Compliance Ambiental', densidade: 0
      }
    ];"""

# Substituir VIVEIROS_DATA no HTML
padrao_dataset = r"let\s+VIVEIROS_DATA\s*=\s*\[[\s\S]*?\];"
if re.search(padrao_dataset, html_content):
    html_content = re.sub(padrao_dataset, novo_dataset_js.strip(), html_content, count=1)
    print("VIVEIROS_DATA substituído com sucesso!")
else:
    print("ERRO: VIVEIROS_DATA não encontrado!")

# 3. Nova seção HTML do Módulo Mapa dos Viveiros 2D
nova_secao_mapa_html = f"""      <!-- ======================================================== -->
      <!-- VIEW: MÓDULO MAPA DOS VIVEIROS 2D & FOTO DE SATÉLITE      -->
      <!-- ======================================================== -->
      <section id="view-viveiros-mapa" class="hidden space-y-6">
        
        <!-- Header da Página do Mapa com Alternador de Modos -->
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
            <p class="text-xs text-slate-500">Fazenda Ceará-Mirim/RN • Coordenadas: 5°40'17.1"S 35°15'04.2"W • Levantamento do Google Maps & Calibração de Campo</p>
          </div>

          <!-- Controles de Modos de Visualização -->
          <div class="flex flex-wrap items-center gap-2">
            <!-- Alternador de Modos (3 Abas) -->
            <div class="bg-slate-100 p-1 rounded-xl flex items-center border border-slate-200 shadow-inner">
              <button id="btn-tab-satelite" onclick="alternarAbaMapa('satelite')" class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition bg-emerald-600 text-white shadow-sm">
                <i class="fa-solid fa-satellite"></i>
                <span>🛰️ Satélite do Pai</span>
              </button>
              <button id="btn-tab-vetorial" onclick="alternarAbaMapa('vetorial')" class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold text-slate-600 hover:text-slate-900 transition">
                <i class="fa-solid fa-layer-group text-aco"></i>
                <span>🗺️ Esquema 2D</span>
              </button>
              <button id="btn-tab-tabela" onclick="alternarAbaMapa('tabela')" class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold text-slate-600 hover:text-slate-900 transition">
                <i class="fa-solid fa-table-list text-purple-600"></i>
                <span>📊 Tabela Geral</span>
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
            <span id="kpi-topo-sub-satelite" class="text-[10px] text-slate-500 block mt-0.5">128.335 m² aerofotogramétricos</span>
          </div>

          <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm border-l-4 border-l-emerald-500">
            <span class="text-[11px] font-bold text-slate-500 uppercase flex items-center gap-1">
              <i class="fa-solid fa-ruler-combined text-emerald-600"></i> Área Calibrada Oficial
            </span>
            <div id="kpi-topo-area-ajustada" class="text-xl sm:text-2xl font-extrabold text-emerald-700 mt-1">12,83 ha</div>
            <span id="kpi-topo-sub-ajustada" class="text-[10px] text-emerald-600 font-semibold block mt-0.5">128.335 m² oficiais vigentes</span>
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

        <!-- ======================================================== -->
        <!-- MODO 1: FOTO DE SATÉLITE REAL COM LISTA INTERATIVA DO PAI -->
        <!-- ======================================================== -->
        <div id="container-modo-satelite" class="space-y-4">
          <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
            
            <!-- Coluna da Foto de Satélite (6 cols no desktop) -->
            <div class="lg:col-span-6 bg-slate-900 rounded-3xl p-4 sm:p-5 border border-slate-800 shadow-xl flex flex-col">
              <div class="flex items-center justify-between pb-3 border-b border-slate-800">
                <div>
                  <h3 class="text-sm font-bold text-white flex items-center gap-2">
                    <i class="fa-solid fa-satellite text-emerald-400"></i> Foto de Satélite Real (Google Maps)
                  </h3>
                  <p class="text-[11px] text-slate-400">Numeração original amarela de 1 a 10 feita pelo seu pai.</p>
                </div>
                
                <!-- Controles de Zoom da Foto -->
                <div class="flex items-center gap-1 bg-slate-800 p-1 rounded-xl">
                  <button onclick="zoomSatelite(-0.15)" title="Diminuir Zoom" class="w-7 h-7 rounded-lg bg-slate-700 hover:bg-slate-600 text-white text-xs flex items-center justify-center transition">
                    <i class="fa-solid fa-minus"></i>
                  </button>
                  <button onclick="resetZoomSatelite()" title="Restaurar Tamanho Original" class="px-2 h-7 rounded-lg bg-slate-700 hover:bg-slate-600 text-slate-200 text-[10px] font-mono font-bold flex items-center justify-center transition">
                    <span id="zoom-satelite-label">100%</span>
                  </button>
                  <button onclick="zoomSatelite(0.15)" title="Aumentar Zoom" class="w-7 h-7 rounded-lg bg-slate-700 hover:bg-slate-600 text-white text-xs flex items-center justify-center transition">
                    <i class="fa-solid fa-plus"></i>
                  </button>
                  <button onclick="abrirModalSateliteAmpliado()" title="Ver Ampliado em Tela Cheia" class="w-7 h-7 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs flex items-center justify-center transition ml-1">
                    <i class="fa-solid fa-expand"></i>
                  </button>
                </div>
              </div>

              <!-- Container da Imagem com Overflow e Scroll -->
              <div id="wrapper-imagem-satelite" class="relative mt-4 bg-slate-950 rounded-2xl overflow-auto max-h-[640px] flex items-center justify-center p-2 border border-slate-800">
                <img id="img-satelite-principal" src="{img_src}" alt="Foto de Satélite Real com Numeração do Pai" class="max-w-full h-auto rounded-xl shadow-2xl transition-transform duration-200 origin-center select-none" style="transform: scale(1.0);">
              </div>

              <!-- Legenda e Rodapé da Foto -->
              <div class="mt-3 pt-3 border-t border-slate-800 flex flex-wrap items-center justify-between gap-2 text-xs text-slate-400">
                <div class="flex items-center gap-3">
                  <span class="flex items-center gap-1">
                    <span class="w-2.5 h-2.5 rounded-full bg-yellow-400"></span> <strong>1 a 10:</strong> Viveiros do Pai
                  </span>
                  <span class="flex items-center gap-1">
                    <span class="w-2.5 h-2.5 rounded-full bg-blue-400"></span> Rio Ceará-Mirim
                  </span>
                </div>
                <div class="text-[11px] text-slate-500">
                  <i class="fa-solid fa-mouse-pointer text-[10px]"></i> Clique em "✏️ Calibrar" ao lado para ajustar metragens
                </div>
              </div>
            </div>

            <!-- Coluna de Tanques e Calibração Rápida (6 cols no desktop) -->
            <div class="lg:col-span-6 space-y-3">
              <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
                <div>
                  <h3 class="text-sm font-bold text-slate-900 flex items-center gap-2">
                    <i class="fa-solid fa-list-ol text-aco"></i> Viveiros Identificados na Foto
                  </h3>
                  <p class="text-xs text-slate-500">10 Viveiros principais de engorda e estruturas de apoio.</p>
                </div>

                <!-- Filtros rápidos de tanques -->
                <div class="flex items-center gap-1 bg-slate-100 p-1 rounded-xl text-xs">
                  <button onclick="filtrarCardsSatelite('todos')" id="filter-sat-todos" class="px-2.5 py-1 rounded-lg font-bold bg-white text-slate-900 shadow-sm">Todos (15)</button>
                  <button onclick="filtrarCardsSatelite('pai')" id="filter-sat-pai" class="px-2.5 py-1 rounded-lg font-semibold text-slate-600 hover:text-slate-900">Pai (1 a 10)</button>
                  <button onclick="filtrarCardsSatelite('apoio')" id="filter-sat-apoio" class="px-2.5 py-1 rounded-lg font-semibold text-slate-600 hover:text-slate-900">Apoio</button>
                </div>
              </div>

              <!-- Lista de Cards Interativos -->
              <div id="lista-cards-satelite" class="space-y-2.5 max-h-[640px] overflow-y-auto pr-1">
                <!-- Injetado dinamicamente via JS -->
              </div>
            </div>

          </div>
        </div>

        <!-- ======================================================== -->
        <!-- MODO 2: ESQUEMA VETORIAL 2D POR SETORES (OESTE, CENTRAL, LESTE) -->
        <!-- ======================================================== -->
        <div id="container-modo-vetorial" class="hidden bg-white rounded-3xl p-5 border border-slate-200 shadow-sm space-y-4">
          <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-3 border-b border-slate-100">
            <div>
              <h3 class="text-sm font-bold text-slate-800 flex items-center gap-2">
                <i class="fa-solid fa-diagram-project text-aco"></i> Disposição Espacial por Setores (Ceará-Mirim/RN)
                <span class="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-blue-100 text-aco border border-blue-200">Esquema Técnico</span>
              </h3>
              <p class="text-xs text-slate-500">Distribuição dos tanques em 3 corredores topográficos reais.</p>
            </div>

            <!-- Filtros de Setor -->
            <div class="flex items-center gap-1 bg-slate-100 p-1 rounded-xl text-xs">
              <button onclick="filtrarMapaSetor('todos')" id="filter-mapa-todos" class="px-2.5 py-1 rounded-lg font-bold bg-white text-slate-800 shadow-sm">Todos (15)</button>
              <button onclick="filtrarMapaSetor('engorda')" id="filter-mapa-engorda" class="px-2.5 py-1 rounded-lg font-semibold text-slate-600 hover:text-slate-900">Engorda (1 a 10)</button>
              <button onclick="filtrarMapaSetor('bercario')" id="filter-mapa-bercario" class="px-2.5 py-1 rounded-lg font-semibold text-slate-600 hover:text-slate-900">Berçários</button>
              <button onclick="filtrarMapaSetor('apoio')" id="filter-mapa-apoio" class="px-2.5 py-1 rounded-lg font-semibold text-slate-600 hover:text-slate-900">Apoio</button>
            </div>
          </div>

          <!-- ÁREA DO GRID TOPOGRÁFICO -->
          <div class="w-full rounded-2xl border border-slate-200 bg-slate-950 p-4 min-h-[500px]">
            <div class="w-full grid grid-cols-1 md:grid-cols-12 gap-4 items-start">
              
              <!-- SETOR OESTE -->
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

              <!-- SETOR CENTRAL -->
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

              <!-- SETOR LESTE -->
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

          <!-- Legenda do Mapa Vetorial -->
          <div class="flex flex-wrap items-center justify-between gap-3 pt-2 text-xs text-slate-500">
            <div class="flex flex-wrap items-center gap-4">
              <span class="flex items-center gap-1.5 font-semibold text-slate-700">
                <span class="w-3 h-3 rounded-full bg-emerald-500"></span> 🟢 Ótimo
              </span>
              <span class="flex items-center gap-1.5 font-semibold text-slate-700">
                <span class="w-3 h-3 rounded-full bg-amber-500"></span> 🟡 Atenção
              </span>
              <span class="flex items-center gap-1.5 font-semibold text-slate-700">
                <span class="w-3 h-3 rounded-full bg-red-500 animate-ping"></span> 🔴 Crítico
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

        <!-- ======================================================== -->
        <!-- MODO 3: TABELA DE CALIBRAÇÃO E AUDITORIA TOPOGRÁFICA     -->
        <!-- ======================================================== -->
        <div id="container-modo-tabela" class="hidden bg-white rounded-3xl p-5 border border-slate-200 shadow-sm space-y-4">
          <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-3 border-b border-slate-100">
            <div>
              <h3 class="text-sm font-bold text-slate-800 flex items-center gap-2">
                <i class="fa-solid fa-table-cells text-aco"></i> Inventário Geral de Metragens & Volumes Úteis
              </h3>
              <p class="text-xs text-slate-500">Auditoria comparativa entre a foto de satélite e a medição de campo calibrada.</p>
            </div>
            <div class="text-xs font-semibold text-slate-500 bg-slate-50 px-3 py-1.5 rounded-xl border border-slate-200">
              15 Tanques Mapeados (10 Engorda + 2 Berçários + 3 Apoio)
            </div>
          </div>

          <div class="overflow-x-auto">
            <table class="w-full text-left text-xs border-collapse">
              <thead>
                <tr class="bg-slate-50 text-slate-500 font-semibold border-b border-slate-200">
                  <th class="py-3 px-3">Tanque (Numeração do Pai)</th>
                  <th class="py-3 px-3">Código Técnico</th>
                  <th class="py-3 px-3">Setor</th>
                  <th class="py-3 px-3 text-right">🛰️ Área Satélite</th>
                  <th class="py-3 px-3 text-right">📐 Área Calibrada</th>
                  <th class="py-3 px-3 text-right">Hectares</th>
                  <th class="py-3 px-3 text-right">Lâmina Média</th>
                  <th class="py-3 px-3 text-right">Volume d'Água</th>
                  <th class="py-3 px-3">Tipo de Uso</th>
                  <th class="py-3 px-3 text-center">Ações</th>
                </tr>
              </thead>
              <tbody id="tbody-tabela-calibracao-metragens" class="divide-y divide-slate-100 font-sans">
                <!-- Injetado dinamicamente via JS -->
              </tbody>
              <tfoot class="bg-slate-50/90 font-bold text-slate-800 border-t-2 border-slate-300">
                <tr>
                  <td class="py-3 px-3" colspan="3">TOTAL GERAL DA FAZENDA</td>
                  <td id="tfoot-total-satelite" class="py-3 px-3 text-right font-mono text-slate-700">128.335 m²</td>
                  <td id="tfoot-total-calibrada" class="py-3 px-3 text-right font-mono text-emerald-700 font-extrabold">128.335 m²</td>
                  <td id="tfoot-total-ha" class="py-3 px-3 text-right font-mono text-slate-800">12,83 ha</td>
                  <td class="py-3 px-3 text-right font-mono text-slate-500">1,18 m méd.</td>
                  <td id="tfoot-total-vol" class="py-3 px-3 text-right font-mono text-blue-700 font-extrabold">154.002 m³</td>
                  <td class="py-3 px-3" colspan="2"></td>
                </tr>
              </tfoot>
            </table>
          </div>
        </div>

      </section>"""

# Substituir a seção view-viveiros-mapa antiga pela nova
padrao_secao = r'<section id="view-viveiros-mapa"[\s\S]*?</section>'
if re.search(padrao_secao, html_content):
    html_content = re.sub(padrao_secao, nova_secao_mapa_html.strip(), html_content, count=1)
    print("Seção view-viveiros-mapa substituída com sucesso!")
else:
    print("ERRO: Seção view-viveiros-mapa não encontrada!")

# 4. Adicionar Modal de Foto de Satélite Ampliada (caso ainda não exista)
modal_satelite_ampliado_html = f"""
  <!-- ======================================================== -->
  <!-- MODAL DE VISUALIZAÇÃO AMPLIADA DA FOTO DE SATÉLITE      -->
  <!-- ======================================================== -->
  <div id="modal-satelite-ampliado" class="hidden fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-md flex items-center justify-center p-3 sm:p-6">
    <div class="bg-slate-900 rounded-3xl max-w-4xl w-full max-h-[92vh] flex flex-col overflow-hidden border border-slate-700 shadow-2xl">
      <div class="p-4 bg-slate-800/90 border-b border-slate-700 flex items-center justify-between">
        <div class="flex items-center gap-2.5">
          <div class="w-8 h-8 rounded-xl bg-emerald-600 text-white flex items-center justify-center font-bold text-sm">
            <i class="fa-solid fa-satellite"></i>
          </div>
          <div>
            <h3 class="text-sm font-bold text-white">Foto de Satélite Real — Numeração do Pai (1 a 10)</h3>
            <p class="text-[11px] text-slate-400">Fazenda Ceará-Mirim/RN • Google Maps SIG</p>
          </div>
        </div>
        <button onclick="fecharModalSateliteAmpliado()" class="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-700 transition">
          <i class="fa-solid fa-xmark text-lg"></i>
        </button>
      </div>
      <div class="flex-1 overflow-auto p-4 flex items-center justify-center bg-slate-950">
        <img id="img-satelite-modal-zoom" src="{img_src}" alt="Foto Ampliada do Satélite com Números do Pai" class="max-w-none w-auto max-h-[80vh] rounded-xl shadow-2xl select-none">
      </div>
      <div class="p-3 bg-slate-800/90 border-t border-slate-700 flex items-center justify-between text-xs text-slate-400">
        <span>Use o scroll para rolar e visualizar todos os viveiros com a numeração em amarelo.</span>
        <button onclick="fecharModalSateliteAmpliado()" class="px-4 py-1.5 rounded-xl bg-slate-700 hover:bg-slate-600 text-white font-bold transition">
          Fechar
        </button>
      </div>
    </div>
  </div>
"""

if "id=\"modal-satelite-ampliado\"" not in html_content:
    pos_modal_calib = html_content.find('id="modal-calibracao-metragem"')
    if pos_modal_calib != -1:
        div_start = html_content.rfind('<div', 0, pos_modal_calib)
        html_content = html_content[:div_start] + modal_satelite_ampliado_html + "\n  " + html_content[div_start:]
        print("Modal de Satélite Ampliado injetado antes do modal de calibração!")
    else:
        last_body = html_content.rfind('</body>')
        html_content = html_content[:last_body] + modal_satelite_ampliado_html + "\n" + html_content[last_body:]
        print("Modal de Satélite Ampliado injetado antes de </body>!")

# 5. Funções JavaScript completas do Módulo Mapa 2D & Calibração
funcoes_mapa_js = """
    // ========================================================
    // LÓGICA DO MÓDULO MAPA DOS VIVEIROS 2D & CALIBRAÇÃO (PAI 1 A 10)
    // ========================================================
    let modoMapaAtual = 'satelite'; // 'satelite', 'vetorial', 'tabela'
    let filtroSetorMapa = 'todos';   // 'todos', 'engorda', 'bercario', 'apoio'
    let filtroCardsSat = 'todos';    // 'todos', 'pai', 'apoio'
    let zoomSateliteNivel = 1.0;
    let viveiroEmCalibracao = null;

    function alternarAbaMapa(modo) {
      modoMapaAtual = modo;
      const btnSat = document.getElementById('btn-tab-satelite');
      const btnVet = document.getElementById('btn-tab-vetorial');
      const btnTab = document.getElementById('btn-tab-tabela');

      const contSat = document.getElementById('container-modo-satelite');
      const contVet = document.getElementById('container-modo-vetorial');
      const contTab = document.getElementById('container-modo-tabela');

      // Reset botões
      [btnSat, btnVet, btnTab].forEach(b => {
        if (b) {
          b.className = 'flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold text-slate-600 hover:text-slate-900 transition';
        }
      });

      // Esconder todos os containers
      if (contSat) contSat.classList.add('hidden');
      if (contVet) contVet.classList.add('hidden');
      if (contTab) contTab.classList.add('hidden');

      if (modo === 'satelite') {
        if (contSat) contSat.classList.remove('hidden');
        if (btnSat) btnSat.className = 'flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition bg-emerald-600 text-white shadow-sm';
        renderizarCardsSatelite();
      } else if (modo === 'vetorial') {
        if (contVet) contVet.classList.remove('hidden');
        if (btnVet) btnVet.className = 'flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition bg-aco text-white shadow-sm';
        renderizarCardsVetoriais();
      } else if (modo === 'tabela') {
        if (contTab) contTab.classList.remove('hidden');
        if (btnTab) btnTab.className = 'flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition bg-purple-600 text-white shadow-sm';
        renderizarTabelaCalibracao();
      }
    }

    function zoomSatelite(delta) {
      zoomSateliteNivel = Math.max(0.7, Math.min(2.5, zoomSateliteNivel + delta));
      const img = document.getElementById('img-satelite-principal');
      const lbl = document.getElementById('zoom-satelite-label');
      if (img) {
        img.style.transform = `scale(${zoomSateliteNivel})`;
      }
      if (lbl) {
        lbl.textContent = `${Math.round(zoomSateliteNivel * 100)}%`;
      }
    }

    function resetZoomSatelite() {
      zoomSateliteNivel = 1.0;
      const img = document.getElementById('img-satelite-principal');
      const lbl = document.getElementById('zoom-satelite-label');
      if (img) img.style.transform = 'scale(1.0)';
      if (lbl) lbl.textContent = '100%';
    }

    function abrirModalSateliteAmpliado() {
      const m = document.getElementById('modal-satelite-ampliado');
      if (m) m.classList.remove('hidden');
    }

    function fecharModalSateliteAmpliado() {
      const m = document.getElementById('modal-satelite-ampliado');
      if (m) m.classList.add('hidden');
    }

    function filtrarCardsSatelite(tipo) {
      filtroCardsSat = tipo;
      const botoes = ['todos', 'pai', 'apoio'];
      botoes.forEach(b => {
        const el = document.getElementById(`filter-sat-${b}`);
        if (el) {
          if (b === tipo) {
            el.className = 'px-2.5 py-1 rounded-lg font-bold bg-white text-slate-900 shadow-sm';
          } else {
            el.className = 'px-2.5 py-1 rounded-lg font-semibold text-slate-600 hover:text-slate-900';
          }
        }
      });
      renderizarCardsSatelite();
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
      renderizarCardsVetoriais();
    }

    function renderizarModuloMapa2D() {
      renderizarCardsSatelite();
      renderizarCardsVetoriais();
      renderizarTabelaCalibracao();
      atualizarTotaisTopograficos();
    }

    function renderizarCardsSatelite() {
      const container = document.getElementById('lista-cards-satelite');
      if (!container) return;

      container.innerHTML = '';
      let lista = VIVEIROS_DATA;
      if (filtroCardsSat === 'pai') {
        lista = VIVEIROS_DATA.filter(v => v.numeroPai !== null);
      } else if (filtroCardsSat === 'apoio') {
        lista = VIVEIROS_DATA.filter(v => v.numeroPai === null);
      }

      lista.forEach(v => {
        const statusBadgeCores = {
          otimo: 'bg-emerald-100 text-emerald-800 border-emerald-300',
          atencao: 'bg-amber-100 text-amber-800 border-amber-300',
          critico: 'bg-red-100 text-red-800 border-red-300 animate-pulse',
          vazio: 'bg-slate-100 text-slate-700 border-slate-300'
        };
        const badgeClasse = statusBadgeCores[v.status] || statusBadgeCores.vazio;

        const badgePai = v.numeroPai
          ? `<span class="w-7 h-7 rounded-xl bg-aco text-white font-black text-xs flex items-center justify-center shadow-sm">
               ${v.numeroPai}
             </span>`
          : `<span class="w-7 h-7 rounded-xl bg-slate-200 text-slate-700 font-bold text-[11px] flex items-center justify-center">
               •
             </span>`;

        container.innerHTML += `
          <div class="bg-white p-3 rounded-2xl border border-slate-200 hover:border-emerald-500 hover:shadow-md transition-all">
            <div class="flex items-center justify-between gap-2">
              <div class="flex items-center gap-2.5">
                ${badgePai}
                <div>
                  <h4 class="text-xs font-bold text-slate-900 flex items-center gap-1.5">
                    ${v.nomePai}
                    <span class="text-[10px] text-slate-400 font-mono">(${v.nomeAntigo || v.id})</span>
                  </h4>
                  <span class="text-[10px] text-slate-500 font-medium">${v.tipoUso} • Setor ${v.setor}</span>
                </div>
              </div>
              <span class="px-2 py-0.5 rounded-lg text-[10px] font-extrabold border ${badgeClasse}">
                ${v.statusLabel}
              </span>
            </div>

            <!-- Caixas de Metragem Lado a Lado -->
            <div class="grid grid-cols-2 gap-2 mt-2.5 pt-2 border-t border-slate-100 text-xs">
              <div class="bg-slate-50 p-2 rounded-xl border border-slate-100">
                <span class="text-[9px] uppercase font-bold text-slate-400 block">🛰️ Satélite</span>
                <strong class="text-slate-800 font-mono text-xs">${v.areaSateliteM2.toLocaleString('pt-BR')} m²</strong>
                <span class="text-[9px] text-slate-400 block">${(v.areaSateliteM2 / 10000).toFixed(2)} ha</span>
              </div>
              <div class="bg-emerald-50/70 p-2 rounded-xl border border-emerald-200/80">
                <span class="text-[9px] uppercase font-bold text-emerald-700 block">📐 Calibrada Oficial</span>
                <strong class="text-emerald-800 font-mono text-xs">${v.areaAjustadaM2.toLocaleString('pt-BR')} m²</strong>
                <span class="text-[9px] text-emerald-600 font-bold block">${v.areaHa} ha • ${(v.volumeM3 || (v.areaAjustadaM2 * 1.2)).toLocaleString('pt-BR')} m³</span>
              </div>
            </div>

            <!-- Ações -->
            <div class="flex items-center justify-between mt-2 pt-2 border-t border-slate-100">
              <span class="text-[10px] text-slate-400">
                ${v.ddc > 0 ? `DDC: <strong class="text-slate-700">${v.ddc}d</strong> | O₂: <strong class="text-slate-700">${v.o2Manha || '--'}</strong>` : v.statusDesc}
              </span>
              <div class="flex items-center gap-1.5">
                <button onclick="abrirModalCalibracao('${v.id}')" class="px-2.5 py-1 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-[10px] shadow-sm transition flex items-center gap-1">
                  <i class="fa-solid fa-pen-ruler"></i> Calibrar
                </button>
                <button onclick="navegarPara('analytics-viveiro-detalhe', '${v.id}')" title="Ver Diário Zootécnico" class="p-1 px-2 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-[10px] font-semibold transition">
                  Zootecnia <i class="fa-solid fa-chevron-right text-[8px] ml-0.5"></i>
                </button>
              </div>
            </div>
          </div>
        `;
      });
    }

    function renderizarCardsVetoriais() {
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
        atencao: 'bg-amber-500 text-slate-950 font-bold',
        critico: 'bg-red-500 text-white font-bold',
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

      const haSat = (totalSat / 10000).toFixed(2);
      const haAjust = (totalAjust / 10000).toFixed(2);

      const elSat = document.getElementById('kpi-topo-area-satelite');
      const elSubSat = document.getElementById('kpi-topo-sub-satelite');
      const elAjust = document.getElementById('kpi-topo-area-ajustada');
      const elSubAjust = document.getElementById('kpi-topo-sub-ajustada');
      const elVol = document.getElementById('kpi-topo-volume');

      if (elSat) elSat.textContent = `${haSat} ha`;
      if (elSubSat) elSubSat.textContent = `${totalSat.toLocaleString('pt-BR')} m² aerofotogramétricos`;
      if (elAjust) elAjust.textContent = `${haAjust} ha`;
      if (elSubAjust) elSubAjust.textContent = `${totalAjust.toLocaleString('pt-BR')} m² oficiais vigentes`;
      if (elVol) elVol.textContent = `${totalVol.toLocaleString('pt-BR')} m³`;

      const tfSat = document.getElementById('tfoot-total-satelite');
      const tfAjust = document.getElementById('tfoot-total-calibrada');
      const tfHa = document.getElementById('tfoot-total-ha');
      const tfVol = document.getElementById('tfoot-total-vol');

      if (tfSat) tfSat.textContent = `${totalSat.toLocaleString('pt-BR')} m²`;
      if (tfAjust) tfAjust.textContent = `${totalAjust.toLocaleString('pt-BR')} m²`;
      if (tfHa) tfHa.textContent = `${haAjust} ha`;
      if (tfVol) tfVol.textContent = `${totalVol.toLocaleString('pt-BR')} m³`;
    }

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

      const elHa = document.getElementById('previa-calc-ha');
      const elVol = document.getElementById('previa-calc-vol');
      const elDif = document.getElementById('previa-calc-dif');

      if (elHa) elHa.textContent = `${ha} ha`;
      if (elVol) elVol.textContent = `${vol.toLocaleString('pt-BR')} m³`;
      
      if (elDif) {
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
        alert('Por favor, informe uma metragem válida maior que zero.');
        return;
      }

      // 1. Tentar persistência no backend FastAPI caso online
      if (backendOnline) {
        try {
          const res = await fetch(`${API_BASE_URL}/viveiros/${viveiroEmCalibracao.id}/metragem`, {
            method: 'PATCH',
            headers: {
              'Content-Type': 'application/json',
              'X-Fazenda-Id': String(fazendaAtivaId)
            },
            body: JSON.stringify({
              area_ajustada_m2: novaAreaM2,
              profundidade_media_m: novaProfM,
              observacoes: obs || `Calibração manual via painel do mapa pelo usuário.`
            })
          });

          if (res.ok) {
            console.log('✅ Metragem persistida no banco SQLite/Postgres com sucesso!');
          }
        } catch (e) {
          console.warn('Backend indisponível no momento, aplicando localmente:', e);
        }
      }

      // 2. Atualização reativa no estado local do frontend
      viveiroEmCalibracao.areaAjustadaM2 = novaAreaM2;
      viveiroEmCalibracao.area_m2 = novaAreaM2;
      viveiroEmCalibracao.areaHa = parseFloat((novaAreaM2 / 10000).toFixed(4));
      viveiroEmCalibracao.area_ha = viveiroEmCalibracao.areaHa;
      viveiroEmCalibracao.profundidadeM = novaProfM;
      viveiroEmCalibracao.volumeM3 = Math.round(novaAreaM2 * novaProfM);

      fecharModalCalibracao();
      renderizarModuloMapa2D();
      renderizarMapaViveiros();

      alert(`✅ Metragem do ${viveiroEmCalibracao.nomePai} calibrada com sucesso!\\n• Nova Área Oficial: ${novaAreaM2.toLocaleString('pt-BR')} m² (${viveiroEmCalibracao.areaHa} ha)\\n• Novo Volume Útil: ${viveiroEmCalibracao.volumeM3.toLocaleString('pt-BR')} m³`);
    }
"""

# 6. Atualizar a função renderizarMapaViveiros para exibir a numeração do pai e metragens completas
novo_card_mapa_macro = """        card.innerHTML = `
          <div>
            <div class="${bgHeader} px-3.5 py-2.5 flex items-center justify-between">
              <div class="flex items-center space-x-1.5">
                <span class="font-extrabold text-xs tracking-tight">${v.nomePai || v.nome}</span>
                <span class="text-[11px] font-semibold text-slate-500">• ${v.nomeAntigo || v.id}</span>
              </div>
              <span class="text-[11px] font-bold ${pulseClass}">${v.statusLabel}</span>
            </div>

            <div class="p-3.5 space-y-2.5 text-xs">
              <div class="flex items-center justify-between text-slate-500">
                <span>Área: <strong class="text-slate-800">${v.areaHa || v.area_ha} ha (${(v.areaAjustadaM2 || v.area_m2).toLocaleString('pt-BR')} m²)</strong></span>
                <span>DDC: <strong class="text-slate-800">${v.ddc > 0 ? v.ddc + ' dias' : '-'}</strong></span>
              </div>"""

padrao_card_macro = r'card\.innerHTML\s*=\s*`\s*<div>\s*<div class="\$\{bgHeader\} px-3\.5 py-2\.5[\s\S]*?<span>DDC: <strong class="text-slate-800">\$\{v\.ddc > 0 \? v\.ddc \+ \' dias\' : \'-\'\}</strong></span>\s*</div>'
if re.search(padrao_card_macro, html_content):
    html_content = re.sub(padrao_card_macro, novo_card_mapa_macro.strip(), html_content, count=1)
    print("Cards do grid macro atualizados com nome do pai e metragem!")

# 7. Injetar as funções JS do mapa antes do fechamento </script> principal
pos_end_script = html_content.find('setInterval(verificarStatusBackend, 10000);\n    });\n\n  </script>')
if pos_end_script == -1:
    pos_end_script = html_content.find('setInterval(verificarStatusBackend, 10000);')
    if pos_end_script != -1:
        pos_close = html_content.find('</script>', pos_end_script)
    else:
        pos_close = html_content.rfind('</script>')
else:
    pos_close = html_content.find('</script>', pos_end_script)

if pos_close != -1:
    html_content = html_content[:pos_close] + funcoes_mapa_js + "\n  " + html_content[pos_close:]
    print("Funções do Mapa 2D injetadas no script com sucesso!")
else:
    print("ERRO: Fechamento de script não encontrado!")

# 8. Garantir que renderizarModuloMapa2D() é chamado no DOMContentLoaded
padrao_dom_content = r"window\.addEventListener\('DOMContentLoaded',\s*\(\)\s*=>\s*\{"
sub_dom_content = """window.addEventListener('DOMContentLoaded', () => {
      renderizarModuloMapa2D();"""

if re.search(padrao_dom_content, html_content):
    html_content = re.sub(padrao_dom_content, sub_dom_content, html_content, count=1)
    print("renderizarModuloMapa2D adicionado ao DOMContentLoaded!")

# 9. Gravar arquivo HTML atualizado
HTML_PATH.write_text(html_content, encoding="utf-8")
print(f"dashboard_interativo_prototipo.html 100% gravado e pronto! Tamanho: {len(html_content)} bytes.")
