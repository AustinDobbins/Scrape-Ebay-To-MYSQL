CREATE DATABASE IF NOT EXISTS ebay_scraper;

CREATE TABLE ebay_scraper.products (
   product_id INT NOT NULL AUTO_INCREMENT,
   product_name VARCHAR(255) NOT NULL,
   PRIMARY KEY (product_id),
   UNIQUE KEY (product_name)
);

CREATE TABLE ebay_scraper.scrape_data (
    scrape_id INT NOT NULL AUTO_INCREMENT,
    scrape_date VARCHAR(100),
    product_name VARCHAR(255) NOT NULL,
    product_id INT NOT NULL,
    FOREIGN KEY (product_id)
        REFERENCES ebay_scraper.products (product_id)
        ON DELETE CASCADE,
    PRIMARY KEY (scrape_id)
);

CREATE TABLE ebay_scraper.product_data (
    data_id INT NOT NULL AUTO_INCREMENT,
    product_title VARCHAR(255),
    product_id INT NOT NULL,
    cond VARCHAR(10),
    date_sold VARCHAR(100),
    price_sold VARCHAR(150),
    scrape_id INT NOT NULL,
    PRIMARY KEY (data_id),
    FOREIGN KEY (product_id)
        REFERENCES ebay_scraper.products (product_id)
        ON DELETE CASCADE,
    FOREIGN KEY (scrape_id)
        REFERENCES ebay_scraper.scrape_data (scrape_id)
        ON DELETE CASCADE
);