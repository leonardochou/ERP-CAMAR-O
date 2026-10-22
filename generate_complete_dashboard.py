# -*- coding: utf-8 -*-
import os

output_path = r"G:\Meu Drive\ANTIGRAVITY DRIVE\CAMARÃO\ERP CAMARÃO\dashboard_interativo_prototipo.html"

# Vamos estruturar o HTML completo com Menu Lateral (Sidebar) e Visões Analíticas (Drill-Down)
html_content = r'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ERP Fazenda de Camarão — Ceará-Mirim/RN</title>
  
  <!-- Google Fonts: Inter & JetBrains Mono -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
  
  <!-- Font Awesome Icons -->
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  
  <!-- Tailwind CSS via CDN -->
  <script src="https://cdn.tailwindcss.com"></script>
  
  <!-- Chart.js via CDN -->
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

  <script>
    tailwind.config = {
      theme: {
        extend: {
          colors: {
            marinho: {
              DEFAULT: '#1B365D',
              dark: '#0F233E',
              light: '#244575'
            },
            aco: {
              DEFAULT: '#2B6CB0',
              light: '#3182CE'
            },
            gelo: {
              DEFAULT: '#EBF8FF',
              light: '#F7FAFC'
            },
            sucesso: {
              DEFAULT: '#16A34A',
              light: '#DCFCE7',
              dark: '#166534'
            },
            alerta: {
              DEFAULT: '#DC2626',
              light: '#FEE2E2',
              dark: '#991B1B'
            },
            aviso: {
              DEFAULT: '#D97706',
              light: '#FEF3C7',
              dark: '#92400E'
            }
          },
          fontFamily: {
            sans: ['Inter', 'sans-serif'],
            mono: ['JetBrains Mono', 'monospace']
          }
        }
      }
    }
  </script>

  <style>
    html, body {
      height: 100%;
      margin: 0;
      padding: 0;
      overflow: hidden;
      font-family: 'Inter', sans-serif;
      background-color: #F8FAFC;
      color: #1E293B;
    }
    .custom-scrollbar::-webkit-scrollbar {
      width: 6px;
      height: 6px;
    }
    .custom-scrollbar::-webkit-scrollbar-track {
      background: #F1F5F9;
    }
    .custom-scrollbar::-webkit-scrollbar-thumb {
      background: #CBD5E1;
      border-radius: 4px;
    }
    .custom-scrollbar::-webkit-scrollbar-thumb:hover {
      background: #94A3B8;
    }
    .sidebar-collapsed {
      width: 72px !important;
    }
    .sidebar-collapsed .sidebar-label,
    .sidebar-collapsed .sidebar-header-text,
    .sidebar-collapsed .sidebar-section-title,
    .sidebar-collapsed .sidebar-badge {
      display: none !important;
    }
    .sidebar-collapsed .nav-item {
      justify-content: center !important;
      padding-left: 0 !important;
      padding-right: 0 !important;
    }
    .clickable-kpi {
      cursor: pointer;
      transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .clickable-kpi:hover {
      transform: translateY(-2px);
      box-shadow: 0 10px 25px -5px rgba(27, 54, 93, 0.12), 0 8px 10px -6px rgba(27, 54, 93, 0.08);
      border-color: #2B6CB0;
    }
    @media print {
      body * {
        visibility: hidden;
      }
      #modal-relatorio-pdf, #modal-relatorio-pdf * {
        visibility: visible;
      }
      #modal-relatorio-pdf {
        position: static !important;
        background: white !important;
        padding: 0 !important;
        margin: 0 !important;
        overflow: visible !important;
      }
      #print-modal-content {
        position: absolute;
        left: 0;
        top: 0;
        width: 100%;
        margin: 0;
        padding: 0;
        background: white !important;
        box-shadow: none !important;
      }
      .no-print {
        display: none !important;
      }
    }
  </style>
</head>
<body class="flex bg-slate-50 text-slate-800">

  <!-- ======================================================== -->
  <!-- 1. MENU LATERAL EXECUTIVO (SIDEBAR DE MÓDULOS)           -->
  <!-- ======================================================== -->
  <aside id="app-sidebar" class="bg-marinho text-white w-64 shrink-0 flex flex-col justify-between transition-all duration-300 z-50 shadow-2xl relative select-none">
    
    <!-- Topo da Sidebar: Identidade & Botão Recolher -->
    <div class="flex flex-col min-h-0">
      <div class="h-20 px-4 border-b border-white/10 flex items-center justify-between">
        <div class="flex items-center space-x-3 overflow-hidden cursor-pointer" onclick="navegarPara('dashboard-macro')">
          <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-aco to-cyan-500 flex items-center justify-center text-xl shadow-md border border-white/20 shrink-0">
            🦐
          </div>
          <div class="sidebar-header-text overflow-hidden">
            <h2 class="text-sm font-extrabold tracking-tight text-white whitespace-nowrap">ERP CAMARÃO</h2>
            <p class="text-[11px] text-blue-200 font-medium truncate">Ceará-Mirim • RN</p>
          </div>
        </div>
        <button onclick="toggleSidebar()" class="p-2 rounded-lg bg-white/10 hover:bg-white/20 text-blue-200 hover:text-white transition shrink-0" title="Expandir/Recolher Menu Lateral">
          <i id="sidebar-toggle-icon" class="fa-solid fa-angles-left text-xs"></i>
        </button>
      </div>

      <!-- Lista de Navegação dos Módulos com Scroll Interno -->
      <nav class="flex-1 overflow-y-auto p-3 space-y-1 custom-scrollbar text-xs">
        
        <!-- Bloco 1: Visão Geral -->
        <div class="sidebar-section-title px-3 pt-2 pb-1 text-[10px] font-bold uppercase tracking-wider text-blue-300/70">
          Visão Geral
        </div>
        <button onclick="navegarPara('dashboard-macro')" id="nav-dashboard-macro" class="nav-item w-full flex items-center space-x-3 px-3 py-2.5 rounded-xl font-semibold transition bg-aco text-white shadow-sm">
          <i class="fa-solid fa-chart-pie w-5 text-center text-cyan-300"></i>
          <span class="sidebar-label">Dashboard Geral</span>
        </button>
        <button onclick="navegarPara('viveiros-mapa')" id="nav-viveiros-mapa" class="nav-item w-full flex items-center space-x-3 px-3 py-2.5 rounded-xl font-medium text-blue-200 hover:text-white hover:bg-white/10 transition">
          <i class="fa-solid fa-map-location-dot w-5 text-center text-emerald-300"></i>
          <span class="sidebar-label">Mapa dos Viveiros</span>
        </button>
        <button onclick="navegarPara('auditoria-central')" id="nav-auditoria-central" class="nav-item w-full flex items-center justify-between px-3 py-2.5 rounded-xl font-medium text-blue-200 hover:text-white hover:bg-white/10 transition">
          <div class="flex items-center space-x-3">
            <i class="fa-solid fa-shield-halved w-5 text-center text-amber-300"></i>
            <span class="sidebar-label">Central de Auditoria</span>
          </div>
          <span id="sidebar-audit-badge" class="sidebar-badge bg-alerta text-white text-[10px] font-extrabold px-1.5 py-0.5 rounded-full shadow-sm">3</span>
        </button>

        <!-- Bloco 2: Zootecnia & Manejo -->
        <div class="sidebar-section-title px-3 pt-4 pb-1 text-[10px] font-bold uppercase tracking-wider text-blue-300/70">
          Zootecnia & Manejo
        </div>
        <button onclick="navegarPara('analytics-biomassa')" id="nav-analytics-biomassa" class="nav-item w-full flex items-center space-x-3 px-3 py-2.5 rounded-xl font-medium text-blue-200 hover:text-white hover:bg-white/10 transition">
          <i class="fa-solid fa-shrimp w-5 text-center text-blue-300"></i>
          <span class="sidebar-label">Biometria & Biomassa</span>
        </button>
        <button onclick="navegarPara('analytics-fca')" id="nav-analytics-fca" class="nav-item w-full flex items-center space-x-3 px-3 py-2.5 rounded-xl font-medium text-blue-200 hover:text-white hover:bg-white/10 transition">
          <i class="fa-solid fa-scale-balanced w-5 text-center text-emerald-400"></i>
          <span class="sidebar-label">FCA & Conversão</span>
        </button>
        <button onclick="navegarPara('analytics-arracoamento')" id="nav-analytics-arracoamento" class="nav-item w-full flex items-center space-x-3 px-3 py-2.5 rounded-xl font-medium text-blue-200 hover:text-white hover:bg-white/10 transition">
          <i class="fa-solid fa-wheat-awn w-5 text-center text-amber-400"></i>
          <span class="sidebar-label">Arraçoamento & Sobras</span>
        </button>
        <button onclick="navegarPara('analytics-agua')" id="nav-analytics-agua" class="nav-item w-full flex items-center space-x-3 px-3 py-2.5 rounded-xl font-medium text-blue-200 hover:text-white hover:bg-white/10 transition">
          <i class="fa-solid fa-droplet w-5 text-center text-cyan-400"></i>
          <span class="sidebar-label">Qualidade da Água</span>
        </button>
        <button onclick="navegarPara('analytics-povoamento')" id="nav-analytics-povoamento" class="nav-item w-full flex items-center space-x-3 px-3 py-2.5 rounded-xl font-medium text-blue-200 hover:text-white hover:bg-white/10 transition">
          <i class="fa-solid fa-seedling w-5 text-center text-teal-300"></i>
          <span class="sidebar-label">Berçários & Pós-Larvas</span>
        </button>
        <button onclick="navegarPara('analytics-despesca')" id="nav-analytics-despesca" class="nav-item w-full flex items-center space-x-3 px-3 py-2.5 rounded-xl font-medium text-blue-200 hover:text-white hover:bg-white/10 transition">
          <i class="fa-solid fa-truck-ramp-box w-5 text-center text-indigo-300"></i>
          <span class="sidebar-label">Despesca & Vendas</span>
        </button>

        <!-- Bloco 3: Suprimentos & Controladoria -->
        <div class="sidebar-section-title px-3 pt-4 pb-1 text-[10px] font-bold uppercase tracking-wider text-blue-300/70">
          Gestão & Controladoria
        </div>
        <button onclick="navegarPara('analytics-estoque')" id="nav-analytics-estoque" class="nav-item w-full flex items-center space-x-3 px-3 py-2.5 rounded-xl font-medium text-blue-200 hover:text-white hover:bg-white/10 transition">
          <i class="fa-solid fa-boxes-stacked w-5 text-center text-orange-300"></i>
          <span class="sidebar-label">Estoque de Ração</span>
        </button>
        <button onclick="navegarPara('analytics-financeiro')" id="nav-analytics-financeiro" class="nav-item w-full flex items-center space-x-3 px-3 py-2.5 rounded-xl font-medium text-blue-200 hover:text-white hover:bg-white/10 transition">
          <i class="fa-solid fa-sack-dollar w-5 text-center text-yellow-300"></i>
          <span class="sidebar-label">Custos, DRE & Contas</span>
        </button>
        <button onclick="navegarPara('analytics-equipe')" id="nav-analytics-equipe" class="nav-item w-full flex items-center space-x-3 px-3 py-2.5 rounded-xl font-medium text-blue-200 hover:text-white hover:bg-white/10 transition">
          <i class="fa-solid fa-users-gear w-5 text-center text-violet-300"></i>
          <span class="sidebar-label">Equipe & Vigia Noturno</span>
        </button>
        <button onclick="navegarPara('analytics-mercado')" id="nav-analytics-mercado" class="nav-item w-full flex items-center space-x-3 px-3 py-2.5 rounded-xl font-medium text-blue-200 hover:text-white hover:bg-white/10 transition">
          <i class="fa-solid fa-arrow-trend-up w-5 text-center text-emerald-300"></i>
          <span class="sidebar-label">Cotações ABCC & Mercado</span>
        </button>
        <button onclick="navegarPara('analytics-ged')" id="nav-analytics-ged" class="nav-item w-full flex items-center space-x-3 px-3 py-2.5 rounded-xl font-medium text-blue-200 hover:text-white hover:bg-white/10 transition">
          <i class="fa-solid fa-folder-open w-5 text-center text-amber-200"></i>
          <span class="sidebar-label">GED & Notas / IDEMA</span>
        </button>

      </nav>
    </div>

    <!-- Rodapé da Sidebar: Status & Versão -->
    <div class="p-3 border-t border-white/10 bg-marinho-dark/80 sidebar-header-text text-[11px] text-blue-200 flex items-center justify-between">
      <div class="flex items-center space-x-2 truncate">
        <span class="w-2 h-2 rounded-full bg-sucesso animate-pulse shrink-0"></span>
        <span class="truncate">Safra 2026/2 • Ceará-Mirim</span>
      </div>
      <span class="text-blue-300 text-[10px] font-mono">v1.2</span>
    </div>

  </aside>

  <!-- ======================================================== -->
  <!-- 2. CONTAINER DE CONTEÚDO PRINCIPAL COM SCROLL           -->
  <!-- ======================================================== -->
  <div class="flex-1 flex flex-col min-w-0 h-screen overflow-y-auto custom-scrollbar">
    
    <!-- Topo / Barra Superior Fixa -->
    <header class="bg-marinho text-white shadow-md sticky top-0 z-40 transition-all">
      <div class="w-full px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-20">
          
          <!-- Botão Mobile para Abrir Sidebar + Título da Página Atual -->
          <div class="flex items-center space-x-3">
            <button onclick="toggleSidebarMobile()" class="p-2 rounded-lg bg-white/10 hover:bg-white/20 text-white lg:hidden">
              <i class="fa-solid fa-bars"></i>
            </button>
            <div>
              <div class="flex items-center space-x-2">
                <span id="page-title-badge" class="text-xs font-semibold px-2 py-0.5 rounded bg-aco/40 text-blue-100 border border-aco/50">Visão Geral</span>
                <h1 id="page-current-heading" class="text-base sm:text-lg font-bold text-white truncate">
                  Dashboard Macro da Fazenda
                </h1>
              </div>
              <p id="page-breadcrumb" class="text-xs text-blue-200 font-medium">Início > Visão Geral > Macro</p>
            </div>
          </div>

          <!-- Ações Rápidas do Topo: Auditoria, Perfil e Relógio -->
          <div class="flex items-center space-x-3">
            
            <!-- Botão Notificação Auditoria -->
            <button onclick="navegarPara('auditoria-central')" class="relative p-2.5 rounded-xl bg-white/10 hover:bg-white/20 text-white transition flex items-center gap-2 text-xs sm:text-sm font-medium">
              <i class="fa-solid fa-shield-halved text-amber-300"></i>
              <span class="hidden md:inline">Auditoria</span>
              <span id="badge-top-audit-count" class="bg-alerta text-white text-[11px] font-extrabold px-2 py-0.5 rounded-full shadow animate-pulse">3</span>
            </button>

            <!-- Alternador de Perfil Executivo vs Operacional -->
            <div class="bg-marinho-dark/90 p-1 rounded-xl border border-white/15 flex items-center shadow-inner">
              <button id="btn-profile-leo" onclick="switchProfile('leo')" class="flex items-center space-x-2 px-3 py-1.5 rounded-lg text-xs font-bold transition bg-aco text-white shadow">
                <i class="fa-solid fa-chart-pie"></i>
                <span class="hidden sm:inline">Visão Leonardo</span>
                <span class="sm:hidden">Escritório</span>
              </button>
              <button id="btn-profile-pai" onclick="switchProfile('pai')" class="flex items-center space-x-2 px-3 py-1.5 rounded-lg text-xs font-bold text-blue-200 hover:text-white transition">
                <i class="fa-solid fa-person-digging"></i>
                <span class="hidden sm:inline">Visão Pai / Campo</span>
                <span class="sm:hidden">Campo</span>
              </button>
            </div>

            <!-- Relógio ao Vivo -->
            <div class="hidden xl:flex flex-col text-right pl-2 border-l border-white/10 text-xs">
              <span id="live-clock" class="font-mono font-semibold text-white">15:30:00</span>
              <span class="text-blue-300 text-[10px]">Sync Nuvem Ativo</span>
            </div>

          </div>

        </div>
      </div>
    </header>

    <!-- Sub-Barra de Status Operacional e Contexto da Fazenda -->
    <div class="bg-white border-b border-slate-200 py-2.5 px-4 sm:px-6 lg:px-8 shadow-sm shrink-0">
      <div class="flex flex-wrap items-center justify-between gap-3 text-xs">
        <div class="flex items-center space-x-4 text-slate-600">
          <span class="flex items-center gap-1.5 font-medium">
            <span class="w-2.5 h-2.5 rounded-full bg-sucesso animate-pulse"></span>
            Operação Normal • Ceará-Mirim/RN
          </span>
          <span class="hidden sm:inline text-slate-300">|</span>
          <span class="hidden md:flex items-center gap-1 text-slate-600">
            <i class="fa-solid fa-cloud-sun text-amber-500"></i>
            Estuário: Maré em Enchente • Salinidade média 14 ppt
          </span>
        </div>

        <div class="flex items-center space-x-3 font-medium text-slate-600">
          <span class="flex items-center gap-1">
            <i class="fa-solid fa-layer-group text-aco"></i>
            15 Tanques Mapeados (11 em Cultivo)
          </span>
          <span class="text-slate-300">|</span>
          <span class="flex items-center gap-1 text-slate-700 cursor-pointer hover:text-aco transition" onclick="navegarPara('analytics-estoque')">
            <i class="fa-solid fa-warehouse text-slate-500"></i>
            Estoque: <strong class="text-slate-900">380 sacos</strong> (14 dias)
          </span>
        </div>
      </div>
    </div>

    <!-- ÁREA DINÂMICA DE VISÕES (SPA) -->
    <main class="flex-1 p-4 sm:p-6 lg:p-8 space-y-6">

      <!-- ======================================================== -->
      <!-- VIEW 1: DASHBOARD GERAL (MACRO) COM CARDS CLICÁVEIS      -->
      <!-- ======================================================== -->
      <section id="view-dashboard-macro" class="space-y-6">
        
        <!-- Banner Pai / Campo (visível apenas no modo pai) -->
        <div id="view-pai-banner" class="hidden bg-gradient-to-r from-amber-500 to-amber-600 rounded-2xl p-5 text-white shadow-md">
          <div class="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            <div class="flex items-center gap-3">
              <div class="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center text-2xl font-bold">🌾</div>
              <div>
                <h2 class="text-xl font-bold">Modo Operacional de Campo — Visão Simplificada</h2>
                <p class="text-amber-100 text-sm">Botões grandes e diretos. Lance medições em 2 cliques ou por áudio no WhatsApp.</p>
              </div>
            </div>
            <div class="flex flex-wrap items-center gap-2">
              <button onclick="openWhatsAppModal()" class="bg-white text-emerald-800 font-bold px-4 py-2.5 rounded-xl shadow hover:bg-emerald-50 transition flex items-center gap-2">
                <i class="fa-brands fa-whatsapp text-emerald-600 text-lg"></i> Gravar Áudio de Campo
              </button>
              <button onclick="abrirModalPreenchimentoRapido('V-01')" class="bg-amber-900/60 hover:bg-amber-900/80 text-white font-bold px-4 py-2.5 rounded-xl shadow transition flex items-center gap-2">
                <i class="fa-solid fa-plus-circle"></i> Lançar Ração Agora
              </button>
            </div>
          </div>
        </div>

        <!-- 4 CARDS DE KPIS CONSOLIDADOS (COM DRILL-DOWN CLICÁVEL) -->
        <div>
          <div class="flex items-center justify-between mb-3">
            <h2 class="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-2">
              <i class="fa-solid fa-gauge-high text-aco"></i> KPIs Consolidados da Fazenda
              <span class="text-[11px] font-normal text-slate-400 capitalize">(Clique no card para abrir o detalhamento analítico)</span>
            </h2>
            <span class="text-xs text-aco font-semibold flex items-center gap-1 hover:underline cursor-pointer" onclick="navegarPara('analytics-biomassa')">
              Ver todas as análises <i class="fa-solid fa-arrow-right text-[10px]"></i>
            </span>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            
            <!-- Card KPI 1: Biomassa Total -->
            <div onclick="navegarPara('analytics-biomassa')" class="clickable-kpi bg-white rounded-2xl p-5 border border-slate-200 shadow-sm relative overflow-hidden group">
              <div class="absolute top-0 right-0 w-24 h-24 bg-blue-50 rounded-bl-full -mr-6 -mt-6 transition group-hover:bg-blue-100"></div>
              <div class="flex items-center justify-between text-slate-500 mb-2 relative z-10">
                <span class="text-xs font-bold uppercase tracking-wider text-slate-600">Biomassa Viva Total</span>
                <div class="w-8 h-8 rounded-lg bg-blue-100/70 text-aco flex items-center justify-center">
                  <i class="fa-solid fa-shrimp"></i>
                </div>
              </div>
              <div class="flex items-baseline space-x-2 relative z-10">
                <span id="kpi-biomassa" class="text-3xl font-extrabold text-slate-800">31.400</span>
                <span class="text-sm font-bold text-slate-500">kg</span>
              </div>
              <div class="mt-2.5 flex items-center justify-between text-xs relative z-10">
                <span class="text-emerald-700 bg-emerald-50 font-bold px-2 py-0.5 rounded-full flex items-center gap-1">
                  <i class="fa-solid fa-arrow-trend-up"></i> +1.380 kg/sem
                </span>
                <span class="text-aco font-bold group-hover:translate-x-0.5 transition flex items-center gap-1">
                  Análise Detalhada <i class="fa-solid fa-chevron-right text-[10px]"></i>
                </span>
              </div>
            </div>

            <!-- Card KPI 2: FCA Médio -->
            <div onclick="navegarPara('analytics-fca')" class="clickable-kpi bg-white rounded-2xl p-5 border border-slate-200 shadow-sm relative overflow-hidden group">
              <div class="absolute top-0 right-0 w-24 h-24 bg-emerald-50 rounded-bl-full -mr-6 -mt-6 transition group-hover:bg-emerald-100"></div>
              <div class="flex items-center justify-between text-slate-500 mb-2 relative z-10">
                <span class="text-xs font-bold uppercase tracking-wider text-slate-600">FCA Médio Ponderado</span>
                <div class="w-8 h-8 rounded-lg bg-emerald-100/70 text-emerald-600 flex items-center justify-center">
                  <i class="fa-solid fa-scale-balanced"></i>
                </div>
              </div>
              <div class="flex items-baseline space-x-2 relative z-10">
                <span id="kpi-fca" class="text-3xl font-extrabold text-emerald-700">1.22</span>
                <span class="text-xs font-bold text-slate-400">Meta: ≤ 1.30</span>
              </div>
              <div class="mt-2.5 flex items-center justify-between text-xs relative z-10">
                <span class="text-emerald-700 bg-emerald-50 font-bold px-2 py-0.5 rounded-full flex items-center gap-1">
                  <i class="fa-solid fa-check"></i> Eficiência Ótima
                </span>
                <span class="text-aco font-bold group-hover:translate-x-0.5 transition flex items-center gap-1">
                  Ranking FCA <i class="fa-solid fa-chevron-right text-[10px]"></i>
                </span>
              </div>
            </div>

            <!-- Card KPI 3: Consumo Diário de Ração -->
            <div onclick="navegarPara('analytics-arracoamento')" class="clickable-kpi bg-white rounded-2xl p-5 border border-slate-200 shadow-sm relative overflow-hidden group">
              <div class="absolute top-0 right-0 w-24 h-24 bg-amber-50 rounded-bl-full -mr-6 -mt-6 transition group-hover:bg-amber-100"></div>
              <div class="flex items-center justify-between text-slate-500 mb-2 relative z-10">
                <span class="text-xs font-bold uppercase tracking-wider text-slate-600">Consumo Ração Hoje</span>
                <div class="w-8 h-8 rounded-lg bg-amber-100/70 text-amber-600 flex items-center justify-center">
                  <i class="fa-solid fa-wheat-awn"></i>
                </div>
              </div>
              <div class="flex items-baseline space-x-2 relative z-10">
                <span id="kpi-racao-hoje" class="text-3xl font-extrabold text-slate-800">685</span>
                <span class="text-sm font-bold text-slate-500">kg/dia</span>
              </div>
              <div class="mt-2.5 flex items-center justify-between text-xs relative z-10">
                <span class="text-slate-600 bg-slate-100 font-semibold px-2 py-0.5 rounded-full">
                  ~27.4 sacos de 25kg
                </span>
                <span class="text-aco font-bold group-hover:translate-x-0.5 transition flex items-center gap-1">
                  Sobras & Turnos <i class="fa-solid fa-chevron-right text-[10px]"></i>
                </span>
              </div>
            </div>

            <!-- Card KPI 4: Autonomia de Estoque -->
            <div onclick="navegarPara('analytics-estoque')" class="clickable-kpi bg-white rounded-2xl p-5 border border-slate-200 shadow-sm relative overflow-hidden group">
              <div class="absolute top-0 right-0 w-24 h-24 bg-orange-50 rounded-bl-full -mr-6 -mt-6 transition group-hover:bg-orange-100"></div>
              <div class="flex items-center justify-between text-slate-500 mb-2 relative z-10">
                <span class="text-xs font-bold uppercase tracking-wider text-slate-600">Autonomia de Estoque</span>
                <div class="w-8 h-8 rounded-lg bg-orange-100/70 text-orange-600 flex items-center justify-center">
                  <i class="fa-solid fa-boxes-stacked"></i>
                </div>
              </div>
              <div class="flex items-baseline space-x-2 relative z-10">
                <span id="kpi-estoque-dias" class="text-3xl font-extrabold text-slate-800">14</span>
                <span class="text-sm font-bold text-slate-500">dias</span>
              </div>
              <div class="mt-2.5 flex items-center justify-between text-xs relative z-10">
                <span class="text-blue-700 bg-blue-50 font-bold px-2 py-0.5 rounded-full">
                  380 sacos no galpão
                </span>
                <span class="text-aco font-bold group-hover:translate-x-0.5 transition flex items-center gap-1">
                  Ver Galpão <i class="fa-solid fa-chevron-right text-[10px]"></i>
                </span>
              </div>
            </div>

          </div>
        </div>

        <!-- SEÇÃO: CENTRAL DE AUDITORIA ATIVA (INTERATIVA COM RESOLUÇÃO DE 1 CLIQUE) -->
        <div id="secao-auditoria" class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
          <div class="bg-gradient-to-r from-slate-900 to-marinho p-4 sm:p-5 text-white flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
            <div class="flex items-center space-x-3">
              <div class="w-10 h-10 rounded-xl bg-amber-400/20 text-amber-300 border border-amber-400/30 flex items-center justify-center text-xl shrink-0">
                <i class="fa-solid fa-shield-halved"></i>
              </div>
              <div>
                <div class="flex items-center gap-2">
                  <h3 class="text-base font-bold text-white">Central de Auditoria Ativa de Dados</h3>
                  <span id="badge-audit-pill" class="bg-alerta text-white text-xs font-extrabold px-2.5 py-0.5 rounded-full">3 Pendências</span>
                </div>
                <p class="text-xs text-blue-200">Motor de integridade em tempo real: identifica duplicatas de planilhas, dias esquecidos e parâmetros fora da faixa zootécnica.</p>
              </div>
            </div>
            <button onclick="navegarPara('auditoria-central')" class="px-3 py-1.5 rounded-lg bg-white/10 hover:bg-white/20 text-white text-xs font-bold border border-white/20 transition flex items-center gap-1.5">
              <span>Abrir Painel Completo de Auditoria</span>
              <i class="fa-solid fa-arrow-up-right-from-square text-[10px]"></i>
            </button>
          </div>

          <!-- Cards das 3 Pendências Interativas -->
          <div class="p-4 sm:p-5 space-y-3.5 bg-slate-50/60">
            
            <!-- Pendência 1: Duplicidade -->
            <div id="card-pendencia-1" class="bg-white rounded-xl p-4 border-l-4 border-l-amber-500 border border-slate-200 shadow-sm transition hover:shadow">
              <div class="flex flex-col md:flex-row items-start md:items-center justify-between gap-3">
                <div class="space-y-1">
                  <div class="flex items-center gap-2">
                    <span class="px-2 py-0.5 rounded bg-amber-100 text-amber-800 text-xs font-bold uppercase">Duplicidade Conflitante</span>
                    <span class="text-xs font-semibold text-slate-500">Viveiro V-02 • Data: Ontem (20/10)</span>
                    <span class="text-xs px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 font-medium">Severidade Alta</span>
                  </div>
                  <p class="text-sm font-semibold text-slate-800">
                    Lançamento divergente no mesmo dia: Já constava <span class="text-slate-900 font-bold bg-slate-100 px-1 rounded">25 kg</span> (Planilha Sync), mas recebido <span class="text-aco font-bold bg-blue-50 px-1 rounded">35 kg</span> (Digitado pelo Operador).
                  </p>
                  <p class="text-xs text-slate-500">Selecione a ação para consolidar o dado e recalcular o FCA do viveiro:</p>
                </div>

                <div class="flex flex-wrap items-center gap-2 w-full md:w-auto shrink-0">
                  <button onclick="resolverPendencia(1, 'manter_novo', 'Substituído pelo novo lançamento (35 kg)')" class="px-3 py-1.5 rounded-lg bg-aco hover:bg-aco-light text-white text-xs font-bold shadow-sm transition flex items-center gap-1.5">
                    <i class="fa-solid fa-check"></i> Manter Novo (35 kg)
                  </button>
                  <button onclick="resolverPendencia(1, 'manter_antigo', 'Mantido valor já existente (25 kg)')" class="px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold border border-slate-300 transition flex items-center gap-1.5">
                    <i class="fa-solid fa-rotate-left"></i> Manter Antigo (25 kg)
                  </button>
                  <button onclick="resolverPendencia(1, 'somar', 'Valores somados como turnos distintos (60 kg)')" class="px-3 py-1.5 rounded-lg bg-emerald-50 hover:bg-emerald-100 text-emerald-700 text-xs font-bold border border-emerald-300 transition flex items-center gap-1.5">
                    <i class="fa-solid fa-plus"></i> Somar Turnos (60 kg)
                  </button>
                </div>
              </div>
            </div>

            <!-- Pendência 2: Dia Esquecido -->
            <div id="card-pendencia-2" class="bg-white rounded-xl p-4 border-l-4 border-l-blue-500 border border-slate-200 shadow-sm transition hover:shadow">
              <div class="flex flex-col md:flex-row items-start md:items-center justify-between gap-3">
                <div class="space-y-1">
                  <div class="flex items-center gap-2">
                    <span class="px-2 py-0.5 rounded bg-blue-100 text-aco text-xs font-bold uppercase">Dia Esquecido / Lacuna</span>
                    <span class="text-xs font-semibold text-slate-500">Viveiro V-04 • Data: Ontem (20/10)</span>
                    <span class="text-xs px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 font-medium">Severidade Média</span>
                  </div>
                  <p class="text-sm font-semibold text-slate-800">
                    Viveiro ativo em cultivo (DDC 30) sem registro de arraçoamento nem medição de água nas últimas 24h.
                  </p>
                  <p class="text-xs text-slate-500">Regularize o lançamento retroativo ou confirme se o viveiro esteve em jejum programado.</p>
                </div>

                <div class="flex flex-wrap items-center gap-2 w-full md:w-auto shrink-0">
                  <button onclick="abrirModalPreenchimentoRapido('V-04')" class="px-3 py-1.5 rounded-lg bg-aco hover:bg-aco-light text-white text-xs font-bold shadow-sm transition flex items-center gap-1.5">
                    <i class="fa-solid fa-pen-to-square"></i> Preencher Agora
                  </button>
                  <button onclick="resolverPendencia(2, 'jejum', 'Justificado: Tanque em Jejum programado para despesca')" class="px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold border border-slate-300 transition flex items-center gap-1.5">
                    <i class="fa-solid fa-ban"></i> Justificar Jejum
                  </button>
                </div>
              </div>
            </div>

            <!-- Pendência 3: O2 Crítico -->
            <div id="card-pendencia-3" class="bg-white rounded-xl p-4 border-l-4 border-l-alerta border border-slate-200 shadow-sm transition hover:shadow">
              <div class="flex flex-col md:flex-row items-start md:items-center justify-between gap-3">
                <div class="space-y-1">
                  <div class="flex items-center gap-2">
                    <span class="px-2 py-0.5 rounded bg-red-100 text-alerta text-xs font-bold uppercase flex items-center gap-1">
                      <i class="fa-solid fa-triangle-exclamation"></i> Alerta Crítico O₂ &lt; 3.0 mg/L
                    </span>
                    <span class="text-xs font-semibold text-slate-500">Viveiro V-08 • 03:30 da Madrugada</span>
                    <span class="text-xs px-2 py-0.5 rounded-full bg-red-50 text-red-700 font-bold">Risco de Asfixia</span>
                  </div>
                  <p class="text-sm font-semibold text-slate-800">
                    Oxigênio medido em <span class="text-alerta font-extrabold bg-red-50 px-1.5 py-0.5 rounded border border-red-200">2.6 mg/L</span> (Abaixo da zona de conforto zootécnico).
                  </p>
                  <p class="text-xs text-slate-500">Dispare alerta para o vigia ou registre a justificativa operacional de acionamento do aerador:</p>
                </div>

                <div class="flex flex-wrap items-center gap-2 w-full md:w-auto shrink-0">
                  <button onclick="dispararAlertaWhatsAppO2('V-08', 2.6)" class="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold shadow-sm transition flex items-center gap-1.5">
                    <i class="fa-brands fa-whatsapp text-sm"></i> Disparar Alerta WhatsApp
                  </button>
                  <button onclick="abrirModalJustificarO2('V-08', 2.6)" class="px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold border border-slate-300 transition flex items-center gap-1.5">
                    <i class="fa-solid fa-file-pen"></i> Justificar
                  </button>
                </div>
              </div>
            </div>

          </div>
        </div>

        <!-- MAPA 2D DOS 15 VIVEIROS DA FAZENDA -->
        <div id="secao-mapa-viveiros" class="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-4">
          <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
            <div>
              <h3 class="text-base font-bold text-slate-800 flex items-center gap-2">
                <i class="fa-solid fa-map text-aco"></i> Mapa Operacional dos 15 Viveiros
              </h3>
              <p class="text-xs text-slate-500">Cores refletem status zootécnico e sanitário em tempo real. Clique em um tanque para abrir a página analítica completa.</p>
            </div>

            <!-- Filtros Rápidos por Status -->
            <div class="flex flex-wrap items-center gap-1.5 text-xs bg-slate-100 p-1 rounded-xl">
              <button onclick="filtrarViveiros('todos')" id="filter-todos" class="px-2.5 py-1 rounded-lg font-bold bg-white text-slate-800 shadow-sm">Todos (15)</button>
              <button onclick="filtrarViveiros('otimo')" id="filter-otimo" class="px-2.5 py-1 rounded-lg font-medium text-slate-600 hover:text-slate-900">🟢 Ótimo</button>
              <button onclick="filtrarViveiros('atencao')" id="filter-atencao" class="px-2.5 py-1 rounded-lg font-medium text-slate-600 hover:text-slate-900">🟡 Atenção</button>
              <button onclick="filtrarViveiros('critico')" id="filter-critico" class="px-2.5 py-1 rounded-lg font-medium text-slate-600 hover:text-slate-900">🔴 Crítico</button>
              <button onclick="filtrarViveiros('vazio')" id="filter-vazio" class="px-2.5 py-1 rounded-lg font-medium text-slate-600 hover:text-slate-900">⚪ Vazio/Bacia</button>
            </div>
          </div>

          <!-- Grade Dinâmica dos 15 Viveiros -->
          <div id="grid-mapa-viveiros" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3.5 pt-2">
            <!-- Injetado dinamicamente via JS -->
          </div>
        </div>

      </section>

      <!-- ======================================================== -->
      <!-- VIEW 2: DETALHAMENTO ANALÍTICO DE BIOMASSA & BIOMETRIA   -->
      <!-- ======================================================== -->
      <section id="view-analytics-biomassa" class="hidden space-y-6">
        
        <!-- Header da Página Analítica com Breadcrumbs e Botão Voltar -->
        <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <div class="space-y-1">
            <div class="flex items-center space-x-2 text-xs font-semibold text-aco">
              <span class="cursor-pointer hover:underline" onclick="navegarPara('dashboard-macro')">Dashboard</span>
              <i class="fa-solid fa-chevron-right text-[10px] text-slate-400"></i>
              <span>Zootecnia</span>
              <i class="fa-solid fa-chevron-right text-[10px] text-slate-400"></i>
              <span class="text-slate-600">Biometria & Biomassa</span>
            </div>
            <h2 class="text-xl font-bold text-slate-900 flex items-center gap-2">
              <i class="fa-solid fa-shrimp text-aco"></i> Detalhamento Analítico de Biomassa e Biometrias
            </h2>
            <p class="text-xs text-slate-500">Consolidado zootécnico de pesagens, ganho de peso semanal, densidades de estocagem e biomassa viva estimada.</p>
          </div>
          <button onclick="navegarPara('dashboard-macro')" class="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs transition flex items-center gap-2">
            <i class="fa-solid fa-arrow-left"></i> Voltar ao Dashboard Geral
          </button>
        </div>

        <!-- Cards Analíticos do Módulo de Biomassa -->
        <div class="grid grid-cols-1 sm:grid-cols-4 gap-4">
          <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
            <span class="text-xs font-bold text-slate-500 uppercase">Biomassa Total Fazenda</span>
            <div class="text-2xl font-extrabold text-slate-800 mt-1">31.400 kg</div>
            <span class="text-[11px] text-emerald-600 font-semibold flex items-center gap-1 mt-1">
              <i class="fa-solid fa-arrow-up"></i> +1.380 kg nos últimos 7 dias
            </span>
          </div>
          <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
            <span class="text-xs font-bold text-slate-500 uppercase">Peso Médio Ponderado</span>
            <div class="text-2xl font-extrabold text-aco mt-1">11.8 g</div>
            <span class="text-[11px] text-slate-500 mt-1">Faixa comercial atual: 10g a 14g</span>
          </div>
          <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
            <span class="text-xs font-bold text-slate-500 uppercase">Ganho Semanal Médio</span>
            <div class="text-2xl font-extrabold text-emerald-600 mt-1">1.25 g/sem</div>
            <span class="text-[11px] text-emerald-700 font-semibold mt-1">Dentro da meta zootécnica</span>
          </div>
          <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
            <span class="text-xs font-bold text-slate-500 uppercase">Densidade Média Atual</span>
            <div class="text-2xl font-extrabold text-slate-800 mt-1">24.2 cam/m²</div>
            <span class="text-[11px] text-slate-500 mt-1">População viva estimada: 2.65M</span>
          </div>
        </div>

        <!-- Gráfico Comparativo de Biomassa por Viveiro -->
        <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
          <h3 class="text-sm font-bold text-slate-800 flex items-center gap-2">
            <i class="fa-solid fa-chart-bar text-aco"></i> Distribuição da Biomassa Estimada por Viveiro (kg)
          </h3>
          <div class="h-64 w-full">
            <canvas id="chart-biomassa-comparativo"></canvas>
          </div>
        </div>

        <!-- Tabela Analítica Completa dos 15 Viveiros -->
        <div class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden space-y-0">
          <div class="p-4 bg-slate-50 border-b border-slate-200 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
            <h3 class="text-sm font-bold text-slate-800 flex items-center gap-2">
              <i class="fa-solid fa-table-list text-aco"></i> Matriz Zootécnica de Biometria por Tanque
            </h3>
            <div class="text-xs text-slate-500">Mostrando 15 viveiros cadastrados</div>
          </div>

          <div class="overflow-x-auto">
            <table class="w-full text-left text-xs text-slate-700">
              <thead class="bg-slate-100 text-slate-600 font-bold uppercase tracking-wider text-[11px] border-b border-slate-200">
                <tr>
                  <th class="p-3">Tanque</th>
                  <th class="p-3">Área (ha)</th>
                  <th class="p-3">DDC</th>
                  <th class="p-3">Status</th>
                  <th class="p-3">Peso Médio (g)</th>
                  <th class="p-3">Ganho Semanal</th>
                  <th class="p-3">Biomassa Est. (kg)</th>
                  <th class="p-3">Densidade</th>
                  <th class="p-3 text-center">Ações</th>
                </tr>
              </thead>
              <tbody id="tbody-analytics-biomassa" class="divide-y divide-slate-100 font-medium">
                <!-- Injetado dinamicamente -->
              </tbody>
            </table>
          </div>
        </div>

      </section>

      <!-- ======================================================== -->
      <!-- VIEW 3: DETALHAMENTO ANALÍTICO DE FCA & EFICIÊNCIA       -->
      <!-- ======================================================== -->
      <section id="view-analytics-fca" class="hidden space-y-6">
        
        <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <div class="space-y-1">
            <div class="flex items-center space-x-2 text-xs font-semibold text-aco">
              <span class="cursor-pointer hover:underline" onclick="navegarPara('dashboard-macro')">Dashboard</span>
              <i class="fa-solid fa-chevron-right text-[10px] text-slate-400"></i>
              <span>Zootecnia</span>
              <i class="fa-solid fa-chevron-right text-[10px] text-slate-400"></i>
              <span class="text-slate-600">Eficiência Alimentar & FCA</span>
            </div>
            <h2 class="text-xl font-bold text-slate-900 flex items-center gap-2">
              <i class="fa-solid fa-scale-balanced text-emerald-600"></i> Detalhamento de Fator de Conversão Alimentar (FCA)
            </h2>
            <p class="text-xs text-slate-500">Relação entre ração total fornecida e biomassa produzida, detecção de desperdícios e custo alimentar por kg.</p>
          </div>
          <button onclick="navegarPara('dashboard-macro')" class="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs transition flex items-center gap-2">
            <i class="fa-solid fa-arrow-left"></i> Voltar ao Dashboard Geral
          </button>
        </div>

        <!-- 4 Cards de Resumo de FCA -->
        <div class="grid grid-cols-1 sm:grid-cols-4 gap-4">
          <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
            <span class="text-xs font-bold text-slate-500 uppercase">FCA Ponderado Fazenda</span>
            <div class="text-3xl font-extrabold text-emerald-700 mt-1">1.22</div>
            <span class="text-[11px] text-emerald-600 font-semibold mt-1">Excelente conversão (Meta ≤ 1.30)</span>
          </div>
          <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
            <span class="text-xs font-bold text-slate-500 uppercase">Melhor Conversão</span>
            <div class="text-2xl font-extrabold text-emerald-600 mt-1">V-05 (1.15)</div>
            <span class="text-[11px] text-slate-500 mt-1">DDC 45 • Bandejas 100% limpas</span>
          </div>
          <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
            <span class="text-xs font-bold text-slate-500 uppercase">Maior Alerta de Desvio</span>
            <div class="text-2xl font-extrabold text-alerta mt-1">V-08 (1.48)</div>
            <span class="text-[11px] text-alerta font-semibold mt-1">Suspeita de sobra/queda de consumo</span>
          </div>
          <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
            <span class="text-xs font-bold text-slate-500 uppercase">Custo Médio Ração/kg</span>
            <div class="text-2xl font-extrabold text-slate-800 mt-1">R$ 6,83 / kg</div>
            <span class="text-[11px] text-slate-500 mt-1">Considerando ração a R$ 5,60/kg</span>
          </div>
        </div>

        <!-- Tabela de Eficiência de FCA por Tanque -->
        <div class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
          <div class="p-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
            <h3 class="text-sm font-bold text-slate-800 flex items-center gap-2">
              <i class="fa-solid fa-ranking-star text-aco"></i> Ranking de Conversão Alimentar por Viveiro
            </h3>
            <span class="text-xs text-slate-500">Ordenado por eficiência</span>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full text-left text-xs text-slate-700">
              <thead class="bg-slate-100 text-slate-600 font-bold uppercase tracking-wider text-[11px] border-b border-slate-200">
                <tr>
                  <th class="p-3">Tanque</th>
                  <th class="p-3">DDC</th>
                  <th class="p-3">Biomassa (kg)</th>
                  <th class="p-3">Ração Acumulada</th>
                  <th class="p-3">FCA Atual</th>
                  <th class="p-3">Desvio da Meta (1.25)</th>
                  <th class="p-3">Custo Ração Acumulado</th>
                  <th class="p-3">Status Zootécnico</th>
                  <th class="p-3 text-center">Ações</th>
                </tr>
              </thead>
              <tbody id="tbody-analytics-fca" class="divide-y divide-slate-100 font-medium">
                <!-- Injetado dinamicamente via JS -->
              </tbody>
            </table>
          </div>
        </div>

      </section>

      <!-- ======================================================== -->
      <!-- VIEW 4: DETALHAMENTO DE ARRAÇOAMENTO & SOBRAS            -->
      <!-- ======================================================== -->
      <section id="view-analytics-arracoamento" class="hidden space-y-6">
        
        <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <div class="space-y-1">
            <div class="flex items-center space-x-2 text-xs font-semibold text-aco">
              <span class="cursor-pointer hover:underline" onclick="navegarPara('dashboard-macro')">Dashboard</span>
              <i class="fa-solid fa-chevron-right text-[10px] text-slate-400"></i>
              <span>Zootecnia</span>
              <i class="fa-solid fa-chevron-right text-[10px] text-slate-400"></i>
              <span class="text-slate-600">Arraçoamento & Sobras</span>
            </div>
            <h2 class="text-xl font-bold text-slate-900 flex items-center gap-2">
              <i class="fa-solid fa-wheat-awn text-amber-600"></i> Arraçoamento Diário & Leitura de Bandejas
            </h2>
            <p class="text-xs text-slate-500">Distribuição da alimentação por turno (manhã, tarde, noite) e controle rigoroso de sobras (nível 0 a 3).</p>
          </div>
          <button onclick="navegarPara('dashboard-macro')" class="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs transition flex items-center gap-2">
            <i class="fa-solid fa-arrow-left"></i> Voltar ao Dashboard Geral
          </button>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-4 gap-4">
          <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
            <span class="text-xs font-bold text-slate-500 uppercase">Consumo Total Hoje</span>
            <div class="text-3xl font-extrabold text-slate-800 mt-1">685 kg</div>
            <span class="text-[11px] text-slate-500 mt-1">27.4 sacos de 25 kg</span>
          </div>
          <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
            <span class="text-xs font-bold text-slate-500 uppercase">Turno Manhã (07h00)</span>
            <div class="text-2xl font-extrabold text-aco mt-1">240 kg</div>
            <span class="text-[11px] text-slate-500 mt-1">35% da ração diária</span>
          </div>
          <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
            <span class="text-xs font-bold text-slate-500 uppercase">Turno Tarde (11h30)</span>
            <div class="text-2xl font-extrabold text-amber-600 mt-1">235 kg</div>
            <span class="text-[11px] text-slate-500 mt-1">34% da ração diária</span>
          </div>
          <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
            <span class="text-xs font-bold text-slate-500 uppercase">Turno Noite (16h30)</span>
            <div class="text-2xl font-extrabold text-slate-700 mt-1">210 kg</div>
            <span class="text-[11px] text-slate-500 mt-1">31% da ração diária</span>
          </div>
        </div>

        <div class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
          <div class="p-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
            <h3 class="text-sm font-bold text-slate-800 flex items-center gap-2">
              <i class="fa-solid fa-list-check text-aco"></i> Arraçoamento de Hoje por Viveiro e Leitura de Bandeja
            </h3>
            <button onclick="abrirModalPreenchimentoRapido('V-01')" class="px-3 py-1.5 rounded-lg bg-aco hover:bg-aco-light text-white font-bold text-xs shadow-sm transition flex items-center gap-1.5">
              <i class="fa-solid fa-plus"></i> Novo Lançamento
            </button>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full text-left text-xs text-slate-700">
              <thead class="bg-slate-100 text-slate-600 font-bold uppercase tracking-wider text-[11px] border-b border-slate-200">
                <tr>
                  <th class="p-3">Tanque</th>
                  <th class="p-3">Tipo Ração</th>
                  <th class="p-3">Manhã (kg)</th>
                  <th class="p-3">Tarde (kg)</th>
                  <th class="p-3">Noite (kg)</th>
                  <th class="p-3">Total Dia (kg)</th>
                  <th class="p-3">Sobra Bandeja</th>
                  <th class="p-3">Ajuste Recomendado</th>
                  <th class="p-3 text-center">Ações</th>
                </tr>
              </thead>
              <tbody id="tbody-analytics-arracoamento" class="divide-y divide-slate-100 font-medium">
                <!-- Injetado dinamicamente via JS -->
              </tbody>
            </table>
          </div>
        </div>

      </section>

      <!-- ======================================================== -->
      <!-- VIEW 5: DETALHAMENTO DE ESTOQUE DE RAÇÃO & INSUMOS       -->
      <!-- ======================================================== -->
      <section id="view-analytics-estoque" class="hidden space-y-6">
        
        <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <div class="space-y-1">
            <div class="flex items-center space-x-2 text-xs font-semibold text-aco">
              <span class="cursor-pointer hover:underline" onclick="navegarPara('dashboard-macro')">Dashboard</span>
              <i class="fa-solid fa-chevron-right text-[10px] text-slate-400"></i>
              <span>Suprimentos</span>
              <i class="fa-solid fa-chevron-right text-[10px] text-slate-400"></i>
              <span class="text-slate-600">Estoque de Ração</span>
            </div>
            <h2 class="text-xl font-bold text-slate-900 flex items-center gap-2">
              <i class="fa-solid fa-boxes-stacked text-orange-600"></i> Gestão do Galpão de Ração e Insumos
            </h2>
            <p class="text-xs text-slate-500">Saldo físico por tipo de ração, cálculo de autonomia em dias e controle do ponto de reposição crítico.</p>
          </div>
          <button onclick="navegarPara('dashboard-macro')" class="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs transition flex items-center gap-2">
            <i class="fa-solid fa-arrow-left"></i> Voltar ao Dashboard Geral
          </button>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-4 gap-4">
          <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
            <span class="text-xs font-bold text-slate-500 uppercase">Saldo Físico Galpão</span>
            <div class="text-3xl font-extrabold text-slate-800 mt-1">380 sacos</div>
            <span class="text-[11px] text-slate-500 mt-1">9.500 kg totais</span>
          </div>
          <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
            <span class="text-xs font-bold text-slate-500 uppercase">Autonomia Estimada</span>
            <div class="text-2xl font-extrabold text-emerald-600 mt-1">14 dias</div>
            <span class="text-[11px] text-slate-500 mt-1">Consumo de 27.4 sacos/dia</span>
          </div>
          <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
            <span class="text-xs font-bold text-slate-500 uppercase">Ponto de Reposição</span>
            <div class="text-2xl font-extrabold text-amber-600 mt-1">7 dias (190 sacos)</div>
            <span class="text-[11px] text-amber-700 font-semibold mt-1">Previsão de pedido: em 7 dias</span>
          </div>
          <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
            <span class="text-xs font-bold text-slate-500 uppercase">Valor em Estoque</span>
            <div class="text-2xl font-extrabold text-slate-800 mt-1">R$ 53.200,00</div>
            <span class="text-[11px] text-slate-500 mt-1">Preço médio R$ 140/saco</span>
          </div>
        </div>

        <!-- Tabela de Lotes de Ração no Galpão -->
        <div class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
          <div class="p-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
            <h3 class="text-sm font-bold text-slate-800 flex items-center gap-2">
              <i class="fa-solid fa-warehouse text-aco"></i> Lotes e Tipos de Ração em Estoque
            </h3>
            <span class="text-xs text-slate-500">Última contagem física: 20/10/2026</span>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full text-left text-xs text-slate-700">
              <thead class="bg-slate-100 text-slate-600 font-bold uppercase tracking-wider text-[11px] border-b border-slate-200">
                <tr>
                  <th class="p-3">Produto / Marca</th>
                  <th class="p-3">Proteína</th>
                  <th class="p-3">Granulometria</th>
                  <th class="p-3">Saldo (Sacos)</th>
                  <th class="p-3">Saldo (kg)</th>
                  <th class="p-3">Autonomia</th>
                  <th class="p-3">Lote</th>
                  <th class="p-3">Validade</th>
                  <th class="p-3">Status</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100 font-medium">
                <tr class="hover:bg-slate-50">
                  <td class="p-3 font-bold text-slate-900">Guabi Nutrimar Engorda</td>
                  <td class="p-3">35% PB</td>
                  <td class="p-3">1.6 mm</td>
                  <td class="p-3 font-extrabold text-slate-800">180</td>
                  <td class="p-3">4.500 kg</td>
                  <td class="p-3 text-emerald-600 font-bold">7.5 dias</td>
                  <td class="p-3 font-mono">GB-26-881</td>
                  <td class="p-3">15/01/2027</td>
                  <td class="p-3"><span class="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 font-bold text-[10px]">Normal</span></td>
                </tr>
                <tr class="hover:bg-slate-50">
                  <td class="p-3 font-bold text-slate-900">Presence Camarão Crescimento</td>
                  <td class="p-3">35% PB</td>
                  <td class="p-3">1.4 mm</td>
                  <td class="p-3 font-extrabold text-slate-800">120</td>
                  <td class="p-3">3.000 kg</td>
                  <td class="p-3 text-emerald-600 font-bold">5.0 dias</td>
                  <td class="p-3 font-mono">PR-26-402</td>
                  <td class="p-3">28/02/2027</td>
                  <td class="p-3"><span class="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 font-bold text-[10px]">Normal</span></td>
                </tr>
                <tr class="hover:bg-slate-50">
                  <td class="p-3 font-bold text-slate-900">Guabi Inicial Micropeletizada</td>
                  <td class="p-3">40% PB</td>
                  <td class="p-3">0.8 - 1.0 mm</td>
                  <td class="p-3 font-extrabold text-slate-800">50</td>
                  <td class="p-3">1.250 kg</td>
                  <td class="p-3 text-emerald-600 font-bold">25 dias</td>
                  <td class="p-3 font-mono">GB-26-109</td>
                  <td class="p-3">10/03/2027</td>
                  <td class="p-3"><span class="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 font-bold text-[10px]">Normal</span></td>
                </tr>
                <tr class="hover:bg-slate-50">
                  <td class="p-3 font-bold text-slate-900">Ração Berçário Pó / PL</td>
                  <td class="p-3">45% PB</td>
                  <td class="p-3">Micro (Pó)</td>
                  <td class="p-3 font-extrabold text-amber-700">30</td>
                  <td class="p-3">750 kg</td>
                  <td class="p-3 text-amber-700 font-bold">15 dias</td>
                  <td class="p-3 font-mono">BC-26-044</td>
                  <td class="p-3">05/12/2026</td>
                  <td class="p-3"><span class="px-2 py-0.5 rounded bg-amber-100 text-amber-800 font-bold text-[10px]">Ponto Atenção</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

      </section>

      <!-- ======================================================== -->
      <!-- VIEW 6: DETALHAMENTO DA QUALIDADE DA ÁGUA                -->
      <!-- ======================================================== -->
      <section id="view-analytics-agua" class="hidden space-y-6">
        
        <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <div class="space-y-1">
            <div class="flex items-center space-x-2 text-xs font-semibold text-aco">
              <span class="cursor-pointer hover:underline" onclick="navegarPara('dashboard-macro')">Dashboard</span>
              <i class="fa-solid fa-chevron-right text-[10px] text-slate-400"></i>
              <span>Zootecnia</span>
              <i class="fa-solid fa-chevron-right text-[10px] text-slate-400"></i>
              <span class="text-slate-600">Qualidade da Água</span>
            </div>
            <h2 class="text-xl font-bold text-slate-900 flex items-center gap-2">
              <i class="fa-solid fa-droplet text-cyan-600"></i> Monitoramento de Parâmetros Físico-Químicos da Água
            </h2>
            <p class="text-xs text-slate-500">Matriz de Oxigênio Dissolvido (manhã e noite), pH, Salinidade estuarina, Transparência Secchi e Amônia Total.</p>
          </div>
          <button onclick="navegarPara('dashboard-macro')" class="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs transition flex items-center gap-2">
            <i class="fa-solid fa-arrow-left"></i> Voltar ao Dashboard Geral
          </button>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-4 gap-4">
          <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
            <span class="text-xs font-bold text-slate-500 uppercase">O2 Médio Matutino (05h30)</span>
            <div class="text-3xl font-extrabold text-slate-800 mt-1">4.3 mg/L</div>
            <span class="text-[11px] text-emerald-600 font-semibold mt-1">Limite crítico: &lt; 3.0 mg/L</span>
          </div>
          <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
            <span class="text-xs font-bold text-slate-500 uppercase">O2 Médio Noturno (22h00)</span>
            <div class="text-2xl font-extrabold text-aco mt-1">4.7 mg/L</div>
            <span class="text-[11px] text-slate-500 mt-1">Aeradores operando em 11 tanques</span>
          </div>
          <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
            <span class="text-xs font-bold text-slate-500 uppercase">Salinidade Estuário</span>
            <div class="text-2xl font-extrabold text-cyan-600 mt-1">14.0 ppt</div>
            <span class="text-[11px] text-slate-500 mt-1">Faixa ideal: 10 a 25 ppt</span>
          </div>
          <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
            <span class="text-xs font-bold text-slate-500 uppercase">Variação Média de pH</span>
            <div class="text-2xl font-extrabold text-slate-800 mt-1">Δ 0.4 pH</div>
            <span class="text-[11px] text-emerald-600 font-semibold mt-1">Equilíbrio de fitoplâncton estável</span>
          </div>
        </div>

        <div class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
          <div class="p-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
            <h3 class="text-sm font-bold text-slate-800 flex items-center gap-2">
              <i class="fa-solid fa-flask-vial text-aco"></i> Matriz de Medições da Água por Viveiro
            </h3>
            <span class="text-xs text-slate-500">Registros das últimas 24h</span>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full text-left text-xs text-slate-700">
              <thead class="bg-slate-100 text-slate-600 font-bold uppercase tracking-wider text-[11px] border-b border-slate-200">
                <tr>
                  <th class="p-3">Tanque</th>
                  <th class="p-3">O2 Manhã (mg/L)</th>
                  <th class="p-3">O2 Noite (mg/L)</th>
                  <th class="p-3">Salinidade</th>
                  <th class="p-3">pH Manhã</th>
                  <th class="p-3">pH Tarde</th>
                  <th class="p-3">Delta pH</th>
                  <th class="p-3">Secchi (cm)</th>
                  <th class="p-3">Amônia (mg/L)</th>
                  <th class="p-3">Status Água</th>
                </tr>
              </thead>
              <tbody id="tbody-analytics-agua" class="divide-y divide-slate-100 font-medium">
                <!-- Injetado dinamicamente via JS -->
              </tbody>
            </table>
          </div>
        </div>

      </section>

      <!-- ======================================================== -->
      <!-- VIEW 7: PÁGINA ANALÍTICA INDIVIDUAL DO VIVEIRO (DRILL)   -->
      <!-- ======================================================== -->
      <section id="view-analytics-viveiro-detalhe" class="hidden space-y-6">
        
        <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <div class="space-y-1">
            <div class="flex items-center space-x-2 text-xs font-semibold text-aco">
              <span class="cursor-pointer hover:underline" onclick="navegarPara('dashboard-macro')">Dashboard</span>
              <i class="fa-solid fa-chevron-right text-[10px] text-slate-400"></i>
              <span class="cursor-pointer hover:underline" onclick="navegarPara('viveiros-mapa')">Viveiros</span>
              <i class="fa-solid fa-chevron-right text-[10px] text-slate-400"></i>
              <span id="detail-viv-breadcrumb" class="text-slate-600">Viveiro 01</span>
            </div>
            <div class="flex items-center space-x-3">
              <h2 id="detail-viv-title" class="text-2xl font-extrabold text-slate-900">Viveiro 01 (V-01)</h2>
              <span id="detail-viv-status-badge" class="px-2.5 py-1 rounded-full text-xs font-extrabold bg-emerald-100 text-emerald-800">🟢 Ótimo</span>
            </div>
            <p id="detail-viv-subtitle" class="text-xs text-slate-500">Povoamento: 24/08/2026 • Área: 1.2 ha (12.000 m²) • Densidade: 23 cam/m²</p>
          </div>
          
          <div class="flex items-center space-x-2">
            <button onclick="gerarRelatorioPDF()" class="px-4 py-2 rounded-xl bg-aco hover:bg-aco-light text-white font-bold text-xs shadow transition flex items-center gap-2">
              <i class="fa-solid fa-file-pdf"></i> Imprimir Relatório Executivo PDF
            </button>
            <button onclick="navegarPara('dashboard-macro')" class="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs transition flex items-center gap-2">
              <i class="fa-solid fa-arrow-left"></i> Voltar
            </button>
          </div>
        </div>

        <!-- 6 Cards de Indicadores do Tanque -->
        <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          <div class="bg-white p-3.5 rounded-xl border border-slate-200 text-center shadow-sm">
            <span class="text-[11px] font-bold text-slate-400 uppercase">DDC (Dias)</span>
            <div id="detail-card-ddc" class="text-xl font-extrabold text-slate-800 mt-0.5">58 dias</div>
          </div>
          <div class="bg-white p-3.5 rounded-xl border border-slate-200 text-center shadow-sm">
            <span class="text-[11px] font-bold text-slate-400 uppercase">Peso Médio</span>
            <div id="detail-card-peso" class="text-xl font-extrabold text-aco mt-0.5">12.4 g</div>
          </div>
          <div class="bg-white p-3.5 rounded-xl border border-slate-200 text-center shadow-sm">
            <span class="text-[11px] font-bold text-slate-400 uppercase">Biomassa Estimada</span>
            <div id="detail-card-biomassa" class="text-xl font-extrabold text-slate-800 mt-0.5">3.420 kg</div>
          </div>
          <div class="bg-white p-3.5 rounded-xl border border-slate-200 text-center shadow-sm">
            <span class="text-[11px] font-bold text-slate-400 uppercase">FCA Parcial</span>
            <div id="detail-card-fca" class="text-xl font-extrabold text-emerald-600 mt-0.5">1.19</div>
          </div>
          <div class="bg-white p-3.5 rounded-xl border border-slate-200 text-center shadow-sm">
            <span class="text-[11px] font-bold text-slate-400 uppercase">Ração Acumulada</span>
            <div id="detail-card-racao-acum" class="text-xl font-extrabold text-amber-700 mt-0.5">4.070 kg</div>
          </div>
          <div class="bg-white p-3.5 rounded-xl border border-slate-200 text-center shadow-sm">
            <span class="text-[11px] font-bold text-slate-400 uppercase">Sobrevivência</span>
            <div id="detail-card-sobrevivencia" class="text-xl font-extrabold text-slate-800 mt-0.5">84.5%</div>
          </div>
        </div>

        <!-- Dois Gráficos do Tanque: Biometria e Oxigênio -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-5">
          <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
            <h3 class="text-sm font-bold text-slate-800 flex items-center gap-2">
              <i class="fa-solid fa-chart-line text-aco"></i> Curva de Crescimento Semanal (Real vs Meta Teórica)
            </h3>
            <div class="h-60 w-full">
              <canvas id="chart-detail-crescimento"></canvas>
            </div>
          </div>
          <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
            <h3 class="text-sm font-bold text-slate-800 flex items-center gap-2">
              <i class="fa-solid fa-wave-square text-cyan-600"></i> Histórico de Oxigênio Dissolvido (Manhã e Noite)
            </h3>
            <div class="h-60 w-full">
              <canvas id="chart-detail-oxigenio"></canvas>
            </div>
          </div>
        </div>

        <!-- Tabela do Diário de Campo Ciclo a Ciclo -->
        <div class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
          <div class="p-4 bg-slate-50 border-b border-slate-200 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
            <h3 class="text-sm font-bold text-slate-800 flex items-center gap-2">
              <i class="fa-solid fa-calendar-days text-aco"></i> Diário de Bordo Operacional (Histórico Diário do Tanque)
            </h3>
            <span class="text-xs text-slate-500">Últimos 10 lançamentos diários do ciclo</span>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full text-left text-xs text-slate-700">
              <thead class="bg-slate-100 text-slate-600 font-bold uppercase tracking-wider text-[11px] border-b border-slate-200">
                <tr>
                  <th class="p-3">DDC</th>
                  <th class="p-3">Data</th>
                  <th class="p-3">Ração Manhã</th>
                  <th class="p-3">Ração Tarde</th>
                  <th class="p-3">Ração Noite</th>
                  <th class="p-3">Total Dia</th>
                  <th class="p-3">Sobra Bandeja</th>
                  <th class="p-3">O2 Manhã</th>
                  <th class="p-3">O2 Noite</th>
                  <th class="p-3">Salinidade</th>
                  <th class="p-3">Biometria</th>
                </tr>
              </thead>
              <tbody id="tbody-detail-diario" class="divide-y divide-slate-100 font-medium">
                <!-- Injetado dinamicamente via JS -->
              </tbody>
            </table>
          </div>
        </div>

      </section>

      <!-- ======================================================== -->
      <!-- VIEW 8: CENTRAL DE AUDITORIA COMPLETA (TELA DEDICADA)    -->
      <!-- ======================================================== -->
      <section id="view-auditoria-central" class="hidden space-y-6">
        
        <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <div class="space-y-1">
            <div class="flex items-center space-x-2 text-xs font-semibold text-aco">
              <span class="cursor-pointer hover:underline" onclick="navegarPara('dashboard-macro')">Dashboard</span>
              <i class="fa-solid fa-chevron-right text-[10px] text-slate-400"></i>
              <span>Integridade</span>
              <i class="fa-solid fa-chevron-right text-[10px] text-slate-400"></i>
              <span class="text-slate-600">Central de Auditoria</span>
            </div>
            <h2 class="text-xl font-bold text-slate-900 flex items-center gap-2">
              <i class="fa-solid fa-shield-halved text-amber-500"></i> Central Executiva de Auditoria & Consistência
            </h2>
            <p class="text-xs text-slate-500">Histórico de verificações, conciliação de lançamentos duplicados, gaps temporais e anomalias zootécnicas tratadas.</p>
          </div>
          <button onclick="navegarPara('dashboard-macro')" class="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs transition flex items-center gap-2">
            <i class="fa-solid fa-arrow-left"></i> Voltar ao Dashboard Geral
          </button>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
            <span class="text-xs font-bold text-slate-500 uppercase">Pendências Ativas</span>
            <div id="full-audit-pending-count" class="text-3xl font-extrabold text-alerta mt-1">3</div>
            <span class="text-[11px] text-slate-500 mt-1">Exigem ação imediata do gestor</span>
          </div>
          <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
            <span class="text-xs font-bold text-slate-500 uppercase">Inconsistências Tratadas</span>
            <div id="full-audit-resolved-count" class="text-3xl font-extrabold text-emerald-600 mt-1">28</div>
            <span class="text-[11px] text-emerald-700 font-semibold mt-1">Na Safra 2026/2</span>
          </div>
          <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
            <span class="text-xs font-bold text-slate-500 uppercase">Taxa de Integridade dos Dados</span>
            <div class="text-3xl font-extrabold text-aco mt-1">99.4%</div>
            <span class="text-[11px] text-slate-500 mt-1">Auditado contra modelos Excel</span>
          </div>
        </div>

        <div class="bg-white rounded-2xl border border-slate-200 shadow-sm p-5 space-y-4">
          <h3 class="text-sm font-bold text-slate-800">Regras e Gatilhos de Disparo Ativos:</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
            <div class="p-3 bg-red-50 border border-red-200 rounded-xl">
              <strong class="text-red-900 block font-bold">🚨 O₂ Dissolvido Crítico (&lt; 3.0 mg/L)</strong>
              <p class="text-red-800 mt-0.5">Disparo sonoro imediato e webhook de WhatsApp para o vigia de oxigênio da madrugada.</p>
            </div>
            <div class="p-3 bg-amber-50 border border-amber-200 rounded-xl">
              <strong class="text-amber-900 block font-bold">⚠️ Duplicidade de Lançamento no Mesmo Dia</strong>
              <p class="text-amber-800 mt-0.5">Bloqueio preventivo de cálculo e abertura de fila de mesclagem em 1 clique.</p>
            </div>
            <div class="p-3 bg-blue-50 border border-blue-200 rounded-xl">
              <strong class="text-blue-900 block font-bold">📅 Lacuna de Registro Diário (&gt; 24h sem arraçoamento)</strong>
              <p class="text-blue-800 mt-0.5">Alerta de dia esquecido com formulário pré-carregado ou opção de justificar jejum.</p>
            </div>
            <div class="p-3 bg-purple-50 border border-purple-200 rounded-xl">
              <strong class="text-purple-900 block font-bold">📉 FCA Acima de 1.8 com DDC &lt; 60 dias</strong>
              <p class="text-purple-800 mt-0.5">Alerta sanitário de mortalidade oculta (mionecrose) ou desperdício de ração em bandejas.</p>
            </div>
          </div>
        </div>

      </section>

      <!-- ======================================================== -->
      <!-- VIEW 9: FINANCEIRO, CUSTOS & DRE                         -->
      <!-- ======================================================== -->
      <section id="view-analytics-financeiro" class="hidden space-y-6">
        <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <div class="space-y-1">
            <div class="flex items-center space-x-2 text-xs font-semibold text-aco">
              <span class="cursor-pointer hover:underline" onclick="navegarPara('dashboard-macro')">Dashboard</span>
              <i class="fa-solid fa-chevron-right text-[10px] text-slate-400"></i>
              <span>Controladoria</span>
              <i class="fa-solid fa-chevron-right text-[10px] text-slate-400"></i>
              <span class="text-slate-600">Custos & DRE</span>
            </div>
            <h2 class="text-xl font-bold text-slate-900 flex items-center gap-2">
              <i class="fa-solid fa-sack-dollar text-yellow-600"></i> Gestão Financeira, Custos por Viveiro & DRE
            </h2>
            <p class="text-xs text-slate-500">Apuração de custos diretos (ração, pós-larvas, energia, insumos) e margem de contribuição por kg despescado.</p>
          </div>
          <button onclick="navegarPara('dashboard-macro')" class="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs transition flex items-center gap-2">
            <i class="fa-solid fa-arrow-left"></i> Voltar ao Dashboard Geral
          </button>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-4 gap-4">
          <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
            <span class="text-xs font-bold text-slate-500 uppercase">Custo Total Acumulado</span>
            <div class="text-2xl font-extrabold text-slate-800 mt-1">R$ 384.200,00</div>
            <span class="text-[11px] text-slate-500 mt-1">Safra 2026/2 até hoje</span>
          </div>
          <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
            <span class="text-xs font-bold text-slate-500 uppercase">Custo Médio / kg Produzido</span>
            <div class="text-2xl font-extrabold text-aco mt-1">R$ 12,23 / kg</div>
            <span class="text-[11px] text-emerald-600 font-semibold mt-1">Margem segura vs venda</span>
          </div>
          <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
            <span class="text-xs font-bold text-slate-500 uppercase">Preço Médio Venda ABCC</span>
            <div class="text-2xl font-extrabold text-emerald-600 mt-1">R$ 21,50 / kg</div>
            <span class="text-[11px] text-slate-500 mt-1">Camarão 12g no atacado RN</span>
          </div>
          <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
            <span class="text-xs font-bold text-slate-500 uppercase">Margem Bruta Projetada</span>
            <div class="text-2xl font-extrabold text-emerald-700 mt-1">43.1%</div>
            <span class="text-[11px] text-emerald-700 font-semibold mt-1">Lucro estimado: R$ 290k</span>
          </div>
        </div>
      </section>

      <!-- ======================================================== -->
      <!-- VIEW 10: EQUIPE, TURNOS & VIGIA NOTURNO                  -->
      <!-- ======================================================== -->
      <section id="view-analytics-equipe" class="hidden space-y-6">
        <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <div class="space-y-1">
            <div class="flex items-center space-x-2 text-xs font-semibold text-aco">
              <span class="cursor-pointer hover:underline" onclick="navegarPara('dashboard-macro')">Dashboard</span>
              <i class="fa-solid fa-chevron-right text-[10px] text-slate-400"></i>
              <span>Operação</span>
              <i class="fa-solid fa-chevron-right text-[10px] text-slate-400"></i>
              <span class="text-slate-600">Equipe & Turnos</span>
            </div>
            <h2 class="text-xl font-bold text-slate-900 flex items-center gap-2">
              <i class="fa-solid fa-users-gear text-violet-600"></i> Gestão de Colaboradores e Escalas de Campo
            </h2>
            <p class="text-xs text-slate-500">Escala de turnos diurnos de arraçoamento e vigia noturno de oxigênio e aeradores.</p>
          </div>
          <button onclick="navegarPara('dashboard-macro')" class="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs transition flex items-center gap-2">
            <i class="fa-solid fa-arrow-left"></i> Voltar ao Dashboard Geral
          </button>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
            <span class="text-xs font-bold text-slate-500 uppercase">Equipe em Campo Hoje</span>
            <div class="text-2xl font-extrabold text-slate-800 mt-1">5 Colaboradores</div>
            <span class="text-[11px] text-emerald-600 font-semibold mt-1">100% presentes</span>
          </div>
          <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
            <span class="text-xs font-bold text-slate-500 uppercase">Vigia Noturno Hoje</span>
            <div class="text-2xl font-extrabold text-violet-700 mt-1">Carlos Silva</div>
            <span class="text-[11px] text-slate-500 mt-1">Turno: 21h00 às 06h00 (Oxigênio)</span>
          </div>
          <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
            <span class="text-xs font-bold text-slate-500 uppercase">Próxima Ronda Noturna</span>
            <div class="text-2xl font-extrabold text-aco mt-1">22h00</div>
            <span class="text-[11px] text-slate-500 mt-1">Medição O2 e checagem de motores</span>
          </div>
        </div>
      </section>

      <!-- ======================================================== -->
      <!-- VIEW 11: MERCADO & COTAÇÕES ABCC                         -->
      <!-- ======================================================== -->
      <section id="view-analytics-mercado" class="hidden space-y-6">
        <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <div class="space-y-1">
            <div class="flex items-center space-x-2 text-xs font-semibold text-aco">
              <span class="cursor-pointer hover:underline" onclick="navegarPara('dashboard-macro')">Dashboard</span>
              <i class="fa-solid fa-chevron-right text-[10px] text-slate-400"></i>
              <span>Comercial</span>
              <i class="fa-solid fa-chevron-right text-[10px] text-slate-400"></i>
              <span class="text-slate-600">Cotações ABCC</span>
            </div>
            <h2 class="text-xl font-bold text-slate-900 flex items-center gap-2">
              <i class="fa-solid fa-arrow-trend-up text-emerald-600"></i> Radar de Cotações ABCC & Apoio à Venda
            </h2>
            <p class="text-xs text-slate-500">Tabela de preços praticados no Nordeste por gramatura e calculadora de momento ótimo de despesca.</p>
          </div>
          <button onclick="navegarPara('dashboard-macro')" class="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs transition flex items-center gap-2">
            <i class="fa-solid fa-arrow-left"></i> Voltar ao Dashboard Geral
          </button>
        </div>

        <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm text-center">
            <span class="text-xs font-bold text-slate-400 uppercase">Camarão 10g</span>
            <div class="text-2xl font-extrabold text-slate-800 mt-1">R$ 18,50 / kg</div>
          </div>
          <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm text-center">
            <span class="text-xs font-bold text-slate-400 uppercase">Camarão 12g</span>
            <div class="text-2xl font-extrabold text-emerald-600 mt-1">R$ 21,50 / kg</div>
          </div>
          <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm text-center">
            <span class="text-xs font-bold text-slate-400 uppercase">Camarão 14g</span>
            <div class="text-2xl font-extrabold text-aco mt-1">R$ 24,00 / kg</div>
          </div>
          <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm text-center">
            <span class="text-xs font-bold text-slate-400 uppercase">Camarão 16g+</span>
            <div class="text-2xl font-extrabold text-indigo-700 mt-1">R$ 27,50 / kg</div>
          </div>
        </div>
      </section>

    </main>
  </div>

  <!-- ======================================================== -->
  <!-- MODAL: PREENCHIMENTO RÁPIDO (PENDÊNCIA 2 / DIA ESQUECIDO)-->
  <!-- ======================================================== -->
  <div id="modal-preenchimento-rapido" class="hidden fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
    <div class="bg-white rounded-2xl max-w-md w-full shadow-2xl border border-slate-200 overflow-hidden">
      <div class="bg-marinho p-4 text-white flex items-center justify-between">
        <h3 class="text-sm font-bold flex items-center gap-2">
          <i class="fa-solid fa-pen-to-square text-cyan-300"></i> Lançamento Retroativo — <span id="modal-rapido-viv-id">V-04</span>
        </h3>
        <button onclick="fecharModalPreenchimentoRapido()" class="text-blue-200 hover:text-white">
          <i class="fa-solid fa-xmark text-lg"></i>
        </button>
      </div>
      <form onsubmit="salvarPreenchimentoRapido(event)" class="p-5 space-y-4">
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Data do Lançamento:</label>
          <input type="text" value="Ontem (20/10/2026)" readonly class="w-full text-xs font-semibold bg-slate-100 border border-slate-200 rounded-lg p-2.5 text-slate-600">
        </div>
        <div class="grid grid-cols-3 gap-2">
          <div>
            <label class="block text-[11px] font-bold text-slate-600 mb-1">Manhã (kg):</label>
            <input type="number" step="0.5" id="input-rapido-manha" value="15.0" class="w-full text-xs font-bold border border-slate-300 rounded-lg p-2 focus:ring-2 focus:ring-aco">
          </div>
          <div>
            <label class="block text-[11px] font-bold text-slate-600 mb-1">Tarde (kg):</label>
            <input type="number" step="0.5" id="input-rapido-tarde" value="15.0" class="w-full text-xs font-bold border border-slate-300 rounded-lg p-2 focus:ring-2 focus:ring-aco">
          </div>
          <div>
            <label class="block text-[11px] font-bold text-slate-600 mb-1">Noite (kg):</label>
            <input type="number" step="0.5" id="input-rapido-noite" value="12.0" class="w-full text-xs font-bold border border-slate-300 rounded-lg p-2 focus:ring-2 focus:ring-aco">
          </div>
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-[11px] font-bold text-slate-600 mb-1">Sobra Bandeja:</label>
            <select id="input-rapido-sobra" class="w-full text-xs border border-slate-300 rounded-lg p-2">
              <option value="0">0 - Limpo</option>
              <option value="1">1 - Pouca sobra</option>
              <option value="2">2 - Média sobra</option>
              <option value="3">3 - Sobra total</option>
            </select>
          </div>
          <div>
            <label class="block text-[11px] font-bold text-slate-600 mb-1">O2 Manhã (mg/L):</label>
            <input type="number" step="0.1" id="input-rapido-o2" value="4.2" class="w-full text-xs font-bold border border-slate-300 rounded-lg p-2">
          </div>
        </div>
        <div class="flex items-center justify-end space-x-2 pt-3 border-t border-slate-100">
          <button type="button" onclick="fecharModalPreenchimentoRapido()" class="px-4 py-2 rounded-xl text-xs font-semibold text-slate-600 hover:bg-slate-100">Cancelar</button>
          <button type="submit" class="px-4 py-2 rounded-xl text-xs font-bold bg-aco text-white hover:bg-aco-light shadow">Gravar e Resolver</button>
        </div>
      </form>
    </div>
  </div>

  <!-- ======================================================== -->
  <!-- MODAL: JUSTIFICAR O2 CRÍTICO (PENDÊNCIA 3)               -->
  <!-- ======================================================== -->
  <div id="modal-justificar-o2" class="hidden fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
    <div class="bg-white rounded-2xl max-w-md w-full shadow-2xl border border-slate-200 overflow-hidden">
      <div class="bg-marinho p-4 text-white flex items-center justify-between">
        <h3 class="text-sm font-bold flex items-center gap-2">
          <i class="fa-solid fa-file-pen text-amber-300"></i> Justificativa Operacional — O₂ Crítico no <span id="modal-just-viv-id">V-08</span>
        </h3>
        <button onclick="fecharModalJustificarO2()" class="text-blue-200 hover:text-white">
          <i class="fa-solid fa-xmark text-lg"></i>
        </button>
      </div>
      <form onsubmit="salvarJustificativaO2(event)" class="p-5 space-y-4">
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Ocorrência Registrada:</label>
          <div class="text-xs bg-red-50 text-red-900 p-2.5 rounded-lg border border-red-200 font-medium">
            Oxigênio medido às 03:30 em <strong>2.6 mg/L</strong> (Abaixo de 3.0 mg/L).
          </div>
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Ação Corretiva Executada:</label>
          <textarea id="textarea-justificativa-o2" rows="3" class="w-full text-xs border border-slate-300 rounded-lg p-2.5 focus:ring-2 focus:ring-aco font-medium">Acionado aerador reserva de 2 CV às 03:35 pelo vigia Carlos Silva. Na medição de controle às 04:30 o O2 subiu para 3.8 mg/L sem perdas.</textarea>
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-700 mb-1">Novo Nível O₂ Restabelecido (mg/L):</label>
          <input type="number" step="0.1" id="input-just-o2-restabelecido" value="3.8" class="w-full text-xs font-bold border border-slate-300 rounded-lg p-2">
        </div>
        <div class="flex items-center justify-end space-x-2 pt-3 border-t border-slate-100">
          <button type="button" onclick="fecharModalJustificarO2()" class="px-4 py-2 rounded-xl text-xs font-semibold text-slate-600 hover:bg-slate-100">Cancelar</button>
          <button type="submit" class="px-4 py-2 rounded-xl text-xs font-bold bg-emerald-600 text-white hover:bg-emerald-700 shadow">Confirmar e Normalizar Tanque</button>
        </div>
      </form>
    </div>
  </div>

  <!-- ======================================================== -->
  <!-- MODAL: RELATÓRIO EXECUTIVO PDF (PREVIEW DE IMPRESSÃO)    -->
  <!-- ======================================================== -->
  <div id="modal-relatorio-pdf" class="hidden fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/70 backdrop-blur-sm overflow-y-auto">
    <div id="print-modal-content" class="bg-white rounded-2xl max-w-3xl w-full shadow-2xl border border-slate-300 overflow-hidden my-8">
      <div class="bg-marinho p-4 text-white flex items-center justify-between no-print">
        <h3 class="text-sm font-bold flex items-center gap-2">
          <i class="fa-solid fa-file-pdf text-red-400"></i> Relatório Executivo Zootécnico — <span id="pdf-header-tanque">V-01</span>
        </h3>
        <div class="flex items-center space-x-2">
          <button onclick="window.print()" class="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold transition flex items-center gap-1.5">
            <i class="fa-solid fa-print"></i> Imprimir / Salvar PDF
          </button>
          <button onclick="fecharModalPDF()" class="text-blue-200 hover:text-white p-1">
            <i class="fa-solid fa-xmark text-lg"></i>
          </button>
        </div>
      </div>

      <!-- Folha Timbrada do Relatório -->
      <div class="p-8 space-y-6 text-slate-800 bg-white">
        <div class="border-b-2 border-marinho pb-4 flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <span class="text-3xl">🦐</span>
            <div>
              <h1 class="text-lg font-black text-marinho uppercase">Fazenda Camarão do Vale</h1>
              <p class="text-xs text-slate-500 font-semibold">Ceará-Mirim/RN • Litopenaeus vannamei • Safra 2026/2</p>
            </div>
          </div>
          <div class="text-right text-xs">
            <span class="font-bold block text-slate-700">Relatório de Fechamento Amostral</span>
            <span id="pdf-data-emissao" class="text-slate-500">21/10/2026</span>
          </div>
        </div>

        <div class="grid grid-cols-3 gap-4 text-xs bg-slate-50 p-4 rounded-xl border border-slate-200">
          <div><strong class="text-slate-500 block">Tanque:</strong> <span id="pdf-tanque-id" class="font-bold text-slate-900 text-sm">Viveiro 01</span></div>
          <div><strong class="text-slate-500 block">DDC Atual:</strong> <span id="pdf-periodo" class="font-bold text-slate-900 text-sm">58 Dias</span></div>
          <div><strong class="text-slate-500 block">Peso Médio:</strong> <span id="pdf-peso" class="font-bold text-aco text-sm">12.4 g</span></div>
          <div><strong class="text-slate-500 block">Biomassa Estimada:</strong> <span id="pdf-biomassa" class="font-bold text-slate-900 text-sm">3.420 kg</span></div>
          <div><strong class="text-slate-500 block">FCA Parcial:</strong> <span id="pdf-fca" class="font-bold text-emerald-600 text-sm">1.19</span></div>
          <div><strong class="text-slate-500 block">Ração Acumulada:</strong> <span id="pdf-racao-acumulada" class="font-bold text-amber-700 text-sm">4.070 kg</span></div>
        </div>

        <div class="border-t border-slate-200 pt-4 text-center text-[11px] text-slate-400">
          ERP Carcinicultura Ceará-Mirim/RN • Relatório gerado eletronicamente com auditoria de integridade.
        </div>
      </div>
    </div>
  </div>

  <!-- ======================================================== -->
  <!-- 3. JAVASCRIPT: MOTOR DE DADOS & NAVEGAÇÃO ANALÍTICA      -->
  <!-- ======================================================== -->
  <script>
    // DATASET COMPLETO DOS 15 VIVEIROS DA FAZENDA
    const VIVEIROS_DATA = [
      {
        id: 'V-01', nome: 'Viveiro 01', tipo: 'engorda', area_ha: 1.2, area_m2: 12000,
        status: 'otimo', statusLabel: '🟢 Ótimo', statusDesc: 'Parâmetros estáveis e bandejas limpas',
        ddc: 58, dataPovoamento: '24/08/2026', pesoMedio: 12.4, ganhoSemanal: 1.35, biomassaKg: 3420, fca: 1.19,
        racaoHojeKg: 75, racaoAcumuladaKg: 4070, o2Manha: 4.6, o2Noite: 4.8, phManha: 7.8, phTarde: 8.2,
        salinidade: 14.5, secchi: 35, amonia: 0.02, sobraNivel: 0, sobraTexto: '0 (Prato Limpo)', densidade: 23
      },
      {
        id: 'V-02', nome: 'Viveiro 02', tipo: 'engorda', area_ha: 1.0, area_m2: 10000,
        status: 'atencao', statusLabel: '🟡 Atenção', statusDesc: 'Duplicidade de lançamento detectada na auditoria',
        ddc: 52, dataPovoamento: '30/08/2026', pesoMedio: 11.2, ganhoSemanal: 1.20, biomassaKg: 2850, fca: 1.24,
        racaoHojeKg: 60, racaoAcumuladaKg: 3534, o2Manha: 4.2, o2Noite: 4.5, phManha: 7.7, phTarde: 8.1,
        salinidade: 14.0, secchi: 32, amonia: 0.03, sobraNivel: 1, sobraTexto: '1 (Pouca Sobra)', densidade: 25
      },
      {
        id: 'V-03', nome: 'Viveiro 03', tipo: 'engorda', area_ha: 1.5, area_m2: 15000,
        status: 'otimo', statusLabel: '🟢 Ótimo', statusDesc: 'Crescimento vigoroso acima da meta',
        ddc: 65, dataPovoamento: '17/08/2026', pesoMedio: 14.1, ganhoSemanal: 1.45, biomassaKg: 4650, fca: 1.21,
        racaoHojeKg: 95, racaoAcumuladaKg: 5626, o2Manha: 4.8, o2Noite: 5.0, phManha: 7.9, phTarde: 8.3,
        salinidade: 15.0, secchi: 38, amonia: 0.02, sobraNivel: 0, sobraTexto: '0 (Prato Limpo)', densidade: 22
      },
      {
        id: 'V-04', nome: 'Viveiro 04', tipo: 'engorda', area_ha: 0.8, area_m2: 8000,
        status: 'atencao', statusLabel: '🟡 Atenção', statusDesc: 'Lacuna de lançamento nas últimas 24h',
        ddc: 30, dataPovoamento: '21/09/2026', pesoMedio: 6.8, ganhoSemanal: 1.10, biomassaKg: 1360, fca: 1.18,
        racaoHojeKg: 42, racaoAcumuladaKg: 1604, o2Manha: 4.1, o2Noite: 4.4, phManha: 7.6, phTarde: 8.0,
        salinidade: 13.5, secchi: 40, amonia: 0.01, sobraNivel: 0, sobraTexto: '0 (Prato Limpo)', densidade: 25
      },
      {
        id: 'V-05', nome: 'Viveiro 05', tipo: 'engorda', area_ha: 1.2, area_m2: 12000,
        status: 'otimo', statusLabel: '🟢 Ótimo', statusDesc: 'Melhor conversão da safra (FCA 1.15)',
        ddc: 45, dataPovoamento: '06/09/2026', pesoMedio: 9.9, ganhoSemanal: 1.30, biomassaKg: 2970, fca: 1.15,
        racaoHojeKg: 68, racaoAcumuladaKg: 3415, o2Manha: 4.5, o2Noite: 4.7, phManha: 7.8, phTarde: 8.2,
        salinidade: 14.0, secchi: 36, amonia: 0.02, sobraNivel: 0, sobraTexto: '0 (Prato Limpo)', densidade: 25
      },
      {
        id: 'V-06', nome: 'Viveiro 06', tipo: 'engorda', area_ha: 1.1, area_m2: 11000,
        status: 'otimo', statusLabel: '🟢 Ótimo', statusDesc: 'Tanque em padrão zootécnico estável',
        ddc: 40, dataPovoamento: '11/09/2026', pesoMedio: 8.6, ganhoSemanal: 1.22, biomassaKg: 2450, fca: 1.20,
        racaoHojeKg: 58, racaoAcumuladaKg: 2940, o2Manha: 4.4, o2Noite: 4.6, phManha: 7.7, phTarde: 8.1,
        salinidade: 14.2, secchi: 35, amonia: 0.02, sobraNivel: 0, sobraTexto: '0 (Prato Limpo)', densidade: 26
      },
      {
        id: 'V-07', nome: 'Viveiro 07', tipo: 'engorda', area_ha: 1.3, area_m2: 13000,
        status: 'otimo', statusLabel: '🟢 Ótimo', statusDesc: 'Excelente transparência Secchi (36 cm)',
        ddc: 50, dataPovoamento: '01/09/2026', pesoMedio: 10.8, ganhoSemanal: 1.28, biomassaKg: 3380, fca: 1.22,
        racaoHojeKg: 72, racaoAcumuladaKg: 4123, o2Manha: 4.3, o2Noite: 4.6, phManha: 7.8, phTarde: 8.2,
        salinidade: 14.0, secchi: 36, amonia: 0.02, sobraNivel: 0, sobraTexto: '0 (Prato Limpo)', densidade: 24
      },
      {
        id: 'V-08', nome: 'Viveiro 08', tipo: 'engorda', area_ha: 1.4, area_m2: 14000,
        status: 'critico', statusLabel: '🔴 Crítico', statusDesc: 'Oxigênio caiu para 2.6 mg/L às 03:30',
        ddc: 55, dataPovoamento: '27/08/2026', pesoMedio: 11.8, ganhoSemanal: 1.15, biomassaKg: 3620, fca: 1.48,
        racaoHojeKg: 80, racaoAcumuladaKg: 5357, o2Manha: 2.6, o2Noite: 3.9, phManha: 7.5, phTarde: 8.4,
        salinidade: 13.8, secchi: 28, amonia: 0.06, sobraNivel: 2, sobraTexto: '2 (Média Sobra)', densidade: 22
      },
      {
        id: 'V-09', nome: 'Viveiro 09', tipo: 'engorda', area_ha: 1.2, area_m2: 12000,
        status: 'otimo', statusLabel: '🟢 Ótimo', statusDesc: 'Condições físico-químicas regulares',
        ddc: 35, dataPovoamento: '16/09/2026', pesoMedio: 7.5, ganhoSemanal: 1.18, biomassaKg: 2160, fca: 1.21,
        racaoHojeKg: 52, racaoAcumuladaKg: 2613, o2Manha: 4.4, o2Noite: 4.7, phManha: 7.8, phTarde: 8.2,
        salinidade: 14.5, secchi: 37, amonia: 0.02, sobraNivel: 0, sobraTexto: '0 (Prato Limpo)', densidade: 24
      },
      {
        id: 'V-10', nome: 'Viveiro 10', tipo: 'engorda', area_ha: 1.0, area_m2: 10000,
        status: 'otimo', statusLabel: '🟢 Ótimo', statusDesc: 'Povoamento homogêneo e sem desvios',
        ddc: 28, dataPovoamento: '23/09/2026', pesoMedio: 6.2, ganhoSemanal: 1.12, biomassaKg: 1550, fca: 1.17,
        racaoHojeKg: 38, racaoAcumuladaKg: 1813, o2Manha: 4.6, o2Noite: 4.8, phManha: 7.7, phTarde: 8.1,
        salinidade: 14.0, secchi: 39, amonia: 0.01, sobraNivel: 0, sobraTexto: '0 (Prato Limpo)', densidade: 25
      },
      {
        id: 'V-11', nome: 'Viveiro 11', tipo: 'engorda', area_ha: 1.6, area_m2: 16000,
        status: 'otimo', statusLabel: '🟢 Ótimo', statusDesc: 'Maior tanque da fazenda operando bem',
        ddc: 38, dataPovoamento: '13/09/2026', pesoMedio: 8.2, ganhoSemanal: 1.25, biomassaKg: 2990, fca: 1.22,
        racaoHojeKg: 65, racaoAcumuladaKg: 3647, o2Manha: 4.3, o2Noite: 4.5, phManha: 7.6, phTarde: 8.0,
        salinidade: 14.0, secchi: 34, amonia: 0.02, sobraNivel: 0, sobraTexto: '0 (Prato Limpo)', densidade: 23
      },
      {
        id: 'BER-01', nome: 'Berçário 01', tipo: 'bercario', area_ha: 0.3, area_m2: 3000,
        status: 'otimo', statusLabel: '🟢 Berçário', statusDesc: 'Pós-larvas PL-12 em aclimatação inicial',
        ddc: 12, dataPovoamento: '09/10/2026', pesoMedio: 1.4, ganhoSemanal: 0.60, biomassaKg: 420, fca: 0.98,
        racaoHojeKg: 15, racaoAcumuladaKg: 411, o2Manha: 5.5, o2Noite: 5.8, phManha: 7.9, phTarde: 8.2,
        salinidade: 15.0, secchi: 45, amonia: 0.01, sobraNivel: 0, sobraTexto: '0 (Micropeletizada)', densidade: 100
      },
      {
        id: 'BER-02', nome: 'Berçário 02', tipo: 'bercario', area_ha: 0.3, area_m2: 3000,
        status: 'vazio', statusLabel: '⚪ Vazio', statusDesc: 'Aguardando lote de PLs da Aquatec na próxima semana',
        ddc: 0, dataPovoamento: '-', pesoMedio: 0, ganhoSemanal: 0, biomassaKg: 0, fca: 0,
        racaoHojeKg: 0, racaoAcumuladaKg: 0, o2Manha: 0, o2Noite: 0, phManha: 0, phTarde: 0,
        salinidade: 0, secchi: 0, amonia: 0, sobraNivel: 0, sobraTexto: 'Vazio', densidade: 0
      },
      {
        id: 'V-14', nome: 'Viveiro 14', tipo: 'preparo', area_ha: 1.0, area_m2: 10000,
        status: 'vazio', statusLabel: '⚪ Vazio Sanitário', statusDesc: 'Secagem de fundo e calagem com calcário dolomítico',
        ddc: 0, dataPovoamento: '-', pesoMedio: 0, ganhoSemanal: 0, biomassaKg: 0, fca: 0,
        racaoHojeKg: 0, racaoAcumuladaKg: 0, o2Manha: 0, o2Noite: 0, phManha: 0, phTarde: 0,
        salinidade: 0, secchi: 0, amonia: 0, sobraNivel: 0, sobraTexto: 'Vazio', densidade: 0
      },
      {
        id: 'BAC-01', nome: 'Bacia Decantação', tipo: 'bacia', area_ha: 1.2, area_m2: 12000,
        status: 'vazio', statusLabel: '⚪ Bacia Ambiental', statusDesc: 'Bacia de sedimentação de efluentes (IDEMA-RN)',
        ddc: 0, dataPovoamento: '-', pesoMedio: 0, ganhoSemanal: 0, biomassaKg: 0, fca: 0,
        racaoHojeKg: 0, racaoAcumuladaKg: 0, o2Manha: 0, o2Noite: 0, phManha: 0, phTarde: 0,
        salinidade: 0, secchi: 0, amonia: 0, sobraNivel: 0, sobraTexto: 'Bacia', densidade: 0
      }
    ];

    // ESTADO GLOBAL DO PROTÓTIPO
    let currentProfile = 'leo'; // 'leo' ou 'pai'
    let currentFilter = 'todos';
    let selectedViveiro = VIVEIROS_DATA[0];
    let resolvedAudits = new Set();
    let currentView = 'dashboard-macro';

    // Instâncias do Chart.js
    let chartBiomassaCompInstance = null;
    let chartDetailCrescimentoInstance = null;
    let chartDetailOxigenioInstance = null;

    // INICIALIZAÇÃO
    window.addEventListener('DOMContentLoaded', () => {
      atualizarRelogio();
      setInterval(atualizarRelogio, 1000);
      renderizarMapaViveiros();
      atualizarContadorAuditoria();
      preencherTabelasAnaliticas();
    });

    function atualizarRelogio() {
      const now = new Date();
      const el = document.getElementById('live-clock');
      if (el) el.textContent = now.toLocaleTimeString('pt-BR');
    }

    // ==========================================
    // SISTEMA DE NAVEGAÇÃO ENTRE MÓDULOS (SPA)
    // ==========================================
    function navegarPara(viewId, param = null) {
      currentView = viewId;

      // Lista de todas as visões
      const views = [
        'dashboard-macro',
        'viveiros-mapa',
        'analytics-biomassa',
        'analytics-fca',
        'analytics-arracoamento',
        'analytics-estoque',
        'analytics-agua',
        'analytics-viveiro-detalhe',
        'auditoria-central',
        'analytics-financeiro',
        'analytics-equipe',
        'analytics-mercado',
        'analytics-povoamento',
        'analytics-despesca',
        'analytics-ged'
      ];

      // Ocultar todas as seções e mostrar apenas a alvo
      views.forEach(v => {
        const el = document.getElementById(`view-${v}`);
        if (el) el.classList.add('hidden');
      });

      // Tratar se for viveiros-mapa: abre dashboard-macro e rola até o mapa
      if (viewId === 'viveiros-mapa') {
        const elMacro = document.getElementById('view-dashboard-macro');
        if (elMacro) elMacro.classList.remove('hidden');
        document.getElementById('secao-mapa-viveiros').scrollIntoView({ behavior: 'smooth' });
        atualizarHeaderNavegacao('Mapa dos Viveiros', 'Início > Topografia > Viveiros');
      } else {
        const target = document.getElementById(`view-${viewId}`);
        if (target) {
          target.classList.remove('hidden');
          window.scrollTo({ top: 0, behavior: 'smooth' });
        }
      }

      // Atualizar classe ativa na Sidebar
      document.querySelectorAll('.nav-item').forEach(btn => {
        btn.classList.remove('bg-aco', 'text-white', 'shadow-sm');
        btn.classList.add('text-blue-200');
      });
      const activeNavBtn = document.getElementById(`nav-${viewId}`);
      if (activeNavBtn) {
        activeNavBtn.classList.remove('text-blue-200');
        activeNavBtn.classList.add('bg-aco', 'text-white', 'shadow-sm');
      }

      // Triggers específicos por visão
      if (viewId === 'dashboard-macro') {
        atualizarHeaderNavegacao('Dashboard Macro da Fazenda', 'Início > Visão Geral > Macro');
      } else if (viewId === 'analytics-biomassa') {
        atualizarHeaderNavegacao('Detalhamento Analítico de Biomassa', 'Início > Zootecnia > Biomassa');
        renderizarGraficoBiomassaComparativo();
      } else if (viewId === 'analytics-fca') {
        atualizarHeaderNavegacao('Eficiência Alimentar & FCA', 'Início > Zootecnia > FCA');
      } else if (viewId === 'analytics-arracoamento') {
        atualizarHeaderNavegacao('Arraçoamento & Sobras de Bandejas', 'Início > Zootecnia > Ração');
      } else if (viewId === 'analytics-estoque') {
        atualizarHeaderNavegacao('Estoque de Ração & Insumos', 'Início > Suprimentos > Galpão');
      } else if (viewId === 'analytics-agua') {
        atualizarHeaderNavegacao('Qualidade da Água & Parâmetros', 'Início > Zootecnia > Água');
      } else if (viewId === 'auditoria-central') {
        atualizarHeaderNavegacao('Central de Auditoria de Dados', 'Início > Integridade > Auditoria');
      } else if (viewId === 'analytics-viveiro-detalhe') {
        if (param) carregarDetalhesViveiro(param);
      }
    }

    function atualizarHeaderNavegacao(titulo, breadcrumb) {
      const elTitle = document.getElementById('page-current-heading');
      const elBreadcrumb = document.getElementById('page-breadcrumb');
      if (elTitle) elTitle.textContent = titulo;
      if (elBreadcrumb) elBreadcrumb.textContent = breadcrumb;
    }

    // ABRIR PÁGINA ANALÍTICA INDIVIDUAL DO VIVEIRO (DRILL-DOWN DIRETO)
    function abrirPaginaAnaliticaViveiro(vivId) {
      const v = VIVEIROS_DATA.find(x => x.id === vivId);
      if (!v) return;
      selectedViveiro = v;
      navegarPara('analytics-viveiro-detalhe', vivId);
    }

    function carregarDetalhesViveiro(vivId) {
      const v = VIVEIROS_DATA.find(x => x.id === vivId) || VIVEIROS_DATA[0];
      selectedViveiro = v;

      atualizarHeaderNavegacao(`Análise Detalhada: ${v.nome}`, `Início > Viveiros > ${v.nome}`);

      document.getElementById('detail-viv-breadcrumb').textContent = v.nome;
      document.getElementById('detail-viv-title').textContent = `${v.nome} (${v.id})`;
      document.getElementById('detail-viv-status-badge').textContent = v.statusLabel;
      document.getElementById('detail-viv-subtitle').textContent = `Povoamento: ${v.dataPovoamento} • Área: ${v.area_ha} ha (${v.area_m2.toLocaleString('pt-BR')} m²) • Densidade: ${v.densidade} cam/m²`;

      document.getElementById('detail-card-ddc').textContent = `${v.ddc} dias`;
      document.getElementById('detail-card-peso').textContent = `${v.pesoMedio} g`;
      document.getElementById('detail-card-biomassa').textContent = `${v.biomassaKg.toLocaleString('pt-BR')} kg`;
      document.getElementById('detail-card-fca').textContent = v.fca > 0 ? v.fca : '-';
      document.getElementById('detail-card-racao-acum').textContent = v.racaoAcumuladaKg > 0 ? `${v.racaoAcumuladaKg.toLocaleString('pt-BR')} kg` : '-';
      document.getElementById('detail-card-sobrevivencia').textContent = v.status === 'vazio' ? '-' : '84.5%';

      // Diário de bordo simulado
      renderizarDiarioBordoViveiro(v);
      renderizarGraficosDoViveiro(v);
    }

    function renderizarDiarioBordoViveiro(v) {
      const tbody = document.getElementById('tbody-detail-diario');
      if (!tbody) return;
      tbody.innerHTML = '';

      if (v.status === 'vazio') {
        tbody.innerHTML = '<tr><td colspan="11" class="p-6 text-center text-slate-400">Tanque atualmente em vazio sanitário ou sem cultivo ativo.</td></tr>';
        return;
      }

      // Gerar 10 linhas retroativas
      for (let i = 0; i < 10; i++) {
        const dia = v.ddc - i;
        if (dia < 1) break;
        const d = new Date();
        d.setDate(d.getDate() - i);
        const dataStr = d.toLocaleDateString('pt-BR');

        const manha = Math.round((v.racaoHojeKg * 0.35) * (1 + (Math.sin(i) * 0.05)));
        const tarde = Math.round((v.racaoHojeKg * 0.34) * (1 - (Math.cos(i) * 0.04)));
        const noite = Math.round((v.racaoHojeKg * 0.31) * (1 + (Math.cos(i) * 0.03)));
        const total = manha + tarde + noite;
        const sobra = (i === 1 && v.id === 'V-08') ? '2 (Média)' : '0 (Limpo)';
        const o2m = (i === 1 && v.id === 'V-08') ? '2.6' : (4.4 + (Math.sin(i)*0.3)).toFixed(1);
        const o2n = (4.7 + (Math.cos(i)*0.2)).toFixed(1);
        const peso = (v.pesoMedio - (i * 0.18)).toFixed(1);

        const tr = document.createElement('tr');
        tr.className = 'hover:bg-slate-50 transition';
        tr.innerHTML = `
          <td class="p-3 font-bold text-slate-900">${dia}</td>
          <td class="p-3">${dataStr}</td>
          <td class="p-3 font-semibold">${manha} kg</td>
          <td class="p-3 font-semibold">${tarde} kg</td>
          <td class="p-3 font-semibold">${noite} kg</td>
          <td class="p-3 font-extrabold text-aco">${total} kg</td>
          <td class="p-3"><span class="px-2 py-0.5 rounded text-[10px] font-bold ${sobra.includes('2') ? 'bg-amber-100 text-amber-800' : 'bg-slate-100 text-slate-700'}">${sobra}</span></td>
          <td class="p-3 font-bold ${parseFloat(o2m) < 3.0 ? 'text-alerta' : 'text-slate-800'}">${o2m} mg/L</td>
          <td class="p-3 text-slate-700">${o2n} mg/L</td>
          <td class="p-3">${v.salinidade} ppt</td>
          <td class="p-3 font-bold text-emerald-700">${peso} g</td>
        `;
        tbody.appendChild(tr);
      }
    }

    // ==========================================
    // SIDEBAR EXPANDIR / RECOLHER
    // ==========================================
    function toggleSidebar() {
      const sidebar = document.getElementById('app-sidebar');
      const icon = document.getElementById('sidebar-toggle-icon');
      sidebar.classList.toggle('sidebar-collapsed');
      if (sidebar.classList.contains('sidebar-collapsed')) {
        icon.className = 'fa-solid fa-angles-right text-xs';
      } else {
        icon.className = 'fa-solid fa-angles-left text-xs';
      }
    }

    function toggleSidebarMobile() {
      const sidebar = document.getElementById('app-sidebar');
      sidebar.classList.toggle('hidden');
    }

    // ==========================================
    // PREENCHIMENTO DAS TABELAS ANALÍTICAS
    // ==========================================
    function preencherTabelasAnaliticas() {
      // 1. Tabela de Biomassa
      const tbodyBio = document.getElementById('tbody-analytics-biomassa');
      if (tbodyBio) {
        tbodyBio.innerHTML = '';
        VIVEIROS_DATA.forEach(v => {
          const tr = document.createElement('tr');
          tr.className = 'hover:bg-slate-50 transition cursor-pointer';
          tr.onclick = () => abrirPaginaAnaliticaViveiro(v.id);
          tr.innerHTML = `
            <td class="p-3 font-bold text-slate-900">${v.nome} (${v.id})</td>
            <td class="p-3">${v.area_ha} ha</td>
            <td class="p-3 font-semibold">${v.ddc > 0 ? v.ddc + ' d' : '-'}</td>
            <td class="p-3"><span class="px-2 py-0.5 rounded text-[10px] font-bold ${v.status === 'otimo' ? 'bg-emerald-100 text-emerald-800' : v.status === 'atencao' ? 'bg-amber-100 text-amber-800' : v.status === 'critico' ? 'bg-red-100 text-red-800' : 'bg-slate-100 text-slate-600'}">${v.statusLabel}</span></td>
            <td class="p-3 font-bold text-aco">${v.pesoMedio > 0 ? v.pesoMedio + ' g' : '-'}</td>
            <td class="p-3 text-emerald-600 font-semibold">${v.ganhoSemanal > 0 ? '+' + v.ganhoSemanal + ' g/sem' : '-'}</td>
            <td class="p-3 font-extrabold text-slate-900">${v.biomassaKg > 0 ? v.biomassaKg.toLocaleString('pt-BR') + ' kg' : '-'}</td>
            <td class="p-3">${v.densidade > 0 ? v.densidade + ' cam/m²' : '-'}</td>
            <td class="p-3 text-center">
              <button onclick="event.stopPropagation(); abrirPaginaAnaliticaViveiro('${v.id}')" class="px-2.5 py-1 rounded bg-aco text-white font-bold text-[10px] hover:bg-aco-light">Ver Análise</button>
            </td>
          `;
          tbodyBio.appendChild(tr);
        });
      }

      // 2. Tabela de FCA
      const tbodyFCA = document.getElementById('tbody-analytics-fca');
      if (tbodyFCA) {
        tbodyFCA.innerHTML = '';
        const ordenados = [...VIVEIROS_DATA].filter(v => v.fca > 0).sort((a,b) => a.fca - b.fca);
        ordenados.forEach(v => {
          const desvio = (v.fca - 1.25).toFixed(2);
          const tr = document.createElement('tr');
          tr.className = 'hover:bg-slate-50 transition cursor-pointer';
          tr.onclick = () => abrirPaginaAnaliticaViveiro(v.id);
          tr.innerHTML = `
            <td class="p-3 font-bold text-slate-900">${v.nome}</td>
            <td class="p-3 font-semibold">${v.ddc} dias</td>
            <td class="p-3 font-bold">${v.biomassaKg.toLocaleString('pt-BR')} kg</td>
            <td class="p-3 text-amber-800 font-bold">${v.racaoAcumuladaKg.toLocaleString('pt-BR')} kg</td>
            <td class="p-3 font-extrabold text-sm ${v.fca <= 1.25 ? 'text-emerald-600' : v.fca <= 1.35 ? 'text-amber-600' : 'text-alerta'}">${v.fca}</td>
            <td class="p-3 font-bold ${desvio <= 0 ? 'text-emerald-600' : 'text-alerta'}">${desvio <= 0 ? desvio : '+' + desvio}</td>
            <td class="p-3 font-mono">R$ ${(v.racaoAcumuladaKg * 5.60).toLocaleString('pt-BR', {minimumFractionDigits: 2})}</td>
            <td class="p-3"><span class="px-2 py-0.5 rounded text-[10px] font-bold ${v.fca <= 1.25 ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'}">${v.fca <= 1.25 ? 'Ótima Conversão' : 'Desvio Detectado'}</span></td>
            <td class="p-3 text-center">
              <button onclick="event.stopPropagation(); abrirPaginaAnaliticaViveiro('${v.id}')" class="px-2 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-[10px]">Histórico</button>
            </td>
          `;
          tbodyFCA.appendChild(tr);
        });
      }

      // 3. Tabela de Arraçoamento
      const tbodyArr = document.getElementById('tbody-analytics-arracoamento');
      if (tbodyArr) {
        tbodyArr.innerHTML = '';
        VIVEIROS_DATA.filter(v => v.racaoHojeKg > 0).forEach(v => {
          const m = Math.round(v.racaoHojeKg * 0.35);
          const t = Math.round(v.racaoHojeKg * 0.34);
          const n = Math.round(v.racaoHojeKg * 0.31);
          const tr = document.createElement('tr');
          tr.className = 'hover:bg-slate-50 transition cursor-pointer';
          tr.onclick = () => abrirPaginaAnaliticaViveiro(v.id);
          tr.innerHTML = `
            <td class="p-3 font-bold text-slate-900">${v.nome}</td>
            <td class="p-3">Guabi 35% 1.6mm</td>
            <td class="p-3 font-semibold">${m} kg</td>
            <td class="p-3 font-semibold">${t} kg</td>
            <td class="p-3 font-semibold">${n} kg</td>
            <td class="p-3 font-extrabold text-aco">${v.racaoHojeKg} kg</td>
            <td class="p-3"><span class="px-2 py-0.5 rounded text-[10px] font-bold ${v.sobraNivel > 1 ? 'bg-amber-100 text-amber-800' : 'bg-slate-100 text-slate-700'}">${v.sobraTexto}</span></td>
            <td class="p-3 font-semibold text-slate-600">${v.sobraNivel === 0 ? 'Manter / +5% amanhã' : v.sobraNivel === 1 ? 'Manter dosagem' : 'Reduzir 25%'}</td>
            <td class="p-3 text-center">
              <button onclick="event.stopPropagation(); abrirModalPreenchimentoRapido('${v.id}')" class="px-2 py-1 rounded bg-aco text-white font-bold text-[10px]">Lançar</button>
            </td>
          `;
          tbodyArr.appendChild(tr);
        });
      }

      // 4. Tabela de Água
      const tbodyAgua = document.getElementById('tbody-analytics-agua');
      if (tbodyAgua) {
        tbodyAgua.innerHTML = '';
        VIVEIROS_DATA.filter(v => v.o2Manha > 0).forEach(v => {
          const delta = (v.phTarde - v.phManha).toFixed(1);
          const tr = document.createElement('tr');
          tr.className = 'hover:bg-slate-50 transition cursor-pointer';
          tr.onclick = () => abrirPaginaAnaliticaViveiro(v.id);
          tr.innerHTML = `
            <td class="p-3 font-bold text-slate-900">${v.nome}</td>
            <td class="p-3 font-bold ${v.o2Manha < 3.0 ? 'text-alerta' : 'text-slate-800'}">${v.o2Manha} mg/L</td>
            <td class="p-3 font-semibold text-slate-700">${v.o2Noite} mg/L</td>
            <td class="p-3">${v.salinidade} ppt</td>
            <td class="p-3">${v.phManha}</td>
            <td class="p-3">${v.phTarde}</td>
            <td class="p-3 font-semibold ${delta > 0.8 ? 'text-amber-600' : 'text-slate-700'}">Δ ${delta}</td>
            <td class="p-3">${v.secchi} cm</td>
            <td class="p-3">${v.amonia} mg/L</td>
            <td class="p-3"><span class="px-2 py-0.5 rounded text-[10px] font-bold ${v.o2Manha < 3.0 ? 'bg-red-100 text-red-800' : 'bg-emerald-100 text-emerald-800'}">${v.o2Manha < 3.0 ? 'Crítico (O2)' : 'Normal'}</span></td>
          `;
          tbodyAgua.appendChild(tr);
        });
      }
    }

    // ==========================================
    // RENDERIZAR MAPA 2D DOS 15 VIVEIROS
    // ==========================================
    function renderizarMapaViveiros() {
      const grid = document.getElementById('grid-mapa-viveiros');
      if (!grid) return;
      grid.innerHTML = '';

      const filtrados = VIVEIROS_DATA.filter(v => {
        if (currentFilter === 'todos') return true;
        if (currentFilter === 'vazio') return v.status === 'vazio' || v.tipo === 'preparo' || v.tipo === 'bacia';
        return v.status === currentFilter;
      });

      filtrados.forEach(v => {
        const card = document.createElement('div');
        let borderClass = 'border-slate-200';
        let bgHeader = 'bg-slate-100 text-slate-700';
        let pulseClass = '';

        if (v.status === 'otimo') {
          borderClass = 'border-emerald-300 hover:border-emerald-500 hover:shadow-emerald-100';
          bgHeader = 'bg-emerald-50 text-emerald-900 border-b border-emerald-200';
        } else if (v.status === 'atencao') {
          borderClass = 'border-amber-300 hover:border-amber-500 hover:shadow-amber-100';
          bgHeader = 'bg-amber-50 text-amber-900 border-b border-amber-200';
        } else if (v.status === 'critico') {
          borderClass = 'border-alerta hover:border-red-600 ring-2 ring-red-400 shadow-red-100';
          bgHeader = 'bg-red-50 text-red-900 border-b border-red-200';
          pulseClass = 'animate-pulse';
        }

        card.className = `clickable-kpi bg-white rounded-2xl border ${borderClass} shadow-sm overflow-hidden flex flex-col justify-between transition group`;
        card.onclick = () => abrirPaginaAnaliticaViveiro(v.id);

        card.innerHTML = `
          <div>
            <div class="${bgHeader} px-3.5 py-2.5 flex items-center justify-between">
              <div class="flex items-center space-x-1.5">
                <span class="font-extrabold text-xs tracking-tight">${v.id}</span>
                <span class="text-[11px] font-semibold text-slate-500">• ${v.nome}</span>
              </div>
              <span class="text-[11px] font-bold ${pulseClass}">${v.statusLabel}</span>
            </div>

            <div class="p-3.5 space-y-2.5 text-xs">
              <div class="flex items-center justify-between text-slate-500">
                <span>Área: <strong>${v.area_ha} ha</strong></span>
                <span>DDC: <strong class="text-slate-800">${v.ddc > 0 ? v.ddc + ' dias' : '-'}</strong></span>
              </div>

              ${v.biomassaKg > 0 ? `
                <div class="grid grid-cols-2 gap-2 bg-slate-50 p-2 rounded-xl text-center">
                  <div>
                    <span class="text-[10px] text-slate-400 font-bold uppercase block">Peso Médio</span>
                    <strong class="text-aco text-xs">${v.pesoMedio} g</strong>
                  </div>
                  <div>
                    <span class="text-[10px] text-slate-400 font-bold uppercase block">Biomassa</span>
                    <strong class="text-slate-800 text-xs">${v.biomassaKg.toLocaleString('pt-BR')} kg</strong>
                  </div>
                </div>
                <div class="flex items-center justify-between text-[11px] pt-1 border-t border-slate-100">
                  <span class="text-slate-500">FCA: <strong class="text-emerald-700">${v.fca}</strong></span>
                  <span class="text-slate-500">O₂ Manhã: <strong class="${v.o2Manha < 3.0 ? 'text-alerta font-extrabold' : 'text-slate-700'}">${v.o2Manha}</strong></span>
                </div>
              ` : `
                <div class="p-4 text-center text-slate-400 text-xs italic">
                  ${v.statusDesc}
                </div>
              `}
            </div>
          </div>

          <div class="px-3 py-2 bg-slate-50/70 border-t border-slate-100 text-center">
            <span class="text-[11px] font-bold text-aco group-hover:underline flex items-center justify-center gap-1">
              Ver Análise Completa <i class="fa-solid fa-arrow-right text-[9px]"></i>
            </span>
          </div>
        `;
        grid.appendChild(card);
      });
    }

    function filtrarViveiros(status) {
      currentFilter = status;
      ['todos', 'otimo', 'atencao', 'critico', 'vazio'].forEach(s => {
        const btn = document.getElementById(`filter-${s}`);
        if (btn) {
          if (s === status) {
            btn.className = 'px-2.5 py-1 rounded-lg font-bold bg-white text-slate-800 shadow-sm';
          } else {
            btn.className = 'px-2.5 py-1 rounded-lg font-medium text-slate-600 hover:text-slate-900';
          }
        }
      });
      renderizarMapaViveiros();
    }

    // ==========================================
    // RESOLUÇÃO DE AUDITORIA EM 1 CLIQUE
    // ==========================================
    function resolverPendencia(id, acao, logMsg) {
      if (resolvedAudits.has(id)) return;
      resolvedAudits.add(id);

      const card = document.getElementById(`card-pendencia-${id}`);
      if (card) {
        card.style.opacity = '0.5';
        card.style.pointerEvents = 'none';
        card.innerHTML = `
          <div class="p-3 bg-emerald-50 text-emerald-900 rounded-xl flex items-center justify-between">
            <div class="flex items-center space-x-2 text-xs font-bold">
              <i class="fa-solid fa-circle-check text-emerald-600 text-base"></i>
              <span>Resolvido com sucesso: ${logMsg}</span>
            </div>
            <span class="text-[10px] text-emerald-700 uppercase font-bold">Auditado</span>
          </div>
        `;
      }

      // Tratar efeitos colaterais nos viveiros
      if (id === 1) {
        const v = VIVEIROS_DATA.find(x => x.id === 'V-02');
        if (v) { v.status = 'otimo'; v.statusLabel = '🟢 Ótimo'; }
      } else if (id === 2) {
        const v = VIVEIROS_DATA.find(x => x.id === 'V-04');
        if (v) { v.status = 'otimo'; v.statusLabel = '🟢 Ótimo'; }
      } else if (id === 3) {
        const v = VIVEIROS_DATA.find(x => x.id === 'V-08');
        if (v) { v.status = 'otimo'; v.statusLabel = '🟢 Ótimo'; v.o2Manha = 3.8; }
      }

      atualizarContadorAuditoria();
      renderizarMapaViveiros();
      preencherTabelasAnaliticas();
    }

    function atualizarContadorAuditoria() {
      const total = 3;
      const pendentes = total - resolvedAudits.size;

      const badgeTop = document.getElementById('badge-top-audit-count');
      const badgePill = document.getElementById('badge-audit-pill');
      const badgeSidebar = document.getElementById('sidebar-audit-badge');
      const fullAuditCount = document.getElementById('full-audit-pending-count');

      if (badgeTop) badgeTop.textContent = pendentes;
      if (badgePill) badgePill.textContent = `${pendentes} Pendência${pendentes !== 1 ? 's' : ''}`;
      if (badgeSidebar) badgeSidebar.textContent = pendentes;
      if (fullAuditCount) fullAuditCount.textContent = pendentes;

      if (pendentes === 0) {
        if (badgeTop) badgeTop.className = 'bg-emerald-600 text-white text-[11px] font-extrabold px-2 py-0.5 rounded-full';
        if (badgePill) badgePill.className = 'bg-emerald-600 text-white text-xs font-extrabold px-2.5 py-0.5 rounded-full';
        if (badgeSidebar) badgeSidebar.className = 'sidebar-badge bg-emerald-600 text-white text-[10px] font-extrabold px-1.5 py-0.5 rounded-full';
      }
    }

    // ==========================================
    // MODAIS DE PREENCHIMENTO E JUSTIFICATIVA
    // ==========================================
    function abrirModalPreenchimentoRapido(vivId) {
      document.getElementById('modal-rapido-viv-id').textContent = vivId;
      document.getElementById('modal-preenchimento-rapido').classList.remove('hidden');
    }
    function fecharModalPreenchimentoRapido() {
      document.getElementById('modal-preenchimento-rapido').classList.add('hidden');
    }
    function salvarPreenchimentoRapido(e) {
      e.preventDefault();
      fecharModalPreenchimentoRapido();
      resolverPendencia(2, 'regularizado', 'Arraçoamento retroativo gravado (42 kg, sobra 0, O2 4.2)');
    }

    function abrirModalJustificarO2(vivId, o2Val) {
      document.getElementById('modal-just-viv-id').textContent = vivId;
      document.getElementById('modal-justificar-o2').classList.remove('hidden');
    }
    function fecharModalJustificarO2() {
      document.getElementById('modal-justificar-o2').classList.add('hidden');
    }
    function salvarJustificativaO2(e) {
      e.preventDefault();
      fecharModalJustificarO2();
      resolverPendencia(3, 'justificado', 'Aerador reserva acionado às 03:35. O2 restabelecido em 3.8 mg/L.');
    }

    function dispararAlertaWhatsAppO2(vivId, o2) {
      alert(`[WhatsApp Simulado]\n\n🚨 ALERTA CRÍTICO ENVIADO PARA O VIGIA NOTURNO (Carlos Silva):\n"Atenção: O oxigênio no ${vivId} mediu ${o2} mg/L. Ligar imediatamente os aeradores reservas!"`);
      abrirModalJustificarO2(vivId, o2);
    }

    // ==========================================
    // RELATÓRIO PDF EXECUTIVO
    // ==========================================
    function gerarRelatorioPDF() {
      const v = selectedViveiro || VIVEIROS_DATA[0];
      document.getElementById('pdf-header-tanque').textContent = `${v.nome} (${v.id})`;
      document.getElementById('pdf-tanque-id').textContent = `${v.nome} (Ciclo 12)`;
      document.getElementById('pdf-periodo').textContent = `${v.ddc} Dias de Cultivo`;
      document.getElementById('pdf-peso').textContent = `${v.pesoMedio} g`;
      document.getElementById('pdf-biomassa').textContent = `${v.biomassaKg.toLocaleString('pt-BR')} kg`;
      document.getElementById('pdf-fca').textContent = v.fca > 0 ? v.fca : '-';
      document.getElementById('pdf-racao-acumulada').textContent = v.racaoAcumuladaKg > 0 ? `${v.racaoAcumuladaKg.toLocaleString('pt-BR')} kg` : '-';
      document.getElementById('modal-relatorio-pdf').classList.remove('hidden');
    }
    function fecharModalPDF() {
      document.getElementById('modal-relatorio-pdf').classList.add('hidden');
    }

    // ==========================================
    // ALTERNAR PERFIL LEONARDO / PAI
    // ==========================================
    function switchProfile(perfil) {
      currentProfile = perfil;
      const btnLeo = document.getElementById('btn-profile-leo');
      const btnPai = document.getElementById('btn-profile-pai');
      const bannerPai = document.getElementById('view-pai-banner');

      if (perfil === 'leo') {
        btnLeo.className = 'flex items-center space-x-2 px-3 py-1.5 rounded-lg text-xs font-bold transition bg-aco text-white shadow';
        btnPai.className = 'flex items-center space-x-2 px-3 py-1.5 rounded-lg text-xs font-bold text-blue-200 hover:text-white transition';
        if (bannerPai) bannerPai.classList.add('hidden');
      } else {
        btnPai.className = 'flex items-center space-x-2 px-3 py-1.5 rounded-lg text-xs font-bold transition bg-amber-500 text-white shadow';
        btnLeo.className = 'flex items-center space-x-2 px-3 py-1.5 rounded-lg text-xs font-bold text-blue-200 hover:text-white transition';
        if (bannerPai) bannerPai.classList.remove('hidden');
      }
    }

    function openWhatsAppModal() {
      alert("🎙️ [Simulador de Áudio de Campo WhatsApp]\n\nÁudio recebido do Pai: 'Viveiro 02, oxigênio da manhã deu 4.2 e ração 25 quilos, pratos limpos!'\n\n✅ O ERP processou e gravou os dados com sucesso.");
    }

    // ==========================================
    // RENDERIZAÇÃO DE GRÁFICOS (CHART.JS)
    // ==========================================
    function renderizarGraficoBiomassaComparativo() {
      const ctx = document.getElementById('chart-biomassa-comparativo');
      if (!ctx) return;
      if (chartBiomassaCompInstance) chartBiomassaCompInstance.destroy();

      const labels = VIVEIROS_DATA.filter(v => v.biomassaKg > 0).map(v => v.id);
      const data = VIVEIROS_DATA.filter(v => v.biomassaKg > 0).map(v => v.biomassaKg);

      chartBiomassaCompInstance = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [{
            label: 'Biomassa Estimada (kg)',
            data: data,
            backgroundColor: '#2B6CB0',
            borderRadius: 6
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            y: { beginAtZero: true, title: { display: true, text: 'Quilos (kg)' } }
          }
        }
      });
    }

    function renderizarGraficosDoViveiro(v) {
      // 1. Gráfico Crescimento
      const ctxCresc = document.getElementById('chart-detail-crescimento');
      if (ctxCresc) {
        if (chartDetailCrescimentoInstance) chartDetailCrescimentoInstance.destroy();
        chartDetailCrescimentoInstance = new Chart(ctxCresc, {
          type: 'line',
          data: {
            labels: ['DDC 10', 'DDC 20', 'DDC 30', 'DDC 40', 'DDC 50', `DDC ${v.ddc}`],
            datasets: [
              {
                label: 'Peso Real (g)',
                data: [1.8, 3.9, 6.7, 9.4, 11.2, v.pesoMedio],
                borderColor: '#2B6CB0',
                backgroundColor: 'rgba(43, 108, 176, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.3
              },
              {
                label: 'Curva Teórica Ideal (g)',
                data: [1.6, 3.6, 6.2, 9.0, 11.5, 12.8],
                borderColor: '#94A3B8',
                borderDash: [5, 5],
                borderWidth: 2,
                tension: 0.3
              }
            ]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: { y: { beginAtZero: true, title: { display: true, text: 'Gramas (g)' } } }
          }
        });
      }

      // 2. Gráfico Oxigênio
      const ctxO2 = document.getElementById('chart-detail-oxigenio');
      if (ctxO2) {
        if (chartDetailOxigenioInstance) chartDetailOxigenioInstance.destroy();
        chartDetailOxigenioInstance = new Chart(ctxO2, {
          type: 'line',
          data: {
            labels: ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Hoje'],
            datasets: [
              {
                label: 'O₂ Manhã (mg/L)',
                data: [4.5, 4.4, 4.6, 4.2, 4.5, 4.3, v.o2Manha],
                borderColor: '#0284C7',
                borderWidth: 2,
                tension: 0.2
              },
              {
                label: 'O₂ Noite (mg/L)',
                data: [4.8, 4.7, 4.9, 4.6, 4.8, 4.7, v.o2Noite],
                borderColor: '#0D9488',
                borderWidth: 2,
                tension: 0.2
              },
              {
                label: 'Limite Crítico (3.0 mg/L)',
                data: [3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0],
                borderColor: '#DC2626',
                borderDash: [4, 4],
                borderWidth: 1.5,
                pointRadius: 0
              }
            ]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: { y: { min: 2.0, max: 7.0, title: { display: true, text: 'mg/L' } } }
          }
        });
      }
    }
  </script>
</body>
</html>
'''

with open(output_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Novo HTML gerado com sucesso em: {output_path}")
print(f"Tamanho gerado: {len(html_content)} caracteres.")
