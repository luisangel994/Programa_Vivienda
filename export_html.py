import os
import sys
import webbrowser
from datetime import datetime
from database import get_recent_notices
from config import BASE_DIR, MAX_PRICE_EUR

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def generate_html_report(output_file: str = "report.html", auto_open: bool = True) -> str:
    """
    Genera un informe HTML interactivo con filtros por Estado, Tipo/Fuente, 
    Buscador en tiempo real y ordenación dinámica por fecha (más recientes primero) o precio.
    """
    notices = get_recent_notices(limit=300)
    file_path = BASE_DIR / output_file

    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Promociones de Vivienda en Valencia (VPO / Obra Nueva)</title>
    <style>
        :root {{
            --primary: #2563eb;
            --primary-hover: #1d4ed8;
            --text-main: #0f172a;
            --text-muted: #64748b;
            --bg: #f8fafc;
            --card-bg: #ffffff;
            --border-light: #e2e8f0;
            --badge-sale: #7c3aed; /* Púrpura EN VENTA */
            --badge-const: #d97706; /* Dorado INICIO CONSTRUCCIÓN */
            --badge-coop: #2563eb;  /* Azul COOPERATIVA */
            --badge-land: #059669;  /* Verde LICITACIÓN SUELO */
            --badge-delivery: #4f46e5; /* Índigo ENTREGA DE VIVIENDAS */
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg);
            color: var(--text-main);
            padding: 30px 20px;
        }}

        .container {{
            max-width: 1240px;
            margin: 0 auto;
        }}

        /* Header Principal */
        .header-box {{
            background: white;
            border-radius: 20px;
            padding: 24px 30px;
            margin-bottom: 25px;
            border: 1px solid var(--border-light);
            box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        }}

        .top-nav {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 15px;
            margin-bottom: 20px;
        }}

        .main-title {{
            font-size: 1.7rem;
            font-weight: 800;
            color: var(--text-main);
        }}

        .main-subtitle {{
            font-size: 0.9rem;
            color: var(--text-muted);
            margin-top: 4px;
        }}

        /* Barra de Filtros y Ordenación */
        .filters-toolbar {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 15px;
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid var(--border-light);
        }}

        .filter-group {{
            display: flex;
            flex-direction: column;
            gap: 6px;
        }}

        .filter-label {{
            font-size: 0.8rem;
            font-weight: 700;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .select-control, .input-control {{
            padding: 10px 14px;
            border: 1.5px solid var(--border-light);
            border-radius: 10px;
            font-size: 0.92rem;
            color: var(--text-main);
            background: white;
            outline: none;
            transition: all 0.2s;
        }}

        .select-control:focus, .input-control:focus {{
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
        }}

        /* Counter Bar */
        .counter-bar {{
            margin-bottom: 20px;
            font-size: 0.9rem;
            color: var(--text-muted);
            font-weight: 600;
        }}

        .counter-bar span {{
            color: var(--primary);
            font-weight: 800;
        }}

        /* Grid Layout de Tarjetas */
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
            gap: 30px;
        }}

        /* Tarjeta */
        .card {{
            background: var(--card-bg);
            border-radius: 20px;
            overflow: hidden;
            border: 1px solid var(--border-light);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: transform 0.25s ease, box-shadow 0.25s ease;
        }}

        .card:hover {{
            transform: translateY(-6px);
            box-shadow: 0 12px 24px rgba(0, 0, 0, 0.09);
        }}

        .card-image-wrap {{
            position: relative;
            width: 100%;
            height: 220px;
            overflow: hidden;
            background-color: #cbd5e1;
        }}

        .card-image-wrap img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.4s ease;
        }}

        .card:hover .card-image-wrap img {{
            transform: scale(1.04);
        }}

        .badge-status {{
            position: absolute;
            top: 14px;
            left: 14px;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.72rem;
            font-weight: 800;
            color: white;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            display: flex;
            align-items: center;
            gap: 6px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }}

        .badge-sale {{ background-color: var(--badge-sale); }}
        .badge-const {{ background-color: var(--badge-const); }}
        .badge-coop {{ background-color: var(--badge-coop); }}
        .badge-land {{ background-color: var(--badge-land); }}
        .badge-delivery {{ background-color: var(--badge-delivery); }}

        .media-badge {{
            position: absolute;
            bottom: 12px;
            right: 12px;
            background: rgba(0, 0, 0, 0.65);
            backdrop-filter: blur(4px);
            color: white;
            font-size: 0.78rem;
            font-weight: 600;
            padding: 4px 10px;
            border-radius: 14px;
            display: flex;
            align-items: center;
            gap: 5px;
        }}

        .card-body {{
            padding: 20px 24px;
            flex-grow: 1;
            display: flex;
            flex-direction: column;
        }}

        .units-count {{
            font-size: 0.82rem;
            font-weight: 700;
            color: var(--primary);
            margin-bottom: 4px;
        }}

        .location-tag {{
            font-size: 0.78rem;
            font-weight: 700;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.6px;
            margin-bottom: 8px;
        }}

        .card-title {{
            font-size: 1.2rem;
            font-weight: 800;
            color: var(--text-main);
            line-height: 1.35;
            margin-bottom: 14px;
            text-transform: uppercase;
        }}

        .price-text {{
            font-size: 1.35rem;
            font-weight: 800;
            color: var(--text-main);
            margin-bottom: 16px;
        }}

        .features-box {{
            border: 1px solid var(--border-light);
            border-radius: 12px;
            padding: 12px 14px;
            background-color: #fafafa;
            margin-top: auto;
        }}

        .type-pill {{
            display: inline-block;
            border: 1px solid #bfdbfe;
            background-color: #eff6ff;
            color: #1d4ed8;
            font-size: 0.7rem;
            font-weight: 800;
            padding: 3px 10px;
            border-radius: 12px;
            text-transform: uppercase;
            margin-bottom: 10px;
        }}

        .features-row {{
            display: flex;
            align-items: center;
            gap: 18px;
            font-size: 0.88rem;
            color: #475569;
            font-weight: 600;
        }}

        .feature-item {{
            display: flex;
            align-items: center;
            gap: 6px;
        }}

        .card-footer {{
            padding: 16px 24px 22px 24px;
            text-align: center;
            background: white;
        }}

        .btn-action {{
            color: var(--primary);
            font-weight: 700;
            font-size: 0.98rem;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            transition: gap 0.2s, color 0.2s;
        }}

        .btn-action:hover {{
            color: var(--primary-hover);
            gap: 12px;
        }}

        footer {{
            text-align: center;
            margin-top: 50px;
            color: var(--text-muted);
            font-size: 0.85rem;
        }}
    </style>
</head>
<body>

<div class="container">
    <div class="header-box">
        <div class="top-nav">
            <div>
                <h1 class="main-title">🏢 Promociones Valencia & Área Metropolitana</h1>
                <div class="main-subtitle">Filtro de VPO / VPP y Obra Nueva hasta {MAX_PRICE_EUR:,.0f} €</div>
            </div>
        </div>

        <div class="filters-toolbar">
            <div class="filter-group">
                <label class="filter-label">🔍 Buscar Texto</label>
                <input type="text" id="searchInput" class="input-control" onkeyup="applyFiltersAndSort()" placeholder="Municipio, barrio o promotora...">
            </div>

            <div class="filter-group">
                <label class="filter-label">🏷️ Estado de la Promoción</label>
                <select id="statusFilter" class="select-control" onchange="applyFiltersAndSort()">
                    <option value="all">Todos los estados</option>
                    <option value="entrega">🔑 Entrega de viviendas</option>
                    <option value="construccion">🏗️ Inicio de construcción</option>
                    <option value="venta">🏷️ En venta</option>
                    <option value="cooperativa">🤝 Cooperativa</option>
                    <option value="licitacion">📜 Licitación / Oficial GVA</option>
                </select>
            </div>

            <div class="filter-group">
                <label class="filter-label">🏢 Tipo de Fuente</label>
                <select id="sourceFilter" class="select-control" onchange="applyFiltersAndSort()">
                    <option value="all">Todas las fuentes</option>
                    <option value="promotora">🏢 Promotoras (Metrovacesa, Olivares...)</option>
                    <option value="cooperativa">🤝 Cooperativas (SFI, Prygesa...)</option>
                    <option value="oficial">🏛️ Oficial GVA / EVha / PLACSP</option>
                </select>
            </div>

            <div class="filter-group">
                <label class="filter-label">↕️ Ordenar Publicaciones</label>
                <select id="sortOrder" class="select-control" onchange="applyFiltersAndSort()">
                    <option value="date-desc">🕒 Más recientes primero</option>
                    <option value="date-asc">⏳ Más antiguas primero</option>
                    <option value="price-asc">💰 Precio: menor a mayor</option>
                    <option value="price-desc">💰 Precio: mayor a menor</option>
                </select>
            </div>
        </div>
    </div>

    <div class="counter-bar">
        Mostrando <span id="visibleCount">{len(notices)}</span> de <span id="totalCount">{len(notices)}</span> oportunidades encontradas
    </div>

    <div class="grid" id="cardsGrid">
"""

    for idx, notice in enumerate(notices):
        id_, title, source, loc, price, url, created_at, notified, image_url, units, bedrooms, size_m2, status = notice
        
        # Clasificar tipo de fuente para filtrado
        source_lower = source.lower()
        if "evha" in source_lower or "gva" in source_lower or "placsp" in source_lower or "dogv" in source_lower:
            source_category = "oficial"
        elif "cooperativa" in source_lower or "sfi" in source_lower or "prygesa" in source_lower or "fecovi" in source_lower or "libra" in source_lower:
            source_category = "cooperativa"
        else:
            source_category = "promotora"

        # Formato de precio
        price_display = f"Desde {price:,.0f}€ + IVA" if price > 0 else "Consultar precio"

        # Formato de insignia de estado
        status_upper = status.upper()
        if "ENTREGA" in status_upper:
            badge_class = "badge-delivery"
            badge_icon = "🔑"
            status_clean = "ENTREGA DE VIVIENDAS"
        elif "CONSTRUCC" in status_upper:
            badge_class = "badge-const"
            badge_icon = "🏗️"
            status_clean = "INICIO CONSTRUCCIÓN"
        elif "COOPERATIVA" in status_upper or "COOP" in status_upper:
            badge_class = "badge-coop"
            badge_icon = "🤝"
            status_clean = "COOPERATIVA VPO"
        elif "LICITAC" in status_upper or "SUELO" in status_upper:
            badge_class = "badge-land"
            badge_icon = "📜"
            status_clean = "LICITACIÓN SUELO"
        else:
            badge_class = "badge-sale"
            badge_icon = "🏷️"
            status_clean = "EN VENTA"

        fallback_img = "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?auto=format&fit=crop&w=800&q=80"
        final_img = image_url if (image_url and image_url.startswith("http")) else fallback_img

        # Formatear timestamp de fecha para ordenación
        date_str = str(created_at)

        html_content += f"""
        <div class="card" 
             data-index="{idx}"
             data-date="{date_str}" 
             data-price="{price}" 
             data-status="{status_clean.lower()}" 
             data-source-category="{source_category}"
             data-search="{title.lower()} {source.lower()} {loc.lower()}">
            <div class="card-image-wrap">
                <img src="{final_img}" alt="{title}" loading="lazy" onerror="this.src='{fallback_img}'">
                <div class="badge-status {badge_class}">
                    <span>{badge_icon}</span> {status_clean}
                </div>
                <div class="media-badge">
                    <span>▶</span> Video / Galería
                </div>
            </div>

            <div class="card-body">
                <div class="units-count">{units}</div>
                <div class="location-tag">📍 {loc}</div>
                <h3 class="card-title">{title}</h3>
                
                <div class="price-text">{price_display}</div>

                <div class="features-box">
                    <span class="type-pill">PLURIFAMILIAR / VPO</span>
                    <div class="features-row">
                        <div class="feature-item">
                            <span>🛏️</span> {bedrooms}
                        </div>
                        <div class="feature-item">
                            <span>📐</span> {size_m2}
                        </div>
                    </div>
                    <!-- Detalles adicionales de la parcela, calle o concurso -->
                    <div style="font-size: 0.78rem; color: #64748b; margin-top: 8px; font-weight: 600; border-top: 1px dashed #cbd5e1; padding-top: 6px;">
                        Detalles: Licitación de Suelo Residencial / VPO
                    </div>
                </div>
            </div>

            <div class="card-footer">
                <a href="{url}" target="_blank" class="btn-action">
                    Ver promoción <span>&rarr;</span>
                </a>
            </div>
        </div>
"""

    html_content += """
    </div>

    <footer>
        Buscador de Viviendas Protegidas y Promociones en Valencia &bull; Filtros y Ordenación Interactiva
    </footer>
</div>

<script>
function applyFiltersAndSort() {
    let searchInput = document.getElementById('searchInput').value.toLowerCase();
    let statusFilter = document.getElementById('statusFilter').value;
    let sourceFilter = document.getElementById('sourceFilter').value;
    let sortOrder = document.getElementById('sortOrder').value;

    let grid = document.getElementById('cardsGrid');
    let cards = Array.from(grid.children);
    let visibleCount = 0;

    cards.forEach(card => {
        let textMatch = card.getAttribute('data-search').includes(searchInput);
        
        let cardStatus = card.getAttribute('data-status');
        let statusMatch = (statusFilter === 'all') || 
            (statusFilter === 'entrega' && cardStatus.includes('entrega')) ||
            (statusFilter === 'construccion' && cardStatus.includes('construcc')) ||
            (statusFilter === 'venta' && cardStatus.includes('venta')) ||
            (statusFilter === 'cooperativa' && cardStatus.includes('coop')) ||
            (statusFilter === 'licitacion' && cardStatus.includes('licitac'));

        let cardSourceCat = card.getAttribute('data-source-category');
        let sourceMatch = (sourceFilter === 'all') || (cardSourceCat === sourceFilter);

        if (textMatch && statusMatch && sourceMatch) {
            card.style.display = "flex";
            visibleCount++;
        } else {
            card.style.display = "none";
        }
    });

    document.getElementById('visibleCount').innerText = visibleCount;

    // Ordenación dinámica de elementos visible e invisibles
    cards.sort((a, b) => {
        if (sortOrder === 'date-desc') {
            return parseInt(b.getAttribute('data-index')) - parseInt(a.getAttribute('data-index'));
        } else if (sortOrder === 'date-asc') {
            return parseInt(a.getAttribute('data-index')) - parseInt(b.getAttribute('data-index'));
        } else if (sortOrder === 'price-asc') {
            let pA = parseFloat(a.getAttribute('data-price')) || 9999999;
            let pB = parseFloat(b.getAttribute('data-price')) || 9999999;
            return pA - pB;
        } else if (sortOrder === 'price-desc') {
            let pA = parseFloat(a.getAttribute('data-price')) || 0;
            let pB = parseFloat(b.getAttribute('data-price')) || 0;
            return pB - pA;
        }
        return 0;
    });

    cards.forEach(card => grid.appendChild(card));
}

// Ejecutar ordenación inicial (más recientes primero)
window.onload = function() {
    applyFiltersAndSort();
};
</script>

</body>
</html>
"""

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"✅ Informe HTML actualizado con filtros y ordenación dinámica en: {file_path}")

    if auto_open:
        webbrowser.open(file_path.as_uri())

    return str(file_path)

if __name__ == "__main__":
    generate_html_report()
