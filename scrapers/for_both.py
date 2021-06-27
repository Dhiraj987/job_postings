from scrapers import indeed_scraper 
from scrapers import linkedIn_scraper

def run():
    print('\n')
    job = input("\tEnter the job: ")
    location = input("\tEnter the location: ")
    print("\n\tWorking with Indeed scraper\n")
    indeed_scraper.run(job, location)
    print("\n\tWorking with LinkedIn scraper")
    linkedIn_scraper.run(job, location)