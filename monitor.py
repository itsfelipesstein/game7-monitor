from playwright.sync_api import sync_playwright
import requests
import re
import time

# ==============================
# CONFIGURAÇÃO
# ==============================

TOKEN = "8677381356:AAG8IrPEL2wEQLTzK GrymHGeo-b3KB9SXX0"
CHAT_ID = "8040951315"

PRECO_MAXIMO = 120.00

URL = "https://www.amazon.com.br/s?k=game+7+nba&s=price-asc-rank"

# ==============================

def enviar(mensagem):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": mensagem,
            "disable_web_page_preview": False
        },
        timeout=30
    )


def limpar_preco(texto):
    texto = texto.replace("R$", "")
    texto = texto.replace(".", "")
    texto = texto.replace(",", ".")

    numero = re.findall(r"\d+\.\d+|\d+", texto)

    if numero:
        return float(numero[0])

    return None


print("=" * 50)
print("GAME7 MONITOR")
print("=" * 50)

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=True
    )

    page = browser.new_page(
        viewport={
            "width": 1400,
            "height": 900
        }
    )

    page.goto(
    URL,
    wait_until="domcontentloaded",
    timeout=120000
)

page.wait_for_timeout(5000)
    )

    page.wait_for_timeout(3000)

    print(page.title())
    produtos = page.locator('[data-component-type="s-search-result"]')

    total = produtos.count()

    print(f"Produtos encontrados: {total}")

    enviados = 0

    for i in range(total):

        try:

            item = produtos.nth(i)

            titulo = item.locator("h2").inner_text(timeout=3000)

            if "game" not in titulo.lower():
                continue

            if "7" not in titulo:
                continue

            preco_whole = ""

            preco_fraction = ""

            if item.locator(".a-price-whole").count() > 0:
                preco_whole = item.locator(".a-price-whole").first.inner_text()

            if item.locator(".a-price-fraction").count() > 0:
                preco_fraction = item.locator(".a-price-fraction").first.inner_text()

            preco_texto = f"{preco_whole},{preco_fraction}"

            preco = limpar_preco(preco_texto)

            if preco is None:
                continue

            link = item.locator("h2 a").get_attribute("href")

            if link:
                link = "https://www.amazon.com.br" + link

            print(titulo)
            print(preco)
            print(link)
            print("-" * 40)

            if preco <= PRECO_MAXIMO:

                mensagem = f"""🏀 GAME 7

{titulo}

💰 R$ {preco:.2f}

🔗 {link}
"""

                enviar(mensagem)

                enviados += 1

                time.sleep(2)


except Exception as erro:
    import traceback
    traceback.print_exc()
    continue

    browser.close()

    if enviados == 0:

        enviar(
            "😕 Nenhuma roupa GAME 7 foi encontrada abaixo do valor definido.\n\n"
            f"Valor máximo: R$ {PRECO_MAXIMO:.2f}"
        )

    else:

        enviar(
            f"✅ Monitor finalizado!\n\n"
            f"Promoções enviadas: {enviados}"
        )

print("=" * 50)
print("Monitor finalizado.")
print("=" * 50)
