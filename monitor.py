from playwright.sync_api import sync_playwright
import requests
import re
import time

# ==============================
# CONFIGURACAO
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

    numeros = re.findall(r"\d+\.\d+|\d+", texto)

    if numeros:
        return float(numeros[0])

    return None


print("=" * 50)
print("GAME 7 MONITOR")
print("=" * 50)

with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)

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

    print("Titulo:", page.title())

    produtos = page.locator('[data-component-type="s-search-result"]')

    total = produtos.count()

    print(f"Produtos encontrados: {total}")

    enviados = 0
    for i in range(total):

        try:

            item = produtos.nth(i)

            if item.locator("h2").count() == 0:
                continue

            titulo = item.locator("h2").inner_text(timeout=3000)

            if "game" not in titulo.lower() or "7" not in titulo:
                continue

            preco_whole = ""
            preco_fraction = ""

            if item.locator(".a-price-whole").count() > 0:
                preco_whole = item.locator(".a-price-whole").first.inner_text()

            if item.locator(".a-price-fraction").count() > 0:
                preco_fraction = item.locator(".a-price-fraction").first.inner_text()

            preco = limpar_preco(f"{preco_whole},{preco_fraction}")

            if preco is None:
                continue

            link = item.locator("h2 a").get_attribute("href")

            if link:
                link = "https://www.amazon.com.br" + link

            print("-" * 40)
            print(titulo)
            print(preco)
            print(link)

            if preco <= PRECO_MAXIMO:

                mensagem = (
                    "GAME 7 EM PROMOCAO!\n\n"
                    f"{titulo}\n\n"
                    f"Preco: R$ {preco:.2f}\n\n"
                    f"Link: {link}"
                )

                enviar(mensagem)

                enviados += 1

                time.sleep(2)

        except Exception:
            import traceback
            traceback.print_exc()
            continue
    browser.close()

if enviados == 0:

    enviar(
        "Nenhuma roupa GAME 7 encontrada abaixo do valor definido.\n\n"
        f"Valor maximo: R$ {PRECO_MAXIMO:.2f}"
    )

else:

    enviar(
        "Monitor finalizado!\n\n"
        f"Promocoes enviadas: {enviados}"
    )

print("=" * 50)
print("Monitor finalizado.")
print("=" * 50)
