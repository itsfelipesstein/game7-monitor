from playwright.sync_api import sync_playwright
import requests
import re
import time

# ==============================
# CONFIGURACAO
# ==============================

TOKEN = "COLOQUE_SEU_TOKEN_AQUI"
CHAT_ID = "8040951315"

PRECO_MAXIMO = 120.00

URL = "https://www.amazon.com.br/s?k=game+7+nba&s=price-asc-rank"

# ==============================

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
    except Exception as e:
        print("Erro Telegram:", e)


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
            "--disable-blink-features=AutomationControlled",
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

        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",

        extra_http_headers={
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Upgrade-Insecure-Requests": "1"
        }
    )

    page = context.new_page()

    page.goto(
        URL,
        wait_until="domcontentloaded",
        timeout=120000
    )

    page.wait_for_timeout(8000)

    print("Titulo da pagina:", page.title())

    print("URL final:", page.url)

    produtos = page.locator('[data-component-type="s-search-result"]')

    total = produtos.count()

    print("Produtos encontrados:", total)

    enviados = 0
    page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });

        Object.defineProperty(navigator, 'languages', {
            get: () => ['pt-BR', 'pt']
        });

        Object.defineProperty(navigator, 'platform', {
            get: () => 'Win32'
        });

        Object.defineProperty(navigator, 'plugins', {
            get: () => [1,2,3,4,5]
        });
    """)

    page.reload(wait_until="domcontentloaded")

    page.wait_for_timeout(5000)

    produtos = page.locator('[data-component-type="s-search-result"]')

    total = produtos.count()

    print("Produtos encontrados apos reload:", total)

    for i in range(total):

        try:

            item = produtos.nth(i)

            if item.locator("h2").count() == 0:
                continue

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

            preco = limpar_preco(f"{preco_whole},{preco_fraction}")

            if preco is None:
                continue

            link = item.locator("h2 a").get_attribute("href")

            if link:
                link = "https://www.amazon.com.br" + link

            print("-" * 50)
            print(titulo)
            print("Preco:", preco)
            print(link)

            if preco <= PRECO_MAXIMO:

                mensagem = (
                    "GAME 7 EM PROMOCAO!\n\n"
                    f"{titulo}\n\n"
                    f"Preco: R$ {preco:.2f}\n\n"
                    f"{link}"
                )

                enviar(mensagem)

                enviados += 1

                time.sleep(2)

        except Exception:
            import traceback
            traceback.print_exc()
            continue
    print("=" * 60)
    print("Produtos enviados:", enviados)
    print("=" * 60)

    context.close()
    browser.close()

print("Monitor finalizado.")
