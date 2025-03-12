
from py.Languages.Python.PythonHighlighter import PythonHighlighter

class PythonLanguage:
    
    def syntaxHighlighter(self, document):
        return PythonHighlighter(document)
