import requests as r
from bs4 import BeautifulSoup

#URL
url = https://www.pro-football-reference.com/

# Fetching page
res = r.get(url)
res.raise_for_status() #if request fails

#parsing
soup = BeautifulSoup(res.text)
