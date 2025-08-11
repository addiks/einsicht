
from PySide6.QtGui import QTextCharFormat, QFont
from PySide6.QtCore import Qt

from .Language import Language, PositionDef, ClassDef, MethodDef, MemberDef, FunctionDef, dumpAST

from .ASTPatterns import OptionalNode, NodeSequence, RepeatingNode
from .ASTPatterns import NodeBranch, LateDefinedASTPattern

from .Tokens import Token, KeywordsTokenMatcher, RegexMatcher
from .Tokens import DirectTokenMatcher, LiteralTokenMatcher, TokenNodePattern

from .SemanticASTNodes import CodeBlock, ImportNode, AsImportNode

from collections import OrderedDict

class UnknownLanguage(Language):

    def name(self):
        return "Unknown"

    def tokenMatchers(self): # list<TokenMatcher>
        return [
            RegexMatcher(r'\s+', "T_SPACE"),
            RegexMatcher(r'\S+', "T_CONTENT")
        ]
        
    def isNodeRelevantForGrammar(self, node): # boolean
        return True
        
    def grammar(self):
        return [
            NodeBranch("unknown", [
                TokenNodePattern("T_UNKNOWN"),
            ])
        ]
        
    def formatForNode(self, node):
        return None