import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from transformers import DistilBertTokenizerFast, DistilBertForQuestionAnswering
import torch

from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd

from difflib import SequenceMatcher as SM

def fix_paths(args):
    return os.path.realpath(
        os.path.join(os.path.dirname(__file__), args))

class Driver():
    def __init__(self):
        self.options = Options()
        self.options.headless = True
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.options)
        self.links = pd.read_csv('./data_cleaning/datasets/final_comparison_df.csv')

    def get_match_by_movie_name(self, name):
        similarities = self.links.apply(lambda x: SM(None, x.title, name).ratio(), axis=1)
        return self.links.iloc[similarities.idxmax()]

    def generate_paragraph(self, wiki_url):
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

    def split_paragraph(self, string):
        return [string[x:x + 500] for x in range(0, len(string), 500)]

    def get_paragraphs_by_movie_rows(self, movie_rows):
        wiki_urls = [movie_row.wikipediaUrl for movie_row in movie_rows]
        combined_paragraphs = [self.generate_paragraph(wiki_url) for wiki_url in wiki_urls]
        return [self.split_paragraph(x) for x in combined_paragraphs]

    def get_paragraphs_by_wiki_urls(self, wiki_urls):
        combined_paragraphs = [self.generate_paragraph(wiki_url) for wiki_url in wiki_urls]
        return [self.split_paragraph(x) for x in combined_paragraphs]


class QA_Chat():
    def __init__(self, model_path, movie_name):
        driver = Driver()
        movie_name_link = ""
        movie_row = driver.get_match_by_movie_name(movie_name)
        print([movie_row['wikipediaUrl']])
        self.text = driver.get_paragraphs_by_wiki_urls([movie_row['wikipediaUrl']])

        self.model = DistilBertForQuestionAnswering.from_pretrained(fix_paths(model_path))
        self.tokenizer = DistilBertTokenizerFast.from_pretrained(fix_paths(model_path))

    def question_answer(self, question):

        ans_list = []

        for i in self.text[0]:
            encoding = self.tokenizer.encode_plus(question, i)

            input_ids, attention_mask = encoding["input_ids"], encoding["attention_mask"]

            inputs_model = torch.tensor([input_ids])

            mask_model = torch.tensor([attention_mask])

            start_scores, end_scores = self.model(inputs_model, attention_mask=mask_model, return_dict=False)

            temp = max(start_scores.tolist()[0])
            temp2 = max(end_scores.tolist()[0])
            top_score = temp + temp2

            ans_list.append((top_score, start_scores, end_scores, input_ids))

        answer_list = sorted(ans_list, key=lambda tup: tup[0], reverse=True)

        for i in range(len(answer_list)):

            if i < 11:
                info = answer_list[i]
                input_ids = answer_list[i][3]

                ans_tokens = input_ids[torch.argmax(info[1]): torch.argmax(info[2]) + 1]

                answer_tokens = self.tokenizer.convert_ids_to_tokens(ans_tokens, skip_special_tokens=True)

                if len(answer_tokens) != 0:
                    print("\nQuestion ", question)
                    print("\nAnswer Tokens: ")
                    print(answer_tokens)

                    answer_tokens_to_string = self.tokenizer.convert_tokens_to_string(answer_tokens)

                    print("\nPredicted answer:\n{}".format(answer_tokens_to_string.capitalize()))

                    cont = 0

                    while cont == 0:
                        x = input('\nIs this answer satisfactory? (Y/N): ')
                        if x == "N" or x == "n":
                            cont = 1
                        elif x == "Y" or x == "y":
                            print("\nProviding the Next Best Answer... ")
                            return
                        else:
                            print("Please give a proper response!")

    def question_looper(self):
        print("Welcome to the QA")
        print("\nPlease note that the answers might not be fully accurate!")
        exeter = ""
        while exeter != "Quit":
            x = input('\nPlease enter your question? or Press Q to quit:')
            if x == "Q" or x == "q":
                exeter = "Quit"
            elif x == "":
                print("\nPlease provided a proper answer!!")
            else:
                self.question_answer(x)

        print("\nThank you")

    def question_answer_chatbot(self, question):
        ans_list = []
        for i in self.text[0]:
            encoding = self.tokenizer.encode_plus(question, i)
            input_ids, attention_mask = encoding["input_ids"], encoding["attention_mask"]
            inputs_model = torch.tensor([input_ids])
            mask_model = torch.tensor([attention_mask])
            start_scores, end_scores = self.model(inputs_model, attention_mask=mask_model, return_dict=False)
            temp = max(start_scores.tolist()[0])
            temp2 = max(end_scores.tolist()[0])
            top_score = temp + temp2
            ans_list.append((top_score, start_scores, end_scores, input_ids))

        answer_list = sorted(ans_list, key=lambda tup: tup[0], reverse=True)

        return answer_list

    def answer_generator_chatbot(self, answer_array, index):

        if index < 10:
            info = answer_array[int(index)]
            input_ids = answer_array[int(index)][3]

            ans_tokens = input_ids[torch.argmax(info[1]): torch.argmax(info[2]) + 1]

            answer_tokens = self.tokenizer.convert_ids_to_tokens(ans_tokens, skip_special_tokens=True)

            answer_tokens_to_string = self.tokenizer.convert_tokens_to_string(answer_tokens)

        else:
            answer_tokens_to_string = "Oops There is no more answer"

        return answer_tokens_to_string


if __name__ == "__main__":
    tester = QA_Chat("./models/distilbert-custom-QuAC-SQUAD", "Toy Story")
    tester.question_looper()

    """example_urls = [862,807,11,274870,339403]
    example_paths = ["toy_story.txt", "seven.txt", "star_wars.txt", "passengers.txt", "baby_driver.txt"]

    for idx,url in enumerate(example_urls):
        print(driver.links.loc[driver.links.id == url]['wikipediaId'].values[0])
        para = driver.get_paragraph(driver.links.loc[driver.links.id == url]['wikipediaId'].values[0])
        with open("examples/"+example_paths[idx], "w", encoding="utf-8") as f:
            f.writelines(para)"""