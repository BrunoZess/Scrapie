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
            <img src="{thumb}" alt="{title}">
            <div class="info">
                <h3>{title}</h3>
                <p class="price">
                    <span class="old">US$ {normal_price:.2f}</span>
                    <span class="new">US$ {sale_price:.2f}</span>
                </p>
                <p class="discount">-{savings:.0f}%</p>
                <a href="{link}" target="_blank">Ver oferta</a>
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
<style>
    body {{
        font-family: Arial, sans-serif;
        background: #1b1b2f;
        color: #eee;
        margin: 0;
        padding: 20px;
    }}
    h1 {{
        text-align: center;
    }}
    .updated {{
        text-align: center;
        color: #aaa;
        margin-bottom: 30px;
        font-size: 0.9em;
    }}
    .grid {{
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
        gap: 16px;
        max-width: 1200px;
        margin: 0 auto;
    }}
    .card {{
        background: #262640;
        border-radius: 10px;
        overflow: hidden;
        display: flex;
        flex-direction: column;
    }}
    .card img {{
        width: 100%;
        display: block;
    }}
    .info {{
        padding: 10px;
        flex: 1;
        display: flex;
        flex-direction: column;
    }}
    .info h3 {{
        font-size: 1em;
        margin: 0 0 8px 0;
        min-height: 2.4em;
    }}
    .price .old {{
        text-decoration: line-through;
        color: #999;
        margin-right: 8px;
        font-size: 0.85em;
    }}
    .price .new {{
        color: #6cf25a;
        font-weight: bold;
    }}
    .discount {{
        color: #ff5f5f;
        font-weight: bold;
        margin: 4px 0;
    }}
    .info a {{
        margin-top: auto;
        text-align: center;
        background: #4c4cff;
        color: white;
        padding: 8px;
        border-radius: 6px;
        text-decoration: none;
    }}
    .info a:hover {{
        background: #6c6cff;
    }}
</style>
</head>
<body>
    <h1>🎮 Promoções de Jogos</h1>
    <p class="updated">Atualizado em {updated_at} — dados via CheapShark API</p>
    <div class="grid">
        {rows}
    </div>
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
