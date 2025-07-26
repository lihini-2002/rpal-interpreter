"""
Utility functions for manipulating Abstract Syntax Tree (AST) nodes in Left-Child Right-Sibling (LCRS) representation.
These functions provide convenient ways to work with the LCRS tree structure by converting between
list-based children access and the LCRS pointer-based representation.
"""

def get_children(node):
    """
    Converts the LCRS representation of children into a list.
    Traverses the right-sibling chain starting from the left child.
    
    Args:
        node: AST node whose children to retrieve
        
    Returns:
        list: List of child nodes in order from left to right
    """
    children = []
    child = node.left
    while child:
        children.append(child)
        child = child.right
    return children

def set_children(node, children):
    """
    Sets the children of a node using LCRS representation.
    Converts a list of children into the appropriate left-child and right-sibling pointers.
    
    Args:
        node: Parent node to set children for
        children: List of child nodes to attach (can be empty)
    """
    if not children:
        node.left = None
        return
        
    # Set first child as left pointer
    node.left = children[0]
    
    # Connect remaining children as right siblings
    for i in range(len(children) - 1):
        children[i].right = children[i + 1]
    children[-1].right = None
