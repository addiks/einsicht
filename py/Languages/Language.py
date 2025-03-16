
from PySide6.QtGui import QSyntaxHighlighter
from collections import OrderedDict
import re

class Language:

    def __init__(self):
        pass
    
    # Returns QSyntaxHighlighter
    def syntaxHighlighter(self, document, syntaxTree):
        return LanguageFromSyntaxTreeHighlighter(document, syntaxTree, self)
    
    def tokenMatcher(self): # OrderedDict<string, TokenMatcher>
        raise NotImplementedError

    def grammar(self): # GrammarBranch
        raise NotImplementedError

    def formatForNode(self, node):
        raise NotImplementedError

    def parse(self, code): # return: ASTNode
        tokens = self.lex(code)

        grammar = self.grammar()
        assert isinstance(grammar, GrammarBranch)

        tokens = grammar.transform(tokens)

        for token in tokens:
            print([token.row, token.col, token.tokenName, token.code])

        return ASTBranch(tokens, "root")

    def lex(self, code):
        tokens = []

        row = 1
        col = 1
        offset = 0

        code = code.replace('\r\n', '\n')
        code = code.replace('\r', '\n')

        matchers = self.tokenMatcher()
        
        while len(code) > 0:
            beforeLength = len(code)
            for matcher in matchers.values():
                if len(code) <= 0:
                    break
                (codeAfter, tokenDef) = matcher.lexNext(code)
                if tokenDef != None:
                    assert isinstance(tokenDef, TokenDef)
                    token = tokenDef.toToken(self, row, col, offset)
                    assert isinstance(token, Token)
                    tokens.append(token)
                offset += len(code) - len(codeAfter)
                code = codeAfter
                if tokenDef != None:
                    break
            if beforeLength == len(code):
                print("Could not parse remaining code!")
                break

        return tokens

class LanguageFromSyntaxTreeHighlighter(QSyntaxHighlighter):
    
    def __init__(self, document, syntaxTree, language):
        super().__init__(document)
        self.syntaxTree = syntaxTree
        self.language = language
        self._offset = 0

    def highlightBlock(self, text):
        print(text)
        self.highlightAstNode(self.syntaxTree, len(text))
        self._offset += len(text) + 1

    def highlightAstNode(self, node, length):

        format = self.language.formatForNode(node)

        if format != None:
            if node.offset >= self._offset:
                self.setFormat(
                    (node.offset + 1) - self._offset, 
                    len(node.code), 
                    format
                )

        if type(node) == ASTBranch:
            for child in node.children:
                self.highlightAstNode(child, length)

### GRAMMAR

class Grammar:
    def transform(self, nodes): # return newNodes
        raise NotImplementedError

class GrammarBranch(Grammar):
    def __init__(self, elements):
        self._elements = elements

    def supports(self, nodes): # return: bool
        for element in self._elements:
            if element.supports(nodes):
                return True
        return False

    def transform(self, nodes):
        for element in self._elements:
            nodes = element.transform(nodes)
        return nodes

class NodePattern:
    def matches(self, node):
        raise NotImplementedError

    def consume(self, nodes):
        raise NotImplementedError

class OptionalNode(NodePattern):
    def __init__(self, element):
        print(element)
        assert isinstance(element, (str, ASTNode, NodePattern))
        self.element = element

class NodeSequence(NodePattern):
    def __init__(self, nodes):
        self.nodes = nodes

class TokenSequenceGrammar(Grammar):
    def __init__(self, sequence, type):
        self._sequence = sequence
        self._type = type

    def supports(self, nodes): # return: bool
        while len(nodes) > 0:
            if self._nodeMatches(nodes[0], self._sequence[0]):
                (success, remainingNodes,) = self._processNodeSequence(nodes)
                if success:
                    return True
        return False
        

    def transform(self, nodes):
        newNodes = []
        while len(nodes) > 0:
            if self._nodeMatches(nodes[0], self._sequence[0]):
                (success, remainingNodes, producedNodes) = self._processNodeSequence(nodes)
                if success:
                    nodes = remainingNodes
                    for node in producedNodes:
                        newNodes.append(node)
            else:
                newNodes.append(nodes.pop(0))
        return newNodes

    def _processNodeSequence(self, nodes):
        sequenceElementsToProcess = self._sequence

        newNodes = []
        success = True
        while len(sequenceElementsToProcess) > 0:
            sequenceElement = sequenceElementsToProcess.pop(0)
            
            (elementSuccess, remainingNodes, producedNodes) = self._consumeSequenceElement(
                sequenceElement, 
                nodes
            )
                
            if elementSuccess:
                nodes = remainingNodes
                for node in producedNodes:
                    newNodes.append(node)
            else:
                success = False
                break

        return (success, nodes, ASTBranch(newNodes, self._type))

    def _consumeSequenceElement(self, sequenceElement, nodes):
        newNodes = []
        success = False
        if self._nodeMatches(nodes[0], sequenceElement):
            if type(sequenceElement) == str:
                newNodes.append(nodes.pop(0))
            if type(sequenceElement) == OptionalToken:
                if self._nodeMatches(nodes[0], sequenceElenement.element):
                    (subSuccess, nodes, newNodes) = self._consumeSequenceElement(sequenceElenement.element, nodes)
                success = True
        return (success, nodes, newNodes)
            
    def _nodeMatches(self, node, requirement):
        if type(requirement) == str:
            if node.code == requirement:
                return True
            elif type(node) == Token:
                return node.tokenName == requirement
            elif type(node) == ASTNode:
                return node.type == requirement
        elif type(requirement) == NodePattern:
            return requirement.matches(node)
        elif type(requirement) == OptionalToken:
            return True # ?
        return False

### AST

class ASTNode:
    def __init__(self, language, code, row, col, offset, type):
        self.language = language
        self.code = code
        self.row = row
        self.col = col
        self.offset = offset
        self.type = type

class ASTBranch(ASTNode):
    def __init__(self, children, type):
        self.children = children
        firstChild = children[0]
        code = ""
        for child in children:
            code += child.code
        super().__init__(
            firstChild.language,
            code,
            firstChild.row,
            firstChild.col,
            firstChild.offset,
            type
        )


### TOKENS

class Token(ASTNode):
    def __init__(self, language, tokenName, code, row, col, offset):
        super().__init__(language, code, row, col, offset, "token")
        self.tokenName = tokenName

class TokenDef:
    def __init__(self, tokenName, code):
        self.tokenName = tokenName
        self.code = code

    def toToken(self, language, row, col, offset):
        return Token(
            language, 
            self.tokenName,
            self.code,
            row,
            col,
            offset
        )


### TOKEN MATCHER

class TokenMatcher:
    def lexNext(self, text): # return: (text, TokenDef|null)
        raise NotImplementedError
        
class KeywordsTokenMatcher(TokenMatcher):
    def __init__(self, keywords, language):
        self._keywords = keywords
        self._language = language

    def lexNext(self, text): # return: (text, TokenDef|None)
        token = None
        for keyword in self._keywords:
            if text[0:len(keyword)].upper() == keyword.upper():
                tokenName = "T_" + keyword.upper()
                token = TokenDef(tokenName, keyword)
                text = text[len(keyword):]
            
        return (text, token)

class LiteralTokenMatcher(TokenMatcher):
    def __init__(self, delimitter, tokenName):
        self._delimitter = delimitter
        self._tokenName = tokenName

    def lexNext(self, text): # return: (text, TokenDef|None)
        token = None
        if text[0] == self._delimitter:
            end = False
            index = 0
            while not end:
                index += 1
                if text[index] == self._delimitter:
                    end = True
            literal = text[0:index + 1]
            token = TokenDef(self._tokenName, literal)
            text = text[len(literal):]
        return (text, token)

class RegexMatcher(TokenMatcher):
    def __init__(self, pattern, tokenName, groupNo=0):
        self._pattern = pattern
        self._tokenName = tokenName
        self._groupNo = groupNo

    def lexNext(self, text): # return: (text, TokenDef|None)
        token = None
        rematch = re.match(self._pattern, text)
        if rematch != None:
            matchedText = rematch.group(self._groupNo)
            token = TokenDef(self._tokenName, matchedText)
            text = text[len(matchedText):]
        return (text, token)
        
class DirectTokenMatcher(TokenMatcher):
    def __init__(self, directTexts, tokenName):
        if type(directTexts) == str:
            directTexts = [directTexts]
        self._directTexts = directTexts
        self._tokenName = tokenName

    def lexNext(self, text): # return: (text, TokenDef|None)
        token = None
        for directText in self._directTexts:
            if text[0:len(directText)] == directText:
                token = TokenDef(self._tokenName, directText)
                text = text[len(directText):]
                break
        return (text, token)
