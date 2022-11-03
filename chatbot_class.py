import pandas as pd
import json
from flair.data import Sentence
from flair.models import SequenceTagger
from typing import *
from recommender import *

"""
    The purpose of this class is to build out the functions and methods so we can store the information in an easy and accessible way.
"""


class MovieRecommender():

    def __init__(self, extracted_keywords: list, chatbot_mode='intent_detection'):
        """
            :self.chatbot_mode: 'intent_detection', 'movie_recommender', 'qa'
        """
        self.chatbot_mode = chatbot_mode

        # Keywords file
        keywords_json_file = open('data_cleaning/datasets/keywords.json')
        self.keywords_set = set(json.load(keywords_json_file))

        # Genre File
        genres_json_file = open('data_cleaning/datasets/genres.json')
        self.genre_set = set(json.load(genres_json_file))

        # Will hold the recorded important keywords
        self.extracted_keywords = extracted_keywords

        self.tracker = 0
        self.limit = 5

        self.prompt_type = 'prompt'

    def ner_recognition(self, input):
        tagger = SequenceTagger.load("flair/ner-english-large")
        input_rejoin = " ".join(input)
        sentence = Sentence(input_rejoin)
        tagger.predict(sentence)

        entities = []

        for entity in sentence.get_spans('ner'):
            entities.append(entity.text)

        return entities

    # This is to check which protocol the user wants to trigger
    def intent_detection(self, input):
        pass

    def recommend_movies(self):
        movie_result = recommend(self.extracted_keywords)

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
            'reply_fallback': "I don't quite understand. Could you clarify that?",
            'reply_searching': "Thank you! That's all the info we need, now we're looking for a movie to recommend...",
            'reply_list_of_movies': self.recommend_movies(),
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
        print(response_prompt_response)
        prompt_type = list(response_prompt_response.keys())[0]

        input_list = self.breakdown_input_into_list(input)

        if prompt_type == 'prompt_genre':
            # Specify what actions to take to retrieve the relevant keywords
            # For genres, we can just look at the genre keyword list
            for word in input_list:
                if word in self.genre_set or self.keywords_set:
                    temp_impt_keywords.append(word)

        elif prompt_type == 'prompt_shows':
            # We will use NER to extract relevant topics
            detected_keywords = self.ner_recognition(input_list)
            print(detected_keywords)
            temp_impt_keywords.append(detected_keywords)

        elif prompt_type == 'prompt_actor':
            # We will use NER to extract relevant topics
            detected_keywords = self.ner_recognition(input_list)
            temp_impt_keywords.append(detected_keywords)

        # If no keywords are detected
        if len(temp_impt_keywords) == 0:
            return self.response_generator_for_recommender('reply_fallback')

        self.extracted_keywords.extend(temp_impt_keywords)

        # Return the response of the prompt

        if self.tracker < self.limit:
            self.tracker += 1

        print('tracker val', self.tracker)

        responses_result = []
        for response_from_prompt in response_prompt_response[prompt_type]:
            print('response', response_from_prompt)
            responses_result.append(
                self.response_generator_for_recommender(response_from_prompt))
            print(responses_result)

        return responses_result

    def breakdown_input_into_list(self, input: str):
        input_list = input.split(" ")
        input_lower = [word.lower() for word in input_list]
        return input_lower
