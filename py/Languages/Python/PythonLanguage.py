
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QFont
from PySide6.QtCore import QRegularExpression, Qt

from ..Language import Language

from ..AbstractSyntaxTree import OptionalNode, NodeSequence, RepeatingNode, NodeBranch, NodesAsASTBranch

from ..Tokens import Token, KeywordsTokenMatcher, RegexMatcher, DirectTokenMatcher, LiteralTokenMatcher
from ..Tokens import TokenNodePattern

from ..SemanticASTNodes import ImportNode, AsImportNode

from collections import OrderedDict

class PythonLanguage(Language):

    def tokenMatchers(self): # list<TokenMatcher>
        return [
            KeywordsTokenMatcher([
                "from", "import", "assert",
                "def", "pass", "class", "lambda",
                "if", "elif", "else", "not",
                "return", "break", "continue", 
                "raise", "except", "try",
                "while", "for",
                "True", "False", "None",
                "and", "or", "xor"
            ], self),
            RegexMatcher(r'\n +', "T_INDENTATION"),
            RegexMatcher(r'\s+', "T_WHITESPACE"),
            RegexMatcher(r'\s+', "T_WHITESPACE"),
                DirectTokenMatcher("@", "T_DECORATOR"),
            RegexMatcher(r'[a-zA-Z0-9_]+', "T_SYMBOL"),
            RegexMatcher(r'\#([^\n]*)', "T_COMMENT"),
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

    def isNodeRelevantForGrammar(self, node): # boolean
        if isinstance(node, Token):
            if node.tokenName in ["T_WHITESPACE", "T_COMMENT"]:
                return False
        return True

    def grammar(self):
        
        #return NodeSequence([
        #    TokenNodePattern("T_FROM"),
        #    TokenNodePattern("T_SYMBOL")
        #])

        identifierStatement = NodesAsASTBranch("import", 
            NodeSequence([
                TokenNodePattern("T_SYMBOL"),
                RepeatingNode(NodeSequence([
                    TokenNodePattern("."),
                    TokenNodePattern("T_SYMBOL")
                ]), True)
            ]),
            #lambda node : node.find(""), # resource TODO
            #lambda node : node.find("") # alias TODO
        )

        importStatement = NodesAsASTBranch("import", NodeSequence([
            OptionalNode(NodeSequence([
                TokenNodePattern("T_FROM"),
                TokenNodePattern("T_SYMBOL")
            ])),
            TokenNodePattern("T_IMPORT"),
            TokenNodePattern("T_SYMBOL"),
            RepeatingNode(NodeSequence([
                TokenNodePattern(","),
                TokenNodePattern("T_SYMBOL")
            ]), True)
        ]))

        print([importStatement, identifierStatement])

        grammar = RepeatingNode(NodeBranch([
            importStatement,
            identifierStatement
        ]), False)

        return grammar

    def formatForNode(self, node):
        if type(node) == Token: 
            format = QTextCharFormat()

            if node.tokenName in ["T_CLASS", "T_DEF"]:
                format.setFontWeight(QFont.Bold)
                format.setForeground(Qt.darkRed)

            if node.tokenName in [
                "T_IF", "T_ELSE", "T_ELIF", 
                "T_PASS", "T_RAISE", "T_RETURN", 
                "T_BREAK", "T_CONTINUE",
                "T_ASSERT",
                "T_WHILE", "T_FOR",
                "T_TRY", "T_CATCH", "T_EXCEPT",
                "T_AND", "T_OR", "T_XOR"
            ]:
                format.setFontWeight(QFont.Bold)
                format.setForeground(Qt.darkMagenta)

            if node.tokenName in ["T_NONE", "T_TRUE", "T_FALSE"]:
                format.setForeground(Qt.magenta)

            if node.tokenName in ["T_FROM", "T_IMPORT"]:
                format.setForeground(Qt.darkYellow)
                if node.tokenName == "T_IMPORT":
                    format.setFontWeight(QFont.Bold)

            if node.tokenName == "T_SYMBOL":
                format.setForeground(Qt.black)
                if node.code in ["self", "super"]:
                    format.setFontWeight(QFont.Bold)
                
            if node.tokenName == "T_LITERAL":
                format.setForeground(Qt.magenta)
                
            if node.tokenName == "T_COMMENT":
                format.setForeground(Qt.gray)
                
            return format
                
            # white, black, red, darkRed, green, darkGreen, blue, darkBlue, cyan, darkCyan, magenta, 
            # darkMagenta, yellow, darkYellow, gray, darkGray, lightGray, transparent, color0, color1
                
        return None
