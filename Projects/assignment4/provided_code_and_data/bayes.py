# Name: Andrew Kluge (ajk386), Vesko Cholakov (vgc917), Richard Gates Porter (rgp633)
# Date: May 22, 2015
# Description:
#
#

import math, os, pickle, re

class Bayes_Classifier:

   def __init__(self):
      """This method initializes and trains the Naive Bayes Sentiment Classifier.  If a 
      cache of a trained classifier has been stored, it loads this cache.  Otherwise, 
      the system will proceed through training.  After running this method, the classifier 
      is ready to classify input text."""
      # If the dictionaries exist, load them
      if (os.path.isfile("positive") and os.path.isfile("negative")):
         self.positive = self.load("positive")
         self.negative = self.load("negative")
         print "The dictionaries exist and won't be recalculated."
      else: 
         print "No existing dictionaries found."
         self.positive = {}
         self.negative = {}
         self.train()
         print "Dictionaries generated."


   def train(self):   
      """Trains the Naive Bayes Sentiment Classifier."""

      # Create a list IFileList which contains the file names of all movie reviews
      IFileList = []
      for fileObj in os.walk("movies_reviews/"):
         IFileList = fileObj[2]
         break

      # For each file
      for fileName in IFileList: 

         def updateFrequency(dictionary, word):
            """ Increments the frequency of the provided word in the provided dictionary. """
            # If word is alrady in dictionary, increment
            if (dictionary.has_key(word)):   
               dictionary[word] += 1
            else: # If not, initialize count to 1
               dictionary[word] = 1

         # Load content of review
         content = self.loadFile("movies_reviews/" + fileName)
         # Tokenize content
         tokenized = self.tokenize(content)

         # Determine the mood of the review.
         for word in tokenized:
            if (fileName[7] == "1"):
               updateFrequency(self.negative, word)
            elif (fileName[7] == "5"):
               updateFrequency(self.positive, word)

      # Save the dictionaries to disk
      self.save(self.negative, "negative")
      self.save(self.positive, "positive")
         
    
   def classify(self, sText):
      """Given a target string sText, the function returns the most likely document
      class to which the target string belongs (i.e., positive, negative or neutral).
      """

      negative_probability = 1
      positive_probability = 1 

      # Tokenize sText
      tokenized = self.tokenize(sText)

      # Get a list of all values in a dictionay
      pos_list = self.positive.values()
      neg_list = self.negative.values()

      # Sum over the list of values
      total_words_in_positive = sum(pos_list)
      total_words_in_negative = sum(neg_list) 


      # Run Bayes Classifier

      i = 0
      j = 0
      
      for word in tokenized:   # For each word in sText  
         if (self.positive.has_key(word)):  # Is word in positive dict?
            positive_probability += math.log(((self.positive[word] + 1.0) / total_words_in_positive))
            i += 1
         if (self.negative.has_key(word)):  # Is word in negative dict?
            negative_probability += math.log(((self.negative[word] + 1.0) / total_words_in_negative))
            j += 1

      positive_probability = positive_probability / i
      negative_probability = negative_probability / j

      diff = positive_probability - negative_probability 

      print diff

      if math.fabs(difference) <= 0.1: //shouldn't this be diff instead of difference?
         return "neutral"
      if diff > 0: 
         return "positive"
      else: 
         return "negative"


   def loadFile(self, sFilename):
      """Given a file name, return the contents of the file as a string."""
      f = open(sFilename, "r")
      sTxt = f.read()
      f.close()
      return sTxt
   
   def save(self, dObj, sFilename):
      """Given an object and a file name, write the object to the file using pickle."""
      f = open(sFilename, "w")
      p = pickle.Pickler(f)
      p.dump(dObj)
      f.close()
   
   def load(self, sFilename):
      """Given a file name, load and return the object stored in the file."""

      f = open(sFilename, "r")
      u = pickle.Unpickler(f)
      dObj = u.load()
      f.close()
      return dObj

   def tokenize(self, sText): 
      """Given a string of text sText, returns a list of the individual tokens that 
      occur in that string (in order)."""

      lTokens = []
      sToken = ""
      for c in sText:
         if re.match("[a-zA-Z0-9]", str(c)) != None or c == "\"" or c == "_" or c == "-":
            sToken += c
         else:
            if sToken != "":
               lTokens.append(sToken)
               sToken = ""
            if c.strip() != "":
               lTokens.append(str(c.strip()))
               
      if sToken != "":
         lTokens.append(sToken)

      return lTokens
