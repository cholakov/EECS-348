# Name: Andrew Kluge (ajk386), Vesko Cholakov (vgc917), Sophia Lou (sll411), Richard Gates Porter (rgp633)
# Date: May 22, 2015
# Description: Bayes Classifier to determine whether a given review is positive or negative
#
#

import math, os, pickle, re, random

class Bayes_Classifier:

   def __init__(self):
      """This method initializes and trains the Naive Bayes Sentiment Classifier.  If a 
      cache of a trained classifier has been stored, it loads this cache.  Otherwise, 
      the system will proceed through training.  After running this method, the classifier 
      is ready to classify input text."""

      # Create a list IFileList which contains the file names of all movie reviews
      self.IFileList = []
      for fileObj in os.walk("movies_reviews/"):
         self.IFileList = fileObj[2]
         break

      # If the dictionaries exist, load them
      if (os.path.isfile("positive") and os.path.isfile("negative")):
         self.positive = self.load("positive")
         self.negative = self.load("negative")
         print "Unigram dictionaries exist and won't be recalculated."
      else: 
         print "No unigram dictionaries found. Generating now..."

         # Generate dictionaries
         dictionaries = self.train()
         
         # Assign the dictionaries to classifier
         self.negative = dictionaries[0]
         self.positive = dictionaries[1]

         # Save the dictionaries to file
         self.save(dictionaries[0], "negative")
         self.save(dictionaries[1], "positive")
         
         print "Dictionaries generated."


   def crossValidate(self):
      """ Runs a 10-fold cross validation and returns performance stats. """

      print "10-fold cross validation started. Please be patient."

      # Create a list IFileList which contains the file names of all movie reviews
      IFileList = []
      for fileObj in os.walk("movies_reviews/"):
         IFileList = fileObj[2]
         break

      # Temporarily, save the original dictionaries to new variables
      positiveOriginal = self.positive
      negativeOriginal = self.negative

      # Run cross-validation 10 times
      for num in range(1,11):

         # Divide the files of the movie reviews into training and testing sets
         testData = random.sample(set(IFileList), len(IFileList)/10)
         trainData = set(IFileList) - set(testData)

         # Generate dictionaires
         dictionaries = self.train(trainData)

         self.negative = dictionaries[0]
         self.positive = dictionaries[1]

         trueNegative = 0
         truePositive = 0
         falsePositive = 0
         falseNegative = 0
         numPos = 0
         numNeg = 0

         for reviewId in testData:
            # Load content of review
            content = self.loadFile("movies_reviews/" + reviewId)
            sentiment = self.classify(content)

            if (reviewId[7] == "1"):
               numNeg += 1
            else:
               numPos += 1

            if ((reviewId[7] == "1" and sentiment == "negative")):
               trueNegative += 1
            elif ((reviewId[7] == "5" and sentiment == "positive")):
               truePositive += 1
            elif ((reviewId[7] == "1" and sentiment == "positive")):
               falsePositive += 1
            elif ((reviewId[7] == "5" and sentiment == "negative")):
               falseNegative += 1



         Precision_Pos = float(truePositive) / float(truePositive + falsePositive)
         Precision_Neg = float(trueNegative) / float(trueNegative + falseNegative)

         Recall_Pos = float(truePositive) / float(numPos)
         Recall_Neg = float(trueNegative) / float(numNeg)

         fMeasure_Pos = 2 * (float(Precision_Pos) * float(Recall_Pos)) / float(Precision_Pos + Recall_Pos)
         fMeasure_Neg = 2 * (float(Precision_Neg) * float(Recall_Neg)) / float(Precision_Neg + Recall_Neg)

         print "Cross Validation #" + str(num)
         print "POSITIVE: Precision " + str(Precision_Pos) + ". Recall " + str(Recall_Pos) + ". F-measure " + str(fMeasure_Pos)
         print "NEGATIVE: Precision " + str(Recall_Neg) + ". Recall " + str(Recall_Neg) + ". F-measure " + str(fMeasure_Neg)
         

      # Restore the original dictionaries
      self.positive = positiveOriginal
      self.negative = negativeOriginal

   def train(self, IFileList = -1):   
      """Trains the Naive Bayes Sentiment Classifier over movie reviews which should be passed as an argument. """

      if (IFileList == -1):
         IFileList = self.IFileList
         
      negative = {}
      positive = {}

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
               updateFrequency(negative, word)
            elif (fileName[7] == "5"):
               updateFrequency(positive, word)

      return negative, positive
         
    
   def classify(self, sText):
      """Given a target string sText, the function returns the most likely document
      class to which the target string belongs (i.e., positive, negative or neutral).
      """
      # initialization 
      negative_probability = 0
      positive_probability = 0 

      # Tokenize sText
      tokenized = self.tokenize(sText)

      # Get a list of all values in a dictionay
      pos_list = self.positive.values()
      neg_list = self.negative.values()

      # Sum over the list of values
      total_words_in_positive = sum(pos_list)
      total_words_in_negative = sum(neg_list) 


      # Run Bayes Classifier
      # Fixes undewflow and uses add 1 smoothing 

      i = 0
      j = 0
      
      for word in tokenized:   # For each word in sText  
         if (self.positive.has_key(word)):  # Is word in positive dict?
            positive_probability += math.log(((self.positive[word] + 1.0) / total_words_in_positive))
            i += 1
         if (self.negative.has_key(word)):  # Is word in negative dict?
            negative_probability += math.log(((self.negative[word] + 1.0) / total_words_in_negative))
            j += 1

      if i == 0:
         i = 1
      if j == 0:
         j = 1 

      # Normalize for the length of the review 
      positive_probability = positive_probability / i
      negative_probability = negative_probability / j

      diff = positive_probability - negative_probability 

      if math.fabs(diff) <= 0.1: 
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
