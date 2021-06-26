from scrapers import indeed_scraper 
from scrapers import linkedIn_scraper

def run():
    print('\n')
    job = input("Enter the job: ")
    location = input("Enter the location: ")
    print("\n\tWorking with Indeed scraper")
    indeed_scraper.run(job, location)
    print("\n\tWorking with LinkedIn scraper")
    linkedIn_scraper.run(job, location)