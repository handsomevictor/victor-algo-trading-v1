"""Try: CNBC Business News 首页的新闻title爬虫"""

import requests
from bs4 import BeautifulSoup

if __name__ == '__main__':
    url = 'https://www.cnbc.com/business/'
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        card_titles = soup.find_all(class_='Card-title')

        with open('cnbc.txt', 'w', encoding='utf-8') as f:
            for title in card_titles:
                f.write(title.get_text() + '\n')
    else:
        print(f"Error: Unable to fetch the page (status code: {response.status_code})")


