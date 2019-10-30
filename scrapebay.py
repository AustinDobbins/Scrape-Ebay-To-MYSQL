#scrapes ebay sold pages and inserts data for each product sold into a three table mysql database.
import requests
import mysql.connector
import datetime
import locale
import re
from bs4 import BeautifulSoup

#print statements to request necessary details to perform scrape
cleanURL = input("What is the Ebay URL? ")
pn = input("What is the product name? ")
condition = input("Is the product used or new? ").lower()
pages_available = input('How many pages of data do you want? ')

def scrape_page():
    #variables for storing/cleaning data for mysql queries
    URL = cleanURL + str(pages_unscraped)
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

    #finds all prices on the page and strips html tags
    for price in soup.findAll("span", {"class": "POSITIVE"}):
        priceResults.append(price.get_text(strip=True))
    
    #finds all dates sold 
    for date in soup.findAll("span", {"s-item__ended-date s-item__endedDate"}):
        dateResults.append(date.get_text(strip=True))

    #finds all product titles
    for title in soup.findAll("h3", {"class": "s-item__title s-item__title--has-tags"}):
        names.append(title.get_text(strip=True))

    #remove false data 
    for i in priceResults:
        if 'to' in priceResults:
            priceResults.remove('to')
    for i in priceResults:
        if '$0.00' in priceResults:
            priceResults.remove('$0.00')

    #preps price for converting string to float
    for dollar_sign in priceResults:
        clean_price.append(dollar_sign[1:])

    #mysql database connection
    mydb = mysql.connector.connect(
        host = 'localhost',
        user = 'root',
        passwd = '',
        database = 'ebay_scraper'
    )
    mycursor = mydb.cursor()

    #insert into product table
    if URL == cleanURL + '1':
        query = 'DELETE FROM products WHERE product_name = ' + "'" + pn + "'"
        mycursor.execute(query)
        query = "INSERT INTO products (product_name) VALUES (%s)"
        mycursor.execute(query,(pn,))
        mydb.commit()
        print('New product saved')
        print ('-')

    #pull primary_id from product table using product_name as unique key 
    query_template = """SELECT product_id FROM ebay_scraper.products WHERE product_name = '<REPLACE>'""" 
    query = (query_template.replace('<REPLACE>', pn))
    mycursor.execute(query)
    primary_key = mycursor.fetchone()
    clean_key = (primary_key[0])

    #deletes old data for matching product name 
    if URL == cleanURL + '1':
        delete_old_data = 'DELETE FROM product_data WHERE product_id =' + str(clean_key)
        mycursor.execute(delete_old_data)
        print('Any old data associated with '+ pn + ' has been deleted.')
        print('-')

    #insert into scrape_data table 
    scrape_query = "INSERT INTO scrape_data (scrape_date, product_name, product_id) VALUES (%s, %s, %s)"
    mycursor.execute(scrape_query, (today, pn, clean_key,))
    mydb.commit()
    print('scrape_data entry saved')
    print ('-')

    #pull scrape_id from database for use in product_data table
    scrape_pull = """SELECT scrape_id FROM scrape_data WHERE product_id = '<REPLACE>' ORDER BY scrape_id DESC LIMIT 1""" 
    scrape_pull_query = (scrape_pull.replace('<REPLACE>', str(clean_key)))
    mycursor.execute(scrape_pull_query)
    scrape_primary_key = mycursor.fetchall()
    scrape_key = (scrape_primary_key[0])
    clean_scrape = scrape_key[0]

    #creates tuple list for use in product_data querie, 1 tuple = 1 row in product_data table 
    for name, date, price in zip(names, dateResults, clean_price):
        tupleList.append(tuple([name, clean_key, condition, date, price, str(clean_scrape)],))

    #inserts data into product_data table, 1 querie for each row 
    for product_data in tupleList:
        mycursor = mydb.cursor()
        sqlFormula = "INSERT INTO product_data (product_title, product_id, cond, date_sold, price_sold, scrape_id) VALUES (%s, %s, %s, %s, %s, %s)"
        mycursor.execute(sqlFormula, product_data)
        mydb.commit()
        print('New product_data entry saved')
        print ('-')
        
#calls the script to be ran once for every page that ebay has data for (as specified by user through input statement)         
for pages_unscraped in range(int(pages_available)+1):
    if (pages_unscraped > 0):
        scrape_page()