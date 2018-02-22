import numpy as np
def splitData(dataBase, trainPercent = 0.8):
    dataBaseLength = np.shape(dataBase)[0]
    trainLength = int(dataBaseLength*float(trainPercent))
    train = dataBase[:trainLength,:]
    validation = dataBase[trainLength:,:]
    return train, validation
def kFold(dataBase, nGroups = 5):
    dataBaseLength = np.shape(dataBase)[0]
    nRowsGroup = int(dataBaseLength/nGroups)
    indexList = range(dataBaseLength)
    trainIndex = []
    testIndex = []
    for n in range(nGroups):
        testIndex.append(indexList[(n*nRowsGroup):(n*nRowsGroup+nRowsGroup)])
        trainIndex.append([i for i in indexList if i not in testIndex[n]])
    return trainIndex , testIndex
def oneOut(dataBase):
    dataBaseLength = np.shape(dataBase)[0]
    indexList = range(dataBaseLength)
    trainIndex = []
    testIndex = []
    for n in indexList:
        testIndex.append([n])
        trainIndex.append([i for i in indexList if i not in testIndex[n]])
    return trainIndex, testIndex
