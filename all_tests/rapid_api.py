import requests

if __name__ == '__main__':
    url = "https://bloomberg-market-and-financial-news.p.rapidapi.com/market/auto-complete"

    querystring = {"query":"<REQUIRED>"}

    headers = {
        "X-RapidAPI-Key": "695e2f31b8mshb75b0634161d5fbp177372jsn2e92a9a1ac13",
        "X-RapidAPI-Host": "bloomberg-market-and-financial-news.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    print(response.text)