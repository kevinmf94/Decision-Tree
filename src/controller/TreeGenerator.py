import math
import numpy as np
import TreeVisualization as tv
import NodeOfTree as nt
import copy
class TreeGenerator:
    _nameOfAttributes = []
    _dictNameAttributesOriginalPos = {}
    _db = None
    _nparams = 0
    _paramobj = 0
    _tree = None
    _visualizationTree = None
    _listOfContinuous = []
    limitToStopSplit = 100
    posOfNodeInChildsList = 0
    databasePos = 0
    labelPos = 1
    valuePos = 2
    probabilityPos = 3
    def __init__(self, db, nameOfAttributes, paramobj=-1,tree = None):
        self._db = db
        self._nameOfAttributes = nameOfAttributes
        self._paramobj = paramobj
        self._tree = tree
        self._visualizationTree = tv.TreeVisualization()
        self._dictNameAttributesOriginalPos = {}
        #inicialization of dictionary
        i = 0
        for name in self._nameOfAttributes:
            if self._dictNameAttributesOriginalPos.has_key(name):
                raise Exception("ERROR initing TreeGenerator: name of attribute duplicated?")
            self._dictNameAttributesOriginalPos[name] = i
            i+=1

    """
    This function takes a dataBase or frame of dataBase and calculates his entropy. "attribute" commonly will be the paramObjective
    Important: This function counts that attribute is discrete. If paramObj not is discrete please, discretitze it of change this
    shit of dataBase.
    """
    def calculateEntropyOfOneAttribute(self, dataBase = None, attribute = -1):
        if dataBase is None:
            print 'In the call to "calculateEntropyOfOneAttribute" you\'re using the default dataBase, check if it\'s really that you want'
            dataBase = self._db
        differentValues, count = np.unique(dataBase[:,attribute], return_counts=True)
        totalLength = np.shape(dataBase[:,attribute])[0]
        entropy = 0
        for pos in range(np.shape(differentValues)[0]):

            p = (count[pos]/float(totalLength))
            entropy -= (p)*math.log(p,2)
        return entropy
    """
    This function takes a dataBase or frame of dataBase, and returns the median entryopy of param objective (paramObj) filtered by
    a parameter param.
    IMPORTANT: This function only works with discretes attributes. You must to discretize "param" if is continuos before to call it.
    """
    def entropyOfParamWithParamObjective(self, param, dataBase = None, paramObj = -1):
        #calculate de different values of param
        if dataBase is None:
            print 'In the call to "entropyOfParam" you\'re using the default dataBase, check if it\'s really that you want'
            dataBase = self._db
        arrayParam = dataBase[:,param]
        differentValuesOfCases, countOfCases = np.unique(arrayParam, return_counts=True)
        totalLength = np.shape(arrayParam)[0]
        #for each different value calculate the entropy with paramObj attribute
        entropy = 0
        for pos in range(np.shape(differentValuesOfCases)[0]):
            dataBaseFilteredByParamValue = dataBase[dataBase[:,param] == differentValuesOfCases[pos]]
            #Calculates the entropy of the attribute in this new filtered case. And have the ponderated sum
            entropy+= (countOfCases[pos]/float(totalLength))*self.calculateEntropyOfOneAttribute(dataBase=dataBaseFilteredByParamValue, attribute=paramObj)
        return entropy
    """
    This function returns the entropy of an continuous attribute, and if you check the flag "returnThresholdAndTwoDatabasses" the return value will
    be (entropy, threshold, databaseL, databaseGE), if you not check, the return will be the (entropy, pLess, pGE, threshold, dBL, dbGE)
    """
    def entropyOfParamContinuousWithParamObjective(self, param, dataBase = None, paramObj = -1, threshold = None, dataBaseL = None, dataBaseGE=None,
                                                   returnThresholdAndTwoDatabases = False):
        if threshold is None:
            threshold = self.bestThresholdForContinuousAttribute(attributeNumber=param, dataBase=dataBase)
        dataBaseL, dataBaseGE = self.getTwoDatabasesForContinuousAtt(dataBase = dataBase,attributeNumber=param,threshold=threshold)
        onlyMyParam = dataBase[:, param]
        totalLength = float(np.shape(onlyMyParam)[0])
        lengthOfLDB = np.shape(dataBaseL[:,param])[0]
        lengthOfGEDB = np.shape(dataBaseGE[:, param])[0]
        entropy = 0
        #Calcul of the Less Database
        pLess = (lengthOfLDB/totalLength)
        entropy+=pLess*self.calculateEntropyOfOneAttribute(dataBase=dataBaseL, attribute=paramObj)
        #Calcul of the GE DataBase
        pGreaterOrEqual = (lengthOfGEDB/totalLength)
        entropy+= pGreaterOrEqual*self.calculateEntropyOfOneAttribute(dataBase=dataBaseGE, attribute=paramObj)
        #stops for not fall in infinite bucles
        if totalLength<self.limitToStopSplit:
            entropy = 0
        if returnThresholdAndTwoDatabases:
            return entropy, threshold, dataBaseL, dataBaseGE
        else:
            return entropy,pLess, pGreaterOrEqual

    """
    This function returns a list of tuples. The tuples are -> (param, entropyOfParam)
    """
    def getEntropysOfAllAttributes(self, dataBase = None, paramObj = -1):
        if dataBase is None:
            print 'In the call to "getIndexOfBestAttribute" you\'re using the default dataBase, check if it\'s really that you want'
            dataBase = self._db
        if paramObj == -1:
            paramObj = (np.shape(dataBase)[1])-1
        listOfParamEntropys = []
        for param in range(np.shape(dataBase)[1]):
            if param != paramObj:
                #if is an continuous param
                try:
                    float(dataBase[0][param])
                    entropyOfParam, pLess, pGreaterOrEqual = self.entropyOfParamContinuousWithParamObjective(param = param, dataBase=dataBase)
                    listOfParamEntropys.append((param, entropyOfParam, pLess, pGreaterOrEqual))
                except:
                #if is an discrete param
                    entropyOfParam = self.entropyOfParamWithParamObjective(param = param, dataBase= dataBase, paramObj = paramObj)
                    listOfParamEntropys.append((param, entropyOfParam))
        return listOfParamEntropys
    #Take a parameter an gets his split info
    def getSplitInfoOfParameter(self, dataBase, parameter):
        arrayParam = dataBase[:, parameter]
        differentValuesOfCases, countOfCases = np.unique(arrayParam, return_counts=True)
        totalLength = np.shape(arrayParam)[0]
        splitInfo = 0.0001
        for valueCount in countOfCases:
            p = valueCount / float(totalLength)
            splitInfo -= p * math.log(p, 2)
        return splitInfo
    """
    This function takes an continuous attribute and returns the best limit for have an split
    """
    def bestThresholdForContinuousAttribute(self, attributeNumber, dataBase): #actualContinuousList):

        #if not actualContinuousList[attributeNumber]:
         #   print dataBase[:, attributeNumber]
          #  raise Exception("This attribute is not continuous")
        differentValues, index= np.unique(dataBase[:,-1], return_inverse=True)
        limits =[]
        for i in range(np.shape(differentValues)[0]):
            dataBaseActual = dataBase[index == i]
            try:
                data = (dataBaseActual[:,attributeNumber]).astype(float)
            except:
                print dataBase[:, attributeNumber]
                raise Exception("Data arribed that is not float?")
            mean = np.mean(data)
            limits.append(mean)
        return np.mean(limits)

    """
    This function takes a database an attributeNumber and a threshold and returns two databases.
    First with elements where the attributeNumber take a value LESS than threshold, and second
    with elements where the atribute number take a value GREATER or EQUAL than threshold.
    """
    def getTwoDatabasesForContinuousAtt(self, dataBase, attributeNumber, threshold):
        dataBaseL = dataBase[dataBase[:,attributeNumber].astype(float) < threshold]
        dataBaseGE = dataBase[dataBase[:,attributeNumber].astype(float) >= threshold]
        return dataBaseL, dataBaseGE


    """
    Case1:
    This function takes the generalEntropy in a moment and a listOfTuples that contains -> (atribute, entropyOfAttribute)
    (The same that returns the "getEntropysOfAllAttributes" function) and returns the attributte with best gain.
    Case2:
    This function takes a dataBase (that is the state of db in a moment) and return the best parameter for divide using ID3
    """
    def getAttributeWithBestGain(self, dataBase = None, paramObj = -1, generalEntropy = None, listOfParams = None,
                                 paramPlaceOnTuple = 0, entropyPlaceOnTuple = 1,ID3=False, C45 = False):
        if ID3 == C45:
            raise Exception ("ERROR in getAttribute with bestGain, you must tu activate flag of ID3 or C45. ONLY ONE!")
        if (generalEntropy is None) or (listOfParams is None):
            if dataBase is None :
                raise Exception("ERROR in function getAttributeWithBestGain: if you not define a generalEntropy\n"
                                +" and listOfParams, you must to define dataBase (and a paramObj if is not the last) for calculate it")
            else:
                generalEntropy = self.calculateEntropyOfOneAttribute(dataBase=dataBase, attribute=paramObj)
                listOfParams = self.getEntropysOfAllAttributes(dataBase=dataBase, paramObj = paramObj)
        if C45:
            bestGainRatio = -1
            bestParam = None
            epsilon = 0.0001
            for param in listOfParams:
                gain = generalEntropy - param[entropyPlaceOnTuple]
                #param == 0
                if ((generalEntropy - epsilon) < gain < (generalEntropy + epsilon)):
                    return (param[paramPlaceOnTuple], -1)
                try:
                    float(dataBase[0][param[paramPlaceOnTuple]])
                    pLess = param[2]
                    pGEqual = param[3]
                    splitInfo = (-pLess*math.log(pLess,2)) - (pGEqual*math.log(pGEqual,2))
                except:
                    splitInfo = self.getSplitInfoOfParameter(dataBase=dataBase, parameter=param[paramPlaceOnTuple])
                gainRatio = gain/splitInfo
                if (gainRatio > bestGainRatio):
                    bestGainRatio = gainRatio
                    bestParam = param
                #print "bestGainRatio "+str(bestGainRatio)
        else:
            bestGain = float(-1)
            bestParam = None
            for param in listOfParams:
                gain = generalEntropy-param[entropyPlaceOnTuple]
                if(gain>bestGain):
                    bestGain = gain
                    bestParam = param
            epsilon = 0.0001
            #If finish return a -1 and the param in a tuple
            if ((generalEntropy-epsilon)<bestGain<(generalEntropy+epsilon)):
                return (bestParam[paramPlaceOnTuple], -1)
        bestParam = (bestParam[paramPlaceOnTuple],bestParam[entropyPlaceOnTuple])
        return bestParam
    """
    This function takes the ACTUALlist of names (variable with the point of recursivity where you are), and the actual index of the element
     (variable with the point of recursivity where you are) and gets the realIndex on the total table (attributeIndex) and the name (attributeName).
    """
    def getRealIndexOfAtributeName(self, actualListOfAttributeNames, actualIndexOfAttribute):
        attributeName = actualListOfAttributeNames[actualIndexOfAttribute]
        attributeIndex = self._dictNameAttributesOriginalPos[attributeName]
        return attributeIndex, attributeName

    """
    This functions takes a dataBase and a param for divide, and returns a list of n tuples -> (numpyArray,label, value , probability)
    numpyArray refers to the new database for a node and label refers to the label that will be printed in the edge of the graph,
    value is the value of attribute and probability refers the probability of the edge
    """
    def splitDatabaseByAnAttribute(self, dataBase, paramForDivide):
        listOfNumpysAndLabels = []
        arrayParam = dataBase[:, paramForDivide]
        totalLength = np.shape(arrayParam)[0]
        differentValuesOfCases, casesOfValue = np.unique(arrayParam, return_counts=True)
        #for each possible value of this attribute
        for pos in range(np.shape(differentValuesOfCases)[0]):
            actualValue = differentValuesOfCases[pos]
            dataBaseFilteredByParamValue = dataBase[dataBase[:, paramForDivide] == actualValue]
            dataBaseFilteredWithNoColumnOfParamValue = np.delete(dataBaseFilteredByParamValue, paramForDivide, axis = 1)
            label = str(differentValuesOfCases[pos])+" - "+str(casesOfValue[pos])+"/"+str(totalLength)
            probability = (casesOfValue[pos]/float(totalLength))
            tupleOfCase = (dataBaseFilteredWithNoColumnOfParamValue, label, actualValue ,probability)
            listOfNumpysAndLabels.append(tupleOfCase)
        return listOfNumpysAndLabels

    """
        This functions takes a dataBase and a continuous param for divide, and returns a threshold a list of n tuples -> (numpyArray, label, value , probability)
        numpyArray refers to the new database for a node and label refers to the label that will be printed in the edge of the graph,
        value is the value of attribute and probability refers the probability of the edge. Value will be L if is Less edge or GE if is GE edge
    """
    def splitDatabaseByAnContinuousAttribute(self, dataBase, paramForDivide, threshold = None, dataBaseL = None, dataBaseGE = None):

        if threshold is None:
            threshold = self.bestThresholdForContinuousAttribute(attributeNumber=paramForDivide, dataBase=dataBase)
            dataBaseL, dataBaseGE = self.getTwoDatabasesForContinuousAtt(dataBase=dataBase, attributeNumber=paramForDivide, threshold=threshold)
        onlyMyParam = dataBase[:, paramForDivide]
        totalLength = float(np.shape(onlyMyParam)[0])
        lengthOfLDB = np.shape(dataBaseL)[0]
        lengthOfGEDB = np.shape(dataBaseGE)[0]
        labelLess = "x<"+str(threshold)+" - "+str(lengthOfLDB)+"/"+str(totalLength)
        labelGreaterEqual = "x>="+str(threshold)+" - "+str(lengthOfGEDB)+"/"+str(totalLength)
        probabilityLess = lengthOfLDB/totalLength
        probabilityGreaterOrEqual = lengthOfGEDB / totalLength
        listOfNumpysAndLabels = []
        splited = False
        if totalLength<self.limitToStopSplit:
            dataBaseL = np.delete(dataBaseL, paramForDivide, axis = 1)
            dataBaseGE = np.delete(dataBaseGE, paramForDivide, axis=1)
            splited = True
        if lengthOfLDB != 0:
            listOfNumpysAndLabels.append((dataBaseL,labelLess, '<',probabilityLess))
        if lengthOfGEDB != 0:
            listOfNumpysAndLabels.append((dataBaseGE, labelGreaterEqual, '>=', probabilityGreaterOrEqual))
        if lengthOfGEDB == 0 or lengthOfLDB == 0:
            threshold = None
            #raise Exception ("ERROR: the 2 continuous databases turns [], revise how to fix it")
        return threshold, listOfNumpysAndLabels,splited

    """
    This gets a list (in numpy) with a number of values, and returns the most common value
    """
    def getTheMostCommonValue(self, numpyList):
        differentValues, count = np.unique(numpyList, return_counts=True)
        return differentValues[np.argmax(count)]

    def setLeafNode(self,parentNameOfVisualization, labelToAssign, valueOfAttributeObjective, myNode, entropyIs0 = False):
        #-----Set the model-------
        myNode.setIsLeaf(isLeaf=True)
        myNode.setParamNumber(paramNumber=len(self._nameOfAttributes)-1)
        myNode.setResponse(response=valueOfAttributeObjective)

        #----------Sets the visualization-------------
        visualizationNameAssigned = self._visualizationTree.addNodeAndReturnValidName(
            nodeName=valueOfAttributeObjective)
        # Adding edge on the tree
        self._visualizationTree.addEdge(node1=parentNameOfVisualization, node2=visualizationNameAssigned,
                                        label=labelToAssign)

    def generate(self, visualizeTheModel = False, ID3=False, C45 = False):
        if self._visualizationTree is None:
            self._visualizationTree = tv.TreeVisualization()
        dataBase = self._db
        #Calculate the best atribute in that case
        attributeWithBestGain, gain = self.getAttributeWithBestGain(dataBase=dataBase,ID3 = ID3, C45=C45)

        realAttributeIndexOfBest,realAttributeNameOfBest =\
            self.getRealIndexOfAtributeName(actualListOfAttributeNames= self._nameOfAttributes, actualIndexOfAttribute= attributeWithBestGain)
        #split by this attribute
        threshold = None
        splitted = False
        try:
            float(dataBase[0][attributeWithBestGain])
            threshold, newDatabasesForChilds, splitted = self.splitDatabaseByAnContinuousAttribute(dataBase=dataBase, paramForDivide=attributeWithBestGain)
        except:
            newDatabasesForChilds = self.splitDatabaseByAnAttribute(dataBase=dataBase, paramForDivide=attributeWithBestGain)

        #-----Generate the node in the model-----
        rootNode = nt.nodeOfTree(paramNumber=realAttributeIndexOfBest,threshold=threshold)
        if splitted:
            threshold = None
        #generate the childs. The childs alredy has the parent assigned
        childs = [(nt.nodeOfTree(parent=rootNode),newDatabasesForChilds[i][self.valuePos],newDatabasesForChilds[i][self.probabilityPos]) for i in range(len(newDatabasesForChilds))]
        #set the childs of node and finish the node
        rootNode.setChilds(childs=childs)
        #Is the first... Is the rootNode
        self._tree = rootNode
        #--------Generate the node in visualization--------
        visualizationNameAssigned = self._visualizationTree.addNodeAndReturnValidName(realAttributeNameOfBest)
        self._visualizationTree.setRoot(visualizationNameAssigned)
        newListOfAttributeNames = self._nameOfAttributes
        if threshold is None:
            newListOfAttributeNames = copy.copy(self._nameOfAttributes)
            newListOfAttributeNames.pop(attributeWithBestGain)
        #for each split generate recursively the model
        i = 0
        if gain == -1:
            # If this is true, the next node is a leaf!
            for part in newDatabasesForChilds:
                valueOfObjective = part[self.databasePos][0][-1]
                self.setLeafNode(parentNameOfVisualization=visualizationNameAssigned,
                                 labelToAssign=part[self.labelPos],
                                 valueOfAttributeObjective=valueOfObjective,
                                 myNode=childs[i][self.posOfNodeInChildsList],
                                 entropyIs0=True)
                i += 1
        else:
            for part in newDatabasesForChilds:
                if self.calculateEntropyOfOneAttribute(part[self.databasePos]) == 0:
                    valueOfObjective = part[self.databasePos][0][-1]
                    self.setLeafNode(parentNameOfVisualization=visualizationNameAssigned,
                                     labelToAssign=part[self.labelPos],
                                     valueOfAttributeObjective=valueOfObjective,
                                     myNode=childs[i][self.posOfNodeInChildsList],
                                     entropyIs0=True)
                else:
                    self.generateRecursive(parentNameOfVisualization= visualizationNameAssigned,
                                       labelToAssign= part[self.labelPos],
                                       newDataBase= part[self.databasePos],
                                       actualListOfAttributeNames=newListOfAttributeNames,
                                       myNode = childs[i][self.posOfNodeInChildsList],
                                       ID3=ID3, C45= C45)

                i+=1
        if(visualizeTheModel):
            print "Tree Created, generating the visualization..."
            self._visualizationTree.showTree()
        #returns the model
        return rootNode

    def generateRecursive(self, parentNameOfVisualization, labelToAssign,  newDataBase, actualListOfAttributeNames,
                          myNode, ID3=False, C45=False):
        if len(actualListOfAttributeNames) == 1:
            #print "acabado por que solo queda "+str(actualListOfAttributeNames)
            mostCommonObjectiveValue = self.getTheMostCommonValue(numpyList= newDataBase[:,-1])
            self.setLeafNode(parentNameOfVisualization=parentNameOfVisualization,
                             labelToAssign=labelToAssign,
                             valueOfAttributeObjective=mostCommonObjectiveValue,
                             myNode=myNode,
                             entropyIs0=False)
            print "Leaf by max"
            return
        if self._visualizationTree is None:
            raise Exception("ERROR in generateRecursive: Visualization Tree not assigned")
        # Calculate the best atribute in that case
        attributeWithBestGain, gain = self.getAttributeWithBestGain(dataBase=newDataBase, ID3=ID3, C45=C45)
        realAttributeIndexOfBest, realAttributeNameOfBest = \
            self.getRealIndexOfAtributeName(actualListOfAttributeNames=actualListOfAttributeNames,
                                            actualIndexOfAttribute=attributeWithBestGain)
        # split by this attribute
        threshold = None
        splitted = False
        try:
            float(newDataBase[0][attributeWithBestGain])
            threshold, newDatabasesForChilds, splitted = self.splitDatabaseByAnContinuousAttribute(dataBase=newDataBase, paramForDivide=attributeWithBestGain)
        except:
            newDatabasesForChilds = self.splitDatabaseByAnAttribute(dataBase=newDataBase, paramForDivide=attributeWithBestGain)
        #-----parent is setted by the upper function setting the node of the model------
        myNode.setParamNumber(paramNumber=realAttributeIndexOfBest)
        myNode.setThreshold(threshold=threshold)
        if splitted:
            threshold = None
        # generate the childs. The childs alredy has the parent assigned
        childs = [(nt.nodeOfTree(parent=myNode), newDatabasesForChilds[i][self.valuePos],
                   newDatabasesForChilds[i][self.probabilityPos]) for i in range(len(newDatabasesForChilds))]
        # set the childs of node and finish the node
        myNode.setChilds(childs=childs)

        # -----Node of model finished, adpating the visualization-------
        visualizationNameAssigned = self._visualizationTree.addNodeAndReturnValidName(nodeName=realAttributeNameOfBest)
        #Adding edge on the tree
        self._visualizationTree.addEdge(node1= parentNameOfVisualization,node2 = visualizationNameAssigned, label = labelToAssign)
        newListOfAttributeNames = actualListOfAttributeNames
        if threshold is None:
            newListOfAttributeNames = copy.copy(actualListOfAttributeNames)
            newListOfAttributeNames.pop(attributeWithBestGain)
        # for each split generate recursively the model
        i = 0
        if gain == -1:
            # If this is true, the next node is a leaf!
            for part in newDatabasesForChilds:
                valueOfObjective = part[self.databasePos][0][-1]
                self.setLeafNode(parentNameOfVisualization=visualizationNameAssigned,
                                 labelToAssign=part[self.labelPos],
                                 valueOfAttributeObjective=valueOfObjective,
                                 myNode=childs[i][self.posOfNodeInChildsList],
                                 entropyIs0=True)
                i += 1
        else:
            for part in newDatabasesForChilds:
                if self.calculateEntropyOfOneAttribute(part[self.databasePos]) == 0:
                    valueOfObjective = part[self.databasePos][0][-1]
                    self.setLeafNode(parentNameOfVisualization=visualizationNameAssigned,
                                     labelToAssign=part[self.labelPos],
                                     valueOfAttributeObjective=valueOfObjective,
                                     myNode=childs[i][self.posOfNodeInChildsList],
                                     entropyIs0=True)
                else:
                    self.generateRecursive(parentNameOfVisualization=visualizationNameAssigned,
                                       labelToAssign=part[self.labelPos],
                                       newDataBase=part[self.databasePos],
                                       actualListOfAttributeNames=newListOfAttributeNames,
                                       myNode=childs[i][self.posOfNodeInChildsList],
                                       ID3=ID3, C45=C45)
                i += 1