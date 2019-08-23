# Scrapes ebay for product search page prices of 200 products and puts them into a list 
import requests
import mysql.connector
import datetime
import locale
from bs4 import BeautifulSoup

URL = 'https://www.ebay.com/sch/i.html?_from=R40&_nkw=oneplus+6t&_sacat=0&_udlo=150&_udhi=450%22&_ipg=200&rt=nc&LH_Sold=1&LH_Complete=1'
headers = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0'}
page = requests.get(URL, headers=headers)
soup = BeautifulSoup(page.content, 'html.parser')
results = []
clean = []
date = datetime.date.today()




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

locale.setlocale( locale.LC_ALL, 'English_United States.1252' )
avgPrice = locale.currency( avg, grouping = True )


#mysql database
mydb = mysql.connector.connect(
    host = 'localhost',
    user = 'root',
    passwd = '',
    database = 'testdb'
)

mycursor = mydb.cursor()

sqlFormula = "INSERT INTO average (product_name, scrape_date, avg_sold_price) VALUES (%s, %s, %s)"
testScrape = ('Oneplus 6t', date, avgPrice)

mycursor.execute(sqlFormula, testScrape)

mydb.commit()




