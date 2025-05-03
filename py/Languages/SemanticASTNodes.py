
from .AbstractSyntaxTree import ASTNode, ASTBranch
from .ASTPatterns import NodePattern

class CodeBlock(ASTNode):
    def __init__(self, language, row, col, offset):
        super().__init__(language, "", row, col, offset, "block")
        self._childToIndex = {}

    def addStatement(self, statement):
        assert isinstance(statement, ASTNode)
        self._childToIndex[statement] = len(self.children)
        self.children.append(statement)
        statement.parent = self
        self.code += statement.reconstructCode()
        
    def nextChild(self, previous):
        if previous in self._childToIndex:
            index = self._childToIndex[previous] + 1
            if index < len(self.children):
                return self.children[index]
        return None
        
    def previousChild(self, next):
        if next in self._childToIndex:
            index = self._childToIndex[next] - 1
            if index >= 0 and len(self.children) > 0:
                return self.children[index]
        return None
        
    #def find(self, selector):
    #    pass

class ImportNode(ASTNode):
    def __init__(self, node, resource, alias):
        super().__init__(
            node.language, 
            node.code, 
            node.row, 
            node.col, 
            node.offset, 
            node.type
        )
        self._resource = resource
        self._alias = alias
        
class AsImportNode(NodePattern):
    def __init__(self, pattern, resourceGetter, aliasGetter):
        self._pattern = pattern
        self._resourceGetter = resourceGetter
        self._aliasGetter = aliasGetter
    
    def matches(self, nodes):
        return self._pattern.matches(nodes)

    def consume(self, nodes):
        (success, remainingNodes, producedNodes) = self._pattern.consume(nodes)
        
        if success:
            node = ASTBranch(producedNodes, 'import')
            resource = self._resourceGetter(node)
            alias = self._aliasGetter(node)
            
            return (success, remainingNodes, [
                ImportNode(node, resource, alias)
            ])
        else:
            return (success, remainingNodes, producedNodes)
