# Converts your LCRS-based ASTNode to senior-style Node
from src.rpal_ast import ASTNode
from src.standerizer.node import Node

def lcrs_to_nary(lcrs_root, depth=0):
    if lcrs_root is None:
        return None

    # Create a new Node
    nary_node = Node()
    nary_node.set_data(lcrs_root.label)
    nary_node.set_depth(depth)

    # Convert children (LCRS left -> first child, right -> next sibling)
    child = lcrs_root.left
    while child:
        converted_child = lcrs_to_nary(child, depth + 1)
        converted_child.set_parent(nary_node)
        nary_node.children.append(converted_child)
        child = child.right

    return nary_node
