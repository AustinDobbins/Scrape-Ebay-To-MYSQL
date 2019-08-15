# Scrapes ebay for product search page prices of 200 products and puts them into a list 
import requests
from bs4 import BeautifulSoup

URL = 'https://www.ebay.com/sch/i.html?_from=R40&_nkw=oneplus+6t&_sacat=0&_udlo=150&_udhi=450%22&_ipg=200&rt=nc&LH_Sold=1&LH_Complete=1'
headers = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0'}
page = requests.get(URL, headers=headers)
soup = BeautifulSoup(page.content, 'html.parser')
results = []
clean = []




#finds all prices on the page and strips html tags
for price in soup.findAll("span", {"class": "POSITIVE"}):
    results.append(price.get_text(strip=True))

#remove false data 
for i in results:
	if 'to' in results:
		results.remove('to')
for i in results:
	if '$0.00' in results:
		results.remove('$0.00')

#removes dollar signs and converts data to floats, appends clean data clean list
for i in results:
  clean.append(float(i[1:]))

sum = sum(map(float,clean))
len = len(clean)
avg = sum / len

print(avg)
