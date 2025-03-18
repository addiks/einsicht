
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QFont
from PySide6.QtCore import QRegularExpression, Qt

from ..Language import Language, Token
from ..Language import KeywordsTokenMatcher, RegexMatcher, DirectTokenMatcher, LiteralTokenMatcher
from ..Language import GrammarBranch, TokenSequenceGrammar
from ..Language import OptionalNode, NodeSequence, RepeatingNode, NodeBranch, TokenNodePattern, NodesAsASTBranch

from collections import OrderedDict

class PythonLanguage(Language):

    def tokenMatchers(self): # list<TokenMatcher>
        return [
            KeywordsTokenMatcher([
                "from", "import", "def", "pass", "class", 
                "if", "elif", "else", "not",
                "return", "break", "continue", "raise", "except", "try"
            ], self),
            RegexMatcher(r'\s+', "T_WHITESPACE"),
            RegexMatcher(r'\s+', "T_WHITESPACE"),
                DirectTokenMatcher("@", "T_DECORATOR"),
            RegexMatcher(r'[a-zA-Z0-9_]+', "T_SYMBOL"),
            DirectTokenMatcher([
                ".", ",", "(", ")", "[", "]", "{", "}", ":", "="
            ], "T_SPECIAL_CHAR"),
            DirectTokenMatcher(
                ["+", "-", "*", "/"], 
                "T_OPERATOR"
            ),
            LiteralTokenMatcher("'", "T_LITERAL"),
            LiteralTokenMatcher('"', "T_LITERAL")
        ]

    def grammar(self):

         importStatement = NodesAsASTBranch("import", NodeSequence([
             OptionalNode(NodeSequence([
                 TokenNodePattern("T_FROM"),
                 TokenNodePattern("T_SYMBOL")
             ])) # ,
#             TokenNodePattern("T_IMPORT"),
#             TokenNodePattern("T_SYMBOL"),
#             RepeatingNode(NodeSequence([
#                 TokenNodePattern(","),
#                 TokenNodePattern("T_SYMBOL")
#             ]))
         ]))

         grammar = RepeatingNode(NodeBranch([
             importStatement
         ]))

         return grammar

    def formatForNode(self, node):
        if type(node) == Token: 

            if node.tokenName in ["T_CLASS", "T_DEF"]:
                # print([node.code, node.offset, node.row, node.col])
                format = QTextCharFormat()
                format.setFontWeight(QFont.Bold)
                format.setForeground(Qt.darkMagenta)
                return format

            if node.tokenName in [
                "T_IF", "T_ELSE", "T_ELIF", 
                "T_PASS", "T_RAISE", "T_RETURN", 
                "T_BREAK", "T_CONTINUE",
                "T_ASSERT",
                "T_TRY", "T_CATCH", "T_EXCEPT"
            ]:
                format = QTextCharFormat()
                format.setFontWeight(QFont.Bold)
                format.setForeground(Qt.darkMagenta)
                return format

            if node.tokenName in ["T_FROM", "T_IMPORT"]:
                # print([node.code, node.offset, node.row, node.col])
                format = QTextCharFormat()
                format.setForeground(Qt.darkYellow)
                if node.tokenName == "T_IMPORT":
                    format.setFontWeight(QFont.Bold)
                return format

            if node.tokenName == "T_SYMBOL":
                # print([node.code, node.offset])
                format = QTextCharFormat()
                format.setForeground(Qt.black)
                if node.code in ["self", "super"]:
                    format.setFontWeight(QFont.Bold)
                return format
                
            if node.tokenName == "T_LITERAL":
                format = QTextCharFormat()
                format.setForeground(Qt.magenta)
                return format
                
        return None