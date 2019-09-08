#scrapes ebay sold pages and inserts data for each product sold into a three table mysql database.
import requests
import mysql.connector
import datetime
import locale
from bs4 import BeautifulSoup

#print statements to request necessary details to perform scrape
cleanURL = input("What is the Ebay URL? ")
p_name = input("What is the product name? ")
product_status = input("Is this product in your database yet? (Please enter yes or no)").lower()
condition = input("Is the product used or new? ").lower()
pages_available = input('How many pages of data does ebay have? ')

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
    for date in soup.findAll("div", {"class": "s-item__title--tag"}):
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

    #cleans name list 
    names.pop(0)

    #cleans dateResults
    dateResults = dateResults[1:]

    #remove false data 
    for i in priceResults:
        if 'to' in priceResults:
            priceResults.remove('to')
    for i in priceResults:
        if '$0.00' in priceResults:
            priceResults.remove('$0.00')
    #preps for converting string to float
    for dollar_sign in priceResults:
        clean_price.append(dollar_sign[1:])

    #mysql database
    mydb = mysql.connector.connect(
        host = 'localhost',
        user = 'root',
        passwd = '',
        database = 'ebay_scraper'
    )
    mycursor = mydb.cursor()

    #insert into product table
    if 'no' in product_status and URL == cleanURL + '1':
        query = "INSERT INTO products (product_name) VALUES (%s)"
        mycursor.execute(query,(p_name,))
        mydb.commit()
        print('New product saved')
        print ('-')

    #pull primary_id from product table using product_name as unique key 
    query_template = """SELECT product_id FROM ebay_scraper.products WHERE product_name = '<REPLACE>'""" 
    pn = p_name
    query = (query_template.replace('<REPLACE>', pn))
    mycursor.execute(query)
    primary_key = mycursor.fetchone()
    clean_key = (primary_key[0])

    #insert into scrape_data table 
    scrape_query = "INSERT INTO scrape_data (scrape_date, product_name, product_id) VALUES (%s, %s, %s)"
    mycursor.execute(scrape_query, (today, p_name, clean_key,))
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

    #creates tuple list for use in product_data querie, 1 tuple = 1 row 
    for a, b, c in zip(names, dateResults, clean_price):
        tupleList.append(tuple([a, clean_key, condition, b, c, str(clean_scrape)],))

    #inserts data into product_data table, 1 querie for each row 
    for i in tupleList:
        mycursor = mydb.cursor()
        sqlFormula = "INSERT INTO product_data (product_title, product_id, cond, date_sold, price_sold, scrape_id) VALUES (%s, %s, %s, %s, %s, %s)"
        mycursor.execute(sqlFormula, i)
        mydb.commit()
        #save_number = save_number + 1
        print('product_data entry saved')
        print ('-')

#calls the script to be ran once for every page that ebay has data for (as specified by user through input statement)         
for pages_unscraped in range(int(pages_available)+1):
    if (pages_unscraped > 0):
        scrape_page()