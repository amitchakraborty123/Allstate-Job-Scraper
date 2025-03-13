'''
Author: Amit Chakraborty
Project: Allstate Job Scraper
Profile URL: https://github.com/amitchakraborty123
E-mail: mr.amitc55@gmail.com
'''

import time
import pandas as pd
from bs4 import BeautifulSoup
import os
import datetime
import warnings
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import requests

day_old = input("How many days old jobs do you want: ")
page_limit = input("How many pages jobs do you want: ")

before_date = (datetime.datetime.now() - datetime.timedelta(days=int(day_old)))
x = datetime.datetime.now()
n = x.strftime("__%b_%d_%Y")
warnings.filterwarnings("ignore")
from datetime import datetime


def driver_conn():
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument("--headless")      # Make the browser Headless. if you don't want to see the display on chrome just uncomment this
    chrome_options.add_argument("--log-level=3")    # Removes error/warning/info messages displayed on the console
    chrome_options.add_argument("--disable-infobars")  # Disable infobars ""Chrome is being controlled by automated test software"  Although is isn't supported by Chrome anymore
    chrome_options.add_argument("start-maximized")     # Make chrome window full screen
    chrome_options.add_argument('--disable-gpu')       # Disable gmaximizepu (not load pictures fully)
    # chrome_options.add_argument("--incognito")       # If you want to run browser as incognito mode then uncomment it
    chrome_options.add_argument("--disable-notifications")  # Disable notifications
    chrome_options.add_argument("--disable-extensions")     # Will disable developer mode extensions
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")    # retrieve_block
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])    # retrieve_block
    chrome_options.add_experimental_option('useAutomationExtension', False)    # retrieve_block
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36')    # retrieve_block
    chrome_options.add_argument('--accept=text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9')    # retrieve_block
    chrome_options.add_argument('--accept-encoding=gzip, deflate, br')    # retrieve_block
    chrome_options.add_argument('--accept-language=en-US,en;q=0.9')    # retrieve_block

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=chrome_options)  # you don't have to download chromedriver it will be downloaded by itself and will be saved in cache
    return driver


headers = {
    'Connection': 'keep-alive',
    'User-Agent': 'Chrome/102.0.5005.63 Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.5 (KHTML, like Gecko) Safari/536.5',
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate',
    'Content-Type': 'text',
    'Accept-Language': 'en-US,en;q=0.8'
}

def get_data():
    driver = driver_conn()
    links = []
    print('======================= Getting Data =======================')
    pag = 0
    while True:
        pag += 1
        print(">>>>>>>>>>>>>>>>>>>>>> Page: " + str(pag))
        driver.get('https://www.allstate.jobs/job-search-results/?pg=' + str(pag))
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, 'lxml')
        divs = soup.find('div', {'id': 'widget-jobsearch-results-list'}).find_all('div', {'class': 'jobTitle'})
        if len(divs) == 0:
            break
        print(f'Job listing: {len(divs)}')
        for div in divs:
            link = div.find('a')['href']
            links.append(link)
            df = pd.DataFrame(links)
            df.to_csv('links.csv')
        if pag >= int(page_limit):
            break
    driver.quit()
    df = pd.read_csv('links.csv')
    links = df['0'].values
    ll = 0
    for link in links:
        ll += 1
        print('Getting link ' + str(ll) + ' out of ' + str(len(links)))
        url = 'https://www.allstate.jobs' + link
        soup = BeautifulSoup(requests.get(url, headers=headers).content, 'lxml')
        id = ''
        title = ''
        category = ''
        job_desc = ''
        job_type = ''
        loc_city = ''
        loc_state = ''
        loc_country = ''

        try:
            date = soup.find('span', {'id': 'gtm-jobdetail-date'}).text
            post_date = datetime.strptime(str(date), '%B %d, %Y')

            if post_date > before_date:
                try:
                    id = soup.find('span', {'id': 'gtm-jobdetail-jobid'}).text.replace('Job # : ', '')
                except:
                    pass
                try:
                    title = soup.find('h1', {'id': 'gtm-jobdetail-title'}).text
                except:
                    pass
                try:
                    category = soup.find('span', {'id': 'gtm-jobdetail-category'}).text
                except:
                    pass
                try:
                    job_type = soup.find('span', {'id': 'gtm-jobdetail-locationtype'}).text
                except:
                    pass
                try:
                    job_desc = soup.find('div', {'id': 'tab-id-5-container'}).get_text()
                except:
                    pass
                try:
                    loc_city = soup.find('span', {'id': 'gtm-jobdetail-city'}).text.replace(',', '').strip()
                except:
                    pass
                try:
                    loc_state = soup.find('span', {'id': 'gtm-jobdetail-state'}).text.replace(',', '').strip()
                except:
                    pass
                try:
                    loc_country = soup.find('span', {'id': 'gtm-jobdetail-country'}).text.replace(',', '').strip()
                except:
                    pass

                data = {
                    'Link': url,
                    'Date': date,
                    'Job Id': id,
                    'Title': title,
                    'Category': category,
                    'Job Desc': job_desc,
                    'Job Type': job_type,
                    'Location City': loc_city,
                    'Location State': loc_state,
                    'Location Country': loc_country,
                }
                print(data)
                df = pd.DataFrame([data])
                df.to_csv('Final_Data_of_allstate' + n + '.csv', mode='a', header=not os.path.exists('data.csv'), encoding='utf-8-sig', index=False)
        except:
            pass
    print('===================== Final Data Saved =====================')


if __name__ == '__main__':
    get_data()
