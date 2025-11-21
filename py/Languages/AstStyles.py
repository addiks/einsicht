
import os, tinycss2

from tinycss2.ast import QualifiedRule, WhitespaceToken, LiteralToken
from tinycss2.ast import IdentToken, SquareBracketsBlock, StringToken
from webencodings import Encoding

class AstStyler:

    def applyStylesToQtWidget(self, widget):
        raise NotImplementedError

class CssAsAstStylesheet:
    def __init__(self, cssFilePath):
        self.cssFilePath = cssFilePath

    def applyStylesToQtWidget(self, widget):
    
        with open(self.cssFilePath, 'rb') as fd:
            css = fd.read()
        cssContents = tinycss2.parse_stylesheet_bytes(css)
    
        transformedCss = self._produceCssFor(cssContents)
    
        # print(transformedCss)
    
        widget.setStyleSheet(transformedCss)

    def _produceCssFor(self, element):
        transformedCss = ""
        if type(element) in [list, tuple]:
            for subElement in element:
                transformedCss += self._produceCssFor(subElement)
            return transformedCss
        if isinstance(element, QualifiedRule):
            transformedCss += self._rewritePrelude(element.prelude)
            transformedCss += "{"
            transformedCss += self._produceCssFor(element.content)
            transformedCss += "}"
            return transformedCss
        if isinstance(element, SquareBracketsBlock):
            transformedCss += "["
            transformedCss += self._produceCssFor(element.content)
            transformedCss += "]"
            return transformedCss
        if isinstance(element, WhitespaceToken):
            return element.value
        if isinstance(element, StringToken):
            return '"' + element.value + '"'
        if isinstance(element, LiteralToken):
            return element.value
        if isinstance(element, IdentToken):
            return element.value
        if isinstance(element, Encoding):
            return transformedCss
        return ""
        
    def _rewritePrelude(self, element):
        transformedCss = ""
        
        if type(element) == list:
            while len(element) > 0:
                subElement = element.pop(0)
                
                if isinstance(subElement, LiteralToken) and subElement.value == ".":
                    className = element.pop(0)
                    transformedCss += self._rewriteCssClass(className)
                elif isinstance(subElement, IdentToken):
                    transformedCss += self._rewriteCssElement(subElement.value)
                else:
                    transformedCss += self._rewritePrelude(subElement)
            return transformedCss
        
        return self._produceCssFor(element)
        
    def _rewriteCssClass(self, className):
        if isinstance(className, IdentToken):
            return self._rewriteCssClass(className.value)
        if str(className) == "keyword":
            return "ASTTokenWidget[is_keyword] > ASTCharacterWidget > QLabel"
        if className[0:2] == "T_":
            return 'ASTTokenWidget[tokenName="' + className + '"] > ASTCharacterWidget > QLabel'
        return "." + className
        
    def _rewriteCssElement(self, elementName):
        return '[type="' + str(elementName) + '"]'