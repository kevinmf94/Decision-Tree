class Node:

    def __init__(self, parent=None):
        self._param = "Name"
        self._parent = parent
        self._entropy = 0
        self._data = [0,1,2,3,4,5,6,7,8,9,10]
        self._childrens = [['a',"HIJO"],["b","HIJO"]]
        self._isLeaf = False
