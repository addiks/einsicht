
import os
from mimetypes import MimeTypes

from py.Languages.PythonLanguage import PythonLanguage
from py.Languages.PHPLanguage import PHPLanguage
from py.Languages.MarkdownLanguage import MarkdownLanguage
from py.Hub import Log, Hub

class LanguageSelector:

    def __init__(self, hub: Hub):
        self.mime = MimeTypes()
        self.hub = hub
    
    def selectForFilePath(self, filePath):
        language = None
    
        (mimeType, n) = self.mime.guess_type(filePath)
        if mimeType != None:
            language = self.selectForMimeType(mimeType)
            
        fileExtension = os.path.splitext(filePath)[-1]
        if fileExtension == ".md":
            language = MarkdownLanguage(self.hub)
        
        Log.debug("Selected " + str(type(language)) + " for " + filePath)
        
        return language
        
    def selectForMimeType(self, mimeType):
        if mimeType == "text/x-python":
            return PythonLanguage(self.hub)
            
        if mimeType == "application/x-python-code":
            return None # cached / compiled python bytecode
        
        if mimeType == "text/php":
            return PHPLanguage(self.hub)
        
        print(mimeType)
        
        [category, subcategory] = mimeType.split("/")
        print(category)
        print(subcategory)
