from bs4 import BeautifulSoup
import requests
import time

# ==========================
# CONFIGURAÇÕES
# ==========================

TOKEN = "8677381356:AAG81rPEL2wEQLTzKGrymHGeo-b3KB9SXX0"
CHAT_ID = "8040951315"

PRECO_MAXIMO = 120.00

URL = (
    "https://www.amazon.com.br/s?"
    "k=game+7+nba+masculino"
    "&s=price-asc-rank"
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/138.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9"
}
# ==========================
# TELEGRAM
# ==========================

def enviar(msg):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": msg,
            "disable_web_page_preview": False
        },
        timeout=30
    )

# ==========================
# BUSCAR AMAZON
# ==========================

def buscar():
    resposta = requests.get(
        URL,
        headers=HEADERS,
        timeout=30
    )

    if resposta.status_code != 200:
        print("Erro ao acessar Amazon:", resposta.status_code)
        return

    soup = BeautifulSoup(resposta.text, "html.parser")

    produtos = soup.select('[data-component-type="s-search-result"]')

    print(f"Produtos encontrados: {len(produtos)}")
    for produto in produtos:

        try:
            link_tag = produto.select_one("h2 a")

        if link_tag is None:
            continue

        titulo = link_tag.get_text(" ", strip=True)

        titulo_lower = titulo.lower()

            # Filtro GAME 7
            if "game" not in titulo_lower or "7" not in titulo_lower:
                continue

            # Procura preço
            preco = produto.select_one(".a-price-whole")
            centavos = produto.select_one(".a-price-fraction")

            if preco is None:
                continue

            valor = preco.get_text(strip=True)

            if centavos:
                valor += "." + centavos.get_text(strip=True)

            valor = float(valor.replace(".", "").replace(",", "."))

            if valor > PRECO_MAXIMO:
                continue

            # Link
            link = produto.select_one("h2 a")

            if link_tag.has_attr("href"):
                link = "https://www.amazon.com.br" + link_tag["href"]
            else:
                link = "Sem link"

            print("=" * 50)
            print(titulo)
            print(valor)
            print(link)
            mensagem = (
                "🏀 GAME 7 ENCONTRADA!\n\n"
                f"{titulo}\n\n"
                f"💰 R$ {valor:.2f}\n\n"
                f"🔗 {link}"
            )

            enviar(mensagem)

        except Exception as e:
            print(e)
            continue


# ==========================
# LOOP INFINITO
# ==========================

print("=" * 50)
print("MONITOR GAME 7 INICIADO")
print("=" * 50)

while True:
    try:
        buscar()
    except Exception as e:
        print("Erro:", e)

    print("Aguardando 10 minutos...")
    time.sleep(600)
