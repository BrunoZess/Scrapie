"""
fetch_deals.py

Busca os jogos em promoção usando a API pública e gratuita da CheapShark
(https://apidocs.cheapshark.com/) e gera um arquivo index.html estático
com a lista de ofertas, pronto para ser publicado no GitHub Pages.

Não precisa de chave de API (API key) para usar a CheapShark.
"""

import requests
from datetime import datetime

# Endpoint da API que retorna as promoções (deals) ordenadas por % de desconto
API_URL = "https://www.cheapshark.com/api/1.0/deals"

# Cotação do dólar (API pública brasileira, sem necessidade de chave)
EXCHANGE_API_URL = "https://economia.awesomeapi.com.br/json/last/USD-BRL"

# Lojas que serão buscadas: nome de exibição -> storeID da CheapShark
# Lista completa de storeIDs em https://www.cheapshark.com/api/1.0/stores
STORES = {
    "Steam": 1,
    "GOG": 7,
    "Humble Store": 11,
    "Epic Games": 25,
}

# Parâmetros comuns da busca — dá pra customizar
BASE_PARAMS = {
    "upperPrice": 50,    # preço máximo em dólar
    "pageSize": 24,      # quantidade de jogos por loja
    "sortBy": "Savings", # ordena pelo maior desconto
}

HEADERS = {
    # A CheapShark exige um User-Agent descritivo nas requisições
    "User-Agent": "GameDealsSite/1.0 (github.com project; contato: seuemail@exemplo.com)"
}


def fetch_exchange_rate():
    """Busca a cotação atual do dólar em reais. Usa um valor de fallback se falhar."""
    try:
        response = requests.get(EXCHANGE_API_URL, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
        return float(data["USDBRL"]["bid"])
    except Exception as exc:
        print(f"Não foi possível buscar a cotação, usando valor de fallback. Erro: {exc}")
        return 5.50  # valor aproximado de fallback


def fetch_deals_for_store(store_name, store_id):
    """Busca as promoções de uma loja específica na API da CheapShark."""
    params = {**BASE_PARAMS, "storeID": store_id}
    response = requests.get(API_URL, params=params, headers=HEADERS, timeout=15)
    if not response.ok:
        print(f"Erro {response.status_code} da API para {store_name}. Resposta: {response.text}")
    response.raise_for_status()
    deals = response.json()
    for deal in deals:
        deal["_store"] = store_name
    return deals


def fetch_all_deals():
    """Busca as promoções de todas as lojas configuradas."""
    all_deals = []
    for store_name, store_id in STORES.items():
        all_deals.extend(fetch_deals_for_store(store_name, store_id))
    return all_deals


def build_html(deals, usd_to_brl):
    """Monta o HTML estático a partir da lista de jogos."""
    rows = ""
    for deal in deals:
        title = deal.get("title", "Sem título")
        sale_price_usd = float(deal.get("salePrice", 0))
        normal_price_usd = float(deal.get("normalPrice", 0))
        savings = float(deal.get("savings", 0))
        thumb = deal.get("thumb", "")
        deal_id = deal.get("dealID", "")
        store = deal.get("_store", "Outro")
        link = f"https://www.cheapshark.com/redirect?dealID={deal_id}"

        sale_price_brl = sale_price_usd * usd_to_brl
        normal_price_brl = normal_price_usd * usd_to_brl

        rows += f"""
        <div class="card" data-store="{store}" data-discount="{savings:.0f}" data-price="{sale_price_brl:.2f}">
            <div class="thumb-wrap">
                <img src="{thumb}" alt="{title}" loading="lazy">
                <span class="badge">-{savings:.0f}%</span>
                <span class="store-tag">{store}</span>
            </div>
            <div class="info">
                <h3>{title}</h3>
                <p class="price">
                    <span class="old">R$ {normal_price_brl:.2f}</span>
                    <span class="new">R$ {sale_price_brl:.2f}</span>
                </p>
                <a class="btn" href="{link}" target="_blank">Ver oferta</a>
            </div>
        </div>
        """

    updated_at = datetime.now().strftime("%d/%m/%Y %H:%M")
    store_tabs = "".join(
        f'<button class="tab" data-filter="{name}">{name}</button>'
        for name in STORES.keys()
    )

    html = f"""<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="UTF-8">
<title>Promoções de Jogos</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
    :root {{
        --bg: #0f1020;
        --bg-alt: #171a33;
        --card: #1c1f3d;
        --accent: #7c5cff;
        --accent-2: #ff5fa2;
        --green: #4ade80;
        --text: #f1f1f8;
        --muted: #9a9cc2;
    }}
    * {{ box-sizing: border-box; }}
    body {{
        font-family: 'Inter', sans-serif;
        background: radial-gradient(circle at top, var(--bg-alt), var(--bg) 60%);
        color: var(--text);
        margin: 0;
        padding: 40px 20px 60px;
        min-height: 100vh;
    }}
    header {{
        text-align: center;
        margin-bottom: 40px;
    }}
    h1 {{
        font-family: 'Poppins', sans-serif;
        font-size: 2.4em;
        margin: 0;
        background: linear-gradient(90deg, var(--accent), var(--accent-2));
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        letter-spacing: -0.5px;
    }}
    .updated {{
        color: var(--muted);
        margin-top: 10px;
        font-size: 0.9em;
    }}
    .grid {{
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
        gap: 22px;
        max-width: 1200px;
        margin: 0 auto;
    }}
    .card {{
        background: var(--card);
        border-radius: 16px;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        box-shadow: 0 4px 20px rgba(0,0,0,0.35);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        border: 1px solid rgba(255,255,255,0.06);
    }}
    .card:hover {{
        transform: translateY(-6px);
        box-shadow: 0 12px 30px rgba(124,92,255,0.25);
    }}
    .thumb-wrap {{
        position: relative;
    }}
    .thumb-wrap img {{
        width: 100%;
        height: 130px;
        object-fit: cover;
        display: block;
    }}
    .badge {{
        position: absolute;
        top: 10px;
        right: 10px;
        background: linear-gradient(90deg, var(--accent-2), #ff8c5f);
        color: white;
        font-weight: 700;
        font-size: 0.85em;
        padding: 4px 10px;
        border-radius: 999px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.4);
    }}
    .store-tag {{
        position: absolute;
        top: 10px;
        left: 10px;
        background: rgba(0,0,0,0.55);
        color: white;
        font-size: 0.75em;
        font-weight: 600;
        padding: 3px 9px;
        border-radius: 999px;
        backdrop-filter: blur(2px);
    }}
    .info {{
        padding: 14px 16px 16px;
        flex: 1;
        display: flex;
        flex-direction: column;
    }}
    .info h3 {{
        font-family: 'Poppins', sans-serif;
        font-size: 1em;
        font-weight: 600;
        margin: 0 0 10px 0;
        min-height: 2.4em;
        line-height: 1.3;
    }}
    .price {{
        margin: 0 0 14px 0;
        display: flex;
        align-items: baseline;
        gap: 8px;
    }}
    .price .old {{
        text-decoration: line-through;
        color: var(--muted);
        font-size: 0.85em;
    }}
    .price .new {{
        color: var(--green);
        font-weight: 700;
        font-size: 1.15em;
    }}
    .btn {{
        margin-top: auto;
        text-align: center;
        background: linear-gradient(90deg, var(--accent), #9b7bff);
        color: white;
        padding: 10px;
        border-radius: 10px;
        text-decoration: none;
        font-weight: 600;
        font-size: 0.9em;
        transition: opacity 0.2s ease;
    }}
    .btn:hover {{
        opacity: 0.85;
    }}
    footer {{
        text-align: center;
        color: var(--muted);
        font-size: 0.8em;
        margin-top: 50px;
    }}
    .controls {{
        max-width: 1200px;
        margin: 0 auto 28px;
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        justify-content: center;
        align-items: center;
    }}
    .tab {{
        background: var(--card);
        color: var(--text);
        border: 1px solid rgba(255,255,255,0.08);
        padding: 8px 16px;
        border-radius: 999px;
        cursor: pointer;
        font-family: 'Inter', sans-serif;
        font-size: 0.9em;
        font-weight: 500;
        transition: all 0.2s ease;
    }}
    .tab:hover {{
        border-color: var(--accent);
    }}
    .tab.active {{
        background: linear-gradient(90deg, var(--accent), var(--accent-2));
        border-color: transparent;
        font-weight: 600;
    }}
    .sort-wrap {{
        margin-left: 10px;
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    .sort-wrap label {{
        color: var(--muted);
        font-size: 0.85em;
    }}
    select {{
        background: var(--card);
        color: var(--text);
        border: 1px solid rgba(255,255,255,0.08);
        padding: 8px 12px;
        border-radius: 10px;
        font-family: 'Inter', sans-serif;
        font-size: 0.9em;
    }}
    .empty-msg {{
        text-align: center;
        color: var(--muted);
        margin-top: 40px;
        display: none;
    }}
</style>
</head>
<body>
    <header>
        <h1>🎮 Promoções de Jogos</h1>
        <p class="updated">Atualizado em {updated_at} · dados via CheapShark API · US$ 1 = R$ {usd_to_brl:.2f}</p>
    </header>

    <div class="controls">
        <button class="tab active" data-filter="all">Todas as lojas</button>
        {store_tabs}
        <div class="sort-wrap">
            <label for="sort">Ordenar por</label>
            <select id="sort">
                <option value="discount">Maior desconto</option>
                <option value="price-asc">Menor preço</option>
                <option value="price-desc">Maior preço</option>
            </select>
        </div>
    </div>

    <div class="grid" id="grid">
        {rows}
    </div>
    <p class="empty-msg" id="empty-msg">Nenhum jogo encontrado com esse filtro.</p>

    <footer>
        Preços e links via <a href="https://www.cheapshark.com" style="color: var(--muted);">CheapShark</a>
    </footer>

    <script>
        const grid = document.getElementById('grid');
        const tabs = document.querySelectorAll('.tab');
        const sortSelect = document.getElementById('sort');
        const emptyMsg = document.getElementById('empty-msg');
        let currentFilter = 'all';

        function applyFilterAndSort() {{
            const cards = Array.from(grid.querySelectorAll('.card'));

            // Ordenação
            const sortBy = sortSelect.value;
            cards.sort((a, b) => {{
                if (sortBy === 'discount') {{
                    return parseFloat(b.dataset.discount) - parseFloat(a.dataset.discount);
                }} else if (sortBy === 'price-asc') {{
                    return parseFloat(a.dataset.price) - parseFloat(b.dataset.price);
                }} else {{
                    return parseFloat(b.dataset.price) - parseFloat(a.dataset.price);
                }}
            }});
            cards.forEach(card => grid.appendChild(card));

            // Filtro
            let visibleCount = 0;
            cards.forEach(card => {{
                const matches = currentFilter === 'all' || card.dataset.store === currentFilter;
                card.style.display = matches ? '' : 'none';
                if (matches) visibleCount++;
            }});
            emptyMsg.style.display = visibleCount === 0 ? 'block' : 'none';
        }}

        tabs.forEach(tab => {{
            tab.addEventListener('click', () => {{
                tabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                currentFilter = tab.dataset.filter;
                applyFilterAndSort();
            }});
        }});

        sortSelect.addEventListener('change', applyFilterAndSort);

        applyFilterAndSort();
    </script>
</body>
</html>
"""
    return html


def main():
    usd_to_brl = fetch_exchange_rate()
    deals = fetch_all_deals()
    html = build_html(deals, usd_to_brl)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"index.html gerado com {len(deals)} jogos em promoção. Cotação usada: R$ {usd_to_brl:.2f}")


if __name__ == "__main__":
    main()
