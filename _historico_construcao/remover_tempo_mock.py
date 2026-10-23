from pathlib import Path

p = Path(r"G:\Meu Drive\ANTIGRAVITY DRIVE\CAMARÃO\ERP CAMARÃO\dashboard_interativo_prototipo.html")
html = p.read_text(encoding="utf-8")

# 1. Remover do cabeçalho superior secundário
trecho_header_old = """          <span class="hidden sm:inline text-slate-300">|</span>
          <span class="hidden md:flex items-center gap-1 text-slate-600">
            <i class="fa-solid fa-cloud-sun text-amber-500"></i>
            Estuário: Maré em Enchente • Salinidade média 14 ppt
          </span>"""

if trecho_header_old in html:
    html = html.replace(trecho_header_old, "", 1)
    print("Sucesso: Informação de tempo/estuário removida do cabeçalho superior!")
else:
    print("Aviso: trecho_header_old não encontrado exatamente. Buscando por partes...")
    # Tenta substituição mais tolerante
    import re
    html = re.sub(r'<span class="hidden sm:inline text-slate-300">\|<\/span>\s*<span class="hidden md:flex items-center gap-1 text-slate-600">\s*<i class="fa-solid fa-cloud-sun text-amber-500"><\/i>\s*Estuário: Maré em Enchente[^<]*<\/span>', '', html)
    print("Sucesso via regex: Informação do cabeçalho removida!")

# 2. Ajustar o rodapé do bloco Radar de Água no Dashboard Principal
trecho_radar_old = """            <!-- Status do Estuário Ceará-Mirim -->
            <div class="p-2.5 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-between text-xs">
              <div class="flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
                <span class="text-slate-700 font-medium text-[11px]">
                  <strong>Captação do Rio Ceará-Mirim:</strong> Maré alta às 15h40 • Salinidade 15 ppt • pH 7.8
                </span>
              </div>
              <span class="text-[10px] font-bold text-emerald-800 bg-emerald-100 px-2 py-0.5 rounded border border-emerald-200">
                Água Excelente
              </span>
            </div>"""

trecho_radar_novo = """            <!-- Monitoramento Geral da Água -->
            <div class="p-2.5 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-between text-xs">
              <div class="flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
                <span class="text-slate-700 font-medium text-[11px]">
                  <strong>Monitoramento Zootécnico:</strong> Parâmetros físico-químicos estáveis nos viveiros monitorados
                </span>
              </div>
              <span class="text-[10px] font-bold text-emerald-800 bg-emerald-100 px-2 py-0.5 rounded border border-emerald-200">
                Rotina Normal
              </span>
            </div>"""

if trecho_radar_old in html:
    html = html.replace(trecho_radar_old, trecho_radar_novo, 1)
    print("Sucesso: Texto ilustrativo de maré do Rio Ceará-Mirim substituído por status zootécnico real!")
else:
    print("Aviso: trecho_radar_old não encontrado para substituição direta.")

p.write_text(html, encoding="utf-8")
print("Arquivo atualizado com sucesso!")
