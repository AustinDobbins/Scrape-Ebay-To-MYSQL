import requests
import mysql.connector
import datetime
import locale
import re
from bs4 import BeautifulSoup
from multiprocessing import Pool

# replace below 4 variables to scrape any desired product on ebay
cleanURL = 'https://www.ebay.com/sch/i.html?_from=R40&_nkw=iphone+xs+max+&_sacat=0&LH_Sold=1&LH_Complete=1&_udlo=200&_ipg=200&_pgn='
pn = 'iphone xs max'
condition = 'used'
pages_available = 10

def scrape_page(URL):
    # variables for storing/cleaning data for mysql queries
    headers = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0'}
    page = requests.get(URL, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    dateResults =[]
    names = []
    cleanName = []
    priceResults = []
    period_deleted = []
    clean_price = []
    shipping = []
    today = datetime.date.today()
    tupleList = []
    save_number = 1


    # finds all prices on the page and strips html tags
    for price in soup.findAll("span", {"class": "POSITIVE"}):
        priceResults.append(price.get_text(strip=True))
    
    # finds all dates sold 
    for date in soup.findAll("span", {"s-item__ended-date s-item__endedDate"}):
        dateResults.append(date.get_text(strip=True))

    # finds all product titles
    for title in soup.findAll("h3", {"class": "s-item__title s-item__title--has-tags"}):
        names.append(title.get_text(strip=True))

    # remove false data 
    for i in priceResults:
        if 'to' in priceResults:
            priceResults.remove('to')
    for i in priceResults:
        if '$0.00' in priceResults:
            priceResults.remove('$0.00')

    # preps price for converting string to float
    for dollar_sign in priceResults:
        clean_price.append(dollar_sign[1:])

    # mysql database connection
    mydb = mysql.connector.connect(
        host = 'localhost',
        user = 'root',
        passwd = '',
        database = 'ebay_scraper'
    )
    mycursor = mydb.cursor()

    # insert into product table
    query = "INSERT IGNORE INTO products (product_name) SELECT * FROM (SELECT" +"'"+ pn +"'"+ ") AS p WHERE NOT EXISTS (select * from products where product_name =" +"'"+ pn +"'"+ ") limit 1;"
    mycursor.execute(query)
    mydb.commit()
    print('New product saved')
    print ('-')

    # pull primary_id from product table using product_name as unique key 
    query_template = """SELECT product_id FROM ebay_scraper.products WHERE product_name = '<REPLACE>'""" 
    query = (query_template.replace('<REPLACE>', pn))
    mycursor.execute(query)
    primary_key = mycursor.fetchone()
    clean_key = (primary_key[0])

    # insert into scrape_data table 
    scrape_query = "INSERT INTO scrape_data (scrape_date, product_name, product_id) VALUES (%s, %s, %s)"
    mycursor.execute(scrape_query, (today, pn, clean_key,))
    mydb.commit()
    print('scrape_data entry saved')
    print ('-')

    # pull scrape_id from database for use in product_data table
    scrape_pull = """SELECT scrape_id FROM scrape_data WHERE product_id = '<REPLACE>' ORDER BY scrape_id DESC LIMIT 1""" 
    scrape_pull_query = (scrape_pull.replace('<REPLACE>', str(clean_key)))
    mycursor.execute(scrape_pull_query)
    scrape_primary_key = mycursor.fetchall()
    scrape_key = (scrape_primary_key[0])
    clean_scrape = scrape_key[0]

    # creates tuple list for use in product_data querie, 1 tuple = 1 r ow in product_data table 
    for name, date, price in zip(names, dateResults, clean_price):
        tupleList.append(tuple([name, clean_key, condition, date, price, str(clean_scrape)],))

    # inserts data into product_data table, 1 querie for each row 
    for product_data in tupleList:
        mycursor = mydb.cursor()
        sqlFormula = "INSERT INTO product_data (product_title, product_id, cond, date_sold, price_sold, scrape_id) VALUES (%s, %s, %s, %s, %s, %s)"
        mycursor.execute(sqlFormula, product_data)
        mydb.commit()
        count_query = 'SELECT COUNT(*) FROM product_data WHERE product_id = ' + str(clean_key)
        mycursor.execute(count_query)
        data_count = str(mycursor.fetchall())
        for count in re.findall(r'\d{1,25}', data_count):
            print(str(count) + ' new products saved to product_data table')
        
   
if __name__=='__main__':
    url_list = []
    # creates list of urls based of number of pages of data available
    for pages_unscraped in range(int(pages_available)+1):
        URL = cleanURL + str(pages_unscraped) + '&rt=nc'
        if (pages_unscraped > 0):
            url_list.append(URL)
    # calls the scrape_page function on every URL in the url_list with multiprocessing
    # the script will run scrape_page on 10 url's simultaneously
    # rather than running the function on one url at a time
    p = Pool(10)
    p.map(scrape_page, url_list)
    p.terminate()
    p.join()