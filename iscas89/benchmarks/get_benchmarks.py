# Author: Arthur Nieh
# Date: 2025-04-20
# Description: get ISCAS89 benchmarks from the web
# URL: https://www.pld.ttu.ee/~maksim/benchmarks/iscas89/bench/

import requests
from bs4 import BeautifulSoup

url = "https://www.pld.ttu.ee/~maksim/benchmarks/iscas89/bench/"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")
links = []
for link in soup.find_all("a"):
    href = link.get("href")
    if href and href.endswith(".bench"):
        print(href)
        links.append(href)
for link in links:
    response = requests.get(url + link)
    with open(link, "wb") as f:
        f.write(response.content)
    print(f"Downloaded {link}")
# This script downloads all ISCAS89 benchmarks from the specified URL.
# It uses the requests library to fetch the HTML content of the page,