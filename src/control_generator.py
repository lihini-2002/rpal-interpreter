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

        # Create control structure for lambda body (new index)
        current_index = control_index
        control_index += 1

        new_control = []
        _traverse(body, new_control)
        control_structures.append((current_index, new_control))

        # Add <lambda i param> instruction
        print(f"Recording lambda {current_index} with param: {param.label}")
        control.append(("lambda", current_index, param.label))

    # Handle binary gamma
    elif label == "gamma":
        _traverse(children[1], control)  # First: right (argument)
        _traverse(children[0], control)  # Then: left (function)
        control.append("gamma")          # Then: gamma instruction


    # Handle constants and names (leaf nodes)
    elif label.startswith("<") and label.endswith(">"):
        control.append(label)

    # Handle conditional
    elif label == "->":
        pass  # already standardized as nested lambdas — no need to handle here

    # Handle tau
    elif label == "tau":
        control.append(f"tau {len(children)}")
        # Right-to-left evaluation
        for child in reversed(children):
            _traverse(child, control)

    else:
        # For all other operators (like +, not, neg, etc.)
        control.append(label)
        for child in children:
            _traverse(child, control)

