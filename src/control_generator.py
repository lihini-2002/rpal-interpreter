from src.rpal_ast import ASTNode
from src.utils import get_children
from typing import List, Tuple

control_structures = []  # List of lists (one per lambda body)
control_index = 0        # Global control structure index

def _traverse(node: ASTNode, control: List):
    if node is None:
        return

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
        control.append(("lambda", current_index, param.label))

    # Handle binary gamma
    elif label == "gamma":
        control.append("gamma")
        _traverse(children[0], control)
        _traverse(children[1], control)

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

def generate_control(node: ASTNode) -> List:
    """
    Entry point to generate control structure from a standardized AST.
    Returns a flat list of control instructions.
    """
    global control_structures, control_index
    control_structures = []
    control_index = 0

    control = []
    _traverse(node, control)
    return control
