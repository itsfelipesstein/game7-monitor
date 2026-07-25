from playwright.sync_api import sync_playwright
import requests
import os

TOKEN = os.getenv("8677381356:AAG8IrPEL2wEQLTzK GrymHGeo-b3KB9SXX0")
CHAT_ID = os.getenv("8040951315")

URL = "https://www.amazon.com.br/s?k=game+7+nba&s=price-asc-rank"

def enviar(msg):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": msg,
            "disable_web_page_preview": True
        }
    )

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    page.goto(URL, wait_until="networkidle")

    print(page.title())

    browser.close()
