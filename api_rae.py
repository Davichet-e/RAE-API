import json
import re
from typing import Dict, List, Optional, Union

import bs4
import requests
import typer

BASE_URL = "https://dle.rae.es{}"


app = typer.Typer()


def create_dict(word: str) -> Dict[int, Dict[str, Union[str, List[str]]]]:
    response: requests.Response = requests.get(BASE_URL.format(f"/{word}"))
    soup = bs4.BeautifulSoup(response.content, "lxml")

    results: Optional[bs4.Tag] = soup.find("div", id="resultados")
    dicc: Dict[int, Dict[str, Union[str, List[str]]]] = {}
    # Check if I has been redirected
    if response.history:

        decision: str = input(
            f"La palabra {word} te redirecciona a {results.find('header').text}, "
            "¿quieres crear la entrada con esa palabra? (s/n) "
        )
        if decision not in {"s", "si", "1"}:
            return {}

    if "La entrada" in results.text:
        word_related: str = results.find("a").text
        decision: str = input(
            f"Aviso: La palabra {word} no está en el Diccionario.\n"
            f"Pero existe una palabra que es parecida: \033[92m{word_related}\033[0m, "
            "¿quiere proceder a su búsqueda? (s/n) "
        )

        if decision in {"s", "si"}:
            dicc = create_dict(word_related)

    elif "Las entradas" in results.text:
        links = {
            link.text if link.text.isalpha() else re.sub(r"\d", "", link.text)
            for link in results.select(".n1 > a")
        }
        print(
            f"Aviso: La palabra «{word}» no está en el Diccionario. "
            "Las entradas que se muestran a continuación podrían estar relacionadas:\n"
            f"{links}"
        )

    elif "Entradas" in results.text:
        print(
            f"Entradas que contienen la forma «{word}»:\n"
            f"{[link.text for link in results.select('.n1 > a')]}"
        )

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

                # Standard meaning
                if "j" in paragraph_class:
                    meaning_number, meaning_text = p.text.split(".", 1)
                    dicc[i][meaning_number] = meaning_text.lstrip()

                # Name of the complex form
                elif paragraph_class in {"k5", "k6"}:
                    complex_form: str = p.text
                    dicc[i][complex_form] = []

                # Different meanings of the complex form
                elif paragraph_class == "m":
                    dicc[i][complex_form].append(p.text)

                # Also see
                elif paragraph_class == "l2":
                    link: Optional[bs4.Tag] = p.find("a")
                    redirected_link: str = BASE_URL.format(link["href"])
                    # If any of the complex forms' array is empty,
                    # it means this 'also see' belongs to the complex form
                    for key, value in dicc[i].items():
                        if not value:
                            dicc[i][key].append(
                                f"Véase '{link.text}' ({redirected_link} )"
                            )
                            break
                    else:
                        print(
                            f"La {i}a acepción le redirecciona al siguiente link: "
                            f"{redirected_link}"
                        )
                        superscript: Optional[bs4.Tag] = link.find("sup")
                        if superscript:
                            link.string = link.text.replace(superscript.text, "")

                        if dicc[i]:
                            dicc[i][
                                "Véase también"
                            ] = f"'{link.text}' ({redirected_link})"
                        else:
                            dicc[i] = f"Véase '{link.text}' ({redirected_link} )"

                # Sendings
                elif "l" in paragraph_class:
                    redirected_link: str = BASE_URL.format(p.a["href"])
                    dicc.setdefault("Envios", []).append(redirected_link)

    return dicc


@app.command()
def rae_cli(word: str, json_: bool = typer.Option(False, "--json", "-j")) -> None:
    dicc = create_dict(word)
    if dicc:
        dicc_formated = json.dumps(dicc, ensure_ascii=False, indent=2)
        if json_:
            with open(f"{word}.json", "w", encoding="utf-8") as output_file:
                output_file.write(dicc_formated)

        typer.echo(dicc_formated)


if __name__ == "__main__":
    app()
