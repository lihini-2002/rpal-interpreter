class ASTNode:
    def __init__(self, label):
        self.label = label       # Node label (e.g., '+', 'assign', '<ID:x>')
        self.left = None         # First child
        self.right = None        # Next sibling

def build_tree(label, n, stack):
    p = None
    for _ in range(n):
        c = stack.pop()
        c.right = p
        p = c
    node = ASTNode(label)
    node.left = p
    stack.append(node)

def print_ast(node, indent=0):
    while node:
        print("." * indent + node.label)
        if node.left:
            print_ast(node.left, indent + 1)
        node = node.right
