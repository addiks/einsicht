
from PySide6.QtCore import QAbstractItemModel, QModelIndex

class AutocompleteItemModel(QAbstractItemModel):
    def __init__(self):
        super().__init__()
        self._autocomplete = None
        self._results = None
        self._language = None
        
    def changeAutocomplete(self, autocomplete):
        self._language = autocomplete.language
        self._autocomplete = autocomplete
        self._results = None
        print("changeAutocomplete")

    def index(self, row, column, parent=None):
        return self.createIndex(row, column, None)

    def parent(self, child):
        return QModelIndex() # <= invalid model-index = "no parent"

    def rowCount(self, parent=None):
        if self._autocomplete == None:
            return 0
        self._fetchResults()
        return len(self._results)

    def columnCount(self, parent=None):
        return 1

    def data(self, index, role=0):
        self._fetchResults()
        if self._results != None:
            if type(index) == QModelIndex:
                row = index.row()
            else:
                row = index
            if row > 0 and row < len(self._results):
                return self._results[index]
        return None
        
    def _fetchResults(self):
        if self._autocomplete != None and self._results == None:
            self._results = self._autocomplete.provide()
            print(len(self._results))
