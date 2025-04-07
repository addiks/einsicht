
class ASTNode:
    def __init__(self, language, code, row, col, offset, type):
        self.language = language
        self.code = code
        self.row = row
        self.col = col
        self.offset = offset
        self.type = type
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

    def find(self, selector):
        pass
        
    def offsetIn(self, nodes):
        for index in range(0, len(nodes)):
            if nodes[index] == self:
                return index
        return None
        
    def grammarKey(self):
        return self.type

class ASTBranch(ASTNode):
    def __init__(self, children, type):
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
        self.children = children
