from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from class_defination.job_posting import job_posting_indeed
import datetime 
CHROME_DRIVER = './chromedriver'
import time
import pandas as pd
import os
import re

def setup_driver(headless=True, driver_type=CHROME_DRIVER) -> webdriver:
    options = ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    if headless:
        options.add_argument('-headless')
    driver = webdriver.Chrome(executable_path=driver_type, chrome_options=options)
    return driver


def get_soup(link):
    #basic function to parse the soup
    driver = setup_driver()
    driver.get(link)
    time.sleep(4)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    executing_query = "document.getElementsByClassName('popover-x-button-close icl-CloseButton')[0].click()"
    #in case a pop up appears, it closes it
    if soup.find('div',{'id':'popover-form-container'}):
        driver.execute_script(executing_query)
        soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()
    return soup


def parse_all_pages(page):
    #from the first page, it gets the links to all other pages..
    page_links = []
    container = page.find('ul',{'class':'pagination-list'})
    if container is not None:
        blocks = container.find_all('li')
        for block in blocks:
            if block.find('a', href = True):
                incomplete_link = block.find('a')['href']
                page_links.append('https://www.indeed.com'+incomplete_link)
    else:
        return "we don't have a posting"
    pages = []
    #stores the soup of all the pages
    pages.append(page)
    #appends the soup for the first page before getting into the loop
    print("parsing page no.: 1")
    i = 2
    for link in set(page_links):
        print('parsing page no.:', i)
        pages.append(get_soup(link))
        i += 1
        #loops with all the links to other pages and stores their soups..
    return pages


def get_all_soups(pages):
    soups = []
    #stores the soups to each job postings, the soup from their specific 
    links_to_postings = []
    #stores all the links to the specific job postings
    for page in pages:
        method_1 = page.find('div',{'class':'mosaic mosaic-provider-jobcards mosaic-provider-hydrated'})
        method_2 = page.find('div',{'class':'jobsearch-SerpJobCard unifiedRow row result clickcard'})
        #this takes care of the two different classes used in the html pages
        if method_1:
            container = method_1
            boxes = container.find_all('a', href = True)
        elif method_2:
            container = method_2
            boxes = container.find_all('a', href = True)
        else:
            return "we don't have the job postings"
            # quits the method if the links are not found.
            
        if boxes: #proceeds only if links to different postings exists
            for box in boxes:
                first = box['href']
                if '/rc/clk?jk' in first:
                    link = first.replace('/rc/clk?','https://www.indeed.com/viewjob?')
                    links_to_postings.append(link)
                    #append all the links to the list
    count = 1
    for link in set(links_to_postings):
        soups.append(get_soup(link))
        #get soups for unique job links parsed from different websites
        print('parsing job posting: ',count,'/', len(set(links_to_postings)))
        count += 1
    print(f'we got {len(soups)} job postings')
    return soups


def parse_job_title(soup):
    title = 'N/A'
    title_text = soup.find('h1',{'class':'icl-u-xs-mb--xs icl-u-xs-mt--none jobsearch-JobInfoHeader-title'})
    if title_text:
        title = title_text.text.title()
    return title    
    
    
def parse_link(soup):
    link = 'N/A'
    link_text = soup.find('div',{'id':'originalJobLinkContainer'})
    if link_text:
        link = link_text.find('a')['href']
    return link
        
        
def parse_company_name(soup):
    name = 'unknown'
    text = soup.find('div',{'class':'jobsearch-InlineCompanyRating icl-u-xs-mt--xs jobsearch-DesktopStickyContainer-companyrating'})
    if text:
        name = re.sub('[0-9]','',text.text)
    final = name.replace('reviews','').replace(',','').title()
    return final


def parse_working_time(soup):
    soup_text = soup.text.lower()
    if 'full time' in soup_text or 'full-time' in soup_text:
        full_time = True
    elif 'part time' in soup_text or 'part-time' in soup_text:
        full_time = False
    else:
        full_time = 'N/A'
    return full_time
    
    
def parse_job_location(soup):
    is_remote = 'N/A'
    final = 'N/A'
    entire_text = soup.find('div',{'class':'icl-u-xs-mt--xs icl-u-textColor--secondary jobsearch-JobInfoHeader-subtitle jobsearch-DesktopStickyContainer-subtitle'})
    if entire_text:
        company_name = soup.find('div',{'class':'jobsearch-InlineCompanyRating icl-u-xs-mt--xs jobsearch-DesktopStickyContainer-companyrating'}).text
        final = entire_text.text.replace(company_name, '')
    if 'remote' in final.lower():
        final = final.lower().split('remote')[0].title()
        is_remote = True
    if final == '':
        final = 'Remote'
    return final , is_remote
    

def filter_for_url(text):
    return text.replace(' ','+').replace(',','')
    

def get_exact_link(job, location):
    if job == None:
        url = 'https://www.indeed.com/jobs?q=software+engineer&l='
    else:
        url = 'https://www.indeed.com/jobs?q=' + filter_for_url(job)+'&l=' + filter_for_url(location)
    return url


def run(job = None, location=None):
    url = get_exact_link(job, location)
    print("The website being parsed is : ", url, '\n')
    page = get_soup(url)
    pages = parse_all_pages(page)
    soups = get_all_soups(pages)
    df = pd.DataFrame()
    for soup in soups:
        job = job_posting_indeed()
        job.job_title = parse_job_title(soup)
        job.original_link = parse_link(soup)
        job.company = parse_company_name(soup)
        job.is_full_time = parse_working_time(soup)
        job.job_location, job.is_remote = parse_job_location(soup)
        df = df.append(job.__dict__, ignore_index=True)

    if df.empty:
        print("Something went wrong")
    else:
        df = df[['company', 'job_title', 'job_location', 'original_link', 'is_full_time','is_remote']]
        todays_date = f'{datetime.datetime.now():%d-%m-%Y-%H-%M}'
        csv_filename = "indeed-" + str(todays_date) +".csv"
        df.to_csv(os.path.expanduser(f'~/Downloads/{csv_filename}'))
        print('\nA csv file with ',len(df),' rows, named ', csv_filename ,' is created in your Downloads folder')
    
    