from splinter import Browser
from bs4 import BeautifulSoup
import requests
import pandas
import time


def init_browser():
    executable_path = {"executable_path": "C:\Program Files\Chrome\chromedriver.exe"}
    return Browser("chrome", **executable_path, headless=False)


def scrape_info():
    browser = init_browser()

    # NASA Mars News
    response = requests.get('https://mars.nasa.gov/news/')
    n_soup = BeautifulSoup(response.text, 'lxml')
    news_title = n_soup.find('div',class_='content_title').text.strip()
    news_text = n_soup.find('div',class_='rollover_description_inner').text.strip()

    # JPL Mars Space Images - Featured Image
    browser.visit('https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars')
    time.sleep(1)
    browser.click_link_by_id('full_image')
    time.sleep(1)
    browser.find_link_by_partial_text('more info').click()
    images = browser.find_by_tag('img')
    featured_image_url = [image['src'] for image in images if image['class']=='main_image'][0]

    # Mars Weather
    response = requests.get('https://twitter.com/marswxreport?lang=en')
    w_soup = BeautifulSoup(response.text, 'lxml')
    w_soup = w_soup.find('div', {'class':'js-tweet-text-container'}).find('p')
    w_soup.a.decompose()
    weather = w_soup.text

    # Mars Facts
    tables = pandas.read_html('https://space-facts.com/mars/')
    df = tables[0]
    df.rename(columns={0:'parameter',1:'value'},inplace=True)
    facts_table = df.to_html(index=False, classes='table table-striped')

    # Mars Hemispheres
    browser.visit('https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars')
    time.sleep(1)
    headers = browser.find_by_css('div[class="description"] h3')
    titles = []
    for h in headers:
        titles.append(h.text)
    items = browser.find_by_css('div[class="description"] a')
    urls = []
    for i in items:
        urls.append(i['href'])
    img_urls = []
    for url in urls:
        browser.visit(url)
        browser.find_link_by_text('Open').click()
        images = browser.find_by_tag('img')
        img_url = [image['src'] for image in images if image['class']=='wide-image'][0]
        img_urls.append(img_url)
    hemispheres = []
    for title, img_url in zip(titles, img_urls):
        hemispheres.append({'title':title,'img_url':img_url})
    

    # Store data in a dictionary
    mars_data = {
        'news_title': news_title,
        'news_text': news_text,
        'featured_image_url': featured_image_url,
        'weather': weather,
        'facts_table': facts_table,
        'hemispheres': hemispheres
    }

    # Close the browser after scraping
    browser.quit()

    # Return results
    return mars_data
