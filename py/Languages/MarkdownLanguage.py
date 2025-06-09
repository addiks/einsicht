
from PySide6.QtGui import QTextCharFormat, QFont
from PySide6.QtCore import Qt

from .Language import Language, ClassDef, MethodDef, MemberDef, FunctionDef, dumpAST

from .ASTPatterns import OptionalNode, NodeSequence, RepeatingNode
from .ASTPatterns import NodeBranch, LateDefinedASTPattern

from .Tokens import Token, KeywordsTokenMatcher, RegexMatcher
from .Tokens import DirectTokenMatcher, LiteralTokenMatcher, TokenNodePattern

from .SemanticASTNodes import CodeBlock, ImportNode, AsImportNode

class MarkdownLanguage(Language):
    
    def name(self):
        return "Markdown"
    
    def tokenMatchers(self): # list<TokenMatcher>
        return [
        ]

    def isNodeRelevantForGrammar(self, node): # boolean
        return True
        
    def grammar(self):
        return [
        ]
        
    def formatForNode(self, node):
        return None

        
