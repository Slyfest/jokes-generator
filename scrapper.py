import pandas as pd

from requests import get
from bs4 import BeautifulSoup
from tqdm import tnrange, tqdm


BASE_URL = 'http://www.allthejokes.com'

base_page = get(BASE_URL)
html_soup = BeautifulSoup(base_page.text, 'html.parser')

category_container = html_soup.find_all('div', id='content')[1]
categories = category_container.find_all('li')


def get_category_pages(category_url):
    main_page = get(category_url)
    category_soup = BeautifulSoup(main_page.text, 'html.parser')
    links_container = category_soup.find_all('div', id='content')[0]
    links = links_container.find_all('a')
    urls = []
    for link in links:
        if "media" not in link["href"]:
            urls.append(category_url + "/" + link["href"])
    try:
        urls.append("_".join(urls[0].split("_")[:2]) + "_1.html")
    except IndexError:
        urls.append(category_url + "/" + "_1.html")
    urls = sorted(set(urls))
    return urls


def scrape_page_jokes(page_url):
    page = get(page_url)
    page_soup = BeautifulSoup(page.text, 'html.parser')
    jokes_containers = page_soup.find_all('div', class_='joke')
    jokes = []
    for container in jokes_containers:
        joke = container.p.text
        jokes.append(joke.strip())
    return jokes


records = []
counter = 0
category_count = len(categories)
ids = [x["id"] for x in records]

for category in categories:
    short_title = " ".join(category.a["title"].split(" ")[:-1])
    print("Scrapping {} jokes...".format(short_title))
    category_url = category.a["href"]
    category_pages = get_category_pages(category_url)
    
    for i in tqdm(range(len(category_pages))):
        url = category_pages[i]
        jokes = scrape_page_jokes(url)
        for joke in jokes:
            counter += 1
            records.append(dict(
                category=category.a["title"],
                id=counter,
                text=joke
            ))
    category_count -= 1
    print("Processed {} jokes".format(short_title))
    print("{} categories left".format(category_count))
    

print("Successfully scraped all jokes. Writing to file...")
jokes_df = pd.DataFrame.from_records(records)
jokes_df.to_csv("data/jokes.csv")
print("Jokes are saved into data/jokes.csv")
