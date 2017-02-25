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

    def extract_movie_sentiment(input):
      return "pos"

    def extract_response(input):
      return "no"


    def starter_mode_response(self, input):
      matches = re.findall(self.pattern_for_movie_titles, input)
      if len(matches) == 0:
        if self.asked_for_another_recommendation or self.asked_to_continue:
          answer = self.extract_response(input)
          if answer == "no":
            self.quit_flag = True
            return "Goodbye!"
          else:
            if self.asked_for_another_recommendation:
              if len(self.movies_to_recommend) < 0 or self.index_in_movies_to_recommend >= len(self.movies_to_recommend):
                self.asked_for_another_recommendation = False
                self.asked_to_continue = True
                return "Sorry I cannot recommend you another movie. I have provided all the recommendations I have found. Would you like to continue talking with me?"
              else:
                response = "I further recommend" + self.movies_to_recommend[self.index_in_movies_to_recommend] + "."
                response = response + "Would you like to me to recommend another movie?"
                self.index_in_movies_to_recommend = self.index_in_movies_to_recommend + 1
                return response
            else:
              self.asked_to_continue = False
              return "Tell me a movie that you love or hate"
        else:
          return "Please tell me about ONE movie that you either did not like and put that movie title in QUOTES!!!"
      elif: len(matches) > 1:
        return "Tell me only one movie at a time please and thank you!!!"
      else:
        self.movie_titles_that_the_user_has_provided.append(matches)
        num_movies_user_has_provided = len(self.movie_titles_that_the_user_has_provided)
        response = ""
        sentiment = self.extract_movie_sentiment(input)
        if sentiment == "neg":
          response = response + "You did not like \"" + matches[0] + "\""
        else:
          response = response + "You liked \"" + matches[0] + "\""

        if num_movies_user_has_provided < self.minimum_number_of_recommendations_needed_by_the_chatbot:
          response = response + "Please tell me more! You intrigue me with your movie taste."
        else:
          response = response + "I have enough information to tell you a movie recommendation"
          find_movies_to_recommend()
          if len(self.movies_to_recommend) > 0:
            movie_to_recommend = self.movies_to_recommend[self.index_in_movies_to_recommend]
            response = response + "I recommend the following movie: \"" +  movie_to_recommend + "\""
          else:
            response = response + "Sorry I could not find any good recommendations. Tell me one more movie that you have seen!"


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
          if self.ratings.shape[r][c] > 2.5:
            self.binarized_ratings[r][c] = 1
          else
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
        norm_of_u = norm_of_u + (u[index]**2)
        norm_of_v = norm_of_v + (v[index]**2)
        sum_of_products_of_features = sum_of_products_of_features + (u[index]*v[index])

      similarity = float(sum_of_products_of_features) / (float(norm_of_u) * float(norm_of_v))

      return similarity




    def recommend(self, u):
      """Generates a list of movies based on the input vector u using
      collaborative filtering"""
      # TODO: Implement a recommendation function that takes a user vector u
      # and outputs a list of movies recommended by the chatbot
      num_movies = len(self.titles)

      list_of_user_movies = []
      number_of_features = u.shape[0]
      for index in xrange(0, number_of_features):
        if u[index] != 0:
          list_of_user_movies.append(index)


      movie_to_score_map = {}

      for movie_index in xrange(0, num_movies):
        if not movie_index in list_of_user_movies:
          movie_vector = np.transpose(np.matrix(self.ratings[movie_index]))
          sum_of_similarities = 0
          for user_movie_index in list_of_user_movies:
            user_movie_vector = np.transpose(np.matrix(self.ratings[user_movie_index]))
            sum_of_similarities = float(sum_of_similarities) + float(self.distance(movie, vector))
          movie_to_score_map[movie_vector] = sum_of_similarities

      number_of_movies = len(movie_to_score_map.keys())

      movies_sorted_by_decreasing_similarity = sorted(movie_to_score_map, key = movie_to_score_map,__getitem__, reverse=True)

      list_movie_titles_to_recommend = []
      for index in xrange(0, number_of_movies):
        list_movie_titles_to_recommend.append(self.titles[movies_sorted_by_decreasing_similarity[index]])

      return list_movie_titles_to_recommend

      


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
