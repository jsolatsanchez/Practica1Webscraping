from turtle import ht
import requests
from bs4 import BeautifulSoup

class datosMacroScraper():

    def __init__(self) -> None:
        self.url = "https://datosmacro.expansion.com"
        self.context = "/demografia"
        self.data = ['País']

    def __download_html(self, url):
        response = requests.get(url)
        return response.text
    
    # Retorna el conjunt d'enllaços de cadascuna de les pàgines temàtiques
    def __get_links_tematics(self, html):
        bs=BeautifulSoup(html, 'html.parser')
        # Els enllaços estan inclosos dins div de tipus row: <div> <h2> <a>
        div_items = bs.findAll("div", {"class": "row"} )
        links_tematics = []
        n = 0
        for div in div_items:
            if n < 3:   # Limita el número d'elements a descarregar (eliminar al final)
                # l'element <div> conté un <a>?
                a = div.next_element.next_element
                if a.name == 'a':
                    href = a['href']
                    links_tematics.append(self.url + href)
            n = n + 1
        return links_tematics

    def __get_item_names(self, links):
        links_secundaris = []
        for e in links:
            html = self.__download_html(e)
            bs = BeautifulSoup(html, 'html.parser')
            h1 = bs.find("h1", {"class": "page-header"})
            titol = h1.next_element.next_element.getText()
            links_secundaris.append(titol)
            print(".")
        return links_secundaris

    # A partir d'una llista de pàgines temàtiques obté les estadístiques de tots els països
    def __get_item_links(self, links):
        noms_estadistiques = []
        links_estadistiqus = []

        # Recorre les pàgines de cada temàtica per obtenir-ne les dades
        for e in links:
            html = self.__download_html(e)
            bs = BeautifulSoup(html, 'html.parser')
            h1 = bs.find("h1", {"class": "page-header"})
            # Obté el títol de la pàgina temàtica actual
            titol = h1.next_element.next_element.getText()
            print(titol)
            print("------------------------------------")
            # Cerca només dins l'element taula de la pàgina
            taula_element = bs.find("table", {"id": "tb1"})
            # Obté els enllaços a les respectives pàgines de cada país
            links_estadistiques = taula_element.find_all("a")

            # Obté la informació de cada país d'una temàtica concreta.
            obtenirCapcalera = True
            for l in links_estadistiques:
                html = self.__download_html(self.url + l["href"])
                bs = BeautifulSoup(html, 'html.parser')
                # Obté la capçalera (només per al primer país accedit d'una temàtica concreta)
                if obtenirCapcalera:
                    print ("Capçalera...")
                    self.__getCapcalera(bs)
                    print ("_____")
                    obtenirCapcalera = False
                    # Comentar el break si es volen extreure les dades, i no només la capçalera (fa que es surti de la iteració de països
                    break
                # Obté les dades (aquesta vegada de cada país, d'una temàtica concreta)
                self.__getDades(bs)
        return

    # Obté les dades d'una URL a un recurs amb taula de dades desglossades per països
    def __getDades(self, bs):
        print(bs.title.string)


    # Obté la capçalera de cada taula
    def __getCapcalera(self, bs):
        taula_elements = bs.find("tr", {"class": "tableheader"})
        ths = taula_elements.find_all("th")
        for th in ths:
            nomColumna = th.getText()
            try:
                posicio = self.data.index(nomColumna)
            except ValueError:
                # Si la columna no existeix, l'afegeix
                self.data += [nomColumna]
                posicio = -1
            print(nomColumna + ": " + str(posicio))

 
    def scrape(self):
        print ("Web scraping de Datos Macro")

        # Obtenir els enllaços principals
        html = self.__download_html(self.url + self.context)
        info_links = self.__get_links_tematics(html)
        print(info_links)
        #titols = self.__get_item_names(info_links)
        links_detall = self.__get_item_links(info_links)
        print(links_detall)
        print(self.data)
