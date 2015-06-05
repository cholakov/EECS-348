# Andrew Kluge (ajk386), Vesko Cholakov (vgc917), Sophia Lou (sll411), Richard Gates Porter (rgp633)

import xml.dom.minidom
import copy
import guid
import math
import os
import random
#import matplotlib.pyplot as plt

# A couple contants
CONTINUOUS = 0
DISCRETE = 1

class HMM:
    ''' Code for a hidden Markov Model '''

    def __init__(self, states, features, contOrDisc, numVals):
        ''' Initialize the HMM.
            Input:
                states: a list of the hidden state possible values
                features: a list of feature names
                contOrDisc: a dictionary mapping feature names to integers
                    representing whether the feature is continuous or discrete
                numVals: a dictionary mapping names of discrete features to
                    the number of values that feature can take on. '''
        self.states = states 
        self.isTrained = False
        self.featureNames = features
        self.featuresCorD = contOrDisc
        self.numVals = numVals

        # All the probabilities start uninitialized until training
        self.priors = None
        self.emissions = None   #evidence model
        self.transitions = None #transition model

    def train(self, trainingData, trainingLabels):
        ''' Train the HMM on the fully observed data using MLE '''
        print "Training the HMM... "
        self.isTrained = True
        self.trainPriors( trainingData, trainingLabels )
        self.trainTransitions( trainingData, trainingLabels )
        self.trainEmissions( trainingData, trainingLabels ) 
        print "HMM trained"
        print "Prior probabilities are:", self.priors
        print "Transition model is:", self.transitions
        print "Evidence model is:", self.emissions
        #print "Possibile states are:", self.states    #######################
        #print "FeatureNames are:", self.featureNames 
        #print "numberVals:", self.numVals 

    def trainPriors( self, trainingData, trainingLabels ):
        ''' Train the priors based on the data and labels '''
        # Set the prior probabilities
        priorCounts = {}
        for s in self.states:
            priorCounts[s] = 0
        for labels in trainingLabels:
            priorCounts[labels[0]] += 1

        self.priors = {}
        for s in self.states:
            self.priors[s] = float(priorCounts[s])/len(trainingLabels)
        

    def trainTransitions( self, trainingData, trainingLabels ):
        ''' Give training data and labels, train the transition model '''
        # Set the transition probabilities
        # First initialize the transition counts
        transitionCounts = {}
        for s in self.states:
            transitionCounts[s] = {}
            for s2 in self.states:
                transitionCounts[s][s2] = 0
                
        for labels in trainingLabels:
            if len(labels) > 1:
                lab1 = labels[0]
                for lab2 in labels[1:]:
                    transitionCounts[lab1][lab2] += 1
                    lab1 = lab2
                    
        self.transitions = {}
        for s in transitionCounts.keys():
            self.transitions[s] = {}
            totForS = sum(transitionCounts[s].values())
            for s2 in transitionCounts[s].keys():
                self.transitions[s][s2] = float(transitionCounts[s][s2])/float(totForS)


    def trainEmissions( self, trainingData, trainingLabels ):
        ''' given training data and labels, train the evidence model.  '''
        self.emissions = {}
        featureVals = {}
        for s in self.states:
            self.emissions[s] = {}
            featureVals[s] = {}
            for f in self.featureNames:
                featureVals[s][f] = []

        # Now gather the features for each state
        for i in range(len(trainingData)):
            oneSketchFeatures = trainingData[i]
            oneSketchLabels = trainingLabels[i]
            
            for j in range(len(oneSketchFeatures)):
                features = oneSketchFeatures[j]
                for f in features.keys():
                    featureVals[oneSketchLabels[j]][f].append(features[f])

        # Do a slightly different thing for conituous vs. discrete features
        for s in featureVals.keys():
            for f in featureVals[s].keys():
                if self.featuresCorD[f] == CONTINUOUS:
                    # Use a gaussian representation, so just find the mean and standard dev of the data
                    # mean is just the sample mean
                    mean = sum(featureVals[s][f])/len(featureVals[s][f])
                    sigmasq = sum([(x - mean)**2 for x in featureVals[s][f]]) / len(featureVals[s][f])
                    sigma = math.sqrt(sigmasq)
                    self.emissions[s][f] = [mean, sigma]
                if self.featuresCorD[f] == DISCRETE:
                    # If the feature is discrete then the CPD is a list
                    # We assume that feature values are integer, starting
                    # at 0.  This assumption could be generalized.
                    counter = 0
                    self.emissions[s][f] = [1]*self.numVals[f]  # Use add 1 smoothing
                    for fval in featureVals[s][f]:
                        self.emissions[s][f][fval] += 1
                    # Now we have counts of each feature and we need to normalize
                    for i in range(len(self.emissions[s][f])):
                        self.emissions[s][f][i] /= float(len(featureVals[s][f])+self.numVals[f])

    def label(self, data):   
        ''' Find the most likely labels for the sequence of data
            This is an implementation of the Viterbi algorithm  '''

        sequences= {} # dictionary with sequences of all states for each stroke 
        probabilities= {} #dictionary holding probabilities for each state 
        labels = [] # array holding return value of labels 
        label = "" # initialized last label 

        for index in range(len(data)): # for each stroke's dictionary of features 
            dic = data[index] 
            sequences.update({index:{}}) # create dictionary entry for each stroke 

            if index == 0: # first stroke in data
                for state in self.states: # for each state 
                    prob = 1.0   
                    prob_state = self.priors[state] 
                    for f_name in self.featureNames: # for each feature name 
                        feature= dic[f_name] # array of probabilities for a feature 
                        prob_state_given_f = self.emissions[state][f_name][feature]
                        prob *= prob_state_given_f
                        #prob += math.log(abs(prob_state * prob_state_given_f))
                    prob *= prob_state
                    entry = {state:prob}
                    probabilities.update(entry) # update the initial set of probabilities 
            else: 
                new_prob = {} # dictionary to hold updated probabilities 
                for state in self.states: # for each state 
                    mapping = {} # holds all possible maximum probabilities for a state 
                    for state2 in self.states: # for each state 
                        prob = 1.0  
                        prob_prior = probabilities[state2] 
                        prob_transition = self.transitions[state2][state] 
                        for f_name in self.featureNames: # for each featurename 
                            feature = dic[f_name] 
                            prob_state_given_f = self.emissions[state][f_name][feature]
                            prob *= prob_state_given_f
                            #prob += math.log(abs(prob_prior * prob_transition * prob_state_given_f))
                        prob *= prob_prior * prob_transition 
                        mapping.update({state2:prob}) # add each probability to mapping dictionary 

                    # most likely previous state 
                    maximum_state = max(mapping, key=mapping.get)
                    # largest probability 
                    maximum_prob = mapping[maximum_state]
                    # update new probabilities 
                    new_prob.update({state:maximum_prob})
                    # add this possible sequence 
                    sequences[index].update({state:maximum_state})
                probabilities = copy.deepcopy(new_prob) # update probabilities 
            
        label = max(probabilities, key=probabilities.get) # last label 
        labels.append(label) # add to labels list 

        for timestep in range(len(data)-1,0,-1): # for each stroke 
            labels.insert(0,sequences[timestep][label]) # use last label to find previous 
            label = sequences[timestep][label] # update last label to previous 

        return labels 



    def getEmissionProb( self, state, features ):
        ''' Get P(features|state).
            Consider each feature independent so
            P(features|state) = P(f1|state)*P(f2|state)*...*P(fn|state). '''
        prob = 1.0
        for f in features:
            if self.featuresCorD[f] == CONTINUOUS:
                # calculate the gaussian prob
                fval = features[f]
                mean = self.emissions[state][f][0]
                sigma = self.emissions[state][f][1]
                g = math.exp((-1*(fval-mean)**2) / (2*sigma**2))
                g = g / (sigma * math.sqrt(2*math.pi))
                prob *= g
            if self.featuresCorD[f] == DISCRETE:
                fval = features[f]
                prob *= self.emissions[state][f][fval]
                
        return prob      

class StrokeLabeler:
    def __init__(self):
        ''' Inialize a stroke labeler. '''
        self.labels = ['text', 'drawing']
        # a map from labels in files to labels we use here
        drawingLabels = ['Wire', 'AND', 'OR', 'XOR', 'NAND', 'NOT']
        textLabels = ['Label']
        self.labels = ['drawing', 'text']
        
        self.labelDict = {}
        for l in drawingLabels:
            self.labelDict[l] = 'drawing'
        for l in textLabels:
            self.labelDict[l] = 'text'

        # Define the features to be used in the featurefy function
        # if you change the featurefy function, you must also change
        # these data structures.
        # featureNames is just a list of all features.
        # contOrDisc is a dictionary mapping each feature
        #    name to whether it is continuous or discrete
        # numFVals is a dictionary specifying the number of legal values for
        #    each discrete feature
        self.featureNames = ['length', 'curvature', 'ratio', 'area', 'duration']
        self.contOrDisc = {'length': DISCRETE, 'curvature': DISCRETE, 'ratio': DISCRETE, 'area': DISCRETE, 'duration': DISCRETE}
        self.numFVals = { 'length': 2, 'curvature': 2, 'ratio': 2, 'area': 2, 'duration': 2}

    def evaluate(self, trainingDir):
        """ Trains HMM with part of the files in trainingDir, and uses the other half for testing.
        Then, prints and returns a confusion matrix with the correctness of the classifications in the testing set. """

        sketchFiles = self.trainHMMHalfAndHalf(trainingDir)  # A list of paths to .xml files of sketches

        true = []               # true = a list with the true classification of the strokes
        classified = []         # classified = a list with classifications

        for sketchFile in sketchFiles:
            # Fetch true values
            true_single = self.loadLabeledFile(sketchFile)[1]            

            # Classify 
            strokes = self.loadStrokeFile(sketchFile)
            classified_single = self.labelStrokes(strokes)

            # Add to list only if all strokes have true labels (because otherwise the values gets mis-mathed)
            if (len(classified_single) == len(true_single)):
                classified.extend(classified_single)
                true.extend(true_single)

        matrix = self.confusion(true, classified)

        return matrix


    def confusion(self, trueLabels, classifications):
        """ Accepts a list of true labels and classified labels and returns a dictionary of the correctness of the estimation. """
        drawing_as_drawing = 0
        drawing_as_text = 0
        text_as_text = 0
        text_as_drawing = 0

        for i in range(len(trueLabels)):
            if trueLabels[i] == "drawing" and classifications[i] == "drawing":
                drawing_as_drawing += 1
            elif trueLabels[i] == "drawing" and classifications[i] == "text":
                drawing_as_text += 1
            elif trueLabels[i] == "text" and classifications[i] == "text":
                text_as_text += 1
            elif trueLabels[i] == "text" and classifications[i] == "drawing":
                text_as_drawing += 1

        cmatrix = {
                    'drawing': {'drawing': drawing_as_drawing, 'text': drawing_as_text}, 
                    'text': {'drawing': text_as_drawing, 'text': text_as_text}
                    }

        return cmatrix

    def featurefy( self, strokes ):
        ''' Converts the list of strokes into a list of feature dictionaries
            suitable for the HMM
            The names of features used here have to match the names
            passed into the HMM'''
        ret = []
        for s in strokes:
            d = {}  # The feature dictionary to be returned for one stroke

            # If we wanted to use length as a continuous feature, we
            # would simply use the following line to set its value
            #d['length'] = s.length()

            # To use it as a discrete feature, we have to "bin" it, that is
            # we define ranges for "short" (<300 units) and "long" (>=300 units)
            # Short strokes get a discrete value 0, long strokes get
            # discrete value 1.
            # Note that these bins were determined by trial and error, and my
            # looking at the length data, to determine what a good discriminating
            # cutoff would be.  You might choose to add more bins
            # or to change the thresholds.  For any other discrete feature you
            # add, it's up to you to determine how many and what bins you want
            # to use.  This is an important process and can be tricky.  Try
            # to use a principled approach (i.e., look at the data) rather
            # than just guessing.

            length = s.length()
            curvature = s.sumOfCurvature(abs)
            boundingBox = s.boundingBox()
            duration = s.duration()
            
            area = boundingBox[0]
            ratio = boundingBox[1]


            if length < 300:
                d['length'] = 0
            else:
                d['length'] = 1

            if curvature < 0.23:
                d['curvature'] = 0
            else:
                d['curvature'] = 1

            if area < 11500:
                d['area'] = 0
            else:
                d['area'] = 1

            if ratio < 1.27:
                d['ratio'] = 0
            else:
                d['ratio'] = 1

            if duration < 285:
                d['duration'] = 0
            else:
                d['duration'] = 1


            # We can add more features here just by adding them to the dictionary
            # d as we did with length.  Remember that when you add features,
            # you also need to add them to the three member data structures
            # above in the contructor: self.featureNames, self.contOrDisc,
            #    self.numFVals (for discrete features only)


            ret.append(d)  # append the feature dictionary to the list
            
        return ret
    
    def trainHMM( self, trainingFiles ):
        ''' Train the HMM '''
        self.hmm = HMM( self.labels, self.featureNames, self.contOrDisc, self.numFVals )
        allStrokes = []
        allLabels = []
        for f in trainingFiles:
            strokes, labels = self.loadLabeledFile( f )
            allStrokes.append(strokes)
            allLabels.append(labels)
        allObservations = [self.featurefy(s) for s in allStrokes]
        self.hmm.train(allObservations, allLabels)

    def trainHMMDir( self, trainingDir ):
        ''' Train the HMM on all the files in a training directory '''
        for fFileObj in os.walk(trainingDir):
            lFileList = fFileObj[2]
            break
        goodList = []
        for x in lFileList:
            if not x.startswith('.'):
                goodList.append(x)
        
        tFiles = [ trainingDir + "/" + f for f in goodList ] 
        self.trainHMM(tFiles)


    def trainHMMHalfAndHalf( self, trainingDir ):
        ''' Train the HMM with half of the files in trainingDir. Return a list of paths to the other half for testing. '''
        for fFileObj in os.walk(trainingDir):
            lFileList = fFileObj[2]
            break
        goodList = []
        for x in lFileList:
            if not x.startswith('.'):
                goodList.append(x)
        
        tFiles = [ trainingDir + "/" + f for f in goodList ] 

        training = random.sample(set(tFiles), len(tFiles)/10*9)    # Randomly choose half of of the files to be for training
        testing = list(set(tFiles) - set(training))     # Find the difference between the two sets

        self.trainHMM(training)
        return testing


    def featureTest( self, trainingDir ):
        ''' Loads all files in the training directory and returns a list of values for drawings and for text.'''

        sketchFiles = self.trainHMMHalfAndHalf(trainingDir)  # A list of paths to .xml files of sketches

        drawing = []
        text = []

        for sketchFile in sketchFiles:
            strokes, labels = self.loadLabeledFile( sketchFile )
            for i in range(len(strokes)):
                if (labels[i] == "drawing"):
                    drawing.append(strokes[i].length())
                elif (labels[i] == "text"):
                   text.append(strokes[i].length())

        print drawing
        print text
        return drawing, text 

        #strokes, labels = self.loadLabeledFile( strokeFile )
        #print " "
        #print strokes[i].substrokeIds[0]
        #print "Label is", labels[i]
        #print "Length is", strokes[i].length()
        #print "Curvature is", strokes[i].sumOfCurvature(abs)
    
    def labelFile( self, strokeFile, outFile ):
        ''' Label the strokes in the file strokeFile and save the labels
            (with the strokes) in the outFile '''
        print "Labeling file", strokeFile
        strokes = self.loadStrokeFile( strokeFile )
        labels = self.labelStrokes( strokes )
        print "Labeling done, saving file as", outFile
        self.saveFile( strokes, labels, strokeFile, outFile )

    def labelStrokes( self, strokes ):
        ''' return a list of labels for the given list of strokes '''
        if self.hmm == None:
            print "HMM must be trained first"
            return []
        strokeFeatures = self.featurefy(strokes)
        return self.hmm.label(strokeFeatures)

    def saveFile( self, strokes, labels, originalFile, outFile ):
        ''' Save the labels of the stroke objects and the stroke objects themselves
            in an XML format that can be visualized by the labeler.
            Need to input the original file from which the strokes were read
            so that we can retrieve a lot of data that we don't store here'''
        sketch = xml.dom.minidom.parse(originalFile)
        # copy most of the data, including all points, substrokes, strokes
        # then just add the shapes onto the end
        impl =  xml.dom.minidom.getDOMImplementation()
        
        newdoc = impl.createDocument(sketch.namespaceURI, "sketch", sketch.doctype)
        top_element = newdoc.documentElement

        # Add the attibutes from the sketch document
        for attrib in sketch.documentElement.attributes.keys():
            top_element.setAttribute(attrib, sketch.documentElement.getAttribute(attrib))

        # Now add all the children from sketch as long as they are points, strokes
        # or substrokes
        sketchElem = sketch.getElementsByTagName("sketch")[0]
        for child in sketchElem.childNodes:
            if child.nodeType == xml.dom.Node.ELEMENT_NODE:
                if child.tagName == "point":
                    top_element.appendChild(child)
                elif child.tagName == "shape":
                    if child.getAttribute("type") == "substroke" or \
                       child.getAttribute("type") == "stroke":
                        top_element.appendChild(child)    

        # Finally, add the new elements for the labels
        for i in range(len(strokes)):
            # make a new element
            newElem = newdoc.createElement("shape")
            # Required attributes are type, name, id and time
            newElem.setAttribute("type", labels[i])
            newElem.setAttribute("name", "shape")
            newElem.setAttribute("id", guid.generate() )
            newElem.setAttribute("time", str(strokes[i].points[-1][2]))  # time is finish time

            # Now add the children
            for ss in strokes[i].substrokeIds:
                ssElem = newdoc.createElement("arg")
                ssElem.setAttribute("type", "substroke")
                ssElem.appendChild(newdoc.createTextNode(ss))
                newElem.appendChild(ssElem)
                
            top_element.appendChild(newElem)
            

        # Write to the file
        filehandle = open(outFile, "w")
        newdoc.writexml(filehandle)
        filehandle.close()

        # unlink the docs
        newdoc.unlink()
        sketch.unlink()

    def loadStrokeFile( self, filename ):
        ''' Read in a file containing strokes and return a list of stroke
            objects '''
        sketch = xml.dom.minidom.parse(filename)
        # get the points
        points = sketch.getElementsByTagName("point")
        pointsDict = self.buildDict(points)
    
        # now get the strokes by first getting all shapes
        allShapes = sketch.getElementsByTagName("shape")
        shapesDict = self.buildDict(allShapes)

        strokes = []
        for shape in allShapes:
            if shape.getAttribute("type") == "stroke":
                strokes.append(self.buildStroke( shape, shapesDict, pointsDict ))

        # I THINK the strokes will be loaded in order, but make sure
        if not self.verifyStrokeOrder(strokes):
            print "WARNING: Strokes out of order"

        sketch.unlink()
        return strokes

    def verifyStrokeOrder( self, strokes ):
        ''' returns True if all of the strokes are temporally ordered,
            False otherwise. '''
        time = 0
        ret = True
        for s in strokes:
            if s.points[0][2] < time:
                ret = False
                break
            time = s.points[0][2]
        return ret

    def buildDict( self, nodesWithIdAttrs ):
        ret = {}
        for n in nodesWithIdAttrs:
            idAttr = n.getAttribute("id")
            ret[idAttr] = n
        
        return ret

    def buildStroke( self, shape, shapesDict, pointDict ):
        ''' build and return a stroke object by finding the substrokes and points
            in the shape object '''
        ret = Stroke( shape.getAttribute("id") )
        points = []
        # Get the children of the stroke
        last = None
        for ss in shape.childNodes:
            if ss.nodeType != xml.dom.Node.ELEMENT_NODE \
               or ss.getAttribute("type") != "substroke":
                continue

            # Add the substroke id to the stroke object
            ret.addSubstroke(ss.firstChild.data)
            
            # Find the shape with the id of this substroke
            ssShape = shapesDict[ss.firstChild.data]

            # now get all the points associated with this substroke
            # We'll filter points that don't move here
            for ptObj in ssShape.childNodes:
                if ptObj.nodeType != xml.dom.Node.ELEMENT_NODE \
                   or ptObj.getAttribute("type") != "point":
                    continue
                pt = pointDict[ptObj.firstChild.data]
                x = int(pt.getAttribute("x"))
                y = int(pt.getAttribute("y"))
                time = int(pt.getAttribute("time"))
                if last == None or last[0] != x or last[1] != y:  # at least x or y is different
                    points.append((x, y, time))
                    last = (x, y, time)
        ret.setPoints(points)
        return ret
                
    def loadLabeledFile( self, filename ):
        ''' load the strokes and the labels for the strokes from a labeled file.
            return the strokes and the labels as a tuple (strokes, labels) '''
        sketch = xml.dom.minidom.parse(filename)
        # get the points
        points = sketch.getElementsByTagName("point")
        pointsDict = self.buildDict(points)
    
        # now get the strokes by first getting all shapes
        allShapes = sketch.getElementsByTagName("shape")
        shapesDict = self.buildDict(allShapes)

        strokes = []
        substrokeIdDict = {}
        for shape in allShapes:
            if shape.getAttribute("type") == "stroke":
                stroke = self.buildStroke( shape, shapesDict, pointsDict )
                strokes.append(self.buildStroke( shape, shapesDict, pointsDict ))
                substrokeIdDict[stroke.strokeId] = stroke
            else:
                # If it's a shape, then just store the label on the substrokes
                for child in shape.childNodes:
                    if child.nodeType != xml.dom.Node.ELEMENT_NODE \
                       or child.getAttribute("type") != "substroke":
                        continue
                    substrokeIdDict[child.firstChild.data] = shape.getAttribute("type")

        # I THINK the strokes will be loaded in order, but make sure
        if not self.verifyStrokeOrder(strokes):
            print "WARNING: Strokes out of order"

        # Now put labels on the strokes
        labels = []
        noLabels = []
        for stroke in strokes:
            # Just give the stroke the label of the first substroke in the stroke
            ssid = stroke.substrokeIds[0]
            if not self.labelDict.has_key(substrokeIdDict[ssid]):
                # If there is no label, flag the stroke for removal
                noLabels.append(stroke)
            else:
                labels.append(self.labelDict[substrokeIdDict[ssid]])

        for stroke in noLabels:
            strokes.remove(stroke)
            
        sketch.unlink()
        if len(strokes) != len(labels):
            print "PROBLEM: number of strokes and labels must match"
            print "numStrokes is", len(strokes), "numLabels is", len(labels)
        return strokes, labels

class Stroke:
    ''' A class to represent a stroke (series of xyt points).
        This class also has various functions for computing stroke features. '''
    def __init__(self, strokeId):
        self.strokeId = strokeId
        self.substrokeIds = []   # Keep around the substroke ids for writing back to file
        
    def __repr__(self):
        ''' Return a string representation of the stroke '''
        return "[Stroke " + self.strokeId + "]"

    def addSubstroke( self, substrokeId ):
        ''' Add a substroke Id to the stroke '''
        self.substrokeIds.append(substrokeId)

    def setPoints( self, points ):
        ''' Set the points for the stroke '''
        self.points = points


    # Feature functions follow this line
    def length( self ):
        ''' Returns the length of the stroke '''
        ret = 0
        prev = self.points[0]
        for p in self.points[1:]:
            # use Euclidean distance
            xdiff = p[0] - prev[0]
            ydiff = p[1] - prev[1]
            ret += math.sqrt(xdiff**2 + ydiff**2)
            prev = p
        return ret

    def sumOfCurvature(self, func=lambda x: x, skip=1):
        ''' Return the normalized sum of curvature for a stroke.
            func is a function to apply to the curvature before summing
                e.g., to find the sum of absolute value of curvature,
                you could pass in abs
            skip is a smoothing constant (how many points to skip)
        '''
        if len(self.points) < 2*skip+1:
            return 0
        ret = 0
        second = self.points[0]
        third = self.points[1*skip]
        for p in self.points[2*skip::skip]:
            
            first = second
            second = third
            third = p
            ax = second[0] - first[0]
            ay = second[1] - first[1]
            bx = third[0] - second[0]
            by = third[1] - second[1]
            
            lena = math.sqrt(ax**2 + ay**2)
            lenb = math.sqrt(bx**2 + by**2)

            dotab = ax*bx + ay*by
            arg = float(dotab)/float(lena*lenb)

            # Fix floating point precision errors
            if arg > 1.0:
                arg = 1.0
            if arg < -1.0:
                arg = -1.0

            curv = math.acos(arg)

            # now we have to find the sign of the curvature
            # get the angle betwee the first vector and the x axis
            anga = math.atan2(ay, ax)
            # and the second
            angb = math.atan2(by, bx)
            # now compare them to get the sign.
            if not(angb < anga and angb > anga-math.pi):
                curv *= -1
            ret += func(curv)

        return ret / len(self.points)

    def boundingBox(self):
        ''' Returns bounding boxed area of a stroke. ''' 
        allPoints = self.points 
        all_x = []
        all_y = []
        for point in allPoints: # for each point's tuple 
            all_x.append(point[0])
            all_y.append(point[1])

        x_max = max(all_x)
        x_min = min(all_x)
        y_max = max(all_y)
        y_min = min(all_y)
        xdiff = x_max - x_min + 0.0 
        ydiff = y_max - y_min + 0.0
        area = xdiff * ydiff
        if xdiff == 0:
            xdiff = 0.00001 
        ratio = ydiff / xdiff 
        return area, ratio 

    def duration(self):
        """ Returns the time taken for drawing a stroke. """
        allPoints = self.points 
        duration = allPoints[len(allPoints)-1][2] - allPoints[0][2]
        return duration



# Part 1 Viterbi Testing Example
def ViterbiTestingExample():
    """ Part 1 Viterbi Testing Example as requested in the assignment PDF. """

    states = ['sunny','cloudy','rainy']
    featureNames = ['groundState']
    numVals = { 'groundState': 3 }

    x = HMM(states, featureNames, 0, numVals)

    x.priors = {'sunny': 0.63, 'cloudy': 0.17, 'rainy': 0.2}
    x.emissions = {'sunny':{'groundState': [0.6,0.15,0.05]}, 'cloudy':{'groundState': [0.25,0.25,0.25]}, 'rainy':{'groundState': [0.05,0.35,0.5]}}
    x.transitions = {'sunny':{'sunny':0.5 ,'cloudy':0.375 ,'rainy':0.125 },'cloudy':{'sunny':0.25 ,'cloudy':0.125 ,'rainy':0.625 }, 'rainy':{'sunny':0.25 ,'cloudy':0.375 ,'rainy':0.375 }}

    observed = [ {'groundState':0}, {'groundState':1}, {'groundState':2}, {'groundState':1} ]

    print x.label(observed)

    # Runing ViterbiTestingExample() and printing probabilities in label(self, data), we get the following probabilities:
    # -------------------------------------------------------------------------------------------------------------------
    # {'rainy': 0.010000000000000002, 'sunny': 0.378, 'cloudy': 0.0425}
    # {'rainy': 0.0165375, 'sunny': 0.02835, 'cloudy': 0.0354375}
    # {'rainy': 0.01107421875, 'sunny': 0.0007087500000000001, 'cloudy': 0.0026578125}
    # {'rainy': 0.0014534912109374998, 'sunny': 0.00041528320312499996, 'cloudy': 0.0010382080078124999}
