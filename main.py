from tinydb import TinyDB, Query
import tinydb_encrypted_jsonstorage as tae
import re
import sys
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import Qt, QRegExp


KEY = "my_secret_key"
PATH = "./encrypted.db"

db=TinyDB(encryption_key=KEY, path=PATH, storage=tae.EncryptedJSONStorage)

""" db.insert({'user': 'Pepe Gonzalez', 'username': 'pepedo'})
db.insert({'user': 'Pablo Alborán', 'username': 'alboranp'})

User = Query()
print(db.search(User.user.matches('.+da', flags=re.IGNORECASE)))
print(db.search(User.users.matches('.*to', flags=re.IGNORECASE)))
print(db.search(User.users.search('pe')))
print(db.all()) """

db_idx = {
    0: "user",
    1: "username"
}

class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole or role == Qt.EditRole:
            # See below for the nested-list data structure.
            # .row() indexes into the outer list,
            # .column() indexes into the sub-list
            return self._data[index.row()].get(db_idx[index.column()])
        
        # if role == Qt.DecorationRole: # EXPERIMENTO QUE NO FUNCIONA
        #     return QtWidgets.QCalendarWidget()

    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self._data[0])
    
    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(db_idx[section])

            if orientation == Qt.Vertical:
                return str(self._data[section].doc_id)

    def flags(self, index):
        return Qt.ItemIsSelectable|Qt.ItemIsEnabled|Qt.ItemIsEditable
    
    def setData(self, index, value, role):
        if role == Qt.EditRole:
            doc_id = self._data[index.row()].doc_id
            db.update({db_idx[index.column()]: value}, doc_ids=[doc_id])
            self._data = db.all()
            return True
    


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.table = QtWidgets.QTableView()
        
        data = db.all()

        self.model = TableModel(data)
        self.proxy = QtCore.QSortFilterProxyModel(self)
        self.proxy.setSourceModel(self.model)
        self.proxy.setFilterKeyColumn(-1) #All collumns

        self.table.setModel(self.proxy)
        self.table.setSortingEnabled(True)
        
        self.layout = QtWidgets.QVBoxLayout()
        self.line_edit = QtWidgets.QLineEdit()
        self.line_edit.textChanged.connect(self.filter)
        self.layout.addWidget(self.line_edit)
        self.layout.addWidget(self.table)

        self.widget = QtWidgets.QWidget()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

    def filter(self, textChanged):
        self.proxy.setFilterRegExp(QRegExp(textChanged, Qt.CaseInsensitive, QRegExp.FixedString))
        

app=QtWidgets.QApplication(sys.argv)
window=MainWindow()
window.show()
app.exec_()