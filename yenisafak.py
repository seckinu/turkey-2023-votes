import requests
import pandas as pd
from bs4 import BeautifulSoup
from unidecode import unidecode

city_meta = 'https://raw.githubusercontent.com/oztalha/2015-11-01-Elections-Turkey/master/data/city_meta.csv'
# Cities w/ Turkish characters
cities = pd.read_csv(city_meta, usecols=['il']).il

results = {}
for c in cities:
    print(c)

    url = 'https://www.yenisafak.com/secim-cumhurbaskanligi-2023/' + \
        unidecode(c).lower() + '-ili-secim-sonuclari'
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    resource = requests.get(url, headers=headers)
    soup = BeautifulSoup(resource.content.decode(
        'utf-8', 'ignore'), "html5lib")

    # kill all script, style, sub, sup and b elements
    for script in soup(["script", "style", "sup", "sub", "b"]):
        script.extract()    # rip it out

    towns = soup.find(
        class_='table-scroll').find_all(class_='table-data')[0].find_all('span')

    results[c] = {}
    period = 7
    for t in range(period+1, len(towns), period):
        results[c][towns[t].text] = [
            float(i.text.strip().replace(',', '.')) for i in towns[t+1:t+period-1]]

cb = pd.DataFrame({(city, town): result for city, towns in results.items() for town, result in towns.items()},
                  index=('opened', 'RTE', 'MI', 'KK', 'SO')).T
cb.index.names = ('city', 'town')
cb.to_csv('cb-ilce-sonuclari.csv')
