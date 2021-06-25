from scrapers import indeed_scraper 
from scrapers import linkedIn_scraper

def run():
    print("working with Indeed scraper\n\n")
    indeed_scraper.run()
    print("\n\nworking with LinkedIn scraper")
    linkedIn_scraper.run()