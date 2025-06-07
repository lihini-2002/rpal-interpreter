"""
Implementation of Abstract Syntax Tree (AST) nodes using Left-Child Right-Sibling (LCRS) representation.
This representation uses two pointers per node: left for first child and right for next sibling,
which allows efficient tree traversal and manipulation.
"""

class ASTNode:
    """
    Represents a node in the Abstract Syntax Tree using LCRS representation.
    Each node has a label and two pointers: left for first child and right for next sibling.
    """
    def __init__(self, label):
        self.label = label       # Node label (e.g., '+', 'assign', '<ID:x>')
        self.left = None         # Pointer to first child
        self.right = None        # Pointer to next sibling

def build_tree(label, n, stack):
    """
    Builds a tree node with n children from the stack.
    The children are popped from the stack in reverse order and connected as siblings.
    
    Args:
        label: Label for the new tree node
        n: Number of children to attach
        stack: Stack containing the child nodes
    """
    p = None
    # Pop n children and connect them as siblings
    for _ in range(n):
        c = stack.pop()
        c.right = p
        p = c
    
    # Create new node and attach children
    node = ASTNode(label)
    node.left = p
    stack.append(node)

def print_ast(node, indent=0):
    """
    Prints the AST in a tree-like structure using indentation.
    Traverses the tree in pre-order, printing each node with appropriate indentation.
    
    Args:
        node: Root node of the tree to print
        indent: Current indentation level (default: 0)
    """
    while node:
        print("." * indent + node.label)
        if node.left:
            print_ast(node.left, indent + 1)
        node = node.right
