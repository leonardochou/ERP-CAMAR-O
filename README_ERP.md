# 🦐 ERP Carcinicultura — Fazenda de Camarão Marinho (Ceará-Mirim/RN)
### *Guia Operacional, Arquitetura Técnica e Manual de Navegação do Sistema Fullstack*

---

## 📌 1. Visão Geral do Sistema

Este repositório contém o sistema ERP integrado da Fazenda de Camarão Marinho (*Litopenaeus vannamei*), localizada em Ceará-Mirim/RN, cobrindo todo o ciclo operacional, zootécnico e de controladoria financeira:

1. **O Trabalho Prático de Campo (Visão Pai / Operador):** Simplicidade máxima, botões amplos, formulários ágeis de 2 toques, comandos de voz/texto via **Assistente WhatsApp com IA** e ausência de telas complexas que atrapalhem o manejo diário.
2. **A Inteligência Zootécnica & Financeira (Visão Leonardo / Gestão):** Análise preditiva de crescimento, monitoramento contínuo de conversão alimentar (FCA), DRE em tempo real, **Central de Auditoria Ativa** e radar de preços de mercado para tomada de decisão sobre despesca ótima.
3. **Multi-Fazenda (Multi-Tenant Nativo):** Segregação estrutural entre a **Fazenda Arrendada** (15 viveiros em operação ativa) e a futura **Fazenda Hakka** (propriedade familiar própria).
4. **Ingestor Híbrido Idempotente:** Sincronização direta com as planilhas do Google Drive (`Controle_Alimentacao_e_Biometria.xlsx` e `Controle_Qualidade_Agua.xlsx`), pulando as linhas 1 a 9 e deduplicando via hash criptográfico SHA-256.

---

## 🚀 2. Como Executar a Aplicação Fullstack

O sistema pode ser utilizado de duas formas:
1. **Modo Integrado Fullstack (Backend FastAPI + Frontend HTML):** Conecta a interface ao vivo ao banco de dados SQLite/PostgreSQL, permitindo sincronização em tempo real de planilhas e respostas do bot WhatsApp via API.
2. **Modo Demonstrativo Standalone (Apenas o Navegador):** O arquivo `.html` é 100% autocontido e abre diretamente no Chrome/Edge com dados locais mockados caso o backend esteja desligado.

### Passo 1: Iniciar o Servidor Backend FastAPI
No terminal do Windows PowerShell, execute:
```powershell
$env:PYTHONPATH="G:\Meu Drive\ANTIGRAVITY DRIVE\CAMARÃO\ERP CAMARÃO\backend"
python "G:\Meu Drive\ANTIGRAVITY DRIVE\CAMARÃO\ERP CAMARÃO\backend\run_server.py"
```
* **Documentação Swagger UI:** Acesse `http://127.0.0.1:8000/docs`
* **Health Check:** `http://127.0.0.1:8000/health`

### Passo 2: Abrir o Painel Interativo no Navegador
Abra diretamente o arquivo no navegador:
`G:\Meu Drive\ANTIGRAVITY DRIVE\CAMARÃO\ERP CAMARÃO\dashboard_interativo_prototipo.html`

O painel detectará automaticamente a API local e exibirá o badge:
`🟢 API Online (FastAPI)` no topo do cabeçalho.

---

## 🧪 3. Suíte de Testes Automatizados (91 Testes — 100% Aprovados)

O sistema possui uma suíte de testes robusta cobrindo 4 camadas operacionais:
* **Tier 1 (Fórmulas Zootécnicas):** Validação matemática de População Estimada, Biomassa Viva, FCA Parcial, GMD e Encerramento de Safra com erro < 0.01%.
* **Tier 2 (Ingestão & Idempotência):** Salto de linhas 1 a 9, leitura a partir da linha 10 e teste de **dupla ingestão consecutiva** comprovando zero duplicatas geradas.
* **Tier 3 (Central de Auditoria):** Interceptação de conflitos de mesma data, alerta crítico sonoro para $O_2 < 3.0\text{ mg/L}$ e detector de dias esquecidos (> 24h sem dados).
* **Tier 4 (Multi-Tenant & E2E):** Isolamento de dados entre Fazenda Arrendada e Fazenda Hakka e integração com WhatsApp.

### Para rodar a suíte completa:
```powershell
$env:PYTHONPATH="G:\Meu Drive\ANTIGRAVITY DRIVE\CAMARÃO\ERP CAMARÃO\backend"
pytest "G:\Meu Drive\ANTIGRAVITY DRIVE\CAMARÃO\ERP CAMARÃO\tests" -v
pytest "G:\Meu Drive\ANTIGRAVITY DRIVE\CAMARÃO\ERP CAMARÃO\backend\tests" -v
```

---

## 📱 4. Assistente WhatsApp com IA (Voz e Texto)

O sistema conta com um Copiloto Zootécnico acessível via WhatsApp e também através do simulador web no canto inferior direito do Dashboard:

* **Lançamento de Arraçoamento:**
  - Digite ou fale: *"V-03 12kg tarde sobra 0"* ou *"V-02 15kg manha"*
  - O robô extrai o peso, turno e sobra, grava no banco e atualiza o FCA e a biomassa.
* **Alerta Crítico de Asfixia Noturna:**
  - Digite: *"V-05 o2 2.4 urgente"*
  - O sistema detecta $O_2 < 3.0\text{ mg/L}$, classifica severidade como `CRITICA`, aciona o protocolo de emergência (ligar aeradores imediatos e suspender ração) e notifica o vigia noturno na Central de Auditoria!
* **Consulta Zootécnica Instantânea:**
  - Digite: *"como tá o V-03?"* ou *"qual a biomassa do V-01?"*
  - Retorna o boletim completo: DOC, lote, peso médio, biomassa viva e oxigênio recente.

---

## 📁 5. Sincronizador de Planilhas do Google Drive

Clique no botão **"Sincronizar Drive"** no topo do cabeçalho ou no menu lateral:
* Lê os arquivos oficiais:
  - `CAMARÃO/MODELOS DE CONTROLE/Controle de alimentação e biometria/Controle_Alimentacao_e_Biometria.xlsx`
  - `CAMARÃO/MODELOS DE CONTROLE/Controle de qualidade de agua/Controle_Qualidade_Agua.xlsx`
* Mais de **1.330 tratos de alimentação** e **2.850 medições de água** sincronizados com proteção criptográfica SHA-256.
* Suporte a upload manual de arquivos `.xlsx` diretamente pelo navegador.

---

## 🗺️ 6. Mapa 2D dos 15 Viveiros & Drill-Down Analítico

* **Visualização Macro:** Status em tempo real por cor (🟢 Ótimo, 🟡 Atenção, 🔴 Alerta Crítico, ⚪ Vazio/Secando).
* **Navegação Analítica por Clique:** Clicar nos cards de KPI do topo (Biomassa, FCA, Ração, Estoque) abre as telas de detalhamento com rankings e gráficos.
* **Página Individual do Tanque:** Diário de bordo ciclo a ciclo (dias 1 a 58), gráficos de crescimento real vs teórico e oxigênio diurno/noturno.
* **Exportação em PDF Timbrado:** Modal de impressão executiva com parecer técnico e campos de assinatura formal.

---

## 🏢 7. Arquitetura Multi-Tenant: Fazenda Arrendada vs Fazenda Hakka

O cabeçalho conta com o seletor **🏢 Fazenda Arrendada** vs **🦐 Fazenda Hakka**:
* **Fazenda Arrendada:** 15 viveiros ativos, histórico completo de 2026 e DRE operacional independente.
* **Fazenda Hakka:** Espaço preparado para cadastro topográfico próprio (quando as dimensões e cotas de terraplenagem estiverem disponíveis), com checklist de onboarding e DRE patrimonial segregado.
