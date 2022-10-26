import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd

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
        print(wiki_url)
        link = self.get_film(wiki_url)
        self.driver.get(link)
        entire_page = self.driver.find_element(By.XPATH, '//*[@id="mw-content-text"]')
        paragraphs = entire_page.find_elements(By.TAG_NAME, 'p')
        list_items = entire_page.find_elements(By.TAG_NAME, 'li')

        combined_paragraph = ""
        for paragraph in paragraphs:
            combined_paragraph += paragraph.get_attribute('textContent')
        combined_paragraph = combined_paragraph.strip()
        return combined_paragraph

if __name__ == "__main__":
    driver = Driver()
    # Toy Story,
    example_urls = [862,807,11,274870,339403]
    example_paths = ["toy_story.txt", "seven.txt", "star_wars.txt", "passengers.txt", "baby_driver.txt"]

    for idx,url in enumerate(example_urls):
        print(driver.links.loc[driver.links.id == url]['wikipediaId'].values[0])
        para = driver.get_paragraph(driver.links.loc[driver.links.id == url]['wikipediaId'].values[0])
        with open("examples/"+example_paths[idx], "w", encoding="utf-8") as f:
            f.writelines(para)