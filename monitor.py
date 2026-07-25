import requests
from bs4 import BeautifulSoup

url = "https://www.amazon.com.br/s?k=game+7+nba"

headers = {
    "User-Agent": "Mozilla/5.0"
}

r = requests.get(url, headers=headers)

print("Status:", r.status_code)
print(r.text[:1000])  # Mostra os primeiros 1000 caracteres da página

