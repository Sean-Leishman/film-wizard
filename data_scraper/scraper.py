import os
import re

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
        last_space_idx = 0
        last_space_indicies = []
        space_after_last_idx = 500
        for idx, x in enumerate(string):
            if x == ".":
                last_space_idx = idx+1
            if idx % space_after_last_idx == 0:
                last_space_indicies.append(last_space_idx)
                space_after_last_idx = last_space_idx + 500
        last_space_indicies.append(len(string))
        strings = [string[last_space_indicies[x-1]:last_space_indicies[x]] for x in range(1,len(last_space_indicies))]
        replacement_pattern = '\[.*?\]'
        strings = [(re.sub(replacement_pattern, "", x)).strip() for x in strings]
        return strings

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
    for x in st[0]:
        print("[",x[:50],"..],")
    """example_urls = [862,807,11,274870,339403]
    example_paths = ["toy_story.txt", "seven.txt", "star_wars.txt", "passengers.txt", "baby_driver.txt"]

    for idx,url in enumerate(example_urls):
        print(driver.links.loc[driver.links.id == url]['wikipediaId'].values[0])
        para = driver.get_paragraph(driver.links.loc[driver.links.id == url]['wikipediaId'].values[0])
        with open("examples/"+example_paths[idx], "w", encoding="utf-8") as f:
            f.writelines(para)"""