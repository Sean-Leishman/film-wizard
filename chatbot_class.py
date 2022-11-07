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

class ChatbotFramework():

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
        self.tokenizer = AutoTokenizer.from_pretrained("dslim/bert-base-NER-uncased")
        self.model = AutoModelForTokenClassification.from_pretrained("dslim/bert-base-NER-uncased")
        self.ner_pipeline = pipeline("ner", model=self.model, tokenizer=self.tokenizer, grouped_entities=True)

        #Intent keywords list:
        self.intent = {'hello': {'hello', 'hi', 'how do you do', 'howdy', 'hullo'},
<<<<<<< HEAD
                       'reset': {'reset', 'quit'},
                       'quit': {'cease', 'chuck up the sponge', 'depart', 'discontinue', 'drop by the wayside',
                                'give up', 'lay off', 'quit', 'relinquish', 'renounce', 'resign', 'step down', 'stop',
                                'take leave', 'throw in', 'throw in the towel'},
                       'recommend': {'advocate', 'commend', 'recommend', 'urge', 'recommended', 'recommendation'},
                       'no': {'none', 'nothing', 'no', 'no more', 'not interested', "i don't know"},
                       'movie': {'film', 'flick', 'motion picture', 'motion picture show', 'movie', 'moving picture',
                                 'moving picture show', 'picture show'},
                       'qa': {"enquire", "questions", "ask", "query", "want to know", "question"}}

=======
                    'reset': {'reset', 'quit'},
                    'quit': {'cease','chuck up the sponge', 'depart', 'discontinue', 'drop by the wayside', 'give up', 'lay off', 'quit', 'relinquish', 'renounce', 'resign', 'step down', 'stop', 'take leave', 'throw in', 'throw in the towel'},
                    'recommend': {'advocate', 'commend', 'recommend', 'urge', 'recommended'},
                    'no': {'none', 'nothing', 'no', 'no more', 'not interested', "i don't know"},
                    'movie': {'film', 'flick', 'motion picture', 'motion picture show', 'movie', 'moving picture', 'moving picture show', 'picture show'}}
        
>>>>>>> parent of f44227c (change to master without models)
        self.intent_keys = list(self.intent.keys())

        self.intent_response = {
            'reply_greet_general': 'Hello back to you!',
            'reply_fallback_general': "I don't quite understand you, could you clarify your question?",
            'reply_movie_recommended': "Thank you! Please go through our prompts as they appear! Type reset/quit to quit the recommender mode",
            'reply_reset': "It appears you'll like to reset your chat, all status wiped!"
        }

    def convo(self, input):
        ## There are three different modes, intent detection, recommender mode and qa

        #What to respond back
        response_list = []

        if self.chatbot_mode == 'intent_detection':

            input_lower = input.lower()
            
            convo_keyword_proc  = KeywordProcessor()
            intent_detected = []
            
            for intent,pattern in self.intent.items():
                convo_keyword_proc.add_keywords_from_list(list(pattern))

                if len(convo_keyword_proc.extract_keywords(input_lower)) > 0:
                    intent_detected.append(intent) 

                convo_keyword_proc.remove_keywords_from_list(list(pattern))
            
            if len(intent_detected) == 0:
                return [self.intent_response['reply_fallback_general']]

            else:
                print('intent detected', intent_detected)
                for intent in intent_detected:
                    if intent == "hello":
                        response_list.append(self.intent_response['reply_greet_general'])
                    elif intent == "recommend":
                        #Going into the movie pipeline
                        response_list.append(self.response_generator_for_recommender('prompt_genre'))
                        self.chatbot_mode =  'movie_recommender'
            
            return response_list
            
        elif self.chatbot_mode == 'movie_recommender':
<<<<<<< HEAD
            print("enter movie recommender")
            # Check if user wants to reset
=======

            #Check if user wants to reset
>>>>>>> parent of f44227c (change to master without models)
            if self.reset_convo(input) == False:
                respond_results = self.get_input_respond_message_for_movie_recommender(input)
            else:
                #Go back to intent detection
                self.tracker = 0
                self.chatbot_mode = 'intent_detection'
                return [self.intent_response['reply_reset']]

            return respond_results

        elif self.chatbot_mode == 'qa':
            #what to say during QA part
            pass
    
    def reset_convo(self, input):
        if input.lower() == "quit" or input.lower() == "reset":
            return True
        return False

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
            'prompt_greet': 'Hello, welcome to our site! Would you like to have a movie recommended? Type reset to stop anytime!',
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
        skip_mode = False

        #Check if users wants to skip this question
        
        no_keyword_proc  = KeywordProcessor()
        no_keyword_proc.add_keywords_from_list(list(self.intent['no']))

        want_to_skip_intent = no_keyword_proc.extract_keywords(input)

        if len(want_to_skip_intent) > 0:
            skip_mode = True

        # The below is the prompt respond logic
        list_of_prompt_response = [
            #{'prompt_greet': ['reply_greet', 'prompt_genre']},
            {'prompt_genre': ['reply_generic_response', 'prompt_shows']},
            {'prompt_shows': ['reply_generic_response', 'prompt_actor']},
            {'prompt_actor': ['reply_generic_response','prompt_production_companies']},
            {'prompt_production_companies': ['reply_generic_response', 'prompt_themes']},
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

        #If there's no skip
        if skip_mode == False:

            if prompt_type == 'prompt_genre':
                # Specify what actions to take to retrieve the relevant keywords
                # For genres, we can just look at the genre keyword list
                # for word in input_list_breakdown:
                #     if word in self.genre_set or self.keywords_set:
                #         temp_impt_keywords.append(word)
                # print(temp_impt_keywords)
                detected_keywords = self.find_words_phrases_from_keywords(input.lower())
                print(detected_keywords)
                temp_impt_keywords.extend(detected_keywords)

            elif prompt_type == 'prompt_shows':
                # We will use NER to extract relevant topics
                detected_ner = self.ner_recognition(input)
                print(detected_ner)
                temp_impt_keywords.extend(detected_ner)

            elif prompt_type == 'prompt_actor':
                # We will use NER to extract relevant topics
                detected_ner = self.ner_recognition(input)
                print(detected_ner)
                temp_impt_keywords.extend(detected_ner)

            elif prompt_type == 'prompt_production_companies':
                detected_ner = self.ner_recognition(input)
                print(detected_ner)
                temp_impt_keywords.extend(detected_ner)

            elif prompt_type == 'prompt_themes':
                # This is the catch all part
                detected_ner = self.ner_recognition(input)
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

    def ner_recognition(self, input):
        #input_rejoin = " ".join(input)
        ner_results = self.ner_pipeline(input)

        entities = self.link_related_ner_together(ner_results)

        return entities

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
    
    def link_related_ner_together(self, ner_entities):
            i = 0
            keywords =  []
            while i < len(ner_entities):
                word = ner_entities[i]['word']
                next_num = i+1
                print(len(ner_entities)-1)
                if (next_num) > (len(ner_entities) - 1):
                    keywords.append(word)
                    i+=1
                else:
                    if '#' in ner_entities[i+1]['word']:
                        print('here')
                        keywords.append(word + ner_entities[i+1]['word'].lstrip('#'))
                        i+=2
                    else:
                        keywords.append(word)
                        i+=1
            return keywords
                    

<<<<<<< HEAD
    def qa_question_chatbot(self, movie_name):
        qa_model = QA_Chat("./models/distilbert-QuAC-SQUAD", movie_name)
        return qa_model

    def qa_mode(self):
        self.chatbot_mode = "qa"
        return "Switching to QA Mode. Type in the name of the movie you would like to answer Questions for"
=======

>>>>>>> parent of f44227c (change to master without models)

