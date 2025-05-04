from src.rpal_ast import ASTNode
from src.utils import get_children
from typing import List, Tuple

control_structures = []  # List of lists (one per lambda body)
control_index = 0        # Global control structure index

def generate_control(node: ASTNode) -> List:
    global control_structures, control_index
    control_structures.clear()  # ✅ Do this instead of reassigning
    control_index = 0

    control = []
    _traverse(node, control)
    return control

def _traverse(node: ASTNode, control: List):
    global control_structures, control_index
    if node is None:
        return

    print(f"Visiting: {node.label}")
    label = node.label
    children = get_children(node)

    # Handle lambda node: lambda X . E
    if label == "lambda":
        param = children[0]
        body = children[1]

        current_index = control_index
        control_index += 1

        new_control = []
        _traverse(body, new_control)
        control_structures.append((current_index, new_control))

        print(f"Recording lambda {current_index} with param: {param.label}")
        control.append(("lambda", current_index, param.label))

    elif label == "gamma":
        _traverse(children[0], control)  # ✅ function first
        _traverse(children[1], control)  # ✅ argument second
        control.append("gamma")

    elif label == "tau":
        for child in reversed(children):
            _traverse(child, control)
        control.append(f"tau {len(children)}")

    elif label.startswith("<") and label.endswith(">"):
        control.append(label)

    else:
        for child in children:
            _traverse(child, control)
        control.append(label)  # Now using post-order

