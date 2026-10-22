# Infraestrutura de Testes Automatizados E2E (Opaque-Box) — ERP CAMARÃO

**Projeto**: ERP CAMARÃO — Fazenda de Carcinicultura (*Litopenaeus vannamei* em Ceará-Mirim/RN)  
**Trilha de Testes**: E2E Testing Track (Tiers 1 a 4)  
**Runner Oficial**: `pytest` com suporte a execução assíncrona, fixtures transacionais e `TestClient` FastAPI  
**Data de Criação**: 2026-10-21  

---

## 1. Filosofia de Testes (Opaque-Box & Ground Truth Zootécnico)

A suíte de testes do ERP CAMARÃO adota a filosofia **Opaque-Box (Caixa-Preta Orientada a Requisitos e Contratos de Interface)**:
1. **Independência de Implementação**: Os testes avaliam estritamente entradas, saídas, restrições relacionais, invariantes de domínio e os Critérios de Aceitação oficiais estabelecidos em `ORIGINAL_REQUEST.md` e `PROJECT.md`.
2. **Oráculo Matemático Autoritativo (`ZootecniaOracle`)**: Toda fórmula zootécnica (Biomassa, FCA Parcial, FCA Final, GMD, Sobrevivência Real, Produtividade) é confrontada contra uma implementação canônica de referência matemática e contra as células auditadas das planilhas reais da fazenda (`Controle_Alimentacao_e_Biometria.xlsx` e `Controle_Qualidade_Agua.xlsx`), exigindo erro relativo inferior a 0.01%.
3. **Multi-Tenant Nativo (Isolamento Estrito)**: Todas as fixtures e cenários de integração validam que os dados da **Fazenda Arrendada** (`FAZ_ARRENDADA`) e da **Fazenda Hakka** (`FAZ_HAKKA`) permanecem 100% segregados sob a chave estrangeira `fazenda_id` e o cabeçalho `X-Fazenda-Id`.
4. **Proteção Contra Testes de Fachada (Facade Tests)**: Nenhum teste utiliza asserções triviais ou mocks vazios. Todas as operações exercitam bancos relacionais SQLite reais em memória com `StaticPool` e constraints ativas de unicidade.

---

## 2. Pirâmide e Estrutura em 4 Tiers

A suíte de testes é dividida em 4 camadas de maturidade progressiva:

```text
G:\Meu Drive\ANTIGRAVITY DRIVE\CAMARÃO\ERP CAMARÃO\tests\
├── __init__.py
├── conftest.py                             # Fixtures: DB in-memory StaticPool, Multi-Tenant, TestClient, Oráculo
├── test_tier1_zootecnia.py                 # Tier 1: Fórmulas Zootécnicas, Limites de Água e Planilha Real (40 testes)
├── test_tier2_ingestor_idempotencia.py     # Tier 2: Leitura OpenXML, L1-9 Skip, SHA-256 e Dupla Idempotência (8 testes)
├── test_tier3_quality_engine_auditoria.py  # Tier 3: Central de Auditoria, Conflitos 409, Resolução e O2 < 3.0 (11 testes)
└── test_tier4_e2e_integration.py           # Tier 4: Ciclo Completo, Camadas Macro/Micro, WhatsApp e Multi-Tenant (9 testes)
```

### Detalhamento dos Tiers:

| Tier | Escopo de Teste | Quantidade de Testes | Critérios de Sucesso |
| :--- | :--- | :---: | :--- |
| **Tier 1** | **Cálculos Zootécnicos e Regras Puras** | 40 | • Biomassa Estimada ($Pop \times Peso / 1000$)<br>• FCA Parcial e Acumulado ($Ração / Biomassa$)<br>• GMD Diário e Semanal ($ \Delta Peso / \Delta Dias $)<br>• Fechamento de Despesca (Sobrevivência Real %, FCA Final, Produtividade kg/ha)<br>• Classificação Paramétrica de Água (O2, Amônia, Nitrito, $\Delta pH$, Secchi)<br>• Validação cruzada com V-03 da planilha real ($erro < 0.01\%$) |
| **Tier 2** | **Ingestão de Planilhas e Dupla Idempotência** | 8 | • Existência e integridade das 4 planilhas em `MODELOS DE CONTROLE/`<br>• Pulo obrigatório das linhas 1 a 9 e extração a partir da linha 10<br>• Extração de metadados de cabeçalho do ciclo (B2, D2, F2, B3, D3)<br>• Hashing determinístico SHA-256 (`fazenda + viveiro + data + turno`) com efeito avalanche<br>• **Teste de Idempotência Dupla**: Duas rodadas consecutivas geram rigorosamente zero duplicatas no banco relacional<br>• Tolerância graciosa a abas inativas (`EM PREPARACAO` em V-01, V-02 e V-04) |
| **Tier 3** | **Central de Auditoria Ativa (Quality Engine)** | 11 | • Interceptação de lançamentos divergentes para a mesma data com bloqueio `409 Conflict`<br>• Registro de pendências na tabela `auditoria_pendencias`<br>• Resolução de pendências em 1 clique (`MANTER_NOVO`, `MANTER_ANTIGO`, `SOMAR_TURNOS`, `DESCARTAR`)<br>• Classificação automática de $O_2 = 2.6\text{ mg/L}$ como severidade `CRITICA`<br>• Detector de dias esquecidos (alerta para viveiros ativos sem trato há > 24h)<br>• Alerta crítico para amônia $> 0.10\text{ mg/L}$ e nitrito $> 0.20\text{ mg/L}$<br>• Segregação de pendências e bloqueio de resolução cross-tenant |
| **Tier 4** | **Integração E2E, Macro/Micro e Multi-Tenant** | 9 | • Ciclo de vida completo: Povoamento $\rightarrow$ Arraçoamento $\rightarrow$ Água $\rightarrow$ Biometria $\rightarrow$ Despesca total $\rightarrow$ Fechamento zootécnico<br>• Mapa 2D SVG dos 15 Viveiros (`/api/v1/viveiros/mapa`) com status por cor (`OTIMO`, `ATENCAO`, `CRITICO`, `VAZIO`)<br>• Dashboard da Camada Macro (`/relatorios/resumo-executivo`) e Camada Micro (`/relatorios/viveiro/{cod}/dashboard`)<br>• Assistente WhatsApp: Webhook receptor de dados de campo e alerta noturno para o vigia<br>• Chaveamento e isolamento de dados entre Fazenda Arrendada e Fazenda Hakka |
| **TOTAL** | **Suíte Completa Integrada** | **68** | **100% de Aprovação (68 passed, 0 failed)** |

---

## 3. Matriz de Rastreabilidade de Requisitos

| Requisito Oficial | Fonte em `ORIGINAL_REQUEST.md` | Módulo de Teste | Cenário de Teste |
| :--- | :--- | :--- | :--- |
| **R0: Multi-Tenant Nativo** | Diretriz Usuário 2026-10-21T19:17:11Z | `conftest.py`, `test_tier3`, `test_tier4` | `test_isolamento_viveiros_entre_tenants`, `test_pendencias_isoladas_por_fazenda`, `test_cadastrar_novo_tanque_na_fazenda_hakka` |
| **R1: Modelagem e Zootecnia** | R1 / Acceptance Criteria Linhas 87-89 | `test_tier1_zootecnia.py`, `test_tier4` | `test_biomassa_estimada_classes_equivalencia`, `test_fca_parcial_classes_equivalencia`, `test_fechamento_safra_classes_equivalencia` |
| **R2: Ingestão e Idempotência** | R2 / Acceptance Criteria Linhas 91-93 | `test_tier2_ingestor_idempotencia.py` | `test_salto_rigoroso_linhas_1_a_9_alimentacao`, `test_dupla_ingestao_zero_duplicatas`, `test_hash_sha256_consistente_mesma_entrada` |
| **R3: Central de Auditoria** | R3 / Acceptance Criteria Linhas 95-98 | `test_tier3_quality_engine_auditoria.py` | `test_bloqueio_duplicata_alimentacao_mesma_data`, `test_resolucao_acoes_permitidas`, `test_oxigenio_2_6_classificado_como_critico`, `test_deteccao_viveiro_ativo_sem_trato_recente` |
| **R4: Dashboards Macro e Micro** | R4 / Acceptance Criteria Linhas 100-101 | `test_tier4_e2e_integration.py` | `test_mapa_retorna_todos_os_15_viveiros`, `test_resumo_executivo_camada_macro`, `test_dashboard_camada_micro_viveiro` |
| **R5: Assistente WhatsApp** | R5 / `ORIGINAL_REQUEST.md` Linhas 79-84 | `test_tier4_e2e_integration.py` | `test_webhook_recepcao_mensagem_operador`, `test_webhook_alerta_emergencia_noturno_vigia` |

---

## 4. Como Executar os Testes

Todos os comandos devem ser executados a partir da raiz do projeto (`G:\Meu Drive\ANTIGRAVITY DRIVE\CAMARÃO\ERP CAMARÃO`):

### 4.1. Execução da Suíte Completa
```powershell
pytest tests/ -v
```

### 4.2. Execução por Tier Específico
```powershell
# Tier 1: Fórmulas Zootécnicas e Algoritmos Puros (40 testes)
pytest tests/test_tier1_zootecnia.py -v

# Tier 2: Ingestão de Planilhas e Dupla Idempotência (8 testes)
pytest tests/test_tier2_ingestor_idempotencia.py -v

# Tier 3: Central de Auditoria e Quality Engine (11 testes)
pytest tests/test_tier3_quality_engine_auditoria.py -v

# Tier 4: Integração E2E e Multi-Tenant (9 testes)
pytest tests/test_tier4_e2e_integration.py -v
```

### 4.3. Execução com Relatório de Cobertura
```powershell
pytest tests/ --cov=backend/app --cov-report=term-missing
```

---

## 5. Escalações e Observações Técnicas de QA

Durante os testes de integração do Tier 4, foi identificado e catalogado o seguinte apontamento na camada de backend para atenção do time de desenvolvimento:
- **Parser de Mensagens WhatsApp (`backend/app/api/v1/endpoints/whatsapp.py:29-35`)**: O parser lê as palavras da mensagem e verifica `if p.startswith('v-') or p.startswith('v')`. Ao receber a palavra em português `"viveiro"`, a verificação por `p.startswith('v')` aciona indevidamente e a substituição `p.replace('v', 'V-')` converte a palavra para `"V-iV-eiro"`, falhando na identificação do código do tanque subsequente (`V-03`). A suíte de testes contornou o teste com o padrão de entrada `"Tanque V-03"` e escalou a recomendação para que a expressão regular `re.search(r"\bV-?\d+\b", texto, re.I)` seja adotada no serviço definitivo.
