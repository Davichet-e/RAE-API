import json
import re
from typing import Dict, List, Optional, Union

import bs4
import requests

BASE_URL = "https://dle.rae.es/{word}"

soup = bs4.BeautifulSoup(
    requests.get(BASE_URL.format(word=input("Palabra a buscar: "))).content, "lxml"
)

results: bs4.Tag = soup.find("div", id="resultados")
dicc: Dict[str, Dict[str, Union[str, List[str]]]] = {}

for i, result in enumerate(results.find_all("article", recursive=False), start=1):
    meanings: List[bs4.Tag] = result.find_all("p", recursive=False)

    dicc[i] = {}
    complex_form: str
    for p in meanings:
        paragraph_class: str = p["class"][0]

        if re.fullmatch("j[0-9]?", paragraph_class):
            meaning_number, meaning_text = p.text.split(".", 1)
            dicc[i][meaning_number] = meaning_text.lstrip()

        elif paragraph_class in {"k5", "k6"}:
            complex_form = p.text
            dicc[i][complex_form] = []

        elif paragraph_class == "m":
            dicc[i][complex_form].append(p.text)


with open("palabra.json", "w", encoding="utf-8") as output_file:
    json.dump(dicc, output_file, ensure_ascii=False, indent=2)
