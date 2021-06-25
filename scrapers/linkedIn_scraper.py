from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from class_defination.job_posting import job_posting_linkedIn
import datetime 
CHROME_DRIVER = './chromedriver'
FIREFOX_DRIVER = './geckodriver'
import time
import pandas as pd
import os
import re

def setup_driver(headless=True, driver_type=CHROME_DRIVER) -> webdriver:
    if 'chrome' in driver_type.lower():
        options = ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        if headless:
            options.add_argument('-headless')
        driver = webdriver.Chrome(executable_path=driver_type, chrome_options=options)
    else:
        options = FirefoxOptions()
        if headless:
            options.add_argument('-headless')
        driver = webdriver.Firefox(executable_path=driver_type, firefox_options=options)
    return driver




def filter_for_url(text):
    return text.replace(' ','%20').replace(',','%2C')
    

def get_exact_link(job = None, location = None):
    base_link = "https://www.linkedin.com/jobs/search?keywords="
    if job == None:
        url = 'https://www.linkedin.com/jobs/search?keywords=software%20Engineer%20Intern&location='
    else:
        url = base_link + filter_for_url(job)+'&location=' + filter_for_url(location)
    return url


def get_links(link):
    #basic function to parse the soup
    driver = setup_driver(driver_type=FIREFOX_DRIVER)
    driver.get(link)
    time.sleep(4)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    links = []
    containers = soup.find_all('a',{'class':'base-card__full-link'})
    for container in containers:
        links.append(container.get('href'))
    return links


def get_soups(links):
    driver = setup_driver(driver_type=FIREFOX_DRIVER)
    count = 1
    soups =[]
    for link in links:
        driver.get(link)
        time.sleep(3)
        soups.append(BeautifulSoup(driver.page_source, "html.parser"))
        print('parsing: ',count ,'/',len(links))
        count += 1
    driver.quit()
    print(f'We parsed {str(len(soups))} job postings')
    return soups


def parse_job_criteria_list(soup):
    try:
        job_seniority = soup.find_all('span',{'class':'description__job-criteria-text description__job-criteria-text--criteria'})[0].text.strip()
        job_type = soup.find_all('span',{'class':'description__job-criteria-text description__job-criteria-text--criteria'})[1].text.strip()
        job_function = soup.find_all('span',{'class':'description__job-criteria-text description__job-criteria-text--criteria'})[2].text.strip()
        job_industry = soup.find_all('span',{'class':'description__job-criteria-text description__job-criteria-text--criteria'})[3].text.strip()
    except:
        job_seniority, job_type, job_function, job_industry = None, None, None, None
    return job_seniority, job_type, job_function, job_industry
        
    
def parse_original_link(soup):
    try:
        link = soup.find('a',{'class':'apply-button apply-button--link top-card-layout__cta top-card-layout__cta--primary'}).get('href')
    except:
        link = soup.find('link',{'rel':'canonical'}).get('href')
    return link


def parse_posted_date(soup):
    try:
        date = soup.find('span',{'class':'posted-time-ago__text topcard__flavor--metadata'}).text.strip()
    except:
        date = None
    return date


def parse_job_company(soup):
    try:
        company = soup.find('a',{'class':'topcard__org-name-link topcard__flavor--black-link'}).text.strip()
    except:
        company = None
    return company


def parse_job_loaction(soup):
    try:
        location = soup.find('span',{'class':'topcard__flavor topcard__flavor--bullet'}).text.strip()
    except:
        location = None
    return location


def run():
    job = 'Software Enginner Intern'
    location = 'New York, NY'
    main_url = get_exact_link(job, location)
    links = get_links(main_url)
    soups = get_soups(links)
    df = pd.DataFrame()
    counter = 1
    for soup in soups:
        if soup.find('link',{'rel':'canonical'}):
            job_title = soup.find('h1',{'class':'top-card-layout__title topcard__title'})
            counter += 1
            if job_title is not None:
                job = job_posting_linkedIn()
                job.job_title = job_title.text
                job.linkedIn_link = soup.find('link',{'rel':'canonical'}).get('href')
                job.original_link = parse_original_link(soup)
                job.posted_date = parse_posted_date(soup)
                job.company = parse_job_company(soup)
                job.job_location = parse_job_loaction(soup)
                job.seniority_level, job.employment_type, job.job_function, job.industries = parse_job_criteria_list(soup)
                df = df.append(job.__dict__, ignore_index = True)
                
            else:
                print('Job posting number ', counter ,"doesn't seem to have all info, so we discarded it" )
    if df.empty:
        print('Something went wrong!')    
    else:    
        df = df [['company', 'job_title',  'job_location', 'original_link', 'posted_date',  'employment_type', 'industries', 'job_function', 'linkedIn_link',  'seniority_level']]
        todays_date = f'{datetime.datetime.now():%d-%m-%Y-%H-%M}'
        csv_filename = "linkedIn-" + str(todays_date) +".csv"
        df.to_csv(os.path.expanduser(f'~/Downloads/{csv_filename}'))
        print('A csv file with ',len(df),' rows, named ', csv_filename ,' is created in your Downloads folder')
    