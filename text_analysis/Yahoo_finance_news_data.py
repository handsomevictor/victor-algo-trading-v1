import requests
from bs4 import BeautifulSoup
from lxml import html

if __name__ == '__main__':
    url = 'https://finance.yahoo.com/news/'

    headers = {
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    # save content to txt
    with open('yahoo.txt', 'w', encoding='utf-8') as f:
        f.write(response.text)
    # print(response.content)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the title by searching for the exact text match
        title_element = soup.find_all(lambda
                                          tag: tag.name == 'a'in tag.get_text())

        if title_element:
            for i in range(len(title_element)):
                print(title_element[i].get_text())
        else:
            print("Title not found on the page")

        # with open('cnbc.txt', 'w', encoding='utf-8') as f:
        #     for title in card_titles:
        #         f.write(title.get_text() + '\n')
    else:
        print(f"Error: Unable to fetch the page (status code: {response.status_code})")

