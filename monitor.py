from playwright.sync_api import sync_playwright
import requests
import traceback
import re
import time

# ==========================================
# CONFIGURAÇÃO
# ==========================================

TOKEN = "8677381356:AAG8IrPEL2wEQLTzK GrymHGeo-b3KB9SXX0"
CHAT_ID = "8040951315"

PRECO_MAXIMO = 115.00

URL = "https://www.amazon.com.br/s?k=game+7+nba"

# ==========================================


def enviar(mensagem):

    try:

        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            data={
                "chat_id": CHAT_ID,
                "text": mensagem,
                "disable_web_page_preview": False
            },
            timeout=30
        )

    except Exception as erro:
        print("Erro Telegram:", erro)


def limpar_preco(texto):

    texto = texto.replace("R$", "")
    texto = texto.replace(".", "")
    texto = texto.replace(",", ".")

    numeros = re.findall(r"\d+\.\d+|\d+", texto)

    if numeros:
        return float(numeros[0])

    return None


print("=" * 60)
print("GAME 7 MONITOR")
print("=" * 60)

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=True,
        args=[
            "--no-sandbox",
            "--disable-dev-shm-usage"
        ]
    )

    context = browser.new_context(

        locale="pt-BR",

        timezone_id="America/Sao_Paulo",

        viewport={
            "width": 1366,
            "height": 768
        },

        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
    )

    page = context.new_page()

    print("Abrindo Amazon...")

page.goto(
    URL,
    wait_until="domcontentloaded",
    timeout=120000
)

page.wait_for_timeout(8000)

print("Título:", page.title())
print("URL:", page.url)

print("=" * 50)
print("HTML recebido:")
print(page.content()[:1500])
print("=" * 50)

produtos = page.locator('[data-component-type="s-search-result"]')

    total = produtos.count()

    print("Produtos encontrados:", total)

    enviados = 0
    for i in range(total):

        try:

            item = produtos.nth(i)

            if item.locator("h2").count() == 0:
                continue

            titulo = item.locator("h2").inner_text().strip()

            titulo_lower = titulo.lower()

            # ===========================
            # FILTROS
            # ===========================

            if "game 7" not in titulo_lower:
                continue

            if "nba" not in titulo_lower:
                continue

            if "mascul" not in titulo_lower:
                continue

            if item.locator(".a-price-whole").count() == 0:
                continue

            preco_whole = item.locator(".a-price-whole").first.inner_text()

            preco_fraction = "00"

            if item.locator(".a-price-fraction").count() > 0:
                preco_fraction = item.locator(".a-price-fraction").first.inner_text()

            preco = limpar_preco(f"{preco_whole},{preco_fraction}")

            if preco is None:
                continue

            if preco > PRECO_MAXIMO:
                continue

            link = ""

            if item.locator("h2 a").count() > 0:

                href = item.locator("h2 a").first.get_attribute("href")

                if href:
                    link = "https://www.amazon.com.br" + href

            print("-" * 60)
            print(titulo)
            print(f"Preço: R$ {preco:.2f}")
            print(link)

            mensagem = (
                "🏀 GAME 7 ENCONTRADA!\n\n"
                f"{titulo}\n\n"
                f"💰 R$ {preco:.2f}\n\n"
                f"{link}"
            )

            enviar(mensagem)

            enviados += 1

            time.sleep(2)

        except Exception:

            traceback.print_exc()

            continue
    print("=" * 60)
    print(f"Total de alertas enviados: {enviados}")
    print("=" * 60)

    if enviados == 0:
        print("Nenhum produto encontrado dentro dos filtros.")

    context.close()
    browser.close()

print("Monitor finalizado.")
