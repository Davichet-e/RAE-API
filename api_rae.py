import json
import re
from typing import Dict, List, Optional, Union

import bs4
import requests

BASE_URL = "https://dle.rae.es/{word}"


def create_dict(word: str) -> Dict[int, Dict[str, Union[str, List[str]]]]:
    soup = bs4.BeautifulSoup(requests.get(BASE_URL.format(word=word)).content, "lxml")

    results: Optional[bs4.Tag] = soup.find("div", id="resultados")
    dicc: Dict[int, Dict[str, Union[str, List[str]]]] = {}

    if "La entrada" in results.text:
        word_related: str = results.find("a").text
        decision: str = input(
            f"Aviso: La palabra {word} no está en el Diccionario.\n"
            f"Pero existe una palabra que es parecida: \033[92m{word_related}\033[0m, "
            "¿quiere proceder a su búsqueda? (s/n) "
        )
        
        if decision in {"s", "si"}:
            dicc = create_dict(word_related)

    elif "Aviso" in results.text:
        print(f"Aviso: La palabra {word} no está en el Diccionario.")

    else:
        for i, result in enumerate(
            results.find_all("article", recursive=False), start=1
        ):
            meanings: List[bs4.Tag] = result.find_all("p", recursive=False)

            dicc[i] = {}
            complex_form: str
            for p in meanings:
                paragraph_class: str = p["class"][0]

                if re.fullmatch("j[0-9]?", paragraph_class):
                    meaning_number, meaning_text = p.text.split(".", 1)
                    dicc[i][meaning_number] = meaning_text.lstrip()

                elif paragraph_class in {"k5", "k6"}:
                    complex_form: str = p.text
                    dicc[i][complex_form] = []

                elif paragraph_class == "m":
                    dicc[i][complex_form].append(p.text)
    return dicc


if __name__ == "__main__":
    dicc = create_dict(input("Introduzca la palabra a buscar: "))
    with open("palabra.json", "w", encoding="utf-8") as output_file:
        json.dump(dicc, output_file, ensure_ascii=False, indent=2)
