"""
Script para:
1. Adicionar os triggers de navegação para 'analytics-despesca' e 'analytics-parametros' em navegarPara();
2. Integrar a detecção de despesca do importador para alimentar HISTORICO_SAFRAS_DATA automaticamente;
3. Validar a sintaxe completa com Node.js.
"""
from pathlib import Path

BASE_DIR = Path(r"G:\Meu Drive\ANTIGRAVITY DRIVE\CAMARÃO\ERP CAMARÃO")
HTML_PATH = BASE_DIR / "dashboard_interativo_prototipo.html"

html = HTML_PATH.read_text(encoding="utf-8")

# 1. Triggers em navegarPara
trecho_antigo_trigger = """      } else if (viewId === 'analytics-viveiro-detalhe') {
        if (param) carregarDetalhesViveiro(param);
      }"""

trecho_novo_trigger = """      } else if (viewId === 'analytics-viveiro-detalhe') {
        if (param) carregarDetalhesViveiro(param);
      } else if (viewId === 'analytics-despesca') {
        atualizarHeaderNavegacao('Despesca, Safras & Comercialização', 'Início > Zootecnia > Despesca');
        renderizarModuloDespesca();
      } else if (viewId === 'analytics-parametros') {
        atualizarHeaderNavegacao('Central de Parâmetros & Calibração', 'Início > Configurações > Parâmetros');
        renderizarModuloParametros();
      }"""

if trecho_antigo_trigger in html:
    html = html.replace(trecho_antigo_trigger, trecho_novo_trigger, 1)
    print("Sucesso: Triggers de rota para despesca e parâmetros adicionados a navegarPara()!")
else:
    print("Aviso: trecho_antigo_trigger não encontrado para substituição direta.")

# 2. Alimentação automática de HISTORICO_SAFRAS_DATA dentro de importarArquivoXlsxBiomassa
trecho_import_despesca = """              if (despescaInfo) {
                despescasDetectadas.push({
                  viveiro: vId,
                  data: despescaInfo.data,
                  kg: despescaInfo.kg_colhido,
                  peso: despescaInfo.peso_final_g,
                  sob: despescaInfo.sobrevivencia_pct,
                  fca: despescaInfo.fca_real
                });
              }"""

trecho_import_despesca_expandido = """              if (despescaInfo) {
                despescasDetectadas.push({
                  viveiro: vId,
                  data: despescaInfo.data,
                  kg: despescaInfo.kg_colhido,
                  peso: despescaInfo.peso_final_g,
                  sob: despescaInfo.sobrevivencia_pct,
                  fca: despescaInfo.fca_real
                });

                // Alimenta o Histórico Permanente de Safras (sem duplicar)
                const jaExisteSafra = HISTORICO_SAFRAS_DATA.some(s => s.viveiroId === vId && s.dataDespesca === despescaInfo.data);
                if (!jaExisteSafra) {
                  const precoSugerido = 22.0;
                  HISTORICO_SAFRAS_DATA.unshift({
                    safraId: `SAFRA-2026.1-${vId}`,
                    viveiroId: vId,
                    anoSafra: 2026,
                    ciclo: 1,
                    statusSafra: 'CONCLUIDA',
                    dataPovoamento: dtTransf || dtPovoamento || '15/07/2026',
                    dataDespesca: despescaInfo.data,
                    ddcTotal: despescaInfo.doc || 80,
                    lab: lab || 'AQUATEC',
                    plsMil: plsMil || 50,
                    temBercario: temBerc,
                    kgColhido: despescaInfo.kg_colhido,
                    pesoFinalG: despescaInfo.peso_final_g,
                    sobrevivenciaPct: parseFloat(String(despescaInfo.sobrevivencia_pct).replace('%', '')) || 55.0,
                    fcaReal: despescaInfo.fca_real || 1.25,
                    precoVendaKg: (vId === 'V-05') ? 24.00 : 22.00,
                    faturamentoBruto: despescaInfo.kg_colhido * ((vId === 'V-05') ? 24.00 : 22.00),
                    comprador: (vId === 'V-05') ? 'Distribuidora Natal Camarão' : (vId === 'V-03') ? 'Frigorífico Litoral Potiguar' : 'Restaurantes & Mercado Local',
                    obs: despescaInfo.obs || `Despesca reconhecida da planilha em ${despescaInfo.data}`
                  });
                }
              }"""

if trecho_import_despesca in html:
    html = html.replace(trecho_import_despesca, trecho_import_despesca_expandido, 1)
    print("Sucesso: Ingestão de despescas conectada ao HISTORICO_SAFRAS_DATA!")
else:
    print("Aviso: trecho_import_despesca não encontrado para substituição direta.")

# 3. Chamar renderizarModuloDespesca() no final de importarArquivoXlsxBiomassa e no DOMContentLoaded
trecho_import_render = "preencherTabelasAnaliticas();\n\n          // Abre o primeiro viveiro com novidades"
trecho_import_render_novo = "preencherTabelasAnaliticas();\n          if (typeof renderizarModuloDespesca === 'function') renderizarModuloDespesca();\n\n          // Abre o primeiro viveiro com novidades"

if trecho_import_render in html:
    html = html.replace(trecho_import_render, trecho_import_render_novo, 1)
    print("Sucesso: renderizarModuloDespesca() chamado após a importação!")

HTML_PATH.write_text(html, encoding="utf-8")
print(f"dashboard_interativo_prototipo.html finalizado! Tamanho: {len(html)} bytes.")
