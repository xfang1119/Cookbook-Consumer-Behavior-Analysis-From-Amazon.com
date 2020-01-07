# @shellysolomonwang

import requests
from bs4 import BeautifulSoup  
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time



def book_scraper():
    executable_path = './shelly/geckodriver'
    page_url="https://www.amazon.com/s?i=stripbooks&rh=n%3A283155%2Cn%3A1000%2Cn%3A6&s=review-count-rank&qid=1570740809&ref=sr_pg_1"
    driver = webdriver.Firefox(executable_path=executable_path)
    driver.implicitly_wait(5) 
    driver.get(page_url)
    
    total_pages = driver.find_element_by_xpath(
        "//*[@id='search']/div[1]/div[2]/div/span[7]/div/span/div/div/ul/li[6]").text
    total_pages = int(total_pages)
    data = []
    error = []
   
    for n_page in range(total_pages):
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        bookslist = soup.select('#search > div.sg-row > div.sg-col-20-of-24.sg-col-28-of-32.sg-col-16-of-20.sg-col.s-right-column.sg-col-32-of-36.sg-col-8-of-12.sg-col-12-of-16.sg-col-24-of-28 > div > span:nth-child(4) > div.s-result-list.s-search-results.sg-row>div')
        
        for idx, x in enumerate(bookslist):
            
            if idx == 16:
                break
            # 1. click the title of one book and scrape
            # this link is for click
            wait = WebDriverWait(driver, 10)
            try:
                xpath = '//*[@id="search"]/div[1]/div[2]/div/span[3]/div[1]/div['+str(idx+1)+']/div/span/div/div/div[2]/div[2]/div/div[1]/div/div/div[1]/h2/a'
                element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                book_link = element.get_attribute("href")
                element.click()
            except:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                # sleep to allow content loaded
                time.sleep(10)
                xpath = '//*[@id="search"]/div[1]/div[2]/div/span[3]/div[1]/div['+str(idx+1)+']/div/span/div/div/div[2]/div[2]/div/div[1]/div/div/div[1]/h2/a'
                element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                book_link = element.get_attribute("href")
                element.click()

                # xpath = '//*[@id="search"]/div[1]/div[2]/div/span[3]/div[1]/div['+str(idx+1)+']/div/span/div/div/div[2]/div[2]/div/div[1]/div/div/div[1]/h2/a'
                # link = driver.find_element_by_xpath(xpath)
                # # this link is for storage
                # # 1
                
                # book_link = link.get_attribute("href")
                # #WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, xpath)))
                # link.click()

            # 2.1 scrape the details of the book
            # 2
            try:
                title = driver.find_element_by_xpath("//*[@id='ebooksProductTitle']").text
                
            except Exception as e:
                try:
                    title = driver.find_element_by_xpath('//*[@id="productTitle"]').text
                except Exception as e:
                    title = None
                    error.append( ("title", n_page, idx))
            # 3
            try:
                author = driver.find_element_by_xpath("//*[@id='bylineInfo']").text
            except Exception as e:
                author = None
                error.append( ("author", n_page, idx))
            # 4
            try:

                star = driver.find_element_by_xpath('//*[@id="acrPopover"]').get_attribute("title")
                star = float(star[:-15])
            except Exception as e:
                star = None
                error.append( ("star", n_page, idx))
            # 5
            try:
                review_amount = driver.find_element_by_xpath("//*[@id='acrCustomerReviewText']").text[:-8]
                review_amount = int(str(review_amount).replace(",", ""))
            except Exception as e:
                review_amount = None
                error.append( ("review_amount", n_page, idx))
            try:
                price = driver.find_element_by_xpath("//*[@id='tmmSwatches']/ul").text
                # 6
                try:
                    kindle_price = float(re.search("Kindle\n\$[0-9]+\.[0-9]+", price).group()[8:])
                except Exception as e:
                    kindle_price = None
                    error.append( ("kindle_price", n_page, idx))
                # 7
                try:
                    paperback_price = float(re.search("Paperback\n\$[0-9]+\.[0-9]+", price).group()[11:])
                except Exception as e:
                    paperback_price = None
                    error.append( ("paperback_price", n_page, idx))
                # 8
                try:
                    hardcover_price = float(re.search("Hardcover\n\$[0-9]+\.[0-9]+", price).group()[11:])
                except Exception as e:
                    hardcover_price = None
                error.append(("hardcover_price", n_page, idx))

            except:
                error.append(("price", n_page, idx))

                
            # 9
            try:
                time.sleep(3)
                ## You have to switch to the iframe like so: ##
                driver.switch_to.frame(driver.find_element_by_xpath('//*[@id="bookDesc_iframe"]'))
                ## Insert text via xpath ##
                intro = driver.find_element_by_xpath('/html/body/div').text
                ## Switch back to the "default content" (that is, out of the iframes) ##
                driver.switch_to.default_content()
            except Exception as e:
                intro = None
                error.append( ("kindle_price", n_page, idx))
            # 10
            try:
                sales_rank = driver.find_element_by_xpath('//*[@id="SalesRank"]').text
            except Exception as e:
                sales_rank = None
                error.append( ("sales_rank", n_page, idx))
            
            try:
                product_desc = driver.find_element_by_xpath('//*[@id="productDescription"]').text
            except Exception as e:
                product_desc = None
                error.append(("product_desc", n_page, idx))
            # 11
            try:
                abt_author = driver.find_element_by_xpath("//*[@id='authorBio']").text

            except Exception as e:

                try:
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    # sleep to allow content loaded
                    time.sleep(2)
                    abt_author = driver.find_element_by_xpath('//*[@id="books-entity-teaser"]').text
                except Exception as e:
                    abt_author = None
                    error.append( ("abt_author", n_page, idx))

            key_words = []
            
            try:
                key_words_css = driver.find_elements_by_css_selector("#cr-lighthut-1- > div > span")
                for i in range(len(key_words_css)):
                    key_word = key_words_css[i].find_element_by_css_selector("a > span").text
                    key_words.append(key_word)
            except Exception as e:
                key_words = None
                error.append( ("key_words", n_page, idx))
            
            data.append((book_link, title, author, star, review_amount, kindle_price, paperback_price, hardcover_price, intro, sales_rank, product_desc, abt_author, key_words))
            
            
            # 2.2 back to previous page
            driver.back()
        

        print(n_page+1, 'th page success!, error:', error[(n_page*16):((n_page+1)*16)])
        
            # click for next page
        if n_page < (total_pages - 1):

                next_link = 'https://www.amazon.com/s?i=stripbooks&rh=n%3A283155%2Cn%3A1000%2Cn%3A6&s=review-count-rank&page='+str(n_page+1)+'&qid=1572370250&ref=sr_pg_'+str(n_page+1)
                driver.get(next_link)
        else:
            driver.quit()
    
    return data, error

if __name__ == "__main__":
    data, error = book_scraper()
    book = pd.DataFrame(data, columns =["book_link", "title", "author", "star", "review_amount", "kindle_price", "paperback_price","hardcover_price", "intro", "sales_rank", "product_desc", "abt_author", "key_words"])
    book_error = pd.DataFrame(error, columns = ["error_item", 'page_num', 'book_num'])
    book.to_csv('Result/book.csv')
    book_error.to_csv('Result/book_error.csv')






