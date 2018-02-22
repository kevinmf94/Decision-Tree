import numpy as np
import copy

"""
This class will take examples, take the model and will return the response of the model for the example
"""


class Predictor:
    _model = None
    _listOfLeafs = []

    def __init__(self, model):
        self._model = model
        self._listOfLeafs = []

    """
    This function takes an example that must to be, an list or array of attributes values in the SAME ORDER that appears in db, and returns a response
    """

    def havePrediction(self, example):
        actualNode = self._model
        while (not actualNode.isLeaf):
            valueOfAttribute = example[actualNode.paramNumber]
            if actualNode.threshold is not None:
                valueOfAttribute = float(valueOfAttribute)
                if valueOfAttribute < actualNode.threshold:
                    actualNode = actualNode.childs[actualNode.posOfLChild][actualNode.posOfNodeInChilds]
                else:
                    actualNode = actualNode.childs[actualNode.posOfGEChild][actualNode.posOfNodeInChilds]
            else:
                for child in actualNode.childs:
                    if child[actualNode.posOfParentValueInChilds] == valueOfAttribute:
                        actualNode = child[actualNode.posOfNodeInChilds]
                        break
                else:
                    # take the more probably
                    bestProbability = 0
                    bestChild = None
                    for child in actualNode.childs:
                        p = child[actualNode.posOfProbabilityOfEdge]
                        if p > bestProbability:
                            bestProbability = p
                            bestChild = child[actualNode.posOfNodeInChilds]
                    actualNode = bestChild
                    # print "fuck... Something go wrong having a prediction... the value of attribute '"+valueOfAttribute+"' don't appears in the model at the place where you're looking"
        return actualNode.response

    def allIsLeaf(self, tracks):
        for track in tracks:
            if not track[-1][0].isLeaf:
                return False

        return True

    def getFirstNotLeaf(self, tracks):
        for track in tracks:
            if not track[-1][0].isLeaf:
                tracks.remove(track)
                return track

        return None

    def havePredictionMissing(self, example):
        tracks = [[(self._model, '-', 1)]]

        #Search the track to solution
        while not self.allIsLeaf(tracks):
            actualTrack = self.getFirstNotLeaf(tracks)
            actualNode = actualTrack[-1][0]
            valueOfAttribute = example[actualNode.paramNumber]

            if valueOfAttribute == "?":
                for child in actualNode.childs:
                    newTrack = []
                    newTrack.extend(actualTrack)
                    newTrack.append(child)
                    tracks.append(newTrack)
            else:
                newTrack = []
                newTrack.extend(actualTrack)
                if actualNode.threshold is not None:
                    valueOfAttribute = float(valueOfAttribute)
                    if valueOfAttribute < actualNode.threshold:
                        child = actualNode.childs[actualNode.posOfLChild]
                        newTrack.append((child[0], child[1], 1))
                    else:
                        child = actualNode.childs[actualNode.posOfGEChild]
                        newTrack.append((child[0], child[1], 1))
                else:
                    for child in actualNode.childs:
                        if child[actualNode.posOfParentValueInChilds] == valueOfAttribute:
                            newTrack.append((child[0], child[1], 1))
                            break
                    else:
                        example[actualNode.paramNumber] = "?"

                tracks.append(newTrack)

        #Choose the best track
        bestTrack = None
        bestProb = -1
        for track in tracks:
            trackProb = 1
            for item in track:
                trackProb *= item[2]

            if trackProb > bestProb:
                bestTrack = track
                bestProb = trackProb

        return bestTrack[-1][0].response

    """
    This function receives a numpy array and returns the error of the tree
    """

    def havePredictionWithNumpyMatrixOfExamples(self, examples):
        lastColumn = np.shape(examples)[1] - 1
        numOfExamples = np.shape(examples)[0]
        examplesWithNoResults = examples[:, :lastColumn]
        results = examples[:, lastColumn]
        errors = 0
        for i in range(numOfExamples):
            prediction = self.havePredictionMissing(example=examplesWithNoResults[i])
            if prediction != results[i]:
                errors += 1
        return errors / float(numOfExamples)

    def FillListOfLeafs(self, node=None):
        if (node == None):
            node = self._model
        if (node.isLeaf):
            self._listOfLeafs.append(node)
        else:
            for child in node.childs:
                self.FillListOfLeafs(child[node.posOfNodeInChilds])

    def mostProbablyResponse(self, node):
        for child in node.childs:
            self.FillListOfLeafs(child[node.posOfNodeInChilds])

    def havePruning(self, levels=1):
        nodesToPrun = set()
        for leaf in self._listOfLeafs:
            node = leaf
            for level in range(levels):
                node = node.parent
                if node is None:
                    raise Exception("You can't prun the top level node")
            nodesToPrun.add(node)
            bestModel = None
            minError = 1
            for node in nodesToPrun:
                bestChild = None
                maxProb = 0
                for child in node.childs:
                    if child[node.posOfProbabilityOfEdge] > maxProb:
                        bestChild = child[node.posOfProbabilityOfEdge]

    def confusionMatrix(self, examples):
        lastColumn = np.shape(examples)[1] - 1
        numOfExamples = np.shape(examples)[0]
        examplesWithNoResults = examples[:, :lastColumn]
        results = examples[:, lastColumn]
        uniqueElements = np.unique(examples[:, lastColumn])
        classtoIndex = {}
        for i in range(uniqueElements.size):
            classtoIndex[uniqueElements[i]] = i
        confusionMatrix = np.zeros((uniqueElements.size, uniqueElements.size), dtype=np.int32)
        errors = 0
        for i in range(numOfExamples):
            prediction = self.havePrediction(example=examplesWithNoResults[i])
            confusionMatrix[classtoIndex[results[i]]][classtoIndex[prediction]] += 1
            if prediction != results[i]:
                errors += 1
        print "ConfusionMatrix: "
        print confusionMatrix
        print "error:"+ str(errors / float(numOfExamples))
        return confusionMatrix, classtoIndex, errors / float(numOfExamples)