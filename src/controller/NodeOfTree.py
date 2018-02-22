class nodeOfTree:
    paramNumber = -1
    #childs is a list of tuples -> (nodeChild, valueOfParentAtribute, probabilityOfEdge)
    childs = []
    _parent = None
    isLeaf = False
    posOfNodeInChilds = 0
    posOfParentValueInChilds = 1
    posOfProbabilityOfEdge = 2
    posOfLChild = 0
    posOfGEChild = 1
    response = None
    threshold = None
    def __init__(self, paramNumber = -1, childs = [], parent = None, threshold = None):
        self.paramNumber = paramNumber
        self.childs = childs
        self._parent = parent
        self.isLeaf = False
        self.response = None
        self.threshold = threshold

    def setThreshold(self, threshold):
        self.threshold = threshold
    def setIsLeaf(self, isLeaf=True):
        self.isLeaf = isLeaf
    def setParamNumber(self, paramNumber):
        if self.paramNumber != -1:
            print "Reasigning the paramNumber of a node?"
        self.paramNumber = paramNumber
    def setChilds(self, childs):
        self.childs = childs
    def setParent(self, parent):
        self._parent = parent
    def setResponse(self, response):
        if not self.isLeaf:
            raise Exception("You can't assign a response to a node that notis a leaf")
        self.response = response