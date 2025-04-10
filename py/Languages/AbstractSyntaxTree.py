
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

    def find(self, selector): # list[ASTNode]
        result = []
        for child in children:
            result += child.find(selector)
        if callable(selector):
            if selector(self):
                result.append(self)
        elif type(selector) == str:
            if self.grammarKey() == str:
                result.append(self)
        return result
        
    def offsetIn(self, nodes):
        for index in range(0, len(nodes)):
            if nodes[index] == self:
                return index
        return None
        
    def grammarKey(self):
        return self.type

class ASTBranch(ASTNode):
    def __init__(self, children, type, parent=None):
        firstChild = children[0]
        code = ""
        for child in children:
            code += child.reconstructCode()
            child.parent = self
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
    