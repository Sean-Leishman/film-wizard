import pandas as pd
import numpy as np
from rake_nltk import Rake
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from rank_bm25 import BM25Okapi
import string

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

def recommend(query:str):
    movie_metadata = pd.read_csv("data_cleaning/datasets/final_comparison_df.csv")
    corpus = movie_metadata['bag_of_words'].to_list()
    tokenized_corpus = [doc.split(" ") for doc in corpus]
    bm25 = BM25Okapi(tokenized_corpus)

    #query = "disney princess."
    query_joined = " ".join(query)
    cleaned_query = clean_words(query_joined)
    tokenized_query = cleaned_query.split(" ")
    bm25_top_result = bm25.get_top_n(tokenized_query, corpus, n=10)

    #Match to video
    result_of_show = []

    for result in bm25_top_result:
        index_of_show = movie_metadata.index[movie_metadata['bag_of_words'] == result].to_list()[0]
        result_of_show.append(movie_metadata.iloc[index_of_show]['title'])

    return result_of_show
