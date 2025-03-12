
from mimetypes import MimeTypes

from py.Languages.Python.PythonLanguage import PythonLanguage

class LanguageSelector:

    def __init__(self):
        self.mime = MimeTypes()
    
    def selectForFilePath(self, filePath):
        (mimeType, n) = self.mime.guess_type(filePath)
        return self.selectForMimeType(mimeType)
        
    def selectForMimeType(self, mimeType):
        print(mimeType)
        
        if mimeType == "text/x-python":
            return PythonLanguage()
        
        [category, subcategory] = mimeType.split("/")
        print(category)
        print(subcategory)
