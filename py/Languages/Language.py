
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
        
    def populateFileContext(self, context):
        return []
        
    def parse(self, code, previousAST=None, previousTokens=None): # return: [ASTNode, list(TokenNode)]
        hash = hashlib.md5(code.encode()).hexdigest()
        if hash not in self._parseCache:
            tokens = self.lex(code, previousTokens)
            #dumpAST(tokens)
            
            if len(tokens) <= 0:
                self._parseCache[hash] = (None, tokens)
                return self._parseCache[hash]

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
            
            #dumpAST(nodes)
            
            grammarMap = self.grammarMap()
            while len(nodeMap) > 0:
                hasMutated = False
                for nodeKey in nodeMap.copy().keys():
                    if nodeKey in grammarMap:
                        
                        if nodeKey not in nodeMap:
                            continue
                    
                        for node in nodeMap[nodeKey].copy():
                            for pattern in grammarMap[nodeKey]:
                                
                                nodeIndex = node.offsetIn(nodes)
                                if nodeIndex == None:
                                    break
                                
                                if pattern.matches(nodes, nodeIndex):
                                    (replacedNodes, newNodeIndex) = pattern.mutate(nodes, nodeIndex)
            
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
            
            nodes = self.groupStatementsIntoBlocks(nodes)
            
            #dumpAST(nodes, depth=1)
            
            self._parseCache[hash] = (ASTBranch(nodes, "root"), tokens)
        return self._parseCache[hash]
        
    def normalize(self, nodes):
        index = 0
        lastRelevantIndex = None # int
        irrelevantIndexes = [] # list<int>
        while index < len(nodes):
            node = nodes[index]
            if self.isNodeRelevantForGrammar(node):
                indexShift = 0
                while len(irrelevantIndexes) > 0:
                    irrelevantIndex = irrelevantIndexes.pop(0)
                    irrelevantNode = nodes.pop(irrelevantIndex + indexShift)
                    index -= 1
                    indexShift -= 1
                    node.prepend(irrelevantNode)
                lastRelevantIndex = index
            else:
                irrelevantIndexes.append(index)
        
            index += 1
        
        if lastRelevantIndex != None and len(irrelevantIndexes) > 0:
            node = nodes[lastRelevantIndex]
            indexShift = 0
            while len(irrelevantIndexes) > 0:
                irrelevantIndex = irrelevantIndexes.pop(0)
                irrelevantNode = nodes.pop(irrelevantIndex + indexShift)
                indexShift -= 1
                node.append(irrelevantNode)
        
        return nodes

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
                for key in pattern.nodeKeys():
                    if not key in self._grammarMap:
                        self._grammarMap[key] = []
                    self._grammarMap[key].append(pattern)
        return self._grammarMap
        
class ClassDef:
    def __init__(self, identifier, namespace=None, parents=[], flags=[], block=None, node=None):
        self.identifier = identifier # string
        self.namespace = namespace # string
        self.parents = parents # list[string]
        self.flags = flags # list[string]
        self.block = block # ASTNode: represents the class code-block
        self.node = node # ASTNode: represents the class definition node
        self._methods = []
        self._members = []
        
    def addMethod(self, methodDef):
        assert isinstance(methodDef, MethodDef)
        self._methods.append(methodDef)
        
    def methods(self):
        return self._methods
        
    def addMember(self, memberDef):
        assert isinstance(memberDef, MemberDef)
        self._members.append(memberDef)
        
    def members(self):
        return self._members
        
class MethodDef:
    def __init__(self, classDef, identifier, arguments=[], node=None):
        self._classDef = classDef
        self.identifier = identifier
        self.flags = []
        self.returntype = ""
        self.node = node
        classDef.addMethod(self)
        
class MemberDef:
    def __init__(self, classDef, identifier, node=None):
        self._classDef = classDef
        self.identifier = identifier
        self.flags = []
        self.membertype = ""
        self.node = node
        classDef.addMember(self)
        
class FunctionDef:
    def __init__(self, identifier, arguments=[]):
        self.identifier = identifier
        self.arguments = arguments
        
class UseDef:
    def __init__(self, identifier, type):
        assert type in ["class", "method", "function"]
        self.identifier = identifier
        self.type = type
        
class FileContext:

    def __init__(self, filePath, projectFolder, syntaxTree, language):
        self.filePath = filePath
        self.projectFolder = projectFolder
        self.syntaxTree = syntaxTree
        self._classes = []
        self._functions = []
        self._uses = []
        self.language = language
        
    def addClass(self, classDef):
        assert isinstance(classDef, ClassDef)
        self._classes.append(classDef)
        
    def addFunction(self, functionDef):
        assert isinstance(functionDef, FunctionDef)
        self._functions.append(functionDef)
        
    def addUse(self, useDef):
        assert isinstance(useDef, UseDef)
        self._uses.append(useDef)
        
    def classes(self):
        return self._classes
        
    def functions(self):
        return self._functions
        
    def uses(self):
        return self._uses
        
        
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
        if node == None:
            return
            
        for predecessor in node.prepended:
            self.highlightAstNode(predecessor, length)

        for successor in node.appended:
            self.highlightAstNode(successor, length)

        for child in node.children:
            self.highlightAstNode(child, length)

        # TODO: This does not work for multiline highlights
        if node.row == self._line:
            format = self.language.formatForNode(node)
            if format != None:
                self.setFormat(
                    node.col - 1,
                    len(node.code), 
                    format
                )

def dumpAST(nodes, level=0, depth=None):
    if depth != None and level + 1 > depth:
        return
    for node in nodes:
        nodeDescr = "node: " + node.type
        if isinstance(node, Token):
            nodeDescr = node.tokenName + " - " + node.code.strip()
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
