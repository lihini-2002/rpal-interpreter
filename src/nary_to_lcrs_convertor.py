from src.rpal_ast import ASTNode
from src.standerizer.node import Node  # n-ary Node class

def nary_to_lcrs(nary_node):
    if nary_node is None:
        return None

    # Create the root ASTNode
    lcrs_node = ASTNode(nary_node.data)

    # If there are children, convert the first to `left` and the rest as right siblings
    if nary_node.children:
        # Convert the first child and assign as left
        lcrs_node.left = nary_to_lcrs(nary_node.children[0])

        # Chain the rest as right siblings
        current = lcrs_node.left
        for child in nary_node.children[1:]:
            current.right = nary_to_lcrs(child)
            current = current.right

    return lcrs_node
