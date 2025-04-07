
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat
from PySide6.QtCore import Qt

from collections import OrderedDict
import re, hashlib

from .AbstractSyntaxTree import ASTNode, ASTBranch
from .ASTPatterns import NodePattern
from .Tokens import Token, TokenMatcher, TokenDef

class Language: # abstract

    def __init__(self):
        self._lexCache = {}
        self._parseCache = {}
        self._grammarMap = None
        
    def name(self):
        raise NotImplementedError
    
    # Returns QSyntaxHighlighter
    def syntaxHighlighter(self, document, syntaxTree):
        return LanguageFromSyntaxTreeHighlighter(document, syntaxTree, self)
    
    def tokenMatchers(self): # list<TokenMatcher>
        raise NotImplementedError

    def grammar(self): # NodePattern
        raise NotImplementedError

    def groupStatementsIntoBlocks(self, nodes): # list<ASTNode>
        return nodes

    def formatForNode(self, node): # QFormat
        raise NotImplementedError

    def isNodeRelevantForGrammar(self, node): # boolean
        raise NotImplementedError

    def parse(self, code, previousAST, previousTokens): # return: [ASTNode, list(TokenNode)]
        hash = hashlib.md5(code.encode()).hexdigest()
        if hash not in self._parseCache:
            tokens = self.lex(code, previousTokens)

            tokens = self.normalize(tokens)
            
            nodeMap = {}
            #for index, token in tokens.items():
            
            for index in range(0, len(tokens)):
                token = tokens[index]
                
                if token.tokenName not in nodeMap:
                    nodeMap[token.tokenName] = []
                nodeMap[token.tokenName].append(token)
                
                if token.code not in nodeMap:
                    nodeMap[token.code] = []
                nodeMap[token.code].append(token)
            
            nodes = tokens.copy()
            
            dumpAST(nodes)
            
            grammarMap = self.grammarMap()
            while len(nodeMap) > 0:
                hasMutated = False
                #print("###")
                for nodeKey in nodeMap.copy().keys():
                    #print(["#", len(nodeMap), nodeKey])
                    if nodeKey in grammarMap:
                    
                        #print(" Processing nodes of " + nodeKey)
                    
                        for node in nodeMap[nodeKey].copy():
                            for pattern in grammarMap[nodeKey]:
                                
                                nodeIndex = node.offsetIn(nodes)
                                if nodeIndex == None:
                                    break
                                    
                                #print(" Trying to match pattern " + pattern.producedNodeKey() + " at node " + str(node))
                                
                                if pattern.matches(nodes, nodeIndex):
                                    #print("MATCH!")
                                    (replacedNodes, newNodeIndex) = pattern.mutate(nodes, nodeIndex)
                                    
                                    #dumpAST(nodes)
            
                                    for replacedNode in replacedNodes:
                                        hasMutated = True
                                        
                                        replacedNodeKey = replacedNode.grammarKey()
                                        nodeMap[replacedNodeKey].remove(replacedNode)
                                        if len(nodeMap[replacedNodeKey]) <= 0:
                                            del nodeMap[replacedNodeKey]
                                            
                                        if replacedNode.code in nodeMap and replacedNode in nodeMap[replacedNode.code]:
                                            nodeMap[replacedNode.code].remove(replacedNode)
                                            if len(nodeMap[replacedNode.code]) <= 0:
                                                del nodeMap[replacedNode.code]
                                                
                                    if newNodeIndex != None:
                                        hasMutated = True
                                        newNode = nodes[newNodeIndex]
                                        newNodeKey = newNode.grammarKey()
                                        if newNodeKey not in nodeMap:
                                            nodeMap[newNodeKey] = []
                                        nodeMap[newNodeKey].append(newNode)
                    if nodeKey in nodeMap and len(nodeMap[nodeKey]) <= 0:
                        del nodeMap[nodeKey]
            
                if not hasMutated:
                    break
                    
            dumpAST(nodes, depth=1)
            
            nodes = self.groupStatementsIntoBlocks(nodes)
            
            self._parseCache[hash] = (ASTBranch(nodes, "root"), tokens)
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

    def lex(self, code, previousTokens):
        # TODO: re-use data from previousTokens for better performance
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
        
    def grammarMap(self):
        if self._grammarMap == None:
            patterns = self.grammar()
            self._grammarMap = {}
            for pattern in patterns:
                assert isinstance(pattern, NodePattern)
                #print([pattern, pattern.nodeKeys()])
                for key in pattern.nodeKeys():
                    #print(key)
                    if not key in self._grammarMap:
                        self._grammarMap[key] = []
                    self._grammarMap[key].append(pattern)
        return self._grammarMap
        
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

        # if type(node) == ASTBranch:
        for child in node.children:
            self.highlightAstNode(child, length)


def dumpAST(nodes, level=0, depth=None):
    if depth == None or level + 1 > depth:
        return
    for node in nodes:
        nodeDescr = "node: " + node.type
        if isinstance(node, Token):
            nodeDescr = node.tokenName + " - " + node.code.strip()
        #elif isinstance(node, ASTBranch)
        print(
            str(node.row).rjust(3, "0") + ":" + str(node.col).rjust(3, "0"),
            "-",
            "".ljust(level, "|") + nodeDescr,
            ">",
            node.code.strip()
        )
        dumpAST(node.children, level + 1, depth)
    if level == 0:
        print("\n")