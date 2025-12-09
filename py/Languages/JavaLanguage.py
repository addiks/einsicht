
import os

from PySide6.QtGui import QTextCharFormat, QFont
from PySide6.QtCore import Qt

from .Language import Language, PositionDef, ClassDef, MethodDef, MemberDef, FunctionDef, dumpAST
from .AstStyles import CssAsAstStylesheet

from .ASTPatterns import OptionalNode, NodeSequence, RepeatingNode
from .ASTPatterns import NodeBranch, LateDefinedASTPattern

from .Tokens import Token, KeywordsTokenMatcher, RegexMatcher
from .Tokens import DirectTokenMatcher, LiteralTokenMatcher, TokenNodePattern

from .SemanticASTNodes import CodeBlock, ImportNode, AsImportNode

from collections import OrderedDict

class JavaLanguage(Language):

    def name(self):
        return "Java"
    
    def tokenMatchers(self): # list<TokenMatcher>
        return [
            KeywordsTokenMatcher([
                "package", "import", 
                "public", "protected", "private",
                "static", "abstract", "final",
                "new", "class", "interface", "enum", "record",
                "return", "break", "continue", "throw",
                "void", "null", "boolean", "int", "long", "double",
                "if", "else", "while", "for", 
                "try", "catch", "finally",
                "assert",
                "switch", "case"
            ]),
            RegexMatcher(r'\n( +)?', "T_INDENTATION"),
            RegexMatcher(r'\s+', "T_WHITESPACE"),
            RegexMatcher(r'[a-zA-Z_][a-zA-Z0-9_]+', "T_SYMBOL"),
            RegexMatcher(r'[0-9_]+(\.[0-9]*)?', "T_NUMBER"),
            RegexMatcher(r'\//([^\n]*)', "T_COMMENT"),
            RegexMatcher(r'\/\*.*\*\/', "T_COMMENT"),
            DirectTokenMatcher([
                ".", ",", "(", ")", "[", "]", "{", "}", ":", "="
            ], "T_SPECIAL_CHAR"),
            DirectTokenMatcher(["=", "+=", "-=", "*=", "/="], "T_ASSIGN"),
            DirectTokenMatcher(["+", "-", "*", "/"], "T_OPERATOR"),
            LiteralTokenMatcher("'", "T_LITERAL"),
            LiteralTokenMatcher('"', "T_LITERAL")
        ]

    def isNodeRelevantForGrammar(self, node): # boolean
        if isinstance(node, Token):
            if node.tokenName in [
                "T_WHITESPACE", 
                "T_COMMENT", 
                "T_INDENTATION"
            ]:
                return False
        return True
        
    def grammar(self): # NodePattern
        return []


    def stylesheet(self):
        return CssAsAstStylesheet(os.path.dirname(__file__) + "/java.css")

    def formatForNode(self, node):
        if type(node) == Token: 
            format = QTextCharFormat()

            if node.tokenName in ["T_CLASS", "T_DEF"]:
                format.setFontWeight(QFont.Bold)
                format.setForeground(Qt.darkRed)

            if node.tokenName in [
                "T_PACKAGE", "T_IMPORT", 
                "T_PUBLIC", "T_PROTECTED", "T_PRIVATE",
                "T_STATIC", "T_FINAL", "T_ABSTRACT",
                "T_NEW", "T_CLASS", "T_INTERFACE", "T_ENUM", "T_RECORD", 
                "T_RETURN", "T_THROW", "T_BREAK", "T_CONTINUE",
                "T_VOID", "T_NULL", "T_BOOLEAN", "T_INT", "T_LONG", "T_DOUBLE",
                "T_IF", "T_ELSE", "T_WHILE", "T_FOR",
                "T_TRY", "T_CATCH", "T_FINALLY",
                "T_ASSERT", 
                "T_SWITCH", "T_CASE"
            ]:
                format.setFontWeight(QFont.Bold)
                format.setForeground(Qt.darkMagenta)

            if node.tokenName in ["T_NULL", "T_TRUE", "T_FALSE", "T_VOID"]:
                format.setForeground(Qt.magenta)

            if node.tokenName in ["T_PACKAGE", "T_IMPORT"]:
                format.setForeground(Qt.darkYellow)

            if node.tokenName == "T_SYMBOL":
                #format.setForeground(Qt.black)
                if node.code in ["self", "super"]:
                    format.setFontWeight(QFont.Bold)
                
            if node.tokenName in ["T_LITERAL", "T_NUMBER"]:
                format.setForeground(Qt.magenta)
                
            if node.tokenName == "T_COMMENT":
                format.setForeground(Qt.gray)
                
            return format
                
            # white, black, red, darkRed, green, darkGreen, blue, darkBlue, cyan, darkCyan, magenta, 
            # darkMagenta, yellow, darkYellow, gray, darkGray, lightGray, transparent, color0, color1
                
        elif node.type == "identifier":
            if node.parent != None and node.parent.type == "throw":
                format = QTextCharFormat()
                format.setForeground(Qt.red)
                return format
                
            if node.parent != None and node.parent.type == "call":
                format = QTextCharFormat()
                format.setForeground(Qt.blue)
                return format
                
            if node.parent != None and node.parent.type in ["function", "class"]:
                format = QTextCharFormat()
                format.setForeground(Qt.darkYellow)
                format.setFontWeight(QFont.Bold)
                return format
                
        return None
