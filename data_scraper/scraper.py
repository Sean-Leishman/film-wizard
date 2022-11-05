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
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.options)
        self.links = pd.read_csv(os.path.realpath(os.path.join(os.path.dirname(__file__),'..', 'source','final_comparison_df.csv')))

    def generate_paragraph(self,wiki_url):
        self.driver.get(wiki_url)
        entire_page = self.driver.find_element(By.XPATH, '//*[@id="mw-content-text"]')
        paragraphs = entire_page.find_elements(By.TAG_NAME, 'p')

        list_items = entire_page.find_elements(By.XPATH, '//*[@class="mw-parser-output"]/ul/li')
        combined_paragraph = ""
        for paragraph in paragraphs:
            combined_paragraph += paragraph.get_attribute('textContent')
        for list in list_items:
            combined_paragraph += list.text
        combined_paragraph = combined_paragraph.strip()
        return combined_paragraph

    def split_paragraph(self,string):
        return [string[x:x+500] for x in range(0,len(string), 500)]

    def get_paragraphs_by_movie_rows(self, movie_rows):
        wiki_urls = [movie_row.wikipediaUrl for movie_row in movie_rows]
        combined_paragraphs = [self.generate_paragraph(wiki_url) for wiki_url in wiki_urls]
        return [self.split_paragraph(x) for x in combined_paragraphs]

    def get_paragraphs_by_wiki_urls(self, wiki_urls):
        combined_paragraphs = [self.generate_paragraph(wiki_url) for wiki_url in wiki_urls]
        return [self.split_paragraph(x) for x in combined_paragraphs]

if __name__ == "__main__":
    driver = Driver()
    # Toy Story
    st = driver.get_paragraphs_by_wiki_urls(["https://en.wikipedia.org/wiki/Toy_Story"])

    """example_urls = [862,807,11,274870,339403]
    example_paths = ["toy_story.txt", "seven.txt", "star_wars.txt", "passengers.txt", "baby_driver.txt"]

    for idx,url in enumerate(example_urls):
        print(driver.links.loc[driver.links.id == url]['wikipediaId'].values[0])
        para = driver.get_paragraph(driver.links.loc[driver.links.id == url]['wikipediaId'].values[0])
        with open("examples/"+example_paths[idx], "w", encoding="utf-8") as f:
            f.writelines(para)"""