import pandas as pd
import json
from typing import *
import recommender as rec
from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline
import truecase
import re
from flashtext import KeywordProcessor

"""
    The purpose of this class is to build out the functions and methods so we can store the information in an easy and accessible way.
"""


class MovieRecommender():

    def __init__(self, extracted_keywords: list, chatbot_mode='intent_detection'):
        """
            :self.chatbot_mode: 'intent_detection', 'movie_recommender', 'qa'
        """
        self.chatbot_mode = chatbot_mode

        self.keyword_processor = KeywordProcessor()

        # Keywords file
        keywords_json_file = open('data_cleaning/datasets/keywords.json')
        self.keywords_set = list(json.load(keywords_json_file))
        self.keyword_processor.add_keywords_from_list(self.keywords_set)

        # Genre File
        genres_json_file = open('data_cleaning/datasets/genres.json')
        self.genre_set = list(json.load(genres_json_file))
        self.keyword_processor.add_keywords_from_list(self.genre_set)

        # Will hold the recorded important keywords
        self.extracted_keywords = extracted_keywords

        self.tracker = 0
        self.limit = 5

        self.prompt_type = 'prompt'

        # Load just once so we don't load like 10 million times.
        self.tokenizer = AutoTokenizer.from_pretrained("dslim/bert-base-NER")
        self.model = AutoModelForTokenClassification.from_pretrained(
            "dslim/bert-base-NER")
        self.ner_pipeline = pipeline(
            "ner", model=self.model, tokenizer=self.tokenizer, grouped_entities=True)

    def ner_recognition(self, input):
        #input_rejoin = " ".join(input)
        ner_results = self.ner_pipeline(input)

        entities = []
        ans = self.tokenizer.convert_tokens_to_string(entities)
        print('ANS', ans)
        for entity in ner_results:
            entities.append(entity)

        return entities

    # This is to check which protocol the user wants to trigger
    def intent_detection(self, input):
        pass

    def recommend_movies(self):
        movie_result = rec.recommend(self.extracted_keywords)

        response = "The following movies have been recommended for you: "

        for movie in movie_result:
            response += "\n - " + movie

        return response

    def response_generator_for_recommender(self, response_prompt):
        """
            If it goes into response generator mode, it will strictly follow this list!
        """
        responses = {
            'prompt_greet': 'Hello, welcome to our site! Would you like to have a movie recommended?',
            'reply_greet': "Awesome! Let's begin!",
            'reply_generic_response': 'Thank you for the reply!',
            'prompt_genre': 'What genre of shows do you like?',
            'prompt_shows': 'What shows have you watched recently?',
            # Look at the actors/actresses
            'prompt_actor': 'Are there any actors or actresses that you enjoy?',
            'prompt_hate': 'Any shows that you hate?',
            'prompt_production_companies': 'Any production companies you like?',
            # Prompt keywords in the dataset
            'prompt_themes': 'What do you look for in a movie?',
            'reply_fallback': "I do not quite understand. Could you clarify that?",
            'reply_searching': "Thank you! That's all the info we need, now we're looking for a movie to recommend...",
            'reply_list_of_movies': self.recommend_movies,
            'reply_movie_prompt': "Which movie would you like to know more about?",
            'reply_end': "Thank you for using our chatbot! Type reset to reset the state of the chatbot",
        }

        return responses[response_prompt]

    def get_input_respond_message_for_movie_recommender(self, input: str):

        temp_impt_keywords = []  # This will be appended into recommender

        # The below is the prompt respond logic
        list_of_prompt_response = [
            #{'prompt_greet': ['reply_greet', 'prompt_genre']},
            {'prompt_genre': ['reply_generic_response', 'prompt_shows']},
            {'prompt_shows': ['reply_generic_response', 'prompt_actor']},
            {'prompt_actor': ['reply_generic_response',
                              'prompt_production_companies']},
            {'prompt_production_companies': [
                'reply_generic_response', 'prompt_themes']},
            {'prompt_themes': ['reply_searching', 'reply_list_of_movies']},
            {'reply_list_of_movies': ['reply_end']}
        ]

        response_prompt_response = list_of_prompt_response[self.tracker]
        prompt_type = list(response_prompt_response.keys())[0]

        # For keyword matching if needed
        input_list_breakdown = self.breakdown_input_into_list(input)

        # For NER, restore truecase is needed if user did not bother
        truecase_input = truecase.get_true_case(input)
        print(truecase_input)

        if prompt_type == 'prompt_genre':
            # Specify what actions to take to retrieve the relevant keywords
            # For genres, we can just look at the genre keyword list
            # for word in input_list_breakdown:
            #     if word in self.genre_set or self.keywords_set:
            #         temp_impt_keywords.append(word)
            # print(temp_impt_keywords)
            detected_keywords = self.find_words_phrases_from_keywords(
                input.lower())
            print(detected_keywords)
            temp_impt_keywords.extend(detected_keywords)

        elif prompt_type == 'prompt_shows':
            # We will use NER to extract relevant topics
            detected_ner = self.ner_recognition(truecase_input)
            print(detected_ner)
            temp_impt_keywords.extend(detected_ner)

        elif prompt_type == 'prompt_actor':
            # We will use NER to extract relevant topics
            detected_ner = self.ner_recognition(truecase_input)
            print(detected_ner)
            temp_impt_keywords.extend(detected_ner)

        elif prompt_type == 'prompt_production_companies':
            detected_ner = self.ner_recognition(truecase_input)
            print(detected_ner)
            temp_impt_keywords.extend(detected_ner)

        elif prompt_type == 'prompt_themes':
            # This is the catch all part
            detected_ner = self.ner_recognition(truecase_input)
            print(detected_ner)
            temp_impt_keywords.extend(detected_ner)

            detected_keywords = self.find_words_phrases_from_keywords(
                input.lower())
            print(detected_keywords)
            temp_impt_keywords.extend(detected_keywords)

            # Remove duplicate if any
            temp_impt_keywords = list(set(temp_impt_keywords))

        # If no keywords are detected
        if self.isNestedListEmpty(temp_impt_keywords):
            return [self.response_generator_for_recommender('reply_fallback')]

        self.extracted_keywords.extend(temp_impt_keywords)

        # Return the response of the prompt

        if self.tracker < self.limit:
            self.tracker += 1

        responses_result = []
        for response_from_prompt in response_prompt_response[prompt_type]:
            responses_result.append(
                self.response_generator_for_recommender(response_from_prompt))

        return responses_result

    def breakdown_input_into_list(self, input: str):
        input_list = input.split(" ")
        input_lower = [word.lower() for word in input_list]
        return input_lower

    # Check if list empty
    def isNestedListEmpty(self, inList):
        if isinstance(inList, list):  # Is a list
            return all(map(self.isListEmpty, inList))
        return False  # Not a list

    def isListEmpty(self, insertedlist):
        if len(insertedlist) == 0:
            return True
        else:
            return False

    def find_words_phrases_from_keywords(self, sentence):
        keywords_found = self.keyword_processor.extract_keywords(sentence)
        return keywords_found
