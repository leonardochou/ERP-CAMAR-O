# -*- coding: utf-8 -*-
"""
Script para atualizar o dashboard_interativo_prototipo.html adicionando:
1. Menu Lateral Completo (Sidebar) com todos os módulos gerenciais e zootécnicos.
2. Navegação Analítica por Clique (Drill-Down): clicar em qualquer card de KPI ou viveiro
   leva diretamente à página de detalhamento analítico com tabelas completas, filtros e gráficos.
3. Páginas analíticas dedicadas:
   - Biomassa & Biometrias
   - FCA & Eficiência Alimentar
   - Arraçoamento & Sobras de Bandejas
   - Estoque & Ração
   - Qualidade da Água
   - Página Analítica Individual Completa do Viveiro
   - Central de Auditoria Completa
   - Custos & DRE
   - Equipe & Turnos
   - Mercado & Cotações ABCC
"""

import os
import re

caminho_html = r"G:\Meu Drive\ANTIGRAVITY DRIVE\CAMARÃO\ERP CAMARÃO\dashboard_interativo_prototipo.html"

# Ler o arquivo atual
with open(caminho_html, "r", encoding="utf-8") as f:
    conteudo = f.read()

print(f"Tamanho original do arquivo: {len(conteudo)} caracteres, {len(conteudo.splitlines())} linhas.")
