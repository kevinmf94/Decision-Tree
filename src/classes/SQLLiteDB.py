import sqlite3

class SQLLiteDB:
    _filename = ""
    _conn = None
    _nparams = 0

    def __init__(self, filename, nparams):
        self._filename = filename
        self._conn = sqlite3.connect(filename)
        self._nparams = nparams

    def createTable(self):

        try:
            cur = self._conn.cursor();
            cur.execute("CREATE TABLE data (" +
                        self._generateParamsString() + ")")
            self._conn.commit()
        except sqlite3.OperationalError:
            return False

        return True

    def _generateParamsString(self):
        params = ""
        for i in range(self._nparams - 1):
            params += "param" + str((i + 1)) + ","

        params += "param" + str(self._nparams)

        return params;

    def loadData(self, filename):

        try:
            cur = self._conn.cursor();
            data = self._loadFile(filename)
            cur.executemany('INSERT INTO data VALUES (' + self._generateSTMT() + ')', data)
            self._conn.commit()

        except Exception as err:
            print err
            return False

        return True

    def _generateSTMT(self):
        stmt = ""
        for i in range(self._nparams - 1):
            stmt += "?,"

        stmt += "?"

        return stmt;

    def _loadFile(self, filename):

        fileObj = open(filename, "r")
        data = fileObj.readlines()
        dataDef = []

        for i in range(len(data)):
            if data[i].count("?") == 0:
                dataDef.append(data[i].replace("\n", "").split(","))

        return data

    def getAll(self):
        cur = self._conn.cursor()
        cur.execute('SELECT * FROM data')
        data = cur.fetchall()
        return data

    def getFiltered(self, column, value):
        pass

    def close(self):
        self._conn.close()
