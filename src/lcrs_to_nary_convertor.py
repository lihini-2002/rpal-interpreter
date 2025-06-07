"""
Converts a Left-Child Right-Sibling (LCRS) tree structure to an N-ary tree structure.
LCRS representation uses left pointer for first child and right pointer for next sibling,
while N-ary representation uses a list of children for each node.
"""

from src.rpal_ast import ASTNode
from src.standerizer.node import Node

def lcrs_to_nary(lcrs_root, depth=0):
    """
    Recursively converts an LCRS tree node to an N-ary tree node.
    
    Args:
        lcrs_root: Root node of the LCRS tree (ASTNode)
        depth: Current depth in the tree (default: 0)
    
    Returns:
        Node: Converted N-ary tree node, or None if input is None
    """
    if lcrs_root is None:
        return None

    # Create new N-ary node with same label and depth
    nary_node = Node()
    nary_node.set_data(lcrs_root.label)
    nary_node.set_depth(depth)

    # Convert LCRS structure to N-ary:
    # - left pointer becomes first child
    # - right pointer becomes next sibling (next child of parent)
    child = lcrs_root.left
    while child:
        converted_child = lcrs_to_nary(child, depth + 1)
        converted_child.set_parent(nary_node)
        nary_node.children.append(converted_child)
        child = child.right

    return nary_node
