#Import Dependencies
import pandas as pd
import requests
import pymongo
from bs4 import BeautifulSoup
from splinter import Browser

def scrape():
    data = {}
    
    #Scrape News Data
    news = 'https://mars.nasa.gov/news/'
    response = requests.get(news)
    news_soup = BeautifulSoup(response.text, 'lxml')
    title = news_soup.find('div', class_= 'content_title')
    news_title = title.a.text.strip()
    p = news_soup.find('div', class_= 'rollover_description_inner')
    news_p = p.text.strip()
    data['news_title'] = news_title
    data['news_text'] = news_p
    
    #Scrape Image Data
    img = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    browser = Browser('chrome', **executable_path, headless=False)
    browser.visit(img)
    browser.links.find_by_partial_text('FULL IMAGE').click()
    browser.links.find_by_partial_text('more info').click()
    featured_img_url = browser.find_by_css('.main_image').first['src']
    data['image_url'] = featured_img_url

    # Scrape Twitter Data
    tweets = 'https://twitter.com/marswxreport?lang=en'
    response = requests.get(tweets)
    tweet_soup = BeautifulSoup(response.text, 'lxml')
    t = tweet_soup.find_all('p', class_ = 'TweetTextSize TweetTextSize--normal js-tweet-text tweet-text')
    for i in t:
        if 'InSight' in i.text:
            i.a.decompose()
            data['tweet'] = i.text
            break
    
    # Scrape Facts Data
    facts = 'https://space-facts.com/mars/'
    facts_html = pd.read_html(facts)
    facts_df = facts_html[0]
    facts_df.columns = ['Description', 'Data']
    facts_df.set_index('Description', inplace=True)
    html_table = facts_df.to_html()
    html_table = html_table.replace('\n', '')
    data['table_html'] = html_table

    # Scrape Hemisphere Data
    hemis = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    browser = Browser('chrome', **executable_path, headless=False)
    browser.visit(hemis)

    for i in range(4):
        link = browser.links.find_by_partial_text('Hemisphere')[i]
        link.click()
        title = browser.find_by_css('.title').first.text
        url = browser.find_by_text('Sample').first['href']
        data[title] = url
        browser.back()
        
    return data