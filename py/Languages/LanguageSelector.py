
from mimetypes import MimeTypes

from py.Languages.Python.PythonLanguage import PythonLanguage

class LanguageSelector:

    def __init__(self):
        self.mime = MimeTypes()
    
    def selectForFilePath(self, filePath):
        (mimeType, n) = self.mime.guess_type(filePath)
        
        if mimeType == None:
            print("No Mime Type!")
            return None
        
        return self.selectForMimeType(mimeType)
        
    def selectForMimeType(self, mimeType):
        if mimeType == "text/x-python":
            return PythonLanguage()
            
        if mimeType == "application/x-python-code":
            return None # cached / compiled python bytecode
        
        if mimeType == "text/php":
            return PHPLanguage()
        
        print(mimeType)
        
        [category, subcategory] = mimeType.split("/")
        print(category)
        print(subcategory)
