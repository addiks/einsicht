
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QFont
from PySide6.QtCore import QRegularExpression, Qt

from ..Language import Language, Token
from ..Language import KeywordsTokenMatcher, RegexMatcher, DirectTokenMatcher, LiteralTokenMatcher
from ..Language import GrammarBranch, TokenSequenceGrammar, OptionalNode, NodeSequence

from collections import OrderedDict

class PythonLanguage(Language):

    def tokenMatcher(self): # OrderedDict<string, TokenMatcher>
        matchers = OrderedDict()
        matchers['KEYWORDS'] = KeywordsTokenMatcher([
            "from", "import", "def", "pass", "class", 
            "if", "elif", "else", "not",
            "return", "break", "continue", "raise", "except", "try"
        ], self)
        matchers['WHITESPACE'] = RegexMatcher(r'\s+', "T_WHITESPACE")
        matchers['DECORATOR'] = DirectTokenMatcher("@", "T_DECORATOR")
        matchers['SYMBOL'] = RegexMatcher(r'[a-zA-Z0-9_]+', "T_SYMBOL")
        matchers['SPECIAL_CHAR'] = DirectTokenMatcher([
            ".", ",", "(", ")", "[", "]", "{", "}", ":", "="
        ], "T_SPECIAL_CHAR")
        matchers['OPERATOR'] = DirectTokenMatcher(
            ["+", "-", "*", "/"], 
            "T_OPERATOR"
        )
        matchers['LITERAL_SINGLE'] = LiteralTokenMatcher("'", "T_LITERAL")
        matchers['LITERAL_DOUBLE'] = LiteralTokenMatcher('"', "T_LITERAL")
        return matchers

    def grammar(self):

        importStatement = TokenSequenceGrammar([
            OptionalNode(NodeSequence(["T_FROM", "T_SYMBOL"]))
        ], "import")

        statement = GrammarBranch([

        ])

        return statement

    def formatForNode(self, node):
        if type(node) == Token: 

            if node.tokenName in ["T_CLASS", "T_DEF"]:
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
                format = QTextCharFormat()
                format.setForeground(Qt.darkYellow)
                return format

            if node.tokenName == "T_SYMBOL":
                # print([node.code, node.offset])
                format = QTextCharFormat()
                format.setForeground(Qt.blue)
                if node.code in ["self", "super"]:
                    format.setFontWeight(QFont.Bold)
                return format
                
            if node.tokenName == "T_LITERAL":
                format = QTextCharFormat()
                format.setForeground(Qt.magenta)
                return format
                
        return None