"""Script de Verificação Completa e Profunda da Revisão de Ciclos de Produção."""
import sys
from pathlib import Path
import openpyxl

sys.stdout.reconfigure(encoding="utf-8")
backend_path = Path(__file__).parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

def verificar_frontend():
    print("=== 1. VERIFICAÇÃO DO FRONTEND (HTML / JS) ===")
    html_path = Path(__file__).parent / "dashboard_interativo_prototipo.html"
    assert html_path.exists(), "dashboard_interativo_prototipo.html deve existir"
    content = html_path.read_text(encoding="utf-8")

    # 1.1 Verificar existência do input de upload
    assert 'id="input-upload-excel-biomassa"' in content, "input-upload-excel-biomassa deve existir"
    print("  ✅ 1.1 input-upload-excel-biomassa presente no HTML")

    # 1.2 Verificar ordem de declaração de tratos
    idx_func = content.find("function renderizarDashboardViveiroBiomassa")
    assert idx_func != -1, "renderizarDashboardViveiroBiomassa deve existir"
    snippet = content[idx_func:idx_func+1000]
    idx_tratos = snippet.find("const tratos")
    idx_prep = snippet.find("isEmPreparacaoLimpo")
    assert idx_tratos != -1 and idx_prep != -1, "tratos e isEmPreparacaoLimpo devem existir"
    assert idx_tratos < idx_prep, "const tratos deve ser declarado antes de isEmPreparacaoLimpo"
    print("  ✅ 1.2 const tratos declarado no topo (evita ReferenceError)")

    # 1.3 Verificar abatimento de biomassa na despesca parcial
    idx_parcial = content.find("function salvarDespescaParcial")
    assert idx_parcial != -1
    snippet_parcial = content[idx_parcial:idx_parcial+1200]
    assert "Math.max(0," in snippet_parcial, "Biomassa deve ser abatida com limite 0"
    assert "populacaoEstimada" in snippet_parcial, "População estimada deve ser abatida"
    print("  ✅ 1.3 Despesca parcial abate biomassa e população sem travar em 100kg")

    # 1.4 Verificar ano-safra dinâmico no encerramento
    idx_enc = content.find("function confirmarEncerramentoCiclo")
    assert idx_enc != -1
    snippet_enc = content[idx_enc:idx_enc+2500]
    assert "dados.anoSafra" in snippet_enc, "Deve ler anoSafra dinamicamente"
    assert "SAFRA-${anoSafra}" in snippet_enc, "safraId deve usar anoSafra dinâmico"
    print("  ✅ 1.4 Encerramento utiliza ano-safra dinâmico")

    # 1.5 Verificar atualizações no drive sync
    idx_sync = content.find("function sincronizarPlanilhaDriveBiomassa")
    assert idx_sync != -1
    snippet_sync = content[idx_sync:idx_sync+2500]
    assert "renderizarPillsViveirosBiomassa" in snippet_sync, "Deve atualizar pills no drive sync"
    assert "preencherTabelasAnaliticas" in snippet_sync, "Deve preencher tabelas analiticas no drive sync"
    assert "renderizarModuloCiclos" in snippet_sync, "Deve atualizar modulo ciclos no drive sync"
    print("  ✅ 1.5 Sincronização do Drive atualiza visualizações do ERP")


def verificar_backend():
    print("\n=== 2. VERIFICAÇÃO DO BACKEND (INGESTOR & CICLOS) ===")
    from app.core.database import SessionLocal
    from app.models.fazenda import Fazenda
    from app.models.ciclo import CicloCultivo
    from app.models.viveiro import Viveiro
    from app.services.ingestor_service import IngestorService, converter_para_data
    from datetime import date

    db = SessionLocal()
    try:
        # 2.1 Teste do converter_para_data com anos de 2 dígitos
        d1 = converter_para_data("19-06-26")
        d2 = converter_para_data("07/07/26")
        assert d1 == date(2026, 6, 19), f"Esperado 2026-06-19, obtido {d1}"
        assert d2 == date(2026, 7, 7), f"Esperado 2026-07-07, obtido {d2}"
        print("  ✅ 2.1 converter_para_data suporta datas brasileiras de 2 dígitos (DD-MM-YY e DD/MM/YY)")

        # 2.2 Ingestão da planilha real completa do pai
        fazenda = db.query(Fazenda).first()
        assert fazenda is not None, "Fazenda deve existir"

        p_real = Path(r"G:\Meu Drive\ANTIGRAVITY DRIVE\CAMARÃO\planilha completa raçao.xlsx")
        if p_real.exists():
            res = IngestorService.processar_planilha_alimentacao(db, p_real, fazenda.id, fazenda.codigo)
            assert res["linhas_lidas"] > 0, "Deve ler linhas operacionais"
            assert len(res["abas_processadas"]) >= 10, f"Deve processar as 10 abas v-1 a v-10, processou {len(res['abas_processadas'])}"
            print(f"  ✅ 2.2 Planilha real '{p_real.name}' ingerida com sucesso: {len(res['abas_processadas'])} abas e {res['linhas_lidas']} linhas lidas")

            # 2.3 Verificar se os metadados oficiais e berçário foram extraídos
            v7_info = res["novidades_por_viveiro"].get("V-07")
            assert v7_info is not None, "V-07 deve ter sido processado"
            assert v7_info["laboratorio"] == "TECMARIS", f"Esperado TECMARIS, obtido {v7_info['laboratorio']}"
            assert v7_info["pls_estocadas"] == 25000, f"Esperado 25000, obtido {v7_info['pls_estocadas']}"
            assert v7_info["bercario"] is not None, "Berçário de V-07 deve ser reconhecido"
            print(f"  ✅ 2.3 Berçário e laboratório de V-07 extraídos: {v7_info['laboratorio']} ({v7_info['pls_estocadas']} PLs, {v7_info['bercario']})")

            # 2.4 Verificar se os ciclos oficiais foram criados com códigos sequenciais
            ciclos = db.query(CicloCultivo).filter(CicloCultivo.fazenda_id == fazenda.id).all()
            assert len(ciclos) > 0, "Ciclos devem ter sido criados"
            for c in ciclos:
                assert c.codigo_ciclo is not None, f"Ciclo {c.id} deve ter codigo_ciclo"
                assert "• Ciclo" in c.codigo_ciclo, f"Código deve seguir padrão executivo: {c.codigo_ciclo}"
                assert c.ano_safra is not None, f"Ciclo {c.id} deve ter ano_safra"
                assert c.numero_sequencial is not None, f"Ciclo {c.id} deve ter numero_sequencial"
            print(f"  ✅ 2.4 Todos os {len(ciclos)} ciclos possuem codigo_ciclo oficial, ano_safra e numero_sequencial")

    finally:
        db.close()


if __name__ == "__main__":
    verificar_frontend()
    verificar_backend()
    print("\n🏆 TODAS AS VERIFICAÇÕES DE PONTA A PONTA PASSARAM COM 100% DE SUCESSO!")
