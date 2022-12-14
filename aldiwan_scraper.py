from dataclasses import dataclass
import enum
from itertools import count
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import json
import os
import concurrent.futures

"""
Given a poet page url, scrape all poems from the page into poems dictionary/json.

example output:
{poet 1: { 
            born: int or None,
            died: int or None,
            first: str or None,
            last: str or None,
            poems: {poem 1: {poem 1 fields}, poem 2: {poem 2 fields}, ...}},
.
.
.
}
"""


def soup_from_url(url: str):
    """
    Given a url, return a BeautifulSoup object.
    """
    response = requests.get(url)
    if not response.status_code == 200:
        raise Exception('Could not get response from url: ' + url)
    return BeautifulSoup(response.text, 'html.parser')


def scrape_poet_name(poet_soup: BeautifulSoup):
    """
    Given a poet BeautifulSoup object, return the author's name.
    """
    return poet_soup.find('h2').text.strip().split('\n')[-1]


def scrape_poem_text(poem_soup: BeautifulSoup):
    """
    Given a poem BeautifulSoup object, return the poem text.
    """
    try:
        # شعر حديث
        return poem_soup.find_all(id='poem_content')[0].find_all('h4')[0].text
    except IndexError:
        pass

    # شعر قديم
    text = ""
    for i, line in enumerate(poem_soup.find_all(id='poem_content')[0].find_all('h3')):
        text += line.text.strip()
        if not i % 2:
            text += '\t'
        else:
            text += '\n'
    return text


def scrape_poems_tags(poet_soup: BeautifulSoup):
    """
    iven a poet BeautifulSoup object, poems classes.
    """
    return poet_soup.find_all('a', class_="float-right")


def scrape_poets_tags(poets_soup: BeautifulSoup):
    """
    iven a poet BeautifulSoup object, poems classes.
    """
    return poets_soup.find_all('a')


class AldiwanScraper:
    def __init__(self, json_path: str = 'poets.json'):
        self.base_url = 'https://www.aldiwan.net/'
        self.json_path = json_path
        self.poets = self.from_json()

    def from_json(self):
        """
        Get poets from a json file if any
        """
        if not os.path.exists(self.json_path):
            return {}
        with open(self.json_path) as f:
            return json.load(f)

    def scrape_poems(self, url: str = None):
        poet_soup = soup_from_url(url)

        # get poet name
        poet_name = scrape_poet_name(poet_soup)

        # check if poet already exists
        if poet_name in self.poets:
            return self.poets[poet_name]

        self.poets[poet_name] = {'name': poet_name, 'poems': {}}

        # scrape poet's poems
        poems_tags = scrape_poems_tags(poet_soup)
        for poem_tag in tqdm(poems_tags):
            self.scrape_poem(poem_tag, poet_name)

        return self.poets[poet_name]

    def scrape_poem(self, poem_tag, poet_name: str):
        # get poem soup
        poem_url = os.path.join(self.base_url, poem_tag.get('href'))
        poem_soup = soup_from_url(poem_url)

        # store poem fields
        poem_dict = {}
        poem_title = poem_tag.text.strip()
        poem_dict['title'] = poem_title
        poem_dict['source'] = poem_url
        poem_dict['author'] = poet_name
        poem_dict['text'] = scrape_poem_text(poem_soup)
        poem_dict['language'] = 'arabic'
        self.poets[poet_name]['poems'][poem_title] = poem_dict

    def get_poets_urls(self):
        """
        Get all poets urls.
        """
        poets_urls = set()
        poets_url = "https://www.aldiwan.net/authers-1?page={}"
        for i in count(start=1):
            url = poets_url.format(i)
            try:
                soup = soup_from_url(url)
            except Exception as e:
                print("Done!")
                break
            duplicate_with_garbage = soup.find_all('a', href=True)
            for tag in duplicate_with_garbage:
                if tag.get('href').startswith('cat-poet'):
                    poets_urls.add(os.path.join(
                        self.base_url, tag.get('href')))
                    print(".", end="")
        return list(poets_urls)

    def to_json(self):
        """
        Save poets as a json file.
        """
        with open(self.json_path, 'w') as f:
            json.dump(self.poets, f, indent=4)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('--urls', type=str, nargs="+", default=None,
                        help='poets urls in Aldiwan. If none is provided, the whole website is scraped', required=True)
    parser.add_argument('--output', type=str,
                        default='poets.json', help='output/input json file')

    args = parser.parse_args()

    scraper = AldiwanScraper(args.output)
    urls = args.urls if args.urls is not None else scraper.get_poets_urls()
    len_urls = len(urls)
    for i, url in enumerate(urls, start=1):
        print(f"[{i}/{len_urls}]")
        scraper.scrape_poems(url)
    scraper.to_json()
