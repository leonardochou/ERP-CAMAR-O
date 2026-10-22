"""Endpoints REST para Gestão de Colaboradores, Vigia Noturno, Escalas e Ocorrências."""
from typing import List, Optional
from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.core.database import get_db
from app.core.tenant import get_current_fazenda
from app.models.fazenda import Fazenda
from app.models.funcionario import Funcionario, EscalaTrabalho
from app.models.viveiro import Viveiro
from app.schemas.funcionario import (
    FuncionarioCreate,
    FuncionarioUpdate,
    FuncionarioResponse,
    EscalaItemResponse,
    EscalaLoteRequest,
    EscalaApontamentoOcorrenciaRequest,
    EscalaTemplateRequest,
    CheckInVigiaRequest,
    ResumoCustosEquipeResponse
)

router = APIRouter()


# -------------------------------------------------------------
# COLABORADORES (CRUD)
# -------------------------------------------------------------
@router.get("/funcionarios", response_model=List[FuncionarioResponse], summary="Listar colaboradores da fazenda")
def listar_funcionarios(
    cargo: Optional[str] = None,
    ativo: Optional[bool] = None,
    fazenda: Fazenda = Depends(get_current_fazenda),
    db: Session = Depends(get_db)
):
    """Lista os funcionários cadastrados na fazenda ativa."""
    query = db.query(Funcionario).filter(Funcionario.fazenda_id == fazenda.id)
    if cargo:
        query = query.filter(Funcionario.cargo.ilike(f"%{cargo}%"))
    if ativo is not None:
        query = query.filter(Funcionario.ativo == ativo)
    return query.order_by(Funcionario.cargo, Funcionario.nome).all()


@router.post("/funcionarios", response_model=FuncionarioResponse, status_code=status.HTTP_201_CREATED, summary="Cadastrar colaborador")
def criar_funcionario(
    func_in: FuncionarioCreate,
    fazenda: Fazenda = Depends(get_current_fazenda),
    db: Session = Depends(get_db)
):
    """Cadastra um novo membro da equipe com dados contratuais e de remuneração."""
    novo = Funcionario(
        fazenda_id=fazenda.id,
        nome=func_in.nome.strip(),
        apelido=func_in.apelido.strip() if func_in.apelido else None,
        cargo=func_in.cargo.strip(),
        telefone=func_in.telefone,
        whatsapp=func_in.whatsapp,
        chave_pix=func_in.chave_pix,
        tipo_contrato=func_in.tipo_contrato.upper(),
        salario_base_mensal=round(func_in.salario_base_mensal, 2),
        valor_diaria_extra=round(func_in.valor_diaria_extra, 2),
        encargos_estimados_pct=func_in.encargos_estimados_pct,
        ativo=func_in.ativo,
        data_admissao=func_in.data_admissao or date.today(),
        observacoes=func_in.observacoes
    )
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo


@router.get("/funcionarios/{id}", response_model=FuncionarioResponse, summary="Obter dados de um colaborador")
def obter_funcionario(
    id: int,
    fazenda: Fazenda = Depends(get_current_fazenda),
    db: Session = Depends(get_db)
):
    func = db.query(Funcionario).filter(Funcionario.id == id, Funcionario.fazenda_id == fazenda.id).first()
    if not func:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Colaborador não encontrado.")
    return func


@router.put("/funcionarios/{id}", response_model=FuncionarioResponse, summary="Atualizar dados do colaborador")
def atualizar_funcionario(
    id: int,
    func_in: FuncionarioUpdate,
    fazenda: Fazenda = Depends(get_current_fazenda),
    db: Session = Depends(get_db)
):
    func = db.query(Funcionario).filter(Funcionario.id == id, Funcionario.fazenda_id == fazenda.id).first()
    if not func:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Colaborador não encontrado.")

    for campo, valor in func_in.dict(exclude_unset=True).items():
        setattr(func, campo, valor)

    db.commit()
    db.refresh(func)
    return func


@router.delete("/funcionarios/{id}", summary="Inativar colaborador")
def inativar_funcionario(
    id: int,
    fazenda: Fazenda = Depends(get_current_fazenda),
    db: Session = Depends(get_db)
):
    func = db.query(Funcionario).filter(Funcionario.id == id, Funcionario.fazenda_id == fazenda.id).first()
    if not func:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Colaborador não encontrado.")
    func.ativo = False
    db.commit()
    return {"message": f"Colaborador '{func.nome}' inativado com sucesso."}


# -------------------------------------------------------------
# ESCALAS, HORÁRIOS, FOLGAS & OCORRÊNCIAS
# -------------------------------------------------------------
@router.get("/escalas", response_model=List[EscalaItemResponse], summary="Consultar grade da equipe no período")
def listar_escalas(
    data_inicio: date = Query(..., description="Data inicial"),
    data_fim: date = Query(..., description="Data final"),
    funcionario_id: Optional[int] = None,
    fazenda: Fazenda = Depends(get_current_fazenda),
    db: Session = Depends(get_db)
):
    """Retorna os turnos, folgas, ocorrências e diárias de cada colaborador no intervalo."""
    query = db.query(EscalaTrabalho).join(Funcionario).filter(
        EscalaTrabalho.fazenda_id == fazenda.id,
        EscalaTrabalho.data >= data_inicio,
        EscalaTrabalho.data <= data_fim
    )
    if funcionario_id:
        query = query.filter(EscalaTrabalho.funcionario_id == funcionario_id)

    itens = query.order_by(EscalaTrabalho.data, Funcionario.nome).all()
    resultado = []
    for item in itens:
        resp = EscalaItemResponse.model_validate(item)
        resp.funcionario_nome = item.funcionario.nome
        resp.funcionario_apelido = item.funcionario.apelido
        resp.funcionario_cargo = item.funcionario.cargo
        resultado.append(resp)
    return resultado


@router.post("/escalas/apontamento", response_model=EscalaItemResponse, summary="Registrar ocorrência, falta ou diária extra de um dia")
def salvar_apontamento_dia(
    apontamento: EscalaApontamentoOcorrenciaRequest,
    fazenda: Fazenda = Depends(get_current_fazenda),
    db: Session = Depends(get_db)
):
    """Registra ou atualiza pontualmente a situação de um colaborador em um dia específico."""
    func = db.query(Funcionario).filter(Funcionario.id == apontamento.funcionario_id, Funcionario.fazenda_id == fazenda.id).first()
    if not func:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Colaborador não encontrado.")

    escala = db.query(EscalaTrabalho).filter(
        EscalaTrabalho.fazenda_id == fazenda.id,
        EscalaTrabalho.funcionario_id == func.id,
        EscalaTrabalho.data == apontamento.data
    ).first()

    valor_diaria = apontamento.valor_diaria_aplicado
    if apontamento.eh_extra and valor_diaria <= 0:
        valor_diaria = func.valor_diaria_extra or 0.0

    if not escala:
        escala = EscalaTrabalho(
            fazenda_id=fazenda.id,
            funcionario_id=func.id,
            data=apontamento.data,
            turno=apontamento.turno,
            eh_extra=apontamento.eh_extra,
            valor_diaria_aplicado=valor_diaria,
            status_presenca=apontamento.status_presenca,
            categoria_ocorrencia=apontamento.categoria_ocorrencia,
            observacoes=apontamento.observacoes
        )
        db.add(escala)
    else:
        escala.turno = apontamento.turno
        escala.eh_extra = apontamento.eh_extra
        escala.valor_diaria_aplicado = valor_diaria
        escala.status_presenca = apontamento.status_presenca
        escala.categoria_ocorrencia = apontamento.categoria_ocorrencia
        escala.observacoes = apontamento.observacoes

    db.commit()
    db.refresh(escala)

    resp = EscalaItemResponse.model_validate(escala)
    resp.funcionario_nome = func.nome
    resp.funcionario_apelido = func.apelido
    resp.funcionario_cargo = func.cargo
    return resp


@router.post("/escalas/lote", summary="Salvar ou atualizar escala em lote")
def salvar_escala_lote(
    lote_in: EscalaLoteRequest,
    fazenda: Fazenda = Depends(get_current_fazenda),
    db: Session = Depends(get_db)
):
    """Grava múltiplos dias da grade de horários de forma transacional."""
    processados = 0
    for item in lote_in.itens:
        escala = db.query(EscalaTrabalho).filter(
            EscalaTrabalho.fazenda_id == fazenda.id,
            EscalaTrabalho.funcionario_id == item.funcionario_id,
            EscalaTrabalho.data == item.data
        ).first()

        if not escala:
            escala = EscalaTrabalho(
                fazenda_id=fazenda.id,
                funcionario_id=item.funcionario_id,
                data=item.data,
                turno=item.turno,
                eh_extra=item.eh_extra,
                valor_diaria_aplicado=item.valor_diaria_aplicado,
                check_in_hora=item.check_in_hora,
                check_out_hora=item.check_out_hora,
                status_presenca=item.status_presenca,
                categoria_ocorrencia=item.categoria_ocorrencia,
                observacoes=item.observacoes
            )
            db.add(escala)
        else:
            escala.turno = item.turno
            escala.eh_extra = item.eh_extra
            escala.valor_diaria_aplicado = item.valor_diaria_aplicado
            if item.check_in_hora:
                escala.check_in_hora = item.check_in_hora
            if item.check_out_hora:
                escala.check_out_hora = item.check_out_hora
            escala.status_presenca = item.status_presenca
            escala.categoria_ocorrencia = item.categoria_ocorrencia
            escala.observacoes = item.observacoes
        processados += 1

    db.commit()
    return {"message": f"{processados} registros de escala salvos com sucesso."}


@router.post("/escalas/template-12x36", summary="Gerar escala 12x36 alternada para vigias noturnos")
def aplicar_template_12x36(
    template_in: EscalaTemplateRequest,
    fazenda: Fazenda = Depends(get_current_fazenda),
    db: Session = Depends(get_db)
):
    """Gera o revezamento 12x36 entre vigias no período (uma noite de vigia, outra de folga)."""
    if len(template_in.funcionario_ids) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A escala 12x36 requer ao menos 2 colaboradores para alternância."
        )

    delta_dias = (template_in.data_fim - template_in.data_inicio).days + 1
    total_vigias = len(template_in.funcionario_ids)
    registros = 0

    for d in range(delta_dias):
        data_atual = template_in.data_inicio + timedelta(days=d)
        vigia_ativo_idx = d % total_vigias

        for idx, func_id in enumerate(template_in.funcionario_ids):
            is_vigia = (idx == vigia_ativo_idx)
            turno = "NOTURNO_VIGIA" if is_vigia else "FOLGA"

            escala = db.query(EscalaTrabalho).filter(
                EscalaTrabalho.fazenda_id == fazenda.id,
                EscalaTrabalho.funcionario_id == func_id,
                EscalaTrabalho.data == data_atual
            ).first()

            if not escala:
                escala = EscalaTrabalho(
                    fazenda_id=fazenda.id,
                    funcionario_id=func_id,
                    data=data_atual,
                    turno=turno,
                    check_in_hora="21:00" if is_vigia else None,
                    check_out_hora="06:00" if is_vigia else None,
                    status_presenca="AGENDADO"
                )
                db.add(escala)
            else:
                escala.turno = turno
                if is_vigia:
                    escala.check_in_hora = "21:00"
                    escala.check_out_hora = "06:00"
            registros += 1

    db.commit()
    return {"message": f"Escala 12x36 gerada para {total_vigias} vigias ({registros} turnos programados)."}


@router.post("/escalas/template-6x1", summary="Gerar escala 6x1 com folga semanal para tratadores")
def aplicar_template_6x1(
    template_in: EscalaTemplateRequest,
    fazenda: Fazenda = Depends(get_current_fazenda),
    db: Session = Depends(get_db)
):
    """Gera escala 6x1 de trabalho diurno com 1 folga semanal fixa/rotativa."""
    delta_dias = (template_in.data_fim - template_in.data_inicio).days + 1
    folga_dia_semana = template_in.dia_folga_semanal if template_in.dia_folga_semanal is not None else 6  # Domingo
    registros = 0

    for d in range(delta_dias):
        data_atual = template_in.data_inicio + timedelta(days=d)
        is_folga = (data_atual.weekday() == folga_dia_semana)
        turno = "FOLGA" if is_folga else "DIURNO"

        for func_id in template_in.funcionario_ids:
            escala = db.query(EscalaTrabalho).filter(
                EscalaTrabalho.fazenda_id == fazenda.id,
                EscalaTrabalho.funcionario_id == func_id,
                EscalaTrabalho.data == data_atual
            ).first()

            if not escala:
                escala = EscalaTrabalho(
                    fazenda_id=fazenda.id,
                    funcionario_id=func_id,
                    data=data_atual,
                    turno=turno,
                    check_in_hora="06:30" if not is_folga else None,
                    check_out_hora="17:00" if not is_folga else None,
                    status_presenca="AGENDADO"
                )
                db.add(escala)
            else:
                escala.turno = turno
            registros += 1

    db.commit()
    return {"message": f"Escala 6x1 aplicada com sucesso ({registros} apontamentos)."}


@router.post("/escalas/{id}/check-in", response_model=EscalaItemResponse, summary="Registrar check-in / check-out do vigia")
def checkin_vigia(
    id: int,
    check_in_in: CheckInVigiaRequest,
    fazenda: Fazenda = Depends(get_current_fazenda),
    db: Session = Depends(get_db)
):
    """Registra a presença e os horários de entrada e saída do vigia na ronda noturna."""
    escala = db.query(EscalaTrabalho).filter(EscalaTrabalho.id == id, EscalaTrabalho.fazenda_id == fazenda.id).first()
    if not escala:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro de escala não encontrado.")

    if check_in_in.check_in_hora:
        escala.check_in_hora = check_in_in.check_in_hora
    if check_in_in.check_out_hora:
        escala.check_out_hora = check_in_in.check_out_hora
    escala.status_presenca = check_in_in.status_presenca
    if check_in_in.observacoes:
        escala.observacoes = check_in_in.observacoes

    db.commit()
    db.refresh(escala)

    resp = EscalaItemResponse.model_validate(escala)
    resp.funcionario_nome = escala.funcionario.nome
    resp.funcionario_apelido = escala.funcionario.apelido
    resp.funcionario_cargo = escala.funcionario.cargo
    return resp


# -------------------------------------------------------------
# CONSOLIDAÇÃO FINANCEIRA & VIGIA NOTURNO HOJE
# -------------------------------------------------------------
@router.get("/resumo-custos", response_model=ResumoCustosEquipeResponse, summary="Resumo financeiro e operacional do mês")
def resumo_custos_equipe(
    mes: Optional[int] = None,
    ano: Optional[int] = None,
    fazenda: Fazenda = Depends(get_current_fazenda),
    db: Session = Depends(get_db)
):
    """Calcula o custo total da folha (fixo + diárias extras), faltas e identifica o vigia de hoje."""
    hoje = date.today()
    mes_alvo = mes or hoje.month
    ano_alvo = ano or hoje.year

    data_ini = date(ano_alvo, mes_alvo, 1)
    if mes_alvo == 12:
        data_fim = date(ano_alvo + 1, 1, 1) - timedelta(days=1)
    else:
        data_fim = date(ano_alvo, mes_alvo + 1, 1) - timedelta(days=1)

    # Funcionários ativos
    funcionarios = db.query(Funcionario).filter(Funcionario.fazenda_id == fazenda.id, Funcionario.ativo == True).all()
    total_colab = len(funcionarios)
    total_fixo = sum(f.salario_base_mensal or 0.0 for f in funcionarios if f.tipo_contrato == "MENSALISTA")

    # Escalas no mês
    escalas_mes = db.query(EscalaTrabalho).filter(
        EscalaTrabalho.fazenda_id == fazenda.id,
        EscalaTrabalho.data >= data_ini,
        EscalaTrabalho.data <= data_fim
    ).all()

    total_diarias_extras = sum(e.valor_diaria_aplicado or 0.0 for e in escalas_mes if e.eh_extra)
    total_faltas = sum(1 for e in escalas_mes if e.turno in ("FALTA_JUSTIFICADA", "FALTA_INJUSTIFICADA"))
    total_noturnos = sum(1 for e in escalas_mes if e.turno == "NOTURNO_VIGIA")

    custo_total = round(total_fixo + total_diarias_extras, 2)

    # Área total da fazenda para custo por ha
    area_total_ha = db.query(func.sum(Viveiro.area_ha)).filter(Viveiro.fazenda_id == fazenda.id).scalar() or 12.83
    custo_por_ha = round(custo_total / float(area_total_ha), 2) if area_total_ha > 0 else 0.0

    # Vigia Noturno de hoje
    vigia_hoje = db.query(EscalaTrabalho).join(Funcionario).filter(
        EscalaTrabalho.fazenda_id == fazenda.id,
        EscalaTrabalho.data == hoje,
        EscalaTrabalho.turno == "NOTURNO_VIGIA"
    ).first()

    vigia_nome = None
    vigia_status = None
    vigia_horario = None

    if vigia_hoje:
        vigia_nome = f"{vigia_hoje.funcionario.nome} ({vigia_hoje.funcionario.apelido or vigia_hoje.funcionario.cargo})"
        vigia_status = vigia_hoje.status_presenca
        vigia_horario = f"{vigia_hoje.check_in_hora or '21:00'} às {vigia_hoje.check_out_hora or '06:00'}"
    else:
        # Fallback: primeiro vigia cadastrado
        primeiro_vigia = next((f for f in funcionarios if "vigia" in f.cargo.lower()), None)
        if primeiro_vigia:
            vigia_nome = f"{primeiro_vigia.nome} ({primeiro_vigia.apelido or 'Vigia'})"
            vigia_status = "AGENDADO"
            vigia_horario = "21:00 às 06:00"

    return ResumoCustosEquipeResponse(
        mes=mes_alvo,
        ano=ano_alvo,
        total_colaboradores=total_colab,
        total_salarios_fixos=round(total_fixo, 2),
        total_diarias_extras=round(total_diarias_extras, 2),
        custo_total_folha=custo_total,
        total_faltas_registradas=total_faltas,
        total_plantoes_noturnos=total_noturnos,
        custo_estimado_por_ha=custo_por_ha,
        vigia_hoje_nome=vigia_nome or "Nenhum vigia agendado",
        vigia_hoje_status=vigia_status or "PENDENTE",
        vigia_hoje_horario=vigia_horario or "21:00 às 06:00"
    )
