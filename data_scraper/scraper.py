import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd

class WikiDataQuery():
    def __init__(self):
        self.sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
        self.links = None
        self.get_films()

    def get_film(self,id):
        if "tt" not in id:
            id = "tt"+id
        if (self.links["IMDb_ID.value"] == id).sum() > 0:
            return self.links.loc[self.links["IMDb_ID.value"] == id]['sitelink.value'].values[0]
        else:
            raise KeyError

    def get_films(self):
        self.sparql.setQuery("""SELECT ?item ?IMDb_ID ?sitelink WHERE {
              {
                {
              ?item wdt:P31 /wdt:P279* wd:Q11424 .
              ?item wdt:P345 ?IMDb_ID .
              ?sitelink schema:about ?item ; schema:isPartOf <https://en.wikipedia.org/> .
                  }
                }
              UNION{
                ?item wdt:P31 /wdt:P279* wd:Q24869 .
                ?item wdt:P345 ?IMDb_ID .
                ?sitelink schema:about ?item ; schema:isPartOf <https://en.wikipedia.org/> .
                }
            }""")
        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        results_df = pd.json_normalize(results['results']['bindings'])
        self.links = results_df[['IMDb_ID.value', 'sitelink.value']]

class Driver():
    def __init__(self):
        self.options = Options()
        self.options.headless = True
        #self.options.add_argument("--window-size=1920,1200")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.options)
        self.links = pd.read_csv('../datasets/movies/master.csv')

    def get_film(self, wiki_url):
        if self.links.loc[self.links.wikipediaId == wiki_url].shape[0] == 1:
            return wiki_url
        else:
            raise KeyError

    def get_paragraph(self, wiki_url):
        link = self.get_film(wiki_url)
        self.driver.get(link)
        entire_page = self.driver.find_element(By.XPATH, '//*[@id="mw-content-text"]')
        paragraphs = entire_page.find_elements(By.TAG_NAME, 'p')
        list_items = entire_page.find_elements(By.TAG_NAME, 'li')

        combined_paragraph = ""
        for paragraph in paragraphs:
            combined_paragraph += paragraph.get_attribute('textContent')
        combined_paragraph = combined_paragraph.strip()
        print(wiki_url)
        return combined_paragraph

if __name__ == "__main__":
    driver = Driver()
    for row in driver.links.T:
        driver.get_paragraph(driver.links.iloc[row]['wikipediaId'])