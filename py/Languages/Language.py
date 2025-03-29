
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat
from PySide6.QtCore import Qt

from collections import OrderedDict
import re, hashlib

from .AbstractSyntaxTree import ASTNode, ASTBranch, NodePattern
from .Tokens import Token, TokenMatcher, TokenDef

class Language: # abstract

    def __init__(self):
        self._lexCache = {}
        self._parseCache = {}
        
    def name(self):
        raise NotImplementedError
    
    # Returns QSyntaxHighlighter
    def syntaxHighlighter(self, document, syntaxTree):
        return LanguageFromSyntaxTreeHighlighter(document, syntaxTree, self)
    
    def tokenMatchers(self): # list<TokenMatcher>
        raise NotImplementedError

    def grammar(self): # NodePattern
        raise NotImplementedError

    def formatForNode(self, node): # QFormat
        raise NotImplementedError

    def isNodeRelevantForGrammar(self, node): # boolean
        raise NotImplementedError

    def parse(self, code): # return: ASTNode
        hash = hashlib.md5(code.encode()).hexdigest()
        if hash not in self._parseCache:
            tokens = self.lex(code)

            tokens = self.normalize(tokens)

            #for token in tokens:
            #    print([token.row, token.col, token.tokenName, token.code])

            grammar = self.grammar()
            assert isinstance(grammar, NodePattern)

            nodes = []
            nodesToProcess = tokens
            while len(nodesToProcess) > 0:
                if grammar.matches(nodesToProcess):
                    (success, remainingNodes, newNodes) = grammar.consume(nodesToProcess)
                    # print([success, remainingNodes, newNodes])
                    if success:
                        nodes = nodes + newNodes
                        nodesToProcess = remainingNodes
                    else:
                        nodes.append(nodesToProcess.pop(0))
                else:
                    nodes.append(nodesToProcess.pop(0))
                


            # nodes = tokens
            #if grammar.matches(tokens):
            #    (success, remainingNodes, newNodes) = grammar.consume(tokens)
            #    print([success, remainingNodes, newNodes])
            #    if success:
            #        nodes = newNodes + remainingNodes

            #for node in nodes:
            #    if type(node) == Token:
            #        print([node.row, node.col, node.tokenName, node.code])
            #    else:
            #        print([node.row, node.col, node.type, node.code])

            self._parseCache[hash] = ASTBranch(nodes, "root")
        return self._parseCache[hash]

    def normalize(self, tokens):
        index = 0
        while index < len(tokens):
            predecessor = None
            if index > 0:
                predecessor = tokens[index - 1]
            successor = None
            if index < len(tokens) - 1:
                successor = tokens[index + 1]
            if not self.isNodeRelevantForGrammar(tokens[index]):
                if index > 0:
                    tokens[index - 1].append(tokens[index])
                    tokens = tokens[:index] + tokens[index+1:]
                    index -= 1
                elif index < len(tokens) - 1:
                    tokens[index + 1].prepend(tokens[index])
                    tokens = tokens[:index] + tokens[index+1:]
                    index -= 1
            index += 1
        return tokens

    def lex(self, code):
        hash = hashlib.md5(code.encode()).hexdigest()
        if hash not in self._lexCache:
            tokens = []

            row = 1
            col = 1
            offset = 0

            code = code.replace('\r\n', '\n')
            code = code.replace('\r', '\n')

            matchers = self.tokenMatchers()
        
            while len(code) > 0:
                beforeLength = len(code)
                for matcher in matchers:
                    if len(code) <= 0:
                        break

                    (codeAfter, tokenDef) = matcher.lexNext(code)

                    if tokenDef != None:
                        assert isinstance(tokenDef, TokenDef)
                        token = tokenDef.toToken(self, row, col, offset)
                        assert isinstance(token, Token)
                        tokens.append(token)

                    processedCode = code[:(len(code) - len(codeAfter))]

                    (offset, row, col) = self._rowAndColForProcessed(processedCode, offset, row, col)
 
                    code = codeAfter
                    if tokenDef != None:
                        break
                        
                if beforeLength == len(code):
                    tokens.append(Token(
                        self, 
                        "T_INVALID",
                        code[0],
                        row,
                        col,
                        offset
                    ))
                    (offset, row, col) = self._rowAndColForProcessed(code[0], offset, row, col)
                    code = code[1:]
                    
            self._lexCache[hash] = tokens
        return self._lexCache[hash]
        
    def _rowAndColForProcessed(self, processedCode, offset, row, col):
        processedLength = len(processedCode)
        offset += processedLength
        row += processedCode.count("\n")
        if "\n" in processedCode:
            col = (len(processedCode) - processedCode.rfind("\n"))
        else:
            col += processedLength
        return (offset, row, col)

class LanguageFromSyntaxTreeHighlighter(QSyntaxHighlighter):
    
    def __init__(self, document, syntaxTree, language):
        super().__init__(document)
        self.syntaxTree = syntaxTree
        self.language = language
        self._selection = ""

    def updateSyntaxTree(self, syntaxTree):
        if self.syntaxTree != syntaxTree:
            self.syntaxTree = syntaxTree
            self.rehighlight()
            
    def updateSelection(self, selection):
        if self._selection != selection:
            self._selection = selection
            self.rehighlight()

    def highlightBlock(self, text):
        block = self.currentBlock()
        self._line = block.firstLineNumber() + 1
        self.highlightAstNode(self.syntaxTree, len(text))
        
        if len(self._selection) > 0:
            format = QTextCharFormat()
            format.setBackground(Qt.yellow)
            offset = 0
            while True:
                pos = text.find(self._selection, offset)
                if pos >= 0:
                    self.setFormat(pos, len(self._selection), format)
                    offset = pos + len(self._selection)
                else:
                    break

    def highlightAstNode(self, node, length):
        if node.row == self._line:
            format = self.language.formatForNode(node)
            if format != None:
                self.setFormat(
                    node.col - 1,
                    len(node.code), 
                    format
                )

        for predecessor in node.prepended:
            self.highlightAstNode(predecessor, length)

        for successor in node.appended:
            self.highlightAstNode(successor, length)

        if type(node) == ASTBranch:
            for child in node.children:
                self.highlightAstNode(child, length)

