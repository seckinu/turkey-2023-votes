import requests
import pandas as pd
import time


# api has rate limiting so we use a custom get function to get around it
def get(url):
    res = requests.get(url, headers={
        "User-Agent": "Mozilla/5.0"
    })

    while res.status_code == 429 or res.status_code == 403:
        time.sleep(.5)
        res = requests.get(url, headers={
            "User-Agent": "Mozilla/5.0"
        })

    if res.status_code != 200:
        return None

    return res


cities = get(
    "https://api-sonuc.oyveotesi.org/api/v1/cities").json()
df = pd.DataFrame(columns=['city', 'town', 'opened', 'RTE', 'MI', 'KK', 'SO'])

for city in cities:
    # skip foreign votes
    if city["id"] == 82:
        continue

    cities = get(
        f"https://api-sonuc.oyveotesi.org/api/v1/cities/{city['id']}/districts").json()

    for district in cities:
        RTE = 0
        MI = 0
        KK = 0
        SO = 0

        nhoods = get(
            f"https://api-sonuc.oyveotesi.org/api/v1/cities/{city['id']}/districts/{district['id']}/neighborhoods").json()

        for nhood in nhoods:
            schools = get(
                f"https://api-sonuc.oyveotesi.org/api/v1/cities/{city['id']}/districts/{district['id']}/neighborhoods/{nhood['id']}/schools").json()

            for school in schools:
                x = get(
                    f"https://api-sonuc.oyveotesi.org/api/v1/submission/school/{school['id']}")
                if x == None:
                    continue

                x = x.json()

                for i in x:
                    print(i["school_name"], i["ballot_box_number"])
                    if i['cm_result'] is None:
                        continue
                    print(i["cm_result"]["votes"]
                          if i["cm_result"] else "NOT FOUND")

                    RTE += i['cm_result']['votes'].get('1', 0)
                    MI += i['cm_result']['votes'].get('2', 0)
                    KK += i['cm_result']['votes'].get('3', 0)
                    SO += i['cm_result']['votes'].get('4', 0)

        df.loc[len(df.index)] = [city['name'],
                                 district['name'], 100, RTE, MI, KK, SO]
print(df)
