
class ASTNode:
    def __init__(self, language, code, row, col, offset, type, parent=None):
        self.language = language
        self.code = code
        self.row = row
        self.col = col
        self.offset = offset
        self.type = type
        self.parent = parent
        self.children = []
        
        # Nodes in these two categories are part of the AST but have no semantic impact.
        # F.e.: Whitespace, Comments, ...
        self.prepended = []
        self.appended = []

    def prepend(self, node):
        self.prepended.append(node)
        
    def append(self, node):
        self.appended.append(node)

    def reconstructCode(self):
        code = ""
        for predecessor in self.prepended:
            code += predecessor.reconstructCode()
        code += self.code
        for successor in self.appended:
            code += successor.reconstructCode()
        return code
        
    def matches(self, selector): # bool
        if callable(selector):
            return selector(self)
        elif type(selector) == str:
            return self.grammarKey() == selector

    def find(self, selector): # list[ASTNode]
        result = []
        for child in self.children:
            result += child.find(selector)
        if self.matches(selector):
            result.append(self)
        return result
        
    def findInPrepended(self, selector): # list[ASTNode]
        result = []
        if len(self.children) > 0:
            result = self.children[0].findInPrepended(selector)
        for child in self.prepended:
            result += child.find(selector)
        if self.matches(selector):
            result.append(self)
        return result
        
    def findInAppended(self, selector): # list[ASTNode]
        result = []
        if len(self.children) > 0:
            result = self.children[-1].findInAppended(selector)
        for child in self.appended:
            result += child.find(selector)
        if self.matches(selector):
            result.append(self)
        return result
        
    def hasParentWith(self, selector): # bool
        if self.parent != None:
            if self.parent.matches(selector):
                return True
            if self.parent.hasParentWith(selector):
                return True
        return False
        
    def offsetIn(self, nodes):
        for index in range(0, len(nodes)):
            if nodes[index] == self:
                return index
        return None
        
    def grammarKey(self):
        return self.type
        
    def next(self):
        if self.parent != None:
            return self.parent.nextChild(self)
        return None
            
    def previous(self):
        if self.parent != None:
            return self.parent.previousChild(self)
        return None
            
    def nextChild(self, previous):
        return None
        
    def previousChild(self, next):
        return None

class ASTBranch(ASTNode):
    def __init__(self, children, type, parent=None):
        firstChild = children[0]
        self._childToIndex = {}
        code = ""
        index = 0
        for child in children:
            code += child.reconstructCode()
            child.parent = self
            self._childToIndex[child] = index
            index += 1
        super().__init__(
            firstChild.language,
            code,
            firstChild.row,
            firstChild.col,
            firstChild.offset,
            type,
            parent
        )
        self.children = children
        self.parent = parent
    
    def nextChild(self, previous):
        index = self._childToIndex[previous] + 1
        if index < len(self.children):
            return self.children[index]
        else:
            return None
        
    def previousChild(self, next):
        index = self._childToIndex[next] - 1
        if index >= 0:
            return self.children[index]
        else:
            return None