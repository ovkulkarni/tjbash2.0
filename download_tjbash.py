import requests
from bs4 import BeautifulSoup
import csv
import re

with open('quotes.csv', 'w+') as f:
    writer = csv.writer(f)
    for i in range(1, 6007):
        r = requests.get("http://tjbash.org/{}.html".format(i))
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            body = soup.select(".quote-body")[0].get_text().strip().encode("utf8").replace("\n", "<br>")
            try:
                votes = int(soup.select(".quote-rating")[0].get_text().strip())
            except:
                votes = int(re.findall(r"\d+", soup.select(".quote-rating")[0].get_text().strip())[0]) * -1
            try:
                tags = [a.get_text().strip().encode("utf8") for a in soup.select(".quote-tags")[0].find_all("a")]
            except:
                tags = []
            writer.writerow([body,votes,','.join(tags)])

