import requests
from bs4 import BeautifulSoup

URL = 'https://www.ebay.com/sch/i.html?_from=R40&_nkw=oneplus+6t&_sacat=0&rt=nc&_udlo=150&_udhi=450%22&_ipg=200'
headers = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0'}
page = requests.get(URL, headers=headers)
soup = BeautifulSoup(page.content, 'html.parser')
clean = []

for price in soup.findAll("span", {"class": "s-item__price"}):
    clean.append(price.get_text(strip=True))

print(clean)