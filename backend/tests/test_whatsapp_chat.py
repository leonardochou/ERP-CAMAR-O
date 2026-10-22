"""Testes para o motor de chat interativo do WhatsApp e PLN zootécnico."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.fazenda import Fazenda
from app.models.viveiro import Viveiro
from app.models.ciclo import CicloCultivo
from datetime import date


def test_chat_consulta_zootecnica(client: TestClient, db_session: Session, fazenda_arrendada: Fazenda):
    """Testa consulta via linguagem natural 'como tá o V-01'."""
    # Prepara um ciclo ativo para V-01
    viv = db_session.query(Viveiro).filter(Viveiro.codigo == "V-01").first()
    if viv:
        ciclo = CicloCultivo(
            fazenda_id=fazenda_arrendada.id,
            viveiro_id=viv.id,
            numero_lote="LOTE-TESTE-V01",
            data_povoamento=date(2026, 6, 1),
            pls_estocadas=60000,
            status="EM CULTIVO ATIVO"
        )
        db_session.add(ciclo)
        db_session.commit()

    resp = client.post(
        "/api/v1/whatsapp/chat-interativo",
        json={"texto": "como tá o V-01?", "remetente": "Pai / Campo"}
    )
    assert resp.status_code == 200
    dados = resp.json()
    assert "BOLETIM ZOOTÉCNICO" in dados["resposta"]
    assert "V-01" in dados["resposta"]


def test_chat_oxigenio_critico(client: TestClient):
    """Testa envio de medição de O2 crítico gerando protocolo de emergência."""
    resp = client.post(
        "/api/v1/whatsapp/chat-interativo",
        json={"texto": "V-03 o2 2.4 urgente", "remetente": "Vigia Noturno"}
    )
    assert resp.status_code == 200
    dados = resp.json()
    assert dados["critico"] is True
    assert "ALERTA VERMELHO" in dados["resposta"]
    assert "aeradores" in dados["resposta"].lower()


def test_chat_arracoamento(client: TestClient):
    """Testa lançamento de trato de arraçoamento via texto simples."""
    resp = client.post(
        "/api/v1/whatsapp/chat-interativo",
        json={"texto": "V-02 12kg tarde sobra 0", "remetente": "Operador"}
    )
    assert resp.status_code == 200
    dados = resp.json()
    assert dados["tipo"] == "ARRACAMENTO"
    assert "Trato Registrado" in dados["resposta"]
