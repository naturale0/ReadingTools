import requests
from bs4 import BeautifulSoup

def get_redirect_url(apple_news_url):
    resp = requests.get(apple_news_url)
    soup = BeautifulSoup(resp.text, 'html5lib')
    redirect_url = soup.find_all('a', href=True)[0]["href"]
    return redirect_url

