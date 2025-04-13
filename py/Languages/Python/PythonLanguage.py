
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QFont
from PySide6.QtCore import QRegularExpression, Qt

from ..Language import Language, ClassDef, MethodDef, FunctionDef

from ..ASTPatterns import OptionalNode, NodeSequence, RepeatingNode
from ..ASTPatterns import NodeBranch, LateDefinedASTPattern

from ..Tokens import Token, KeywordsTokenMatcher, RegexMatcher
from ..Tokens import DirectTokenMatcher, LiteralTokenMatcher, TokenNodePattern

from ..SemanticASTNodes import CodeBlock, ImportNode, AsImportNode

from collections import OrderedDict

class PythonLanguage(Language):
    
    def name(self):
        return "Python"
    
    def tokenMatchers(self): # list<TokenMatcher>
        return [
            KeywordsTokenMatcher([
                "from", "import", "assert",
                "def", "pass", "class", "lambda",
                "if", "elif", "else", "not",
                "return", "break", "continue", 
                "raise", "except", "try", "finally",
                "while", "for",
                "True", "False", "None",
                "and", "or", "xor", "not",
                "del", "as", "in", "breakpoint"
            ], self),
            #RegexMatcher(r'\n+', "T_WHITESPACE"),
            RegexMatcher(r'\n( +)?', "T_INDENTATION"),
            #RegexMatcher(r'\s+', "T_WHITESPACE"),
            RegexMatcher(r'\s+', "T_WHITESPACE"),
            DirectTokenMatcher("@", "T_DECORATOR"),
            RegexMatcher(r'[a-zA-Z_][a-zA-Z0-9_]+', "T_SYMBOL"),
            RegexMatcher(r'[0-9_]+(\.[0-9]*)?', "T_NUMBER"),
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
            if node.tokenName in ["T_WHITESPACE", "T_COMMENT", "T_INDENTATION"]:
                return False
        return True

    def grammar(self):
        
        #return [NodeSequence("test", [
        #    TokenNodePattern("T_FROM"),
        #    TokenNodePattern("T_SYMBOL")
        #])]
        
        # return [RepeatingNode("test", TokenNodePattern("T_INDENTATION"), False)]
        
        expression = LateDefinedASTPattern()

        identifier = NodeSequence("identifier", [
            TokenNodePattern("T_SYMBOL"),
            RepeatingNode("identifier-path", NodeSequence("identifier-element", [
                TokenNodePattern("."),
                TokenNodePattern("T_SYMBOL")
            ]), True)
        ])
        
        importFrom = NodeSequence("import-from", [
            TokenNodePattern("T_FROM"),
            RepeatingNode("import-from-parent", TokenNodePattern("."), True),
            identifier
        ])

        importStatement = NodeSequence("import", [
            OptionalNode(importFrom),
            TokenNodePattern("T_IMPORT"),
            identifier
        ])
        
        tuple = NodeSequence("tuple", [
            TokenNodePattern("("),
            RepeatingNode("tuple-content", NodeSequence("tuple-element", [
                expression,
                OptionalNode(TokenNodePattern(","))
            ]), True),
            TokenNodePattern(")")
        ])
        
        call = NodeSequence("call", [
            identifier,
            tuple
        ])
        
        raiseDef = NodeSequence("raise", [
            TokenNodePattern("T_RAISE"),
            identifier,
            tuple
        ])
        
        decorator = NodeSequence("decorator", [
            TokenNodePattern("@"),
            identifier,
            OptionalNode(tuple)
        ])
        
        operation = NodeSequence("operation", [
            expression,
            TokenNodePattern("T_OPERATOR"),
            expression
        ])
        
        assignment = NodeSequence("assignment", [
            expression,
            TokenNodePattern("="),
            expression
        ])
        
        classDefinition = NodeSequence("class", [
            TokenNodePattern("T_CLASS"),
            identifier,
            tuple,
            TokenNodePattern(":"),
        ])
        
        functionDefinition = NodeSequence("function", [
            TokenNodePattern("T_DEF"),
            identifier,
            tuple,
            TokenNodePattern(":"),
        ])
        
        expression.definePattern(NodeBranch("expression", [
            identifier,
            call,
            TokenNodePattern("T_LITERAL"),
            TokenNodePattern("T_NUMBER"),
            # operation # Infinite loop? expr => operation => expression => ... HOW?!
        ]))
        
        return [
            importStatement,
            importFrom,
            identifier,
            tuple,
            classDefinition,
            functionDefinition,
            raiseDef,
            call,
            decorator,
            operation,
            assignment,
            expression
        ]

    def groupStatementsIntoBlocks(self, nodes): # list<ASTNode>
        level = 0
        currentIndentation = 0
        stack = [CodeBlock(self, 1, 1, 0)]
        depthStack = [0]
        for node in nodes:
            if isinstance(node, Token) and node.tokenName == "T_INDENTATION":
                currentIndentation = node.code.count(" ")
                if currentIndentation > level:
                    level = currentIndentation
                    stack.append(CodeBlock(self, node.row, node.col, node.offset))
                    depthStack.append(level)
                elif currentIndentation < level:
                    while currentIndentation < level:
                        endedBlock = stack.pop()
                        depthStack.pop()
                        level = depthStack[-1]
                        stack[-1].addStatement(endedBlock)
            stack[-1].addStatement(node)
        while len(stack) > 1:
            block = stack.pop()
            stack[-1].addStatement(block)
        return stack[0].children

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
                "T_AND", "T_OR", "T_XOR", "T_NOT"
            ]:
                format.setFontWeight(QFont.Bold)
                format.setForeground(Qt.darkMagenta)

            if node.tokenName in ["T_NONE", "T_TRUE", "T_FALSE"]:
                format.setForeground(Qt.magenta)

            if node.tokenName in ["T_FROM", "T_IMPORT"]:
                format.setForeground(Qt.darkYellow)

            if node.tokenName == "T_SYMBOL":
                #format.setForeground(Qt.black)
                if node.code in ["self", "super"]:
                    format.setFontWeight(QFont.Bold)
                
            if node.tokenName in ["T_LITERAL", "T_NUMBER"]:
                format.setForeground(Qt.magenta)
                
            if node.tokenName == "T_COMMENT":
                format.setForeground(Qt.gray)
                
            return format
                
            # white, black, red, darkRed, green, darkGreen, blue, darkBlue, cyan, darkCyan, magenta, 
            # darkMagenta, yellow, darkYellow, gray, darkGray, lightGray, transparent, color0, color1
                
        elif node.type == "identifier":
            if node.parent != None and node.parent.type == "raise":
                format = QTextCharFormat()
                format.setForeground(Qt.red)
                return format
                
            if node.parent != None and node.parent.type == "call":
                format = QTextCharFormat()
                format.setForeground(Qt.blue)
                return format
                
            if node.parent != None and node.parent.type in ["function", "class"]:
                format = QTextCharFormat()
                format.setForeground(Qt.darkYellow)
                format.setFontWeight(QFont.Bold)
                return format
                
        return None

    def populateFileContext(self, context):
    
        filePath = context.filePath[len(context.projectFolder)+1:]
        
        # TODO: This assumes that the project-root is also the python-path root
        pythonPath = filePath.replace(".py", "").replace("/", ".")
        
        # print(filePath, pythonPath)
    
        for classNode in context.syntaxTree.find("class"):
            classBlock = classNode.next()
            classDef = ClassDef(
                classNode.find("identifier")[0].code, 
                namespace = pythonPath,
                parents=list(map(lambda a: a.code, classNode.find("tuple-element"))),
                node=classNode,
                block=classBlock
            )
            context.addClass(classDef)
            
            for methodNode in classBlock.find("function"):
                print(methodNode)
                
                methodArguments = []
                for element in methodNode.find("tuple-element"):
                    methodArguments.append(element.code)
                
                MethodDef(
                    classDef,
                    methodNode.children[1].code,
                    methodArguments
                )
                
        for functionNode in context.syntaxTree.find("function"):
            functionArguments = []
            for element in functionNode.find("tuple-element"):
                functionArguments.append(element.code)
            context.addFunction(FunctionDef(
                functionNode.children[1].code,
                functionArguments
            ))
        