# RAE-API

RAE-API es una librería cuya misión es crear un archivo JSON con las diferentes entradas, acepciones y formas complejas
de la palabra seleccionada por el usuario. Esto se consigue haciendo web-scrapping en la página de la <a href="https://dle.rae.es/">RAE</a>.
Dispone de un comando instalable mediante `pip`.

## Instalación
Para instalar el comando `rae`, ejecute `pip install .` en la consola de comandos en la carpeta donde esté alojado el repositorio. Una vez instalado, ejecute `rae {palabra}` para obtener sus definiciones. El comando tiene una opción que puede ser activada con el argumento `--json`, el cual crea un archivo JSON con las definiciones de la palabra.

## Uso 
También puede ser lanzado como archivo normal de Python, simplemente ejecute `python api_rae.py [--json] {palabra}`
