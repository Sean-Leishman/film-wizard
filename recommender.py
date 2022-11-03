import pandas as pd
import numpy as np
from nltk import corpus
from rake_nltk import Rake
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from rank_bm25 import BM25Okapi
import string

import pandas as pd

from data_scraper.scraper import Driver

def clean_words(text:str):
    remove_all_punc_text = text.translate(str.maketrans("", "", string.punctuation))
    stop_words = set(stopwords.words('english'))
    list_of_text = remove_all_punc_text.split(" ")

    if (len(list_of_text) == 0):
        return []

    filtered_sentence = []

    for w in list_of_text:
        lower_text = w.lower()
        if lower_text not in stop_words:
            filtered_sentence.append(lower_text)

    return " ".join(filtered_sentence)

class Recommender:
    def __init__(self):
        self.movie_metadata = pd.read_csv("source/final_comparison_df.csv")
        self.corpus = self.movie_metadata['bag_of_words'].to_list()
        self.tokenized_corpus = [doc.split(" ") for doc in self.corpus]
        self.bm25 = BM25Okapi(self.tokenized_corpus)

    def get_recommended_movies(self,query):
        cleaned_query = clean_words(query)
        tokenized_query = cleaned_query.split(" ")
        bm25_top_result = self.bm25.get_top_n(tokenized_query, self.corpus, n=10)

        # Match to video
        result_of_show = []

        for result in bm25_top_result:
            index_of_show = self.movie_metadata.index[self.movie_metadata['bag_of_words'] == result].to_list()[0]
            result_of_show.append(self.movie_metadata.iloc[index_of_show])

        return result_of_show

if __name__=="__main__":
    driver = Driver()
    print(driver.get_paragraphs_by_wiki_urls(["https://en.wikipedia.org/wiki/Toy_Story"]))