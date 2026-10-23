"""Carga inicial e seed topográfico Multi-Tenant da fazenda em Ceará-Mirim/RN."""
from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.core.database import Base, engine, SessionLocal
import app.models  # Garante o registro de todos os modelos ORM no Base.metadata
from app.models.fazenda import Fazenda
from app.models.viveiro import Viveiro
from app.models.funcionario import Funcionario, EscalaTrabalho
from app.core.tenant import (
    FAZENDA_PADRAO_ID,
    FAZENDA_PADRAO_CODIGO,
    FAZENDA_HAKKA_ID,
    FAZENDA_HAKKA_CODIGO,
)

# Fazendas cadastradas na arquitetura Multi-Tenant
FAZENDAS_SEED = [
    {
        "id": FAZENDA_PADRAO_ID,
        "codigo": FAZENDA_PADRAO_CODIGO,
        "nome": "Fazenda Arrendada (Ceará-Mirim/RN)",
        "tipo_propriedade": "arrendada",
        "municipio_uf": "Ceará-Mirim/RN",
        "status": "ativa",
    },
    {
        "id": FAZENDA_HAKKA_ID,
        "codigo": FAZENDA_HAKKA_CODIGO,
        "nome": "Fazenda Hakka (Propriedade Familiar)",
        "tipo_propriedade": "propria",
        "municipio_uf": "Ceará-Mirim/RN",
        "status": "planejada",
    },
]

# Topografia oficial auditada integrando a Numeração do Pai (1 a 10) e Metragens
VIVEIROS_SEED = [
    {
        "codigo": "V-01",
        "nome_operacional": "C1 (Central 1)",
        "nome_pai": "Viveiro 1",
        "numero_pai": 1,
        "setor": "Central",
        "area_m2": 12600.0,
        "area_ha": 1.260,
        "area_satelite_m2": 12600.0,
        "area_ajustada_m2": 12600.0,
        "profundidade_media_m": 1.20,
        "volume_m3": 15120.0,
        "tipo_uso": "Engorda",
        "origem_metragem": "SATELITE_GOOGLE_MAPS",
        "observacoes": "Pai: Viveiro 1 (C1 Norte)",
    },
    {
        "codigo": "V-02",
        "nome_operacional": "C2 (Central 2)",
        "nome_pai": "Viveiro 2",
        "numero_pai": 2,
        "setor": "Central",
        "area_m2": 13285.0,
        "area_ha": 1.3285,
        "area_satelite_m2": 13285.0,
        "area_ajustada_m2": 13285.0,
        "profundidade_media_m": 1.20,
        "volume_m3": 15942.0,
        "tipo_uso": "Engorda",
        "origem_metragem": "SATELITE_GOOGLE_MAPS",
        "observacoes": "Pai: Viveiro 2 (C2 Médio-Norte)",
    },
    {
        "codigo": "V-03",
        "nome_operacional": "C3 (Central 3)",
        "nome_pai": "Viveiro 3",
        "numero_pai": 3,
        "setor": "Central",
        "area_m2": 15500.0,
        "area_ha": 1.550,
        "area_satelite_m2": 15500.0,
        "area_ajustada_m2": 15500.0,
        "profundidade_media_m": 1.20,
        "volume_m3": 18600.0,
        "tipo_uso": "Engorda",
        "origem_metragem": "SATELITE_GOOGLE_MAPS",
        "observacoes": "Pai: Viveiro 3 (C3 Médio-Sul)",
    },
    {
        "codigo": "V-04",
        "nome_operacional": "C4 (Central 4)",
        "nome_pai": "Viveiro 4",
        "numero_pai": 4,
        "setor": "Central",
        "area_m2": 16400.0,
        "area_ha": 1.640,
        "area_satelite_m2": 16400.0,
        "area_ajustada_m2": 16400.0,
        "profundidade_media_m": 1.20,
        "volume_m3": 19680.0,
        "tipo_uso": "Engorda",
        "origem_metragem": "SATELITE_GOOGLE_MAPS",
        "observacoes": "Pai: Viveiro 4 (C4 Sul)",
    },
    {
        "codigo": "V-05",
        "nome_operacional": "L1 (Leste 1)",
        "nome_pai": "Viveiro 5",
        "numero_pai": 5,
        "setor": "Leste",
        "area_m2": 13040.0,
        "area_ha": 1.304,
        "area_satelite_m2": 13040.0,
        "area_ajustada_m2": 13040.0,
        "profundidade_media_m": 1.20,
        "volume_m3": 15648.0,
        "tipo_uso": "Engorda",
        "origem_metragem": "SATELITE_GOOGLE_MAPS",
        "observacoes": "Pai: Viveiro 5 (L1 Norte)",
    },
    {
        "codigo": "V-06",
        "nome_operacional": "L2 (Leste 2)",
        "nome_pai": "Viveiro 6",
        "numero_pai": 6,
        "setor": "Leste",
        "area_m2": 14710.0,
        "area_ha": 1.471,
        "area_satelite_m2": 14710.0,
        "area_ajustada_m2": 14710.0,
        "profundidade_media_m": 1.20,
        "volume_m3": 17652.0,
        "tipo_uso": "Engorda",
        "origem_metragem": "SATELITE_GOOGLE_MAPS",
        "observacoes": "Pai: Viveiro 6 (L2 Sul)",
    },
    {
        "codigo": "V-07",
        "nome_operacional": "O1 (Oeste 1)",
        "nome_pai": "Viveiro 7",
        "numero_pai": 7,
        "setor": "Oeste",
        "area_m2": 8060.0,
        "area_ha": 0.806,
        "area_satelite_m2": 8060.0,
        "area_ajustada_m2": 8060.0,
        "profundidade_media_m": 1.20,
        "volume_m3": 9672.0,
        "tipo_uso": "Engorda",
        "origem_metragem": "SATELITE_GOOGLE_MAPS",
        "observacoes": "Pai: Viveiro 7 (O1 Sul)",
    },
    {
        "codigo": "V-08",
        "nome_operacional": "O2 (Oeste 2)",
        "nome_pai": "Viveiro 8",
        "numero_pai": 8,
        "setor": "Oeste",
        "area_m2": 7550.0,
        "area_ha": 0.755,
        "area_satelite_m2": 7550.0,
        "area_ajustada_m2": 7550.0,
        "profundidade_media_m": 1.20,
        "volume_m3": 9060.0,
        "tipo_uso": "Engorda",
        "origem_metragem": "SATELITE_GOOGLE_MAPS",
        "observacoes": "Pai: Viveiro 8 (O2 Médio-Sul)",
    },
    {
        "codigo": "V-09",
        "nome_operacional": "O3 (Oeste 3)",
        "nome_pai": "Viveiro 9",
        "numero_pai": 9,
        "setor": "Oeste",
        "area_m2": 5400.0,
        "area_ha": 0.540,
        "area_satelite_m2": 5400.0,
        "area_ajustada_m2": 5400.0,
        "profundidade_media_m": 1.20,
        "volume_m3": 6480.0,
        "tipo_uso": "Engorda",
        "origem_metragem": "SATELITE_GOOGLE_MAPS",
        "observacoes": "Pai: Viveiro 9 (O3 Médio-Norte)",
    },
    {
        "codigo": "V-10",
        "nome_operacional": "O5 (Oeste 5)",
        "nome_pai": "Viveiro 10",
        "numero_pai": 10,
        "setor": "Oeste",
        "area_m2": 4650.0,
        "area_ha": 0.465,
        "area_satelite_m2": 4650.0,
        "area_ajustada_m2": 4650.0,
        "profundidade_media_m": 1.20,
        "volume_m3": 5580.0,
        "tipo_uso": "Engorda",
        "origem_metragem": "SATELITE_GOOGLE_MAPS",
        "observacoes": "Pai: Viveiro 10 (O5 Norte)",
    },
    {
        "codigo": "V-11",
        "nome_operacional": "N1 (Berçário 1)",
        "nome_pai": "Berçário 1",
        "numero_pai": None,
        "setor": "Leste",
        "area_m2": 6340.0,
        "area_ha": 0.634,
        "area_satelite_m2": 6340.0,
        "area_ajustada_m2": 6340.0,
        "profundidade_media_m": 1.00,
        "volume_m3": 6340.0,
        "tipo_uso": "Berçário",
        "origem_metragem": "SATELITE_GOOGLE_MAPS",
        "observacoes": "Berçário N1 de pós-larvas",
    },
    {
        "codigo": "V-12",
        "nome_operacional": "N2 (Berçário 2)",
        "nome_pai": "Berçário 2",
        "numero_pai": None,
        "setor": "Leste",
        "area_m2": 5540.0,
        "area_ha": 0.554,
        "area_satelite_m2": 5540.0,
        "area_ajustada_m2": 5540.0,
        "profundidade_media_m": 1.00,
        "volume_m3": 5540.0,
        "tipo_uso": "Berçário",
        "origem_metragem": "SATELITE_GOOGLE_MAPS",
        "observacoes": "Berçário N2 de aclimatação",
    },
    {
        "codigo": "V-13",
        "nome_operacional": "O0 (Tanque Apoio 1)",
        "nome_pai": "Tanque Apoio 1",
        "numero_pai": None,
        "setor": "Oeste",
        "area_m2": 1430.0,
        "area_ha": 0.143,
        "area_satelite_m2": 1430.0,
        "area_ajustada_m2": 1430.0,
        "profundidade_media_m": 1.20,
        "volume_m3": 1716.0,
        "tipo_uso": "Tanque Apoio",
        "origem_metragem": "SATELITE_GOOGLE_MAPS",
        "observacoes": "Reservatório hídrico e decantação interna",
    },
    {
        "codigo": "V-14",
        "nome_operacional": "O4 (Tanque Apoio 2)",
        "nome_pai": "Tanque Apoio 2",
        "numero_pai": None,
        "setor": "Oeste",
        "area_m2": 1980.0,
        "area_ha": 0.198,
        "area_satelite_m2": 1980.0,
        "area_ajustada_m2": 1980.0,
        "profundidade_media_m": 1.20,
        "volume_m3": 2376.0,
        "tipo_uso": "Tanque Apoio",
        "origem_metragem": "SATELITE_GOOGLE_MAPS",
        "observacoes": "Tanque auxiliar de bombeamento oeste",
    },
    {
        "codigo": "V-15",
        "nome_operacional": "L0 (Bacia Decantação)",
        "nome_pai": "Bacia Decantação",
        "numero_pai": None,
        "setor": "Leste",
        "area_m2": 1850.0,
        "area_ha": 0.185,
        "area_satelite_m2": 1850.0,
        "area_ajustada_m2": 1850.0,
        "profundidade_media_m": 1.50,
        "volume_m3": 2775.0,
        "tipo_uso": "Bacia de Decantação",
        "origem_metragem": "SATELITE_GOOGLE_MAPS",
        "observacoes": "Bacia de sedimentação e decantação ambiental na margem do estuário",
    },
]

# Equipe Inicial da Fazenda Arrendada (Ceará-Mirim/RN)
FUNCIONARIOS_SEED = [
    {
        "nome": "Carlos Silva",
        "apelido": "Carlinhos",
        "cargo": "Vigia Noturno",
        "telefone": "(84) 99876-1101",
        "whatsapp": "(84) 99876-1101",
        "chave_pix": "carlinhos.vigia@email.com",
        "tipo_contrato": "MENSALISTA",
        "salario_base_mensal": 1800.0,
        "valor_diaria_extra": 80.0,
        "encargos_estimados_pct": 10.0,
        "ativo": True,
        "observacoes": "Vigia titular noturno (ronda de oxigênio e aeradores). Escala 12x36.",
    },
    {
        "nome": "Sebastião Oliveira",
        "apelido": "Tião",
        "cargo": "Vigia Noturno Folguista",
        "telefone": "(84) 99876-1102",
        "whatsapp": "(84) 99876-1102",
        "chave_pix": "84998761102",
        "tipo_contrato": "DIARISTA",
        "salario_base_mensal": 0.0,
        "valor_diaria_extra": 90.0,
        "encargos_estimados_pct": 0.0,
        "ativo": True,
        "observacoes": "Vigia folguista e plantonista de apoio. Recebe por plantão noturno cumprido.",
    },
    {
        "nome": "Francisco Santos",
        "apelido": "Chico",
        "cargo": "Arraçoador Principal",
        "telefone": "(84) 99876-1103",
        "whatsapp": "(84) 99876-1103",
        "chave_pix": "chico.camarao@pix.com",
        "tipo_contrato": "MENSALISTA",
        "salario_base_mensal": 1650.0,
        "valor_diaria_extra": 75.0,
        "encargos_estimados_pct": 10.0,
        "ativo": True,
        "observacoes": "Responsável pelo trato diurno e conferência de bandejas de sobra (0 a 3).",
    },
    {
        "nome": "José Ferreira",
        "apelido": "Zé do Motor",
        "cargo": "Operador de Máquinas e Bombas",
        "telefone": "(84) 99876-1104",
        "whatsapp": "(84) 99876-1104",
        "chave_pix": "zedomotor@email.com",
        "tipo_contrato": "MENSALISTA",
        "salario_base_mensal": 1750.0,
        "valor_diaria_extra": 85.0,
        "encargos_estimados_pct": 10.0,
        "ativo": True,
        "observacoes": "Manutenção preventiva de motores, compressores e aeradores de pá.",
    },
    {
        "nome": "Antônio Costa",
        "apelido": "Tonho",
        "cargo": "Apoio de Campo e Arraçoamento",
        "telefone": "(84) 99876-1105",
        "whatsapp": "(84) 99876-1105",
        "chave_pix": "tonho.costa@pix.com",
        "tipo_contrato": "MENSALISTA",
        "salario_base_mensal": 1500.0,
        "valor_diaria_extra": 70.0,
        "encargos_estimados_pct": 10.0,
        "ativo": True,
        "observacoes": "Serviços gerais de talude, limpeza de filtros e apoio no turno da tarde.",
    },
]


def init_db(db: Session = None) -> None:
    """Cria todas as tabelas e semeia fazendas, viveiros e equipe com escala do mês."""
    Base.metadata.create_all(bind=engine)

    own_session = False
    if db is None:
        db = SessionLocal()
        own_session = True

    try:
        # 1. Seed das Fazendas
        for f_data in FAZENDAS_SEED:
            fazenda = db.query(Fazenda).filter(Fazenda.id == f_data["id"]).first()
            if not fazenda:
                fazenda = Fazenda(**f_data)
                db.add(fazenda)
        db.commit()

        # 2. Seed dos 15 Viveiros na Fazenda Arrendada
        for v_data in VIVEIROS_SEED:
            viveiro = db.query(Viveiro).filter(
                Viveiro.fazenda_id == FAZENDA_PADRAO_ID,
                Viveiro.codigo == v_data["codigo"]
            ).first()

            if not viveiro:
                item = dict(v_data)
                item["fazenda_id"] = FAZENDA_PADRAO_ID
                viveiro = Viveiro(**item)
                db.add(viveiro)
            else:
                viveiro.nome_pai = v_data["nome_pai"]
                viveiro.numero_pai = v_data["numero_pai"]
                viveiro.nome_operacional = v_data["nome_operacional"]
                viveiro.setor = v_data["setor"]
                viveiro.area_satelite_m2 = v_data["area_satelite_m2"]
                if not viveiro.area_ajustada_m2:
                    viveiro.area_ajustada_m2 = v_data["area_ajustada_m2"]
                viveiro.tipo_uso = v_data["tipo_uso"]
        db.commit()

        # 3. Seed dos Colaboradores da Fazenda
        funcs_criados = {}
        for f_data in FUNCIONARIOS_SEED:
            func = db.query(Funcionario).filter(
                Funcionario.fazenda_id == FAZENDA_PADRAO_ID,
                Funcionario.nome == f_data["nome"]
            ).first()
            if not func:
                item = dict(f_data)
                item["fazenda_id"] = FAZENDA_PADRAO_ID
                func = Funcionario(**item)
                db.add(func)
                db.flush()
            funcs_criados[func.apelido or func.nome] = func
        db.commit()

        # 4. Seed da Escala do Mês Corrente (com revezamento de vigias e folgas)
        hoje = date.today()
        primeiro_dia_mes = date(hoje.year, hoje.month, 1)
        if hoje.month == 12:
            ultimo_dia_mes = date(hoje.year + 1, 1, 1) - timedelta(days=1)
        else:
            ultimo_dia_mes = date(hoje.year, hoje.month + 1, 1) - timedelta(days=1)

        dias_no_mes = (ultimo_dia_mes - primeiro_dia_mes).days + 1

        carlinhos = funcs_criados.get("Carlinhos")
        tiao = funcs_criados.get("Tião")
        chico = funcs_criados.get("Chico")
        ze = funcs_criados.get("Zé do Motor")
        tonho = funcs_criados.get("Tonho")

        for d in range(dias_no_mes):
            dt = primeiro_dia_mes + timedelta(days=d)

            # Revezamento 12x36 Vigias (Carlinhos dias pares, Tião dias ímpares)
            if carlinhos and tiao:
                carlinhos_escala = db.query(EscalaTrabalho).filter(
                    EscalaTrabalho.funcionario_id == carlinhos.id,
                    EscalaTrabalho.data == dt
                ).first()
                if not carlinhos_escala:
                    is_carlinhos = (dt.day % 2 == 1)
                    db.add(EscalaTrabalho(
                        fazenda_id=FAZENDA_PADRAO_ID,
                        funcionario_id=carlinhos.id,
                        data=dt,
                        turno="NOTURNO_VIGIA" if is_carlinhos else "FOLGA",
                        check_in_hora="21:00" if is_carlinhos else None,
                        check_out_hora="06:00" if is_carlinhos else None,
                        status_presenca="CONFIRMADO" if dt < hoje else "AGENDADO"
                    ))

                tiao_escala = db.query(EscalaTrabalho).filter(
                    EscalaTrabalho.funcionario_id == tiao.id,
                    EscalaTrabalho.data == dt
                ).first()
                if not tiao_escala:
                    is_tiao = (dt.day % 2 == 0)
                    db.add(EscalaTrabalho(
                        fazenda_id=FAZENDA_PADRAO_ID,
                        funcionario_id=tiao.id,
                        data=dt,
                        turno="NOTURNO_VIGIA" if is_tiao else "FOLGA",
                        eh_extra=is_tiao,
                        valor_diaria_aplicado=90.0 if is_tiao else 0.0,
                        check_in_hora="21:00" if is_tiao else None,
                        check_out_hora="06:00" if is_tiao else None,
                        status_presenca="CONFIRMADO" if dt < hoje else "AGENDADO"
                    ))

            # Escala 6x1 Tratadores Diurnos
            # Chico folga aos domingos (weekday == 6)
            if chico:
                escala = db.query(EscalaTrabalho).filter(EscalaTrabalho.funcionario_id == chico.id, EscalaTrabalho.data == dt).first()
                if not escala:
                    folga = (dt.weekday() == 6)
                    db.add(EscalaTrabalho(
                        fazenda_id=FAZENDA_PADRAO_ID,
                        funcionario_id=chico.id,
                        data=dt,
                        turno="FOLGA" if folga else "DIURNO",
                        check_in_hora="06:30" if not folga else None,
                        check_out_hora="17:00" if not folga else None,
                        status_presenca="CONFIRMADO" if dt < hoje else "AGENDADO"
                    ))

            # Zé do Motor folga aos sábados (weekday == 5)
            if ze:
                escala = db.query(EscalaTrabalho).filter(EscalaTrabalho.funcionario_id == ze.id, EscalaTrabalho.data == dt).first()
                if not escala:
                    folga = (dt.weekday() == 5)
                    db.add(EscalaTrabalho(
                        fazenda_id=FAZENDA_PADRAO_ID,
                        funcionario_id=ze.id,
                        data=dt,
                        turno="FOLGA" if folga else "DIURNO",
                        check_in_hora="06:30" if not folga else None,
                        check_out_hora="17:00" if not folga else None,
                        status_presenca="CONFIRMADO" if dt < hoje else "AGENDADO"
                    ))

            # Tonho folga às segundas (weekday == 0)
            if tonho:
                escala = db.query(EscalaTrabalho).filter(EscalaTrabalho.funcionario_id == tonho.id, EscalaTrabalho.data == dt).first()
                if not escala:
                    folga = (dt.weekday() == 0)
                    db.add(EscalaTrabalho(
                        fazenda_id=FAZENDA_PADRAO_ID,
                        funcionario_id=tonho.id,
                        data=dt,
                        turno="FOLGA" if folga else "DIURNO",
                        check_in_hora="06:30" if not folga else None,
                        check_out_hora="17:00" if not folga else None,
                        status_presenca="CONFIRMADO" if dt < hoje else "AGENDADO"
                    ))

        # Adicionar uma ocorrência de exemplo em um dia específico do mês
        if carlinhos:
            dt_ocorr = primeiro_dia_mes + timedelta(days=5)
            escala_ocorr = db.query(EscalaTrabalho).filter(EscalaTrabalho.funcionario_id == carlinhos.id, EscalaTrabalho.data == dt_ocorr).first()
            if escala_ocorr:
                escala_ocorr.categoria_ocorrencia = "COBERTURA_TURNO"
                escala_ocorr.eh_extra = True
                escala_ocorr.valor_diaria_aplicado = 80.0
                escala_ocorr.observacoes = "Cobriu plantão extra pós-temporal para checar motores dos viveiros 3 e 4."

        db.commit()
    finally:
        if own_session:
            db.close()


if __name__ == "__main__":
    init_db()
    print("Banco de dados inicializado com sucesso, topografia e equipe sincronizadas!")
