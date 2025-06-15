
import os

from ..Languages.Language import AutocompletionType

class Autocompletion:
    def __init__(self, language, projectIndex, tokens, syntaxTree, offset):
        self.language = language
        self.projectIndex = projectIndex
        self.tokens = tokens
        self.syntaxTree = syntaxTree
        self.offset = offset
        
        self.token = self.tokenAt(offset)
        self.prefix = ""
        self.postfix = ""
        
        if self.token != None:
            tokenPosition = offset - self.token.offset
            self.prefix = self.token.code[:tokenPosition]
            self.postfix = self.token.code[tokenPosition:]
        
        self.node = None
        if self.syntaxTree != None:
            self.node = self.syntaxTree.findAtOffset(offset)
        
    def provide(self):
        results = []
        
        if self.prefix != "":
            for token in self.tokens:
                if self.prefix == token.code[:len(self.prefix)]:
                    if len(token.code) > len(self.prefix) and len(token.code.strip()) > 0:
                        results.append(AutocompletionOffer(
                            self.token.offset,
                            len(self.token.code),
                            token.code,
                            1000
                        ))
        
        for completionType in self.language.autocompleTypesForNode(self.node):
            match completionType:
                case AutocompletionType.CLASS:
                    for classDef in self.projectIndex.searchClasses(self.prefix, self.postfix):
                        results.append(AutocompletionOffer(
                            offset,
                            len(self.postfix),
                            classDef.identifier[len(self.prefix):],
                            2000
                        ))
                    
                case AutocompletionType.METHOD:
                    break
                    
                case AutocompletionType.MEMBER:
                    break
                    
                case AutocompletionType.FUNCTION:
                    break
        
        # results = self.projectIndex.search(self.prefix, self.postfix, self.node)
            
        return results
        

    def tokenAt(self, position):
        for token in self.tokens:
            if token.offset < position and (token.offset + len(token.code)) >= position:
                return token
        return None
        
class AutocompletionOffer:
    def __init__(self, offset, length, text, priority):
        self.offset = offset
        self.length = length
        self.text = text
        self.priority = priority
        
    def applyToTextField(self, textField):
        print(self)
        print(textField) 
        
        print(self.offset)
        print(self.length)
        print(self.text)
        
        if self.length > 0:
            textField.removeTextAt(self.offset + self.length, self.length)
        textField.insertTextAt(self.offset, self.text)
        
        textField.setFocus()
                    
        
    def apply(self, text): # TODO: BAD IDEA, redo with cursors
        return text[:self.offset] + self.text + text[self.offset + self.length:]
