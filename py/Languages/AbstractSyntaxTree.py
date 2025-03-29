
### NODE PATTERNS

class NodePattern:
    def matches(self, nodes):
        raise NotImplementedError

    def consume(self, nodes): # return (success, remainingNodes, producedNodes)
        raise NotImplementedError

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
    def __init__(self, elements):
        self._elements = elements

    def matches(self, nodes):
        for pattern in self._elements:
            if len(nodes) <= 0:
                break
            if not pattern.matches(nodes):
                return False
            else:
                (success, nodes, producedNodes) = pattern.consume(nodes.copy())
                if not success:
                    False
        return True

    def consume(self, nodes):
        newNodes = []
        success = False
        for pattern in self._elements:
            if len(nodes) <= 0:
                break
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
        for pattern in self._patterns:
            assert isinstance(pattern, NodePattern)
    
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
    def __init__(self, pattern, optional):
        self._pattern = pattern
        self._optional = optional

    def matches(self, nodes):
        if self._optional:
            return True
        else:
            return self._pattern.matches(nodes)

    def consume(self, nodes):
        newNodes = []
        hasAtLeastOneSuccessful = False
        while len(nodes) > 0 and self._pattern.matches(nodes):
            (success, remainingNodes, producedNodes) = self._pattern.consume(nodes)
            if success:
                nodes = remainingNodes
                newNodes = newNodes + producedNodes
                hasAtLeastOneSuccessful = True
            else:
                break
        if self._optional:
            return (True, nodes, newNodes)
        else:
            return (hasAtLeastOneSuccessful, nodes, newNodes)

class NodesAsASTBranch(NodePattern):
    def __init__(self, astType, pattern):
        self._pattern = pattern
        self._astType = astType

    def matches(self, nodes):
        return self._pattern.matches(nodes)

    def consume(self, nodes):
        (success, remainingNodes, producedNodes) = self._pattern.consume(nodes)
        #print(["ASD", success, producedNodes])
        if success:
            return (success, remainingNodes, [ASTBranch(producedNodes, self._astType)])
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
        
        # Nodes in these two categories are part of the AST but have no semantic impact.
        # F.e.: Whitespace, Comments, ...
        self.prepended = []
        self.appended = []

    def prepend(self, node):
        self.prepended.append(node)
        
    def append(self, node):
        self.appended.append(node)

    def children(self):
        return []
        
    def reconstructCode(self):
        code = ""
        for predecessor in self.prepended:
            code += predecessor.reconstructCode()
        code += self.code
        for successor in self.appended:
            code += successor.reconstructCode()
        return code

    def find(self, selector):
        pass

class ASTBranch(ASTNode):
    def __init__(self, children, type):
        self.children = children
        firstChild = children[0]
        code = ""
        for child in children:
            code += child.reconstructCode()
        super().__init__(
            firstChild.language,
            code,
            firstChild.row,
            firstChild.col,
            firstChild.offset,
            type
        )


