from turtle import ht
import requests
from bs4 import BeautifulSoup

class datosMacroScraper():

    def __init__(self) -> None:
        self.url = "https://datosmacro.expansion.com"
        self.context = "/demografia"
        self.data = []

    def __download_html(self, url):
        response = requests.get(url)
        return response.text
    
    def __get_info_links(self, html):
        bs=BeautifulSoup(html, 'html.parser')
        # Els enllaços estan inclosos dins div de tipus row: <div> <h2> <a>
        div_items = bs.findAll("div", {"class": "row"} )
        links_principals = []
        for div in div_items:
            # l'element <div> conté un <a>?
            a = div.next_element.next_element
            if a.name == 'a':
                href = a['href']
                links_principals.append(self.url + href)
        return links_principals

    def __get_item_links(self, links):
        links_secundaris = []
        for e in links:
            html = self.__download_html(e)
            bs = BeautifulSoup(html, 'html.parser')
            h1 = bs.find("h1", {"class": "page-header"})
            titol = h1.next_element.next_element
            links_secundaris.append(titol)
            print(".")
        return links_secundaris



    def scrape(self):
        print ("Web scraping de Datos Macro")

        # Obtenir els enllaços principals
        html = self.__download_html(self.url + self.context)
        info_links = self.__get_info_links(html)
        print(info_links)
        titols = self.__get_item_links(info_links)
        print(titols)
