
from PySide6.QtGui import QSyntaxHighlighter
from collections import OrderedDict
import re, hashlib

class Language: # abstract

    def __init__(self):
        self._lexCache = {}
        self._parseCache = {}
    
    # Returns QSyntaxHighlighter
    def syntaxHighlighter(self, document, syntaxTree):
        return LanguageFromSyntaxTreeHighlighter(document, syntaxTree, self)
    
    def tokenMatchers(self): # list<TokenMatcher>
        raise NotImplementedError

    def grammar(self): # GrammarBranch
        raise NotImplementedError

    def formatForNode(self, node):
        raise NotImplementedError

    def parse(self, code): # return: ASTNode
        hash = hashlib.md5(code.encode()).hexdigest()
        if hash not in self._parseCache:
            tokens = self.lex(code)

            grammar = self.grammar()
            assert isinstance(grammar, NodePattern)

            if grammar.matches(tokens):
                (success, remainingNodes, newNodes) = grammar.consume(tokens)
                print([success, remainingNodes, newNodes])
                if success:
                    nodes = remainingNodes + newNodes

            for node in nodes:
                print([node.row, node.col, node.code])

            self._parseCache[hash] = ASTBranch(nodes, "root")
        return self._parseCache[hash]

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

                    processedLength = len(code) - len(codeAfter)
                    processedCode = code[:processedLength]

                    offset += processedLength
                    row += processedCode.count("\n")
                    if "\n" in processedCode:
                        col = (len(processedCode) - processedCode.rfind("\n"))
                    else:
                        col += processedLength

                    code = codeAfter
                    if tokenDef != None:
                        break
                if beforeLength == len(code):
                    print("Could not parse remaining code!")
                    break
            self._lexCache[hash] = tokens
        return self._lexCache[hash]

class LanguageFromSyntaxTreeHighlighter(QSyntaxHighlighter):
    
    def __init__(self, document, syntaxTree, language):
        super().__init__(document)
        self.syntaxTree = syntaxTree
        self.language = language

    def updateSyntaxTree(self, syntaxTree):
        if self.syntaxTree != syntaxTree:
            self.syntaxTree = syntaxTree
            self.rehighlight()

    def highlightBlock(self, text):
        block = self.currentBlock()
        self._line = block.firstLineNumber() + 1
        self.highlightAstNode(self.syntaxTree, len(text))

    def highlightAstNode(self, node, length):
        if node.row == self._line:
            format = self.language.formatForNode(node)
            if format != None:
                self.setFormat(
                    node.col - 1,
                    len(node.code), 
                    format
                )

        if type(node) == ASTBranch:
            for child in node.children:
                self.highlightAstNode(child, length)

### NODE PATTERNS

class NodePattern:
    def matches(self, nodes):
        raise NotImplementedError

    def consume(self, nodes):
        raise NotImplementedError

class TokenNodePattern(NodePattern):
    def __init__(self, tokenName):
        self._tokenName = tokenName

    def matches(self, nodes):
        node = nodes[0]
        if type(node) == Token:
            expected = self._tokenName
            return node.tokenName == expected or node.code == expected
        return False

    def consume(self, nodes):
        success = False
        newNodes = []

        if self.matches(nodes):
            success = True
            newNodes.append(nodes.pop(0))

        return (success, nodes, newNodes)

class OptionalNode(NodePattern):
    def __init__(self, element):
        # print(element)
        assert isinstance(element, (str, ASTNode, NodePattern))
        self.element = element

    def matches(self, nodes):
        return True

    def consume(self, nodes):
        if self.element.matches(nodes):
            return self.element.consume(nodes)
        return (False, nodes, [])


class NodeSequence(NodePattern):
    def __init__(self, patterns):
        self._patterns = patterns

    def matches(self, nodes):
        for pattern in self._patterns:
            if not pattern.matches(nodes):
                return False
            else:
                (success, nodes, producedNodes) = pattern.consume(nodes)
        return True

    def consume(self, nodes):
        newNodes = []
        success = False
        for pattern in self._patterns:
            if not pattern.matches(nodes):
                success = False
                break
            else:
                (success, nodes, producedNodes) = pattern.consume(nodes)
                if not success:
                    break
                for node in producedNodes:
                    newNodes.append(node)
        return (success, nodes, newNodes)

class NodeBranch(NodePattern):
    def __init__(self, patterns):
        self._patterns = patterns
    
    def matches(self, nodes):
        for pattern in self._patterns:
            if pattern.matches(nodes):
                return True
        return False

    def consume(self, nodes):
        newNodes = []
        success = False
        for pattern in self._patterns:
            if pattern.matches(nodes):
                return pattern.consume(nodes)
        return (False, nodes, [])

class RepeatingNode(NodePattern):
    def __init__(self, pattern):
        self._pattern = pattern

    def matches(self, nodes):
        return True

    def consume(self, nodes):
        newNodes = []
        while self._pattern.matches(nodes):
            (success, remainingNodes, producedNodes) = self._pattern.consume(nodes)
            if success:
                nodes = remainingNodes
                newNodes = newNodes + producedNodes
            else:
                break
        return (True, nodes, newNodes)

class NodesAsASTBranch(NodePattern):
    def __init__(self, astType, pattern):
        self._pattern = pattern
        self._astType = astType

    def matches(self, nodes):
        return self._pattern.matches(nodes)

    def consume(self, nodes):
        (success, remainingNodes, producedNodes) = self._pattern.consume(nodes)
        if success:
            return (success, remainingNodes, ASTBranch(producedNodes, self._astType))
        else:
            return (success, remainingNodes, producedNodes)

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
