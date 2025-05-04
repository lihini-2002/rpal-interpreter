from src.rpal_ast import ASTNode
from utils import get_children, set_children

def standardize(node: ASTNode) -> ASTNode:
    """
    Entry point: recursively transforms the AST into standard form.
    """
    if node is None:
        return None

    # Standardize children first (post-order traversal)
    children = get_children(node)
    standardized = [standardize(child) for child in children]
    set_children(node, standardized)

    # Apply specific transformation rule if applicable
    return apply_transformation(node)

def apply_transformation(node: ASTNode) -> ASTNode:
    label = node.label
    children = get_children(node)

    # Rule 1: let => gamma(lambda x . E) E
    if label == "let":
        eq = children[0]
        body = children[1]
        eq_children = get_children(eq)
        x = eq_children[0]
        e = eq_children[1]

        lambda_node = ASTNode("lambda")
        set_children(lambda_node, [x, body])

        gamma_node = ASTNode("gamma")
        set_children(gamma_node, [lambda_node, e])
        return gamma_node

    # Rule 2: where => gamma(lambda x . body, e)
    if label == "where":
        body = children[0]
        eq = children[1]
        eq_children = get_children(eq)
        x = eq_children[0]
        e = eq_children[1]

        lambda_node = ASTNode("lambda")
        set_children(lambda_node, [x, body])

        gamma_node = ASTNode("gamma")
        set_children(gamma_node, [lambda_node, e])
        return gamma_node

    # Rule 3: @ => gamma(E1, E2)
    if label == "@":
        E1, E2 = children
        gamma_node = ASTNode("gamma")
        set_children(gamma_node, [E1, E2])
        return gamma_node

    if label == "tau":
        exprs = get_children(node)

        # Create gamma(aug, .nil)
        gamma_inner = ASTNode("gamma")
        set_children(gamma_inner, [ASTNode("aug"), ASTNode(".nil")])

        # Nest expressions on top: gamma(..., E1, E2, ...)
        gamma = ASTNode("gamma")
        set_children(gamma, [gamma_inner] + exprs)
        return gamma

    if label == "not":
        E = children[0]
        gamma = ASTNode("gamma")
        set_children(gamma, [ASTNode("not"), E])
        return gamma

    if label == "within":
        first_eq = children[0]
        second_eq = children[1]

        X1, E1 = get_children(first_eq)
        X2, E2 = get_children(second_eq)

        # lambda X1 . E2
        lambda_node = ASTNode("lambda")
        set_children(lambda_node, [X1, E2])

        # gamma(lambda X1 . E2, E1)
        gamma_node = ASTNode("gamma")
        set_children(gamma_node, [lambda_node, E1])

        # = (X2, gamma(...))
        eq_node = ASTNode("=")
        set_children(eq_node, [X2, gamma_node])

        return eq_node

    if label == "->":
        B, T, E = children

        # lambda ( ) . T
        empty_tuple = ASTNode("()")
        lambda_then = ASTNode("lambda")
        set_children(lambda_then, [empty_tuple, T])

        gamma_cond = ASTNode("gamma")
        set_children(gamma_cond, [ASTNode("Cond"), B])

        gamma_then = ASTNode("gamma")
        set_children(gamma_then, [gamma_cond, lambda_then])

        # lambda ( ) . E
        lambda_else = ASTNode("lambda")
        set_children(lambda_else, [empty_tuple, E])

        inner_gamma = ASTNode("gamma")
        set_children(inner_gamma, [ASTNode("nil"), gamma_then])

        outer_gamma = ASTNode("gamma")
        set_children(outer_gamma, [inner_gamma, lambda_else])
        return outer_gamma

    if label == "neg":
        E = children[0]
        gamma = ASTNode("gamma")
        set_children(gamma, [ASTNode("neg"), E])
        return gamma

    if label == "rec":
        eq_node = children[0]
        X, E = get_children(eq_node)

        lambda_node = ASTNode("lambda")
        set_children(lambda_node, [X, E])

        gamma_node = ASTNode("gamma")
        set_children(gamma_node, [ASTNode("Ystar"), lambda_node])

        eq_transformed = ASTNode("=")
        set_children(eq_transformed, [X, gamma_node])
        return eq_transformed

    if label == "function_form":
        P = children[0]      # Function name
        params = get_children(children[1])  # V++
        E = children[2]      # Function body

        # Build nested lambdas from last param to first
        current = E
        for param in reversed(params):
            lam = ASTNode("lambda")
            set_children(lam, [param, current])
            current = lam

        eq_node = ASTNode("=")
        set_children(eq_node, [P, current])
        return eq_node

    if label == "and":
        eqs = get_children(children[0])  # The =++ node
        Xs = []
        Es = []

        for eq in eqs:
            xi, ei = get_children(eq)
            Xs.append(xi)
            Es.append(ei)

        tau_left = ASTNode("tau")
        set_children(tau_left, Xs)

        tau_right = ASTNode("tau")
        set_children(tau_right, Es)

        eq_node = ASTNode("=")
        set_children(eq_node, [tau_left, tau_right])
        return eq_node

    if label == "lambda":
        V_or_tuple = children[0]
        E = children[1]

        # Case 1: lambda with multiple parameters (V++)
        params = get_children(V_or_tuple)
        if len(params) > 1:
            # Curry them into nested lambdas
            current = E
            for param in reversed(params):
                lam = ASTNode("lambda")
                set_children(lam, [param, current])
                current = lam
            return current

        # Case 2: lambda (X, i)  -- tuple binding with integer
        elif V_or_tuple.label == ",":
            parts = get_children(V_or_tuple)
            if len(parts) == 2 and parts[1].label.startswith("<INT:"):
                xi = ASTNode(".")           # Dot access node: X.i
                set_children(xi, parts)     # children = [X, i]

                dotE = ASTNode(".")         # Dot access for function body
                set_children(dotE, [E, parts[1]])

                lam_inner = ASTNode("lambda")
                set_children(lam_inner, [xi, dotE])

                gamma = ASTNode("gamma")
                set_children(gamma, [ASTNode("lambda"), lam_inner, ASTNode("Temp")])

                lam_outer = ASTNode("lambda")
                set_children(lam_outer, [ASTNode("Temp"), gamma])
                return lam_outer

        # Otherwise, return as-is (already standard)
        return node

    # Handle binary operators
    binary_operators = {
        "aug", "or", "&", "+", "-", "/", "*", "**", "gr", "ge", "ls", "le", "eq", "ne"
    }

    if label in binary_operators:
        E1, E2 = children

        # gamma(Op, E1)
        gamma_inner = ASTNode("gamma")
        set_children(gamma_inner, [ASTNode(label), E1])

        # gamma(gamma(Op, E1), E2)
        gamma_outer = ASTNode("gamma")
        set_children(gamma_outer, [gamma_inner, E2])
        return gamma_outer

    return node  # No change if no rule applies
