"""
Converts an N-ary tree structure to a Left-Child Right-Sibling (LCRS) tree structure.
N-ary representation uses a list of children for each node, while LCRS uses
left pointer for first child and right pointer for next sibling.
"""

from src.rpal_ast import ASTNode
from src.standerizer.node import Node  # n-ary Node class

def nary_to_lcrs(nary_node):
    """
    Recursively converts an N-ary tree node to an LCRS tree node.
    
    Args:
        nary_node: Root node of the N-ary tree (Node)
    
    Returns:
        ASTNode: Converted LCRS tree node, or None if input is None
        
    Note:
        The conversion follows these rules:
        - First child becomes left pointer
        - Remaining children become right siblings of the first child
    """
    if nary_node is None:
        return None

    # Create LCRS node with same data as N-ary node
    lcrs_node = ASTNode(nary_node.data)

    # Convert children if they exist
    if nary_node.children:
        # First child becomes the left child in LCRS
        lcrs_node.left = nary_to_lcrs(nary_node.children[0])

        # Convert remaining children to right siblings
        current = lcrs_node.left
        for child in nary_node.children[1:]:
            current.right = nary_to_lcrs(child)
            current = current.right

    return lcrs_node
