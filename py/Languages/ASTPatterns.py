
from .AbstractSyntaxTree import ASTNode, ASTBranch

class NodePattern:
    def matches(self, nodes, index): # boolean
        raise NotImplementedError

    def nodeKeys(self): # list(string)
        # Identifies the type of (starting-) AST node that this pattern would match
        # F.e.: "T_BLAH", "method-call", "identifier", ...
        raise NotImplementedError
        
    def producedNodeKey(self): # string
        # node- / grammar-key that new nodes of this pattern would have
        raise NotImplementedError
        
    def mutate(self, nodes, index): # return (replacedNodes, newNodeIndex)
        # mutates nodes to combine some nodes into a new node
        #
        # returns all nodes that were removed as replacedNodes
        # returns the index of the newly created node as newNodeIndex
        # if no mutation happened, original index is returned as newNodeIndex
        # On failure, None is returned as newNodeIndex (has to be handled by caller)
        raise NotImplementedError
        
class OptionalNode(NodePattern):
    def __init__(self, pattern):
        assert isinstance(pattern, (str, ASTNode, NodePattern))
        self.pattern = pattern

    def matches(self, nodes, index):
        return True

    def nodeKeys(self): # list(string)
        return self.pattern.nodeKeys()
        
    def producedNodeKey(self): # string
        return self.pattern.producedNodeKey()
        
    def mutate(self, nodes, index): # return (replacedNodes, newNodeIndex)
        if self.pattern.matches(nodes, index):
            return self.pattern.mutate(nodes, index)
        return ([], None)
        
class NodeSequence(NodePattern):
    def __init__(self, sequenceType, elements):
        self._elements = elements
        self._sequenceType = sequenceType

    def nodeKeys(self): # list(string)
        return [self._elements[0].producedNodeKey()]
        
    def producedNodeKey(self): # string
        return self._sequenceType
        
    def matches(self, nodes, index):
        nodes = nodes.copy()
        for pattern in self._elements:
            if len(nodes) <= index:
                break
            if pattern.matches(nodes, index):
                (replacedNodes, newNodeIndex) = pattern.mutate(nodes, index)
                #if newNodeIndex == None:
                #    return False
                if newNodeIndex != None:
                    index = newNodeIndex + 1
            elif pattern.producedNodeKey() == nodes[index].grammarKey():
                index += 1
            else:
                return False
        return True

    def mutate(self, nodes, index): # return (replacedNodes, newNodeIndex)
        allNewNodes = []
        allReplacedNodes = []
        
        start = index
        end = index
        
        for pattern in self._elements:
            if len(nodes) <= index:
                break
            if pattern.matches(nodes, index):
                (replacedNodes, newNodeIndex) = pattern.mutate(nodes, index)
                if newNodeIndex != None:
                    allNewNodes.append(nodes[newNodeIndex])
                    allReplacedNodes += replacedNodes
                    start = min(start, newNodeIndex)
                    end = max(end, newNodeIndex)
                    index = newNodeIndex + 1
            elif pattern.producedNodeKey() == nodes[index].grammarKey():
                allNewNodes.append(nodes[index])
                start = min(start, index)
                end = max(end, index)
                index += 1
                
        for subIndex in reversed(range(start + 1, end + 1)):
            nodes.pop(subIndex)
                
        nodes[start] = ASTBranch(allNewNodes, self._sequenceType)
        
        return (allReplacedNodes, start)
        
class NodeBranch(NodePattern):
    def __init__(self, newNodeType, patterns):
        self._newNodeType = newNodeType
        self._patternMap = {}
        for pattern in patterns:
            assert isinstance(pattern, NodePattern)
            nodeKey = pattern.producedNodeKey()
            if nodeKey not in self._patternMap:
                self._patternMap[nodeKey] = []
            self._patternMap[nodeKey].append(pattern)
    
    def nodeKeys(self): # list(string)
        return self._patternMap.keys()
        
    def producedNodeKey(self): # string
        return self._newNodeType
        
    def matches(self, nodes, index):
        nodeKey = nodes[index].grammarKey()
        if nodeKey in self._patternMap:
            for pattern in self._patternMap[nodeKey]:
                if pattern.producedNodeKey() == nodes[index].grammarKey():
                    return True
                if pattern.matches(nodes, index):
                    return True
        return False

    def mutate(self, nodes, index): # return (replacedNodes, newNodeIndex)
        nodeKey = nodes[index].grammarKey()
        if nodeKey in self._patternMap:
            for pattern in self._patternMap[nodeKey]:
                if pattern.producedNodeKey() == nodes[index].grammarKey():
                    replacedNode = nodes[index]
                    nodes[index] = ASTBranch([nodes[index]], self._newNodeType)
                    return ([replacedNode], index)
                if pattern.matches(nodes, index):
                    (replacedNodes, newNodeIndex) = pattern.mutate(nodes, index)
                    nodes[newNodeIndex] = ASTBranch([nodes[newNodeIndex]], self._newNodeType)
                    return (replacedNodes, newNodeIndex)
        return ([], None)
        
class RepeatingNode(NodePattern):
    def __init__(self, elementType, pattern, optional):
        self._pattern = pattern
        self._optional = optional
        self._elementType = elementType

    def nodeKeys(self): # list(string)
        return self._pattern.nodeKeys()
        
    def producedNodeKey(self): # string
        return self._elementType
        
    def matches(self, nodes, index):
        if self._optional:
            return True
        else:
            return self._pattern.matches(nodes, index)

    def mutate(self, nodes, index): # return (replacedNodes, newNodeIndex)
        allReplacedNodes = []
        allNewNodes = []
        start = index
        end = index
        
        nodeKeys = self.nodeKeys()
        while True:
            if len(nodes) <= index:
                break
            #if self._pattern.producedNodeKey() == "tuple-element":
            #    breakpoint()
            if self._pattern.matches(nodes, index):
                (replacedNodes, newNodeIndex) = self._pattern.mutate(nodes, index)
                
                start = min(start, newNodeIndex)
                end = max(end, newNodeIndex)
                
                allReplacedNodes += replacedNodes
                allNewNodes.append(nodes[newNodeIndex])
                
                index = newNodeIndex + 1
            elif nodes[index].grammarKey() == self._pattern.producedNodeKey():
                index += 1
            else:
                break
            
        for subIndex in reversed(range(start + 1, end + 1)):
            nodes.pop(subIndex)
            
        if len(allNewNodes) > 0:
            nodes[start] = ASTBranch(allNewNodes, self._elementType)
        else:
            start = None
        
        return (allReplacedNodes, start)
            
class LateDefinedASTPattern(NodePattern):
    def __init__(self, producedNodeKey=None):
        self._pattern = None
        self._producedNodeKey = producedNodeKey
        
    def definePattern(self, pattern):
        self._pattern = pattern

    def nodeKeys(self): # list(string)
        assert isinstance(self._pattern, NodePattern)
        return self._pattern.nodeKeys()
        
    def producedNodeKey(self): # string
        if self._producedNodeKey != None:
            return self._producedNodeKey
        assert isinstance(self._pattern, NodePattern)
        return self._pattern.producedNodeKey()
        
    def matches(self, nodes, index):
        assert isinstance(self._pattern, NodePattern)
        return self._pattern.matches(nodes, index)

    def mutate(self, nodes, index): # return (replacedNodes, newNodeIndex)
        assert isinstance(self._pattern, NodePattern)
        return self._pattern.mutate(nodes, index)
        