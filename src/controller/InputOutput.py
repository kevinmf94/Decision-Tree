import numpy as np


class InputOutput:
	_db = None
	_numpyDb = None
	_paramToPredict = -1
	_valueContinuousList = []
	_minimumRangeForBeContinuous = 15

	def __init__(self, db, paramToPredict):
		self._db = db
		self._paramToPredict = paramToPredict
		self.readDBWithContinuous()

	# self._nparams = nparams
	# self._paramobj = paramobj

	def readStringDb(self):
		self._numpyDb = np.loadtxt(self._db, dtype='str', delimiter=',')
		if self._paramToPredict != -1:
			self._numpyDb[:, [self._paramToPredict, -1]] = self._numpyDb[:, [-1, self._paramToPredict]]
		np.random.shuffle(self._numpyDb)

	def readDBWithContinuous(self):
		self._numpyDb = np.genfromtxt(self._db, dtype='str', delimiter=',')

		for i in range(self._numpyDb.shape[1]):
			try:
				float(self._numpyDb[:, i][0])
				mean = self._numpyDb[:, i][np.where(self._numpyDb[:, i] != "?")].astype(np.float32).mean()
				self._numpyDb[:, i][np.where(self._numpyDb[:, i] == "?")] = mean
			except Exception:
				counts = np.unique(self._numpyDb[:, i][np.where(self._numpyDb[:, i] != "?")], return_counts=True)
				idxMax = counts[1].argmax()
				self._numpyDb[:, i][np.where(self._numpyDb[:, i] == "?")] = counts[0][idxMax]

		# self._numpyDb = np.delete(self._numpyDb, listOfFilesToErase, axis = 0)
		np.random.shuffle(self._numpyDb)
		if self._paramToPredict != -1:
			self._numpyDb[:, [self._paramToPredict, -1]] = self._numpyDb[:, [-1, self._paramToPredict]]

	def printDb(self):
		if (self._numpyDb is None):
			raise Exception("Db not readed")
		# self._numpyDb = np.loadtxt(self._db, dtype='string')
		print self._numpyDb

	def getNumpyDb(self):
		return self._numpyDb
