"""Endpoints REST e Motor Inteligente de PLN do Assistente WhatsApp do ERP CAMARÃO."""
import re
from datetime import date, datetime
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.database import get_db
from app.core.tenant import get_current_fazenda
from app.models.fazenda import Fazenda
from app.models.viveiro import Viveiro
from app.models.ciclo import CicloCultivo
from app.models.alimentacao import LancamentoAlimentacao
from app.models.agua import MonitoramentoAgua
from app.models.biometria import Biometria
from app.models.auditoria import AuditoriaPendencia
from app.schemas.whatsapp import WhatsAppMensagemEntrada, AlertaEmergenciaRequest
from app.services.zootecnia_service import ZootecniaService

router = APIRouter()


class WhatsAppChatSimulacao(BaseModel):
    """Payload para o simulador web de WhatsApp do dashboard."""
    texto: str
    remetente: Optional[str] = "Operador de Campo"


def identificar_viveiro(texto: str) -> Optional[str]:
    """Identifica o código canônico do viveiro (ex: V-01 a V-15)."""
    match = re.search(r"(?:v-|v|tanque\s*|viveiro\s*)(\d{1,2})", texto, re.IGNORECASE)
    if match:
        num = int(match.group(1))
        return f"V-{num:02d}"
    return None


@router.post("/webhook", summary="Webhook de entrada de mensagens do operador de campo")
def webhook_whatsapp(
    payload: WhatsAppMensagemEntrada,
    fazenda: Fazenda = Depends(get_current_fazenda),
    db: Session = Depends(get_db)
):
    """Recebe texto ou metadados de áudio, processa a intenção e enfileira para auditoria/registro."""
    texto = (payload.texto or "").strip()
    if not texto and not payload.audio_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A mensagem recebida não contém texto nem arquivo de mídia."
        )

    partes = texto.lower().split()
    viveiro_detectado = identificar_viveiro(texto) or "V-01"

    pendencia = AuditoriaPendencia(
        fazenda_id=fazenda.id,
        origem="WHATSAPP",
        entidade="ALIMENTACAO",
        viveiro_codigo=viveiro_detectado,
        data_evento=date.today(),
        tipo_anomalia="CONFLITO_DADOS",
        severidade="INFO",
        mensagem=f"Mensagem recebida de {payload.remetente}: '{texto}'. Aguardando confirmação de gravação.",
        dados_novos_json=f'{{"texto_original": "{texto}", "remetente": "{payload.remetente}"}}'
    )
    db.add(pendencia)
    db.commit()
    db.refresh(pendencia)

    return {
        "status": "recebido",
        "fazenda": fazenda.codigo,
        "remetente": payload.remetente,
        "pendencia_id": pendencia.id,
        "mensagem_confirmacao": f"Lançamento do viveiro {viveiro_detectado} na fazenda {fazenda.nome} pré-registrado na Central de Auditoria!"
    }


@router.post("/chat-interativo", summary="Processamento inteligente de mensagens de campo para o simulador web")
def chat_interativo_whatsapp(
    payload: WhatsAppChatSimulacao,
    fazenda: Fazenda = Depends(get_current_fazenda),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Interpreta em tempo real comandos zootécnicos em linguagem natural e executa ações diretas."""
    texto = payload.texto.strip()
    if not texto:
        return {"resposta": "Por favor, digite uma mensagem ou parâmetro de manejo."}

    texto_lower = texto.lower()
    viveiro_cod = identificar_viveiro(texto)

    # 1. Consulta Zootécnica (ex: "como tá o V-03", "qual a biomassa do v1", "status v-02")
    if any(termo in texto_lower for termo in ["como tá", "como esta", "biomassa", "fca", "resumo", "status", "peso"]) and viveiro_cod:
        viveiro = db.query(Viveiro).filter(
            Viveiro.fazenda_id == fazenda.id,
            Viveiro.codigo == viveiro_cod
        ).first()

        if not viveiro:
            return {"resposta": f"Viveiro {viveiro_cod} não encontrado na fazenda {fazenda.nome}."}

        ciclo = db.query(CicloCultivo).filter(
            CicloCultivo.fazenda_id == fazenda.id,
            CicloCultivo.viveiro_id == viveiro.id,
            CicloCultivo.status == "EM CULTIVO ATIVO"
        ).first()

        if not ciclo:
            return {"resposta": f"O viveiro {viveiro_cod} está atualmente vazio ou em preparação (sem ciclo ativo)."}

        doc_atual = (date.today() - ciclo.data_povoamento).days

        # Última biometria
        ultima_bio = db.query(Biometria).filter(
            Biometria.ciclo_id == ciclo.id
        ).order_by(desc(Biometria.data)).first()

        peso_txt = f"{ultima_bio.peso_medio_g:.2f}g" if ultima_bio else "Sem pesagem"
        bio_txt = f"{ultima_bio.biomassa_estimada_kg:.1f} kg" if ultima_bio and ultima_bio.biomassa_estimada_kg else "Calculando"
        fca_txt = f"{ultima_bio.fca_parcial:.2f}" if ultima_bio and ultima_bio.fca_parcial else "1.25 (est.)"

        # Último oxigênio
        ultimo_o2 = db.query(MonitoramentoAgua).filter(
            MonitoramentoAgua.viveiro_id == viveiro.id
        ).order_by(desc(MonitoramentoAgua.data)).first()

        o2_txt = f"Manhã: {ultimo_o2.o2_manha or '--'} | Noite: {ultimo_o2.o2_noite or '--'} mg/L" if ultimo_o2 else "Sem medição recente"

        resposta = (
            f"📊 *BOLETIM ZOOTÉCNICO - {viveiro_cod} ({fazenda.nome})*\n"
            f"• Lote: {ciclo.numero_lote} (DOC: {doc_atual} dias)\n"
            f"• População Inicial: {ciclo.pls_estocadas:,} PLs\n"
            f"• Peso Médio Atual: *{peso_txt}*\n"
            f"• Biomassa Viva Estimada: *{bio_txt}*\n"
            f"• FCA Parcial: *{fca_txt}*\n"
            f"• Oxigênio Recente: {o2_txt}\n"
            f"• Status: 🟢 Em Cultivo Normal"
        )
        return {"resposta": resposta, "tipo": "CONSULTA_ZOOTECNICA", "viveiro": viveiro_cod}

    # 2. Medição de Qualidade da Água (ex: "V-03 o2 2.6", "v02 oxigenio 4.5 ph 8.0")
    if "o2" in texto_lower or "oxigenio" in texto_lower or "oxigênio" in texto_lower:
        match_o2 = re.search(r"(?:o2|oxigênio|oxigenio)\s*[:=]?\s*(\d+(?:[.,]\d+)?)", texto_lower)
        valor_o2 = float(match_o2.group(1).replace(",", ".")) if match_o2 else None

        if valor_o2 is not None and viveiro_cod:
            viveiro = db.query(Viveiro).filter(
                Viveiro.fazenda_id == fazenda.id,
                Viveiro.codigo == viveiro_cod
            ).first()

            if viveiro:
                eh_critico = valor_o2 < 3.0
                severidade = "CRITICA" if eh_critico else "INFO"

                pend = AuditoriaPendencia(
                    fazenda_id=fazenda.id,
                    origem="WHATSAPP",
                    entidade="AGUA",
                    viveiro_codigo=viveiro_cod,
                    data_evento=date.today(),
                    tipo_anomalia="O2_CRITICO" if eh_critico else "REGISTRO_AGUA",
                    severidade=severidade,
                    mensagem=f"Medição de O2 via WhatsApp: {valor_o2:.2f} mg/L por {payload.remetente}."
                )
                db.add(pend)

                medicao_hoje = db.query(MonitoramentoAgua).filter(
                    MonitoramentoAgua.viveiro_id == viveiro.id,
                    MonitoramentoAgua.data == date.today()
                ).first()

                if not medicao_hoje:
                    medicao_hoje = MonitoramentoAgua(
                        fazenda_id=fazenda.id,
                        viveiro_id=viveiro.id,
                        data=date.today(),
                        o2_manha=valor_o2,
                        status_tanque="CRITICO" if eh_critico else "OTIMO"
                    )
                    db.add(medicao_hoje)
                else:
                    medicao_hoje.o2_manha = valor_o2
                    if eh_critico:
                        medicao_hoje.status_tanque = "CRITICO"

                db.commit()

                if eh_critico:
                    resposta = (
                        f"🚨 *ALERTA VERMELHO DE ASFIXIA - {viveiro_cod}*\n"
                        f"• Oxigênio medido: *{valor_o2:.1f} mg/L* (CRÍTICO < 3.0 mg/L)!\n"
                        f"• PROTOCOLO IMEDIATO:\n"
                        f"  1. Ligar imediatamente todos os aeradores do {viveiro_cod};\n"
                        f"  2. SUSPENDER o próximo trato de ração;\n"
                        f"  3. Vigia noturno e encarregado foram notificados na Central de Auditoria!"
                    )
                else:
                    resposta = (
                        f"✅ *Medição de Oxigênio Registrada - {viveiro_cod}*\n"
                        f"• O2 Matutino: *{valor_o2:.1f} mg/L* (Parâmetro normal e seguro).\n"
                        f"• Status: 🟢 Tanque Saudável."
                    )
                return {"resposta": resposta, "tipo": "MEDICAO_AGUA", "o2": valor_o2, "critico": eh_critico}

    # 3. Lançamento de Arraçoamento (ex: "V-03 14kg tarde sobra 1", "v02 10 kilos manha")
    match_kg = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:kg|kilos|quilos)", texto_lower)
    if match_kg and viveiro_cod:
        kg_valor = float(match_kg.group(1).replace(",", "."))
        turno = "TARDE" if "tarde" in texto_lower else "MANHA"
        
        match_sobra = re.search(r"sobra\s*(\d)", texto_lower)
        sobra_val = int(match_sobra.group(1)) if match_sobra else 0

        viveiro = db.query(Viveiro).filter(
            Viveiro.fazenda_id == fazenda.id,
            Viveiro.codigo == viveiro_cod
        ).first()

        if viveiro:
            ciclo = db.query(CicloCultivo).filter(
                CicloCultivo.fazenda_id == fazenda.id,
                CicloCultivo.viveiro_id == viveiro.id,
                CicloCultivo.status == "EM CULTIVO ATIVO"
            ).first()

            if not ciclo:
                # Cria ciclo provisório para garantir registro em campo
                ciclo = CicloCultivo(
                    fazenda_id=fazenda.id,
                    viveiro_id=viveiro.id,
                    numero_lote=f"LOTE-{viveiro_cod}-ATIVO",
                    data_povoamento=date.today(),
                    pls_estocadas=60000,
                    status="EM CULTIVO ATIVO"
                )
                db.add(ciclo)
                db.flush()

            # Localiza ou cria o lançamento de hoje
            trato_hoje = db.query(LancamentoAlimentacao).filter(
                LancamentoAlimentacao.ciclo_id == ciclo.id,
                LancamentoAlimentacao.data == date.today()
            ).first()

            doc_atual = (date.today() - ciclo.data_povoamento).days

            if not trato_hoje:
                trato_hoje = LancamentoAlimentacao(
                    fazenda_id=fazenda.id,
                    ciclo_id=ciclo.id,
                    data=date.today(),
                    doc=doc_atual if doc_atual > 0 else 1,
                    racao_manha_kg=kg_valor if turno == "MANHA" else 0.0,
                    sobra_manha=sobra_val if turno == "MANHA" else None,
                    racao_tarde_kg=kg_valor if turno == "TARDE" else 0.0,
                    sobra_tarde=sobra_val if turno == "TARDE" else None,
                    total_dia_kg=kg_valor,
                    consumo_acumulado_kg=kg_valor,
                    observacoes=f"Lançado via WhatsApp por {payload.remetente}"
                )
                db.add(trato_hoje)
            else:
                if turno == "MANHA":
                    trato_hoje.racao_manha_kg = kg_valor
                    trato_hoje.sobra_manha = sobra_val
                else:
                    trato_hoje.racao_tarde_kg = kg_valor
                    trato_hoje.sobra_tarde = sobra_val
                trato_hoje.total_dia_kg = (trato_hoje.racao_manha_kg or 0.0) + (trato_hoje.racao_tarde_kg or 0.0)

            if sobra_val == 3:
                pend = AuditoriaPendencia(
                    fazenda_id=fazenda.id,
                    origem="WHATSAPP",
                    entidade="ALIMENTACAO",
                    viveiro_codigo=viveiro_cod,
                    data_evento=date.today(),
                    tipo_anomalia="SOBRA_EXCESSIVA",
                    severidade="ATENCAO",
                    mensagem=f"Sobra nível 3 (Muita ração na bandeja) no {viveiro_cod} turno {turno}!"
                )
                db.add(pend)

            db.commit()

            resposta = (
                f"✅ *Trato Registrado com Sucesso - {viveiro_cod}*\n"
                f"• Turno: *{turno}*\n"
                f"• Ração Fornecida: *{kg_valor:.1f} kg*\n"
                f"• Sobra de Bandeja: *Nível {sobra_val}*\n"
                f"• Total do Dia: *{trato_hoje.total_dia_kg:.1f} kg*\n"
                f"• Sincronizado no banco do ERP CAMARÃO."
            )
            return {"resposta": resposta, "tipo": "ARRACAMENTO", "viveiro": viveiro_cod, "kg": kg_valor}

    # 4. Caso padrão / Observação de rotina
    pend = AuditoriaPendencia(
        fazenda_id=fazenda.id,
        origem="WHATSAPP",
        entidade="OUTROS",
        viveiro_codigo=viveiro_cod or "GERAL",
        data_evento=date.today(),
        tipo_anomalia="MENSAGEM_CAMPO",
        severidade="INFO",
        mensagem=f"Nota de campo de {payload.remetente}: '{texto}'"
    )
    db.add(pend)
    db.commit()

    resposta = (
        f"📝 Mensagem registrada na Central de Auditoria da {fazenda.nome}!\n"
        f"Texto: \"{texto}\"\n"
        f"Se desejar lançar trato, use o padrão: *V-03 12kg tarde sobra 0*\n"
        f"Para oxigênio: *V-03 o2 4.2*\n"
        f"Para consultar: *como tá o V-03*"
    )
    return {"resposta": resposta, "tipo": "GERAL"}


@router.post("/alerta-emergencia", summary="Disparar alerta de emergência de campo (ex: vigia noturno)")
def disparar_alerta_emergencia(
    alerta: AlertaEmergenciaRequest,
    fazenda: Fazenda = Depends(get_current_fazenda),
    db: Session = Depends(get_db)
):
    """Envia notificação crítica imediata para o vigia noturno ou equipe de aeração."""
    if alerta.parametro_critico == "Oxigênio Dissolvido < 3.0 mg/L" or alerta.valor_aferido < 3.0:
        severidade = "CRITICA"
    else:
        severidade = "ATENCAO"

    pendencia = AuditoriaPendencia(
        fazenda_id=fazenda.id,
        origem="WHATSAPP",
        entidade="AGUA",
        viveiro_codigo=alerta.viveiro_codigo,
        data_evento=date.today(),
        tipo_anomalia="O2_CRITICO",
        severidade=severidade,
        mensagem=f"ALERTA EMITIDO PARA {alerta.destinatario}: {alerta.mensagem} (Valor: {alerta.valor_aferido})"
    )
    db.add(pendencia)
    db.commit()

    return {
        "status": "alerta_disparado",
        "fazenda": fazenda.codigo,
        "destinatario": alerta.destinatario,
        "viveiro": alerta.viveiro_codigo,
        "severidade": severidade,
        "mensagem_entregue": alerta.mensagem
    }
