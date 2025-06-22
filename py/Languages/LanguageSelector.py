
import os
from mimetypes import MimeTypes

from py.Languages.PythonLanguage import PythonLanguage
from py.Languages.PHPLanguage import PHPLanguage
from py.Languages.MarkdownLanguage import MarkdownLanguage
from py.Log import Log

class LanguageSelector:

    def __init__(self):
        self.mime = MimeTypes()
    
    def selectForFilePath(self, filePath):
        language = None
    
        (mimeType, n) = self.mime.guess_type(filePath)
        if mimeType != None:
            language = self.selectForMimeType(mimeType)
            
        fileExtension = os.path.splitext(filePath)[-1]
        if fileExtension == ".md":
            language = MarkdownLanguage()
        
        Log.debug("Selected " + str(type(language)) + " for " + filePath)
        
        return language
        
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
