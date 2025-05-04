def get_children(node):
    children = []
    child = node.left
    while child:
        children.append(child)
        child = child.right
    return children

def set_children(node, children):
    if not children:
        node.left = None
        return
    node.left = children[0]
    for i in range(len(children) - 1):
        children[i].right = children[i + 1]
    children[-1].right = None
