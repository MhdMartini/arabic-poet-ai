from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import json
import os

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


def scrape_poems_classes(poet_soup: BeautifulSoup):
    """
    iven a poet BeautifulSoup object, poems classes.
    """
    return poet_soup.find_all('a', class_="float-right")


class AldiwanScraper:
    def __init__(self, json_path: str = 'poets.json'):
        self.base_url = 'https://www.aldiwan.net/'
        self.json_path = json_path
        self.poets = self.get_poets()

    def get_poets(self):
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
        poems_classes = scrape_poems_classes(poet_soup)
        for poem_class in tqdm(poems_classes):
            poem_dict = {}

            # get poem soup
            poem_url = os.path.join(self.base_url, poem_class.get('href'))
            poem_soup = soup_from_url(poem_url)

            # store poem fields
            poem_title = poem_class.text.strip()
            poem_dict['title'] = poem_title
            poem_dict['source'] = poem_url
            poem_dict['author'] = poet_name
            poem_dict['text'] = scrape_poem_text(poem_soup)

            self.poets[poet_name]['poems'][poem_title] = poem_dict
        return self.poets[poet_name]

    def to_json(self):
        """
        Save poets as a json file.
        """
        with open('poets.json', 'w') as f:
            json.dump(self.poets, f, indent=4)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('--url', type=str, help='poet url in Aldiwan')
    parser.add_argument('--output', type=str,
                        default='output.json', help='output file')

    args = parser.parse_args()
