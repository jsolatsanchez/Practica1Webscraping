import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
from datetime import datetime

class datosMacroScraper():

    def __init__(self) -> None:
        self.url = "https://datosmacro.expansion.com"
        self.context = "/demografia"
        self.data = []
        self.header = ['País']
        self.dades = np.empty(0)
        self.dataset = None

    def __download_html(self, url):
        response = requests.get(url, timeout=None)
        return response.text
    
    # Retorna el conjunt d'enllaços de cadascuna de les pàgines temàtiques
    def __get_links_tematics(self, html):
        bs=BeautifulSoup(html, 'html.parser')
        # Els enllaços estan inclosos dins div de tipus row: <div> <h2> <a>
        div_items = bs.findAll("div", {"class": "row"} )
        links_tematics = []
        for div in div_items:
            # l'element <div> conté un <a>?
            a = div.next_element.next_element
            if a.name == 'a':
                href = a['href']
                links_tematics.append(self.url + href)

        return links_tematics[0:-1]# S'exclou l'apartat de religions

    # Es va definir la funció get_item_names per obtenir els noms de les estadístiques, ara no s'empra.
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
        links_estadistiques = []
        links_num = 0

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
                    # self.__getDades(bs)
                    # break
                # Obté les dades (aquesta vegada de cada país, d'una temàtica concreta)
                self.__getDades(bs)
            
            # Actualitzar el contador de links
            links_num += 1
            # Si és la primera característica carregada, es crea el datafreame de nou,
            # si no, es fa una join per país i data
            if links_num == 1:
                self.dataset = pd.DataFrame(self.data)
                self.dataset.columns = self.header
                # Resetegem la capçalera i les dades de l'array
                self.header = ['País']
                self.data = []
            else:
                aux_dataset = pd.DataFrame(self.data)
                aux_dataset.columns = self.header
                self.dataset = pd.merge(self.dataset,aux_dataset,on=['País','Fecha'],how='outer')
                # Resetegem la capçalera i les dades de l'array
                self.header = ['País']
                self.data = []
        return

    # Obté les dades d'una URL a un recurs amb taula de dades desglossades per països
    def __getDades(self, bs):
        # Obté el país actual
        pais = bs.title.string.split(' - ', 1)[0]
        print(pais)
        taula = bs.find("tbody")
        entrades = taula.find_all("tr")
        fila = [pais]
        for entrada in entrades:
            camps = entrada.find_all("td")
            for camp in camps:
                if camp['class'][0]=='fecha':
                    fila += [datetime.strptime(str(camp['data-value']),'%Y-%m-%d')]
                elif camp['class'][0]=='numero':
                    fila += [camp['data-value']]
                else:
                    fila += [camp.getText().replace("º", "")]
            self.dades = np.append(self.dades, fila)
            self.data.append(fila)
            fila = [pais]

    # Obté la capçalera de cada taula
    def __getCapcalera(self, bs):
        taula_elements = bs.find("tr", {"class": "tableheader"})
        ths = taula_elements.find_all("th")
        for th in ths:
            nomColumna = th.getText()
            try:
                # Si el nom de columna ja existeix, es fa un duplicat
                posicio = self.header.index(nomColumna)
                self.header += [nomColumna+'_'+str(posicio)]
            except ValueError:
                # Si la columna no existeix, l'afegeix
                self.header += [nomColumna]
                posicio = -1
            print(nomColumna + ": " + str(posicio))
        self.dades = np.append (self.dades, [self.header])
        print("Caçalera: " + str(self.header))
 
    def __persistir(self):
        print('Guardant dades a un fitxer csv...')
        # Passem les dates a text
        self.dataset['Fecha'] = self.dataset['Fecha'].apply(lambda x: x.strftime('%m-%Y'))
        # Escriptura a un csv
        self.dataset.to_csv("dades_macro.csv", index = False)

    def scrape(self):
        print ("Web scraping de Datos Macro")

        # Obtenir els enllaços principals
        html = self.__download_html(self.url + self.context)
        info_links = self.__get_links_tematics(html)
        print(info_links)
        #titols = self.__get_item_names(info_links)
        links_detall = self.__get_item_links(info_links)
        self.__persistir()
