#!/usr/bin/env python
# -*- coding: utf-8 -*-

# PA6, CS124, Stanford, Winter 2016
# v.1.0.2
# Original Python code by Ignacio Cases (@cases)
# Ported to Java by Raghav Gupta (@rgupta93) and Jennifer Lu (@jenylu)
######################################################################
import csv
import math
import re
import numpy as np
from PorterStemmer import *

from movielens import ratings
from random import randint

class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    #############################################################################
    # `moviebot` is the default chatbot. Change it to your chatbot's name       #
    #############################################################################
    def __init__(self, is_turbo=False):
      self.name = 'moviebot'
      self.is_turbo = is_turbo
      self.read_data()
      self.pattern_for_movie_titles = ".*?\"([^\"]+)\".*?"
      self.movie_titles_that_the_user_has_provided = []
      self.minimum_number_of_recommendations_needed_by_the_chatbot = 4
      self.max_minimum_number_of_recommendations_needed_by_the_chatbot = 10
      self.movies_to_recommend = []
      self.index_in_movies_to_recommend = 0
      self.negation_pattern = "neither|nor|never|no|nothing|nowhere|noone|none|not|havent|hasnt|hadnt|cant|couldnt|shouldnt|wont|wouldnt|dont|doesnt|didnt|isnt|arent|aint|[a-z]+n't"
      self.stopList = set(self.readFile('data/english.stop'))
      self.porter_stemmer = PorterStemmer()
      self.end_of_a_clause_pattern = "[\.:;!,?]"
      self.asked_for_another_recommendation = False 
      self.asked_to_continue = False
      self.possible_quotes_for_telling_how_to_quit_the_application = ["Sorry to hear that. Please enter \":quit\" to exit the application. Have a great day!",
                                                                      "All good things have to come to an end. You can exit the application by hitting \":quit\". Thank you for your time!",
                                                                      "Please enter \":quit\" to exit the application. Thank you!"]
      self.possible_quotes_for_telling_how_to_express_positive_sentiment_just_using_like = [("Wow! I like", "too!"), ("Awesome, I thought that", "was also a pretty good movie."), ("Yup, I remember watching", ". I had a great time!")]
      self.possible_quotes_for_telling_how_to_express_negative_sentiment_just_using_like = [("I agree that", "was not pretty good"), ("Finally I found someone that agrees with me about"), (". I did not have good time watching it.")]
      self.indices_of_movie_titles_submitted_by_user = []
      self.map_from_indices_of_movie_titles_submitted_by_user_to_binarized_rating_score = {}

    #############################################################################
    # 1. WARM UP REPL
    #############################################################################

    def greeting(self):
      """chatbot greeting message"""
      #############################################################################
      # TODO: Write a short greeting message                                      #
      #############################################################################

      greeting_message = "Hi! I'm MovieBot! I'm going to recommend a movie to you. First I will ask you about your taste in movies. Tell me about a movie that you have seen."

      #############################################################################
      #                             END OF YOUR CODE                              #
      #############################################################################

      return greeting_message

    def goodbye(self):
      """chatbot goodbye message"""
      #############################################################################
      # TODO: Write a short farewell message                                      #
      #############################################################################

      goodbye_message = "Thank you for hanging out with me! Stay in touch! Goodbye!"

      #############################################################################
      #                             END OF YOUR CODE                              #
      #############################################################################

      return goodbye_message


    #############################################################################
    # 2. Modules 2 and 3: extraction and transformation                         #
    #############################################################################

    def readFile(self, fileName):
      """
      * Code for reading a file.  you probably don't want to modify anything here, 
      * unless you don't like the way we segment files.
      """
      contents = []
      f = open(fileName)

      for line in f:
        contents.append(line)
      f.close()
      result = self.segmentWords('\n'.join(contents)) 
      return result

    
    def segmentWords(self, s):
      """
      * Splits lines on whitespace for file reading
      """
      return s.split()

    def filterStopWords(self, words):
      """Filters stop words."""
      filtered = []
      for word in words:
        if not word in self.stopList and word.strip() != '':
          filtered.append(word)
      return filtered

    def negate_words(self, words):
      we_have_seen_negative_word = False
      filtered_words = []
      for word in words:
        if(re.search(self.negation_pattern, word) != None):
          we_have_seen_negative_word = True
          filtered_words.append(word)
        elif(re.search(self.end_of_a_clause_pattern, word) != None):
          we_have_seen_negative_word = False
          filtered_words.append(word)
        elif(we_have_seen_negative_word):
          filtered_words.append("NEG_" + word)
        else:
          filtered_words.append(word)

      return filtered_words

    def extract_not(self, word):
      pattern = "NEG_(.+)"
      match_result = re.search(pattern, word)
      if match_result != None:
        return (match_result.group(1), True)
      else:
        return (word, False)

    def extract_out_punction(self, word):
      pattern  = "[\.:;!,?]*?([^\.:;!,?]+)[[\.:;!,?]*?"
      match_result = re.search(pattern, word)
      if match_result != None:
        return match_result.group(1)
      else:
        return word

    def calculate_sentiment_from_lexicon(self, words, type_of_sentiment):
      sentiment_value = 0.0
      for index, word in zip(range(0, len(words)), words):
        processed_word, opposite = self.extract_not(word)
        processed_word = self.extract_out_punction(processed_word)
        processed_word_stemmed = self.porter_stemmer.stem(processed_word, 0, len(processed_word) - 1)

        if processed_word_stemmed in self.sentiment.keys():
          isSentiment = (self.sentiment[processed_word_stemmed] == type_of_sentiment and not opposite) or (self.sentiment[processed_word_stemmed] != type_of_sentiment and opposite)
          if isSentiment:
            if index < (float(len(words)) / float(3)):
              sentiment_value = sentiment_value + 1
            elif index >= (float(len(words)) / float(3)) and index < ((2*float(len(words))) / float(3)):
              sentiment_value = sentiment_value + 2
            else:
              sentiment_value = sentiment_value + 4
        else:
          if processed_word in self.sentiment.keys():
            isSentiment = (self.sentiment[processed_word] == type_of_sentiment and not opposite) or (self.sentiment[processed_word] != type_of_sentiment and opposite)
            if isSentiment:
              if index < (float(len(words)) / float(3)):
                sentiment_value = sentiment_value + 1
              elif index >= (float(len(words)) / float(3)) and index < ((2*float(len(words))) / float(3)):
                sentiment_value = sentiment_value + 2
              else:
                sentiment_value = sentiment_value + 4
      return sentiment_value


    def extract_movie_sentiment(self, input):
      words_for_weights = []
      sentence_fragments = input.split("\"")
      sentence_fragments_excluding_those_enclosed_by_quotations = []
      num_sentence_fragments = len(sentence_fragments)
      for index in xrange(0, num_sentence_fragments):
        if index % 2 == 0:
          sentence_fragments_excluding_those_enclosed_by_quotations.append(sentence_fragments[index])
      for fragment in sentence_fragments_excluding_those_enclosed_by_quotations:
        possible_words = fragment.split(" ")
        for word in possible_words:
          if len(word) > 1:
            words_for_weights.append(word)

      words_for_weights = self.negate_words(words_for_weights)
      negative_sentiment = self.calculate_sentiment_from_lexicon(words_for_weights, "neg")
      positive_sentiment = self.calculate_sentiment_from_lexicon(words_for_weights, "pos")

      if abs(float(negative_sentiment) - float(positive_sentiment)) <= 0.00001:
        return "neutral"
      elif negative_sentiment > positive_sentiment:
        return "neg"
      else:
        return "pos"


    def extract_response_to_an_yes_or_no_question(self, input):
      pattern_for_no = ".*?(?:\\b[nN][oO]\\b|\\b[nN]\\b)(?:thank you|thanks)?.*?"
      pattern_for_yes = ".*?(?:\\b[yY]\\b|\\b[yY][eE][sS]\\b|\\b[yY][eE][aA][hH]\\b|\\b[yY][uU][pP])\\b.*?(?:\\b[pP][lL][eE][aA][sS][eE]\\b)?.*?(?:\\b[tT][hH][aA][nN][kK] [yY][oO][uU]\\b)?.*?"
      match_result_for_no = re.search(pattern_for_no, input)
      match_result_for_yes = re.search(pattern_for_yes, input)
      if match_result_for_no != None:
        return "no"
      elif match_result_for_yes != None:
        return "yes"
      else:
        return "neither"

    def movie_exists(self, user_movie_title):
      pattern_for_english_articles = "(An|A|The)\s(.+)"
      match_result = re.search(pattern_for_english_articles, user_movie_title)
      found_the_movie_in_movie_database = False
      index_of_movie_title_submitted_by_user = -1
      
      if match_result != None:
        movie_title_without_english_article = match_result.group(2)
        english_article = match_result.group(1)
        pattern = user_movie_title + "\s\(\d\d\d\d\).*?|" + movie_title_without_english_article + ",\s" + english_article + "\s\(\d\d\d\d\).*?"
        for index_movie_title in xrange(0, len(self.titles)):
          movie_title = self.titles[index_movie_title]
          match_result_for_movie_title = re.search(pattern, movie_title[0])
          if match_result_for_movie_title != None:
            index_of_movie_title_submitted_by_user = index_movie_title
            found_the_movie_in_movie_database = True
            break
      else:
        pattern_str = user_movie_title + "\s\(\d\d\d\d\).*?|" + "A\s" + user_movie_title + "\s\(\d\d\d\d\).*?|" + user_movie_title + ",\sA\s\(\d\d\d\d\).*?|" + "An\s" + user_movie_title + "\s\(\d\d\d\d\).*?|" + user_movie_title + ",\sAn\s\(\d\d\d\d\).*?|" + "The\s" + user_movie_title + "\s\(\d\d\d\d\).*?|" + user_movie_title + ",\sThe\s\(\d\d\d\d\).*?"
        pattern = re.compile(pattern_str)
        for index_movie_title in xrange(0, len(self.titles)):
          movie_title = self.titles[index_movie_title]
          match_result_for_movie_title = re.search(pattern_str, movie_title[0])
          if match_result_for_movie_title != None:
            index_of_movie_title_submitted_by_user = index_movie_title
            found_the_movie_in_movie_database = True
            break
      
      return (found_the_movie_in_movie_database, index_of_movie_title_submitted_by_user)

    def find_movies_to_recommend(self):
      self.binarize()
      self.recommend()


    def starter_mode_response(self, input):
      ##
      # Count the number of quotes in order to inform
      # the user if they are missing a closing or opening quote.
      ##
      number_of_quotes = 0  
      for c in input:
        if c == "\"":
          number_of_quotes = number_of_quotes + 1

      ##
      # Find all the pair of quotations that exist in the user's
      # input. 
      ##
      matches = re.findall(self.pattern_for_movie_titles, input)
      if len(matches) == 0:
        if self.asked_for_another_recommendation or self.asked_to_continue:
          answer = self.extract_response_to_an_yes_or_no_question(input)
          if answer == "no" and not self.asked_to_continue:
            self.asked_for_another_recommendation = False
            self.asked_to_continue = True
            self.map_from_indices_of_movie_titles_submitted_by_user_to_binarized_rating_score = {}
            self.movies_to_recommend = []
            self.index_in_movies_to_recommend = 0
            return "Would you like to continue providing more movies that you have seen?"
          elif answer == "no" and self.asked_to_continue:
            return "Please enter \":quit\" to exit the application. Thank you!"
          elif answer == "neither":
            return "Very sorry about this. But I did not understand what you just said. Can you give me a \"yes\"/\"no\" answer? Thank you!"
          else:
            if self.asked_for_another_recommendation:
              if len(self.movies_to_recommend) < 0 or self.index_in_movies_to_recommend >= len(self.movies_to_recommend):
                self.asked_for_another_recommendation = False
                self.asked_to_continue = True
                return " Sorry I cannot recommend you another movie. I have provided all the recommendations I have found. Would you like to continue talking with me? Please enter \"yes\" or \"no\". Thanks!"
              else:
                self.asked_for_another_recommendation = True
                self.asked_to_continue = False
                response = "I further recommend " + self.movies_to_recommend[self.index_in_movies_to_recommend] + "."
                response = response + " Would you like to me to recommend another movie? Please enter \"yes\" or \"no\". Thanks!"
                self.index_in_movies_to_recommend = self.index_in_movies_to_recommend + 1
                return response
            else:
              self.asked_to_continue = False
              return "Tell me a movie that you love or hate."
        else:
          return "Please tell me about ONE movie that you either did not like and put that movie title in QUOTES!!!"
      elif len(matches) > 1:
        return "Tell me only one movie at a time please and thank you!!!"
      else:
        if number_of_quotes % 2 == 0:
          movie_exists_result = self.movie_exists(matches[0])
          if movie_exists_result[0]:
            response = ""
            sentiment = self.extract_movie_sentiment(input)
            if sentiment == "neutral":
              response = response + "Can you tell me more information about \"" + matches[0] + "\"? Do you like it or hate it?"
            else:
              self.movie_titles_that_the_user_has_provided.append(matches[0])
              num_movies_user_has_provided = len(self.movie_titles_that_the_user_has_provided)
              self.indices_of_movie_titles_submitted_by_user.append(movie_exists_result[1])

              if sentiment == "neg":
                response = response + "You told me you did not like \"" + matches[0] + "\"."
                self.map_from_indices_of_movie_titles_submitted_by_user_to_binarized_rating_score[movie_exists_result[1]] = -1 
              else:
                response = response + "You told me you liked \"" + matches[0] + "\"."
                self.map_from_indices_of_movie_titles_submitted_by_user_to_binarized_rating_score[movie_exists_result[1]] = 1

              if num_movies_user_has_provided < self.minimum_number_of_recommendations_needed_by_the_chatbot:
                response = response + "Please tell me more! You intrigue me with your movie taste."
              else:
                response = response + " You have given me enough information to make a prediction."
                self.find_movies_to_recommend()
                if len(self.movies_to_recommend) > 0:
                  movie_to_recommend = self.movies_to_recommend[self.index_in_movies_to_recommend]
                  self.asked_to_continue = False
                  self.asked_for_another_recommendation = True
                  response = response + " I recommend the following movie: \"" +  movie_to_recommend + "\"" + " Would you like to me to recommend another movie, yes or no? Thank you!"
                  self.index_in_movies_to_recommend = self.index_in_movies_to_recommend + 1
                else:
                  self.asked_for_another_recommendation = False
                  self.asked_to_continue = True
                  response = response + " Sorry I could not find any good recommendations. Would you like to continue, yes or no?"
            return response
          else:
            return "Sorry I could not recognize the movie \"" + matches[0] + "\". If the movie is part of a series, please provide the full name of the specific entry of the series. In addition, check for punctuation and/or spelling errors. Otherwise, tell me another movie that you have seen."
        else:
          return "I recommend checking you quotations. You seemed to missing a beginning or closing quotation"  




    def process(self, input):
      """Takes the input string from the REPL and call delegated functions
      that
        1) extract the relevant information and
        2) transform the information into a response to the user
      """
      #############################################################################
      # TODO: Implement the extraction and transformation in this method, possibly#
      # calling other functions. Although modular code is not graded, it is       #
      # highly recommended                                                        #
      #############################################################################
      if self.is_turbo == True:
        response = 'processed %s in creative mode!!' % input
      else:
        response = self.starter_mode_response(input)
      return response

    #############################################################################
    # 3. Movie Recommendation helper functions                                  #
    #############################################################################

    def read_data(self):
      """Reads the ratings matrix from file"""
      # This matrix has the following shape: num_movies x num_users
      # The values stored in each row i and column j is the rating for
      # movie i by user j
      self.titles, self.ratings = ratings()
      reader = csv.reader(open('data/sentiment.txt', 'rb'))
      self.sentiment = dict(reader)


    def binarize(self):
      """Modifies the ratings matrix to make all of the ratings binary"""

      num_movies = self.ratings.shape[0]
      num_users = self.ratings.shape[1]
      self.binarized_ratings = np.zeros((num_movies, num_users))
      for r in xrange(0, num_movies):
        for c in xrange(0, num_users):
          if self.ratings[r][c] > 2.5:
            self.binarized_ratings[r][c] = 1
          else:
            self.binarized_ratings[r][c] = -1


    def distance(self, u, v):
      """Calculates a given distance function between vectors u and v"""
      # TODO: Implement the distance function between vectors u and v]
      # Note: you can also think of this as computing a similarity measure

      num_features = u.shape[0]
      norm_of_u = 0
      norm_of_v = 0
      sum_of_products_of_features = 0
      for index in xrange(0, num_features):
        norm_of_u = norm_of_u + (float(u[index])**2)
        norm_of_v = norm_of_v + (float(v[index])**2)
        sum_of_products_of_features = sum_of_products_of_features + (u[index]*v[index])

      norm_of_u = math.sqrt(float(norm_of_u))
      norm_of_v = math.sqrt(float(norm_of_v))

      similarity = float(sum_of_products_of_features) / (float(norm_of_u) * float(norm_of_v))

      return similarity




    def recommend(self):
      """Generates a list of movies based on the input vector u using
      collaborative filtering"""
      num_movies = len(self.titles)
      movie_to_score_map = {}

      for movie_index in xrange(0, num_movies):
        if not movie_index in self.indices_of_movie_titles_submitted_by_user:
          movie_vector = self.binarized_ratings[movie_index]
          sum_of_similarities = 0
          for user_movie_index in self.indices_of_movie_titles_submitted_by_user:
            user_movie_vector = self.binarized_ratings[user_movie_index]
            sum_of_similarities = float(sum_of_similarities) + (float(self.distance(movie_vector, user_movie_vector)) * self.map_from_indices_of_movie_titles_submitted_by_user_to_binarized_rating_score[user_movie_index])
          movie_to_score_map[movie_index] = sum_of_similarities

      number_of_movies = len(movie_to_score_map.keys())

      movies_sorted_by_decreasing_similarity = sorted(movie_to_score_map, key = movie_to_score_map.__getitem__, reverse=True)

      for index in xrange(0, number_of_movies):
        self.movies_to_recommend.append(self.titles[movies_sorted_by_decreasing_similarity[index]][0])



    #############################################################################
    # 4. Debug info                                                             #
    #############################################################################

    def debug(self, input):
      """Returns debug information as a string for the input string from the REPL"""
      # Pass the debug information that you may think is important for your
      # evaluators
      debug_info = 'debug info'
      return debug_info


    #############################################################################
    # 5. Write a description for your chatbot here!                             #
    #############################################################################
    def intro(self):
      return """
      Your task is to implement the chatbot as detailed in the PA6 instructions.
      Remember: in the starter mode, movie names will come in quotation marks and
      expressions of sentiment will be simple!
      Write here the description for your own chatbot!
      """


    #############################################################################
    # Auxiliary methods for the chatbot.                                        #
    #                                                                           #
    # DO NOT CHANGE THE CODE BELOW!                                             #
    #                                                                           #
    #############################################################################

    def bot_name(self):
      return self.name


if __name__ == '__main__':
    Chatbot()
