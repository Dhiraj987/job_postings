from scrapers import indeed_scraper
from scrapers import linkedIn_scraper
import sys

def run():
    while True:
        try:
            print('\n')
            job = input("\tEnter the job: ")
            location = input("\tEnter the location: ")
            scrap = input('\n\n\t\tYou want to parse from? \n\tLinkedIn \t\tIndeed \t\tBoth\n\t\t Enter: ')
            if  'both' in scrap.lower():
                print("\n\n\tWorking with Indeed scraper\n")
                indeed_scraper.run(job, location)
                print("\n\n\tWorking with LinkedIn scraper")
                linkedIn_scraper.run(job, location)
            elif 'linkedin' in scrap.lower():
                print("\n\n\tWorking with LinkedIn scraper")
                linkedIn_scraper.run(job, location)
            elif 'indeed' in scrap.lower():
                print("\n\n\tWorking with Indeed scraper\n")
                indeed_scraper.run(job, location)


        except Exception:
            print("\n\nInvalid Entry; Try again")
            continue

if __name__ =='scrapers.for_both':
    run()
