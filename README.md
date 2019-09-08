# Scrape-Ebay-To-MYSQL

I wanted to make this script as easy to use, for anyone with near zero knowledge about programming.

Once you have MYSQL Workbench 8 installed and your Python dependencies installed correctly, it is as simple as the steps below describe it.

Step 1. Run create_database.sql in Workbench
Step 2. Run create_tables.sql in Workbench
Step 3. Copy the ebay link and add "&_ipg=200&_pgn=" to the end of the URL
Step 4. Run scrapebay.py and answer the 4 questions as prompted in the shell window *make sure to use no spaces and everything is typed correct*

The script will go through every sold page as specified and save the data for every single product sold that ebay still shows data for. 

Able to process inifinite amount of SQL queries (only limited by data available) with just one Python script. 
Only limited by how much data ebay has.
