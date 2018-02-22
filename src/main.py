from src.classes.SQLLiteDB import *
#from src.controller.DecisionTree import DecisionTree
from src.controller.InputOutput import InputOutput
from src.controller.TreeVisualization import TreeVisualization
from src.controller.Predictor import Predictor
from src.controller.TreeGenerator import TreeGenerator
import src.classes.DataFunctions as df
import numpy as np

DB_NAME = "agaricus-lepiota"
DB_NAME2 = "Balloons"
DB_NAME3 = "BaseRara"
DB_NAME4 = "Adult"
#DB_PARAMS = 22
DB_PARAMTO_PREDICT = -1
#DB_TYPE = ()
DB_NAME_OF_ATTRIBUTES = ["habitat","cap-shape","cap-surface","cap-color","bruises?","odor","gill-attachment","gill-spacing","gill-size","gill-color","stalk-shape",
                         "stalk-root","stalk-surface-above-ring","stalk-surface-below-ring","stalk-color-above-ring","stalk-color-below-ring",
                         "veil-type","veil-color","ring-number","ring-type","spore-print-color","population","class"]
DB_NAME_OF_ATTRIBUTES2 = ["At.0", "At.1", "At.2", "At.3", "At.obj"]
DB_NAME_OF_ATTRIBUTES3 = ["At.0", "At.1", "At.2", "At.3", "At.4", "At.5", "At.obj"]
DB_NAME_OF_ATTRIBUTES4 = ["At.0", "At.1", "At.2", "At.3", "At.4", "At.5", "At.obj", "stalk-color-below-ring",
                         "veil-type","veil-color","ring-number","ring-type","spore-print-color","population","class"]

def kFold(data,k = 8124):
    dataK = np.zeros(k, dtype=np.ndarray)
    dataN = int(data.shape[0] / k)

    for kIndex in range(k):
        dataK[kIndex] = data[(dataN * kIndex):(dataN * (kIndex + 1)), :]

    print "Generant 8124 conjunts..."
    error = 0.0
    for kIndex in range(0, k):
        indexes = np.delete(np.arange(k), kIndex)
        train = np.concatenate(dataK[indexes])
        val = dataK[kIndex]
        treeGen = TreeGenerator(train, DB_NAME_OF_ATTRIBUTES)
        model = treeGen.generate(visualizeTheModel=False, ID3=True, C45=False)
        predictor = Predictor(model=model)
        error += predictor.havePredictionWithNumpyMatrixOfExamples(val)
    error = error/k
    print "8124-fold: Error = "+str(error)
    #print ("Error:",error)


if __name__ == "__main__":

    reader = InputOutput("../"+DB_NAME4+ ".data", DB_PARAMTO_PREDICT)
    dataBase = reader.getNumpyDb()
    #print continuousAttList
    #treeGen = TreeGenerator(dataBase, DB_NAME_OF_ATTRIBUTES4, listOfContinuous=continuousAttList)
    #treeGen = TreeGenerator(dataBase, nameOfAttributes=DB_NAME_OF_ATTRIBUTES)
    #treeGen.entropyOfParamContinuousWithParamObjective(0, dataBase)
    train, validation = df.splitData(dataBase=dataBase, trainPercent=0.66)
    treeGen = TreeGenerator(train, DB_NAME_OF_ATTRIBUTES4)
    model = treeGen.generate(visualizeTheModel=True, ID3=True, C45=False)
    #print "Generated"
    #predictor = Predictor(model=model)
    #predictor.confusionMatrix(validation)
    #error = predictor.havePredictionWithNumpyMatrixOfExamples(validation)
    #kFold(dataBase, 100)
    #prueba = predictor.havePredictionMissing(np.array(['?', '?', 's', '?', 't', 'l', 'f', 'c', 'b', 'k', '?', '?', 's', '?', 'w', 'w', 'p', 'w', 'o', '?', '?', '?']))
    #print prueba
    #print "Error is... "+str(error)


