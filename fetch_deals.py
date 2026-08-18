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

# Parâmetros da busca — dá pra customizar
PARAMS = {
    "storeID": 1,        # 1 = Steam. Veja a lista de lojas em /api/1.0/stores
    "upperPrice": 50,    # preço máximo em dólar
    "pageSize": 30,      # quantidade de jogos
    "sortBy": "Savings", # ordena pelo maior desconto
}


HEADERS = {
    # A CheapShark exige um User-Agent descritivo nas requisições
    "User-Agent": "GameDealsSite/1.0 (github.com project; contato: seuemail@exemplo.com)"
}


def fetch_deals():
    """Busca as promoções na API da CheapShark."""
    response = requests.get(API_URL, params=PARAMS, headers=HEADERS, timeout=15)
    if not response.ok:
        # Mostra o corpo da resposta de erro para facilitar o diagnóstico
        print(f"Erro {response.status_code} da API. Resposta: {response.text}")
    response.raise_for_status()
    return response.json()


def build_html(deals):
    """Monta o HTML estático a partir da lista de jogos."""
    rows = ""
    for deal in deals:
        title = deal.get("title", "Sem título")
        sale_price = float(deal.get("salePrice", 0))
        normal_price = float(deal.get("normalPrice", 0))
        savings = float(deal.get("savings", 0))
        thumb = deal.get("thumb", "")
        deal_id = deal.get("dealID", "")
        link = f"https://www.cheapshark.com/redirect?dealID={deal_id}"

        rows += f"""
        <div class="card">
            <div class="thumb-wrap">
                <img src="{thumb}" alt="{title}" loading="lazy">
                <span class="badge">-{savings:.0f}%</span>
            </div>
            <div class="info">
                <h3>{title}</h3>
                <p class="price">
                    <span class="old">US$ {normal_price:.2f}</span>
                    <span class="new">US$ {sale_price:.2f}</span>
                </p>
                <a class="btn" href="{link}" target="_blank">Ver oferta</a>
            </div>
        </div>
        """

    updated_at = datetime.now().strftime("%d/%m/%Y %H:%M")

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
</style>
</head>
<body>
    <header>
        <h1>🎮 Promoções de Jogos</h1>
        <p class="updated">Atualizado em {updated_at} · dados via CheapShark API</p>
    </header>
    <div class="grid">
        {rows}
    </div>
    <footer>
        Preços e links via <a href="https://www.cheapshark.com" style="color: var(--muted);">CheapShark</a>
    </footer>
</body>
</html>
"""
    return html


def main():
    deals = fetch_deals()
    html = build_html(deals)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"index.html gerado com {len(deals)} jogos em promoção.")


if __name__ == "__main__":
    main()
