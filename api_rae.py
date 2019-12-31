import json
import re
from collections import defaultdict
from typing import Dict, Iterator, List, Union

import bs4
import requests

BASE_URL = "https://dle.rae.es/"

soup = bs4.BeautifulSoup(
    requests.get(BASE_URL + input("Palabra a buscar: ")).content, "lxml"
)

results: bs4.Tag = soup.find("div", id="resultados")
dicc: Dict[str, Dict[str, Union[str, List[str]]]] = {}

for i, result in enumerate(results.find_all("article"), start=1):
    meanings = result.find_all("p")

    dicc[i] = {}
    complex_form = None
    for p in meanings:
        paragraph_class = p["class"][0]
        
        if re.fullmatch("j[0-9]?", paragraph_class):
            meaning_number, meaning_text = p.text.split(".", 1)
            dicc[i][meaning_number] = meaning_text[1:]

        elif paragraph_class in {"k5", "k6"}:
            complex_form = p.text
            dicc[i][complex_form] = []

        elif paragraph_class == "m":
            dicc[i][complex_form].append(p.text)


with open("palabra.json", "w", encoding="utf-8") as output_file:
    json.dump(dicc, output_file, ensure_ascii=False, indent=2)
