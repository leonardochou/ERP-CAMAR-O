-- =========================================================
-- SCHEMA DDL OFICIAL - ERP CAMARÃO (Ceará-Mirim/RN)
-- Compatibilidade Total: PostgreSQL 14+ / Supabase
-- Tabelas Zootécnicas, Operacionais, Multi-Tenant e Contabilidade
-- Idempotente: seguro para rodar em base nova ou já existente
-- =========================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Tabela: fazendas
CREATE TABLE IF NOT EXISTS fazendas (
	id VARCHAR(36) NOT NULL, 
	codigo VARCHAR(30) NOT NULL, 
	nome VARCHAR(100) NOT NULL, 
	tipo_propriedade VARCHAR(20), 
	municipio_uf VARCHAR(100), 
	status VARCHAR(20), 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	updated_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id)
);

-- Tabela: auditoria_pendencias
CREATE TABLE IF NOT EXISTS auditoria_pendencias (
	id SERIAL NOT NULL, 
	fazenda_id VARCHAR(36) NOT NULL, 
	origem VARCHAR(30), 
	entidade VARCHAR(30) NOT NULL, 
	viveiro_codigo VARCHAR(10) NOT NULL, 
	data_evento DATE NOT NULL, 
	tipo_anomalia VARCHAR(40) NOT NULL, 
	severidade VARCHAR(20), 
	mensagem VARCHAR(255) NOT NULL, 
	dados_atuais_json TEXT, 
	dados_novos_json TEXT, 
	resolvido BOOLEAN, 
	acao_resolucao VARCHAR(30), 
	resolvido_em TIMESTAMP WITHOUT TIME ZONE, 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(fazenda_id) REFERENCES fazendas (id) ON DELETE CASCADE
);

-- Tabela: funcionarios
CREATE TABLE IF NOT EXISTS funcionarios (
	id SERIAL NOT NULL, 
	fazenda_id VARCHAR(36) NOT NULL, 
	nome VARCHAR(100) NOT NULL, 
	apelido VARCHAR(50), 
	cargo VARCHAR(50) NOT NULL, 
	telefone VARCHAR(30), 
	whatsapp VARCHAR(30), 
	chave_pix VARCHAR(100), 
	tipo_contrato VARCHAR(20), 
	salario_base_mensal FLOAT, 
	valor_diaria_extra FLOAT, 
	encargos_estimados_pct FLOAT, 
	ativo BOOLEAN, 
	data_admissao DATE, 
	observacoes TEXT, 
	criado_em TIMESTAMP WITHOUT TIME ZONE, 
	atualizado_em TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(fazenda_id) REFERENCES fazendas (id)
);

-- Tabela: lancamentos_contabeis
CREATE TABLE IF NOT EXISTS lancamentos_contabeis (
	id SERIAL NOT NULL, 
	fazenda_id VARCHAR(36) NOT NULL, 
	data_competencia DATE NOT NULL, 
	data_vencimento DATE NOT NULL, 
	data_liquidacao DATE, 
	tipo_movimento VARCHAR(15) NOT NULL, 
	codigo_conta VARCHAR(20) NOT NULL, 
	nome_conta VARCHAR(120) NOT NULL, 
	grupo_contabil VARCHAR(50) NOT NULL, 
	descricao VARCHAR(255) NOT NULL, 
	fornecedor_cliente VARCHAR(120) NOT NULL, 
	valor_rs FLOAT NOT NULL, 
	status_pagamento VARCHAR(20) NOT NULL, 
	forma_pagamento VARCHAR(40), 
	centro_custo_viveiro VARCHAR(30) NOT NULL, 
	arquivo_nota VARCHAR(180), 
	origem VARCHAR(30) NOT NULL, 
	chave_dedup VARCHAR(64) NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	updated_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(fazenda_id) REFERENCES fazendas (id) ON DELETE CASCADE
);

-- Tabela: logs_backups_contabeis
CREATE TABLE IF NOT EXISTS logs_backups_contabeis (
	id SERIAL NOT NULL, 
	fazenda_id VARCHAR(36) NOT NULL, 
	tipo_operacao VARCHAR(40) NOT NULL, 
	arquivo_backup VARCHAR(200), 
	novos_lancamentos INTEGER, 
	atualizacoes_status INTEGER, 
	duplicatas_bloqueadas INTEGER, 
	detalhes VARCHAR(255), 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(fazenda_id) REFERENCES fazendas (id) ON DELETE CASCADE
);

-- Tabela: viveiros
CREATE TABLE IF NOT EXISTS viveiros (
	id SERIAL NOT NULL, 
	fazenda_id VARCHAR(36) NOT NULL, 
	codigo VARCHAR(10) NOT NULL, 
	nome_operacional VARCHAR(50) NOT NULL, 
	nome_pai VARCHAR(50), 
	numero_pai INTEGER, 
	setor VARCHAR(20) NOT NULL, 
	area_m2 FLOAT NOT NULL, 
	area_ha FLOAT NOT NULL, 
	area_satelite_m2 FLOAT, 
	area_ajustada_m2 FLOAT, 
	profundidade_media_m FLOAT, 
	volume_m3 FLOAT NOT NULL, 
	tipo_uso VARCHAR(40), 
	origem_metragem VARCHAR(50), 
	ativo BOOLEAN, 
	observacoes VARCHAR(255), 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	updated_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_viveiro_fazenda_codigo UNIQUE (fazenda_id, codigo), 
	FOREIGN KEY(fazenda_id) REFERENCES fazendas (id) ON DELETE CASCADE
);

-- Tabela: ciclos_cultivo
CREATE TABLE IF NOT EXISTS ciclos_cultivo (
	id SERIAL NOT NULL, 
	fazenda_id VARCHAR(36) NOT NULL, 
	viveiro_id INTEGER NOT NULL, 
	numero_lote VARCHAR(50) NOT NULL, 
	data_povoamento DATE NOT NULL, 
	pls_estocadas INTEGER NOT NULL, 
	densidade_pl_m2 FLOAT, 
	laboratorio VARCHAR(50), 
	peso_inicial_g FLOAT, 
	status VARCHAR(30), 
	codigo_ciclo VARCHAR(50), 
	ano_safra INTEGER, 
	numero_sequencial INTEGER, 
	racao_total_kg FLOAT, 
	despescas_parciais_kg FLOAT, 
	data_despesca DATE, 
	camarao_colhido_kg FLOAT, 
	peso_final_g FLOAT, 
	sobrevivencia_real_pct FLOAT, 
	fca_real_final FLOAT, 
	produtividade_kg_ha FLOAT, 
	faturamento_total_rs FLOAT, 
	observacoes VARCHAR(255), 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	updated_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_ciclo_fazenda_lote UNIQUE (fazenda_id, numero_lote), 
	FOREIGN KEY(fazenda_id) REFERENCES fazendas (id) ON DELETE CASCADE, 
	FOREIGN KEY(viveiro_id) REFERENCES viveiros (id) ON DELETE CASCADE
);

-- Tabela: escalas_trabalho
CREATE TABLE IF NOT EXISTS escalas_trabalho (
	id SERIAL NOT NULL, 
	fazenda_id VARCHAR(36) NOT NULL, 
	funcionario_id INTEGER NOT NULL, 
	data DATE NOT NULL, 
	turno VARCHAR(30) NOT NULL, 
	eh_extra BOOLEAN, 
	valor_diaria_aplicado FLOAT, 
	check_in_hora VARCHAR(10), 
	check_out_hora VARCHAR(10), 
	status_presenca VARCHAR(20), 
	categoria_ocorrencia VARCHAR(30), 
	observacoes TEXT, 
	criado_em TIMESTAMP WITHOUT TIME ZONE, 
	atualizado_em TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(fazenda_id) REFERENCES fazendas (id), 
	FOREIGN KEY(funcionario_id) REFERENCES funcionarios (id)
);

-- Tabela: biometrias
CREATE TABLE IF NOT EXISTS biometrias (
	id SERIAL NOT NULL, 
	fazenda_id VARCHAR(36) NOT NULL, 
	ciclo_id INTEGER NOT NULL, 
	data DATE NOT NULL, 
	doc INTEGER NOT NULL, 
	peso_medio_g FLOAT NOT NULL, 
	amostra_qtd INTEGER, 
	ganho_peso_semanal_g FLOAT, 
	gmd_g_dia FLOAT, 
	sobrevivencia_estimada_pct FLOAT, 
	populacao_estimada INTEGER, 
	biomassa_estimada_kg FLOAT, 
	racao_acumulada_ate_data_kg FLOAT, 
	fca_parcial FLOAT, 
	uniformidade_pct FLOAT, 
	observacoes VARCHAR(255), 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	updated_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_biometria_ciclo_data UNIQUE (ciclo_id, data), 
	FOREIGN KEY(fazenda_id) REFERENCES fazendas (id) ON DELETE CASCADE, 
	FOREIGN KEY(ciclo_id) REFERENCES ciclos_cultivo (id) ON DELETE CASCADE
);

-- Tabela: despescas_vendas
CREATE TABLE IF NOT EXISTS despescas_vendas (
	id SERIAL NOT NULL, 
	fazenda_id VARCHAR(36) NOT NULL, 
	ciclo_id INTEGER NOT NULL, 
	data DATE NOT NULL, 
	tipo_despesca VARCHAR(20), 
	gramatura_media_g FLOAT NOT NULL, 
	camarao_colhido_kg FLOAT NOT NULL, 
	comprador VARCHAR(100) NOT NULL, 
	preco_kg_rs FLOAT NOT NULL, 
	faturamento_bruto_rs FLOAT NOT NULL, 
	data_vencimento DATE, 
	status_pagamento VARCHAR(20), 
	data_pagamento DATE, 
	forma_pagamento VARCHAR(30), 
	numero_romaneio VARCHAR(50), 
	observacoes VARCHAR(255), 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	updated_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(fazenda_id) REFERENCES fazendas (id) ON DELETE CASCADE, 
	FOREIGN KEY(ciclo_id) REFERENCES ciclos_cultivo (id) ON DELETE CASCADE
);

-- Tabela: lancamentos_alimentacao
CREATE TABLE IF NOT EXISTS lancamentos_alimentacao (
	id SERIAL NOT NULL, 
	fazenda_id VARCHAR(36) NOT NULL, 
	ciclo_id INTEGER NOT NULL, 
	data DATE NOT NULL, 
	doc INTEGER NOT NULL, 
	racao_manha_kg FLOAT, 
	sobra_manha INTEGER, 
	racao_tarde_kg FLOAT, 
	sobra_tarde INTEGER, 
	racao_noite_kg FLOAT, 
	sobra_noite INTEGER, 
	total_dia_kg FLOAT, 
	consumo_acumulado_kg FLOAT, 
	hash_linha VARCHAR(64), 
	observacoes VARCHAR(255), 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	updated_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_alimentacao_ciclo_data UNIQUE (ciclo_id, data), 
	FOREIGN KEY(fazenda_id) REFERENCES fazendas (id) ON DELETE CASCADE, 
	FOREIGN KEY(ciclo_id) REFERENCES ciclos_cultivo (id) ON DELETE CASCADE
);

-- Tabela: monitoramentos_agua
CREATE TABLE IF NOT EXISTS monitoramentos_agua (
	id SERIAL NOT NULL, 
	fazenda_id VARCHAR(36) NOT NULL, 
	viveiro_id INTEGER NOT NULL, 
	ciclo_id INTEGER, 
	data DATE NOT NULL, 
	dia_ciclo INTEGER, 
	o2_manha FLOAT, 
	temperatura_manha FLOAT, 
	ph_manha FLOAT, 
	o2_noite FLOAT, 
	temperatura_noite FLOAT, 
	ph_tarde FLOAT, 
	delta_ph FLOAT, 
	salinidade_ppt FLOAT, 
	transparencia_secchi_cm FLOAT, 
	amonia_mg_l FLOAT, 
	nitrito_mg_l FLOAT, 
	alcalinidade_mg_l FLOAT, 
	status_tanque VARCHAR(20), 
	acoes_adotadas VARCHAR(255), 
	hash_linha VARCHAR(64), 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	updated_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_agua_viveiro_data UNIQUE (viveiro_id, data), 
	FOREIGN KEY(fazenda_id) REFERENCES fazendas (id) ON DELETE CASCADE, 
	FOREIGN KEY(viveiro_id) REFERENCES viveiros (id) ON DELETE CASCADE, 
	FOREIGN KEY(ciclo_id) REFERENCES ciclos_cultivo (id) ON DELETE SET NULL
);
